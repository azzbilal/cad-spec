"""Sandbox export, independent BREP inspection, and code sensitivity tests.

No scorer implementation is replaced. Model code is executed only by score.
Export appends a trusted BREP write to the sandboxed completion; its result
and complete score are checked against the uninstrumented recorded result.
Independent inspection never calls cad_spec.measure's measurement functions.
"""
import ast
import collections
import hashlib
import itertools
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'environments/cad_spec'))
os.environ.pop('CAD_SPEC_INPROC', None)
os.environ['CAD_SPEC_SANDBOX']='reuse'
from cad_spec.measure import extract_code, shutdown_worker
from cad_spec.rubric import score
from cad_spec.tasks import make_test_split

OUT = ROOT/'audit/scratch'
BREPS = OUT/'run1-breps'

def rows():
    return [r for line in (ROOT/'results/training/run1/eval/adapter-test.jsonl').read_text(encoding='utf-8').splitlines()
            if 'tier' in (r:=json.loads(line))]

def inspect(path,spec):
    import cadquery as cq
    shape = cq.importers.importBrep(str(path)).val()
    bb=shape.BoundingBox()
    volume=shape.Volume()
    cylinders=[]
    face_types=collections.Counter()
    for f in shape.Faces():
        kind=f.geomType()
        face_types[kind]+=1
        if kind=='CYLINDER':
            cyl=f._geomAdaptor().Cylinder()
            p=cyl.Location()
            direction=cyl.Axis().Direction()
            fb=f.BoundingBox()
            cylinders.append(dict(x=p.X(),y=p.Y(),diameter=2*cyl.Radius(),axis=[direction.X(),direction.Y(),direction.Z()],
                z_min=fb.zmin,z_max=fb.zmax,area=f.Area()))
    expected=sorted((sx*spec.pitch_x/2,sy*spec.pitch_y/2,spec.hole_diameter) for sx in (-1,1) for sy in (-1,1))
    actual=sorted((h['x'],h['y'],h['diameter']) for h in cylinders)
    exact=lambda a,b: abs(a-b)<1e-5
    envelope=[bb.xlen,bb.ylen,bb.zlen]
    target=[spec.length,spec.width,spec.thickness]
    datum=[(bb.xmin+bb.xmax)/2,(bb.ymin+bb.ymax)/2,(bb.zmin+bb.zmax)/2]
    max_position_error=max((math.dist(a,b) for a,b in zip(actual,expected)),default=0) if len(actual)==4 else None
    checks=dict(envelope=all(exact(a,b) for a,b in zip(envelope,target)),
        datum=all(exact(a,0) for a in datum),holes=len(actual)==4 and all(all(exact(a,b) for a,b in zip(h,t)) for h,t in zip(actual,expected)),
        through=len(cylinders)==4 and all(exact(h['z_min'],-spec.thickness/2) and exact(h['z_max'],spec.thickness/2) and abs(abs(h['axis'][2])-1)<1e-8 for h in cylinders),
        volume=abs(volume-spec.ideal_volume)<1e-5*max(1,spec.ideal_volume),valid=shape.isValid(),single_solid=len(shape.Solids())==1,
        face_inventory=dict(face_types)=={'PLANE':6,'CYLINDER':4})
    # Independent oracle uses primitive cylinders and boolean subtraction,
    # rather than the model's workplane/hole API or the scorer's bore probes.
    ideal=cq.Workplane('XY').box(spec.length,spec.width,spec.thickness).val()
    for x,y,d in expected:
        cutter=cq.Solid.makeCylinder(d/2,spec.thickness+2,cq.Vector(x,y,-spec.thickness/2-1),cq.Vector(0,0,1))
        ideal=ideal.cut(cutter)
    missing=ideal.cut(shape).Volume()
    extra=shape.cut(ideal).Volume()
    checks['symmetric_difference']=abs(missing)+abs(extra)<1e-5
    return dict(envelope=envelope,datum=datum,volume=volume,ideal_volume=spec.ideal_volume,
        cylinders=cylinders,face_types=dict(face_types),checks=checks,pass_exact=all(checks.values()),
        max_position_error=max_position_error,missing_volume=missing,extra_volume=extra)

class Perturb(ast.NodeTransformer):
    def __init__(self,kind,delta):
        self.kind=kind
        self.delta=delta
        self.edits=[]
    def visit_Call(self,node):
        self.generic_visit(node)
        if not isinstance(node.func,ast.Attribute): return node
        attr=node.func.attr
        if self.kind=='diameter' and attr=='hole':
            before=ast.unparse(node.args[0])
            node.args[0]=ast.BinOp(left=node.args[0],op=ast.Add(),right=ast.Constant(self.delta))
            self.edits.append({'before':before,'after':ast.unparse(node.args[0]),'line':node.lineno})
        if self.kind=='length' and attr=='box':
            before=ast.unparse(node.args[0])
            node.args[0]=ast.BinOp(left=node.args[0],op=ast.Add(),right=ast.Constant(self.delta))
            self.edits.append({'before':before,'after':ast.unparse(node.args[0]),'line':node.lineno})
        if self.kind=='pitch' and attr=='rect':
            before=ast.unparse(node.args[0])
            node.args[0]=ast.BinOp(left=node.args[0],op=ast.Add(),right=ast.Constant(self.delta))
            self.edits.append({'before':before,'after':ast.unparse(node.args[0]),'line':node.lineno})
        if self.kind=='pitch' and attr=='pushPoints':
            before=ast.unparse(node.args[0])
            # Increase total X pitch by delta, moving each signed X axis by delta/2.
            node.args[0]=ast.parse(f'[(x + ({self.delta}/2 if x >= 0 else -{self.delta}/2), y) for x,y in ({before})]',mode='eval').body
            self.edits.append({'before':before,'after':ast.unparse(node.args[0]),'line':node.lineno})
        return node

def main():
    BREPS.mkdir(parents=True,exist_ok=True)
    specs={s.id:s for s in make_test_split()}
    data=[]
    for i,row in enumerate(rows()):
        path=BREPS/f"{row['tier']}-{row['spec_id']}.brep"
        code=extract_code(row['completion'])
        # The audited answers all use an ordinary CadQuery Workplane result.
        instrument=code+'\nresult.val().exportBrep('+repr(str(path))+')\n'
        rep=score(instrument,specs[row['spec_id']])
        checks={c.name:c.passed for c in rep.checks}
        rec=dict(tier=row['tier'],spec_id=row['spec_id'],recorded_pass=row['reward']==1,
            export_score_equal=rep.reward==row['reward'] and checks==row['checks'],
            brep=str(path.relative_to(ROOT)).replace('\\','/'),brep_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        rec.update(inspect(path,specs[row['spec_id']]))
        data.append(rec)
        if (i+1)%60==0: print(f'Independent geometry {i+1}/240',flush=True)
    shutdown_worker()
    # 24 passing answers: four each L1-L3, twelve L4. Deterministic first specs.
    selected=[]
    for tier,n in [('L1',4),('L2',4),('L3',4),('L4',12)]:
        selected.extend([r for r in rows() if r['tier']==tier and r['reward']==1][:n])
    mutants=[]
    mdir=OUT/'run1-perturbations'
    mdir.mkdir(exist_ok=True)
    for row,(kind,delta) in itertools.product(selected,[('diameter',0.5),('length',1.0),('pitch',1.0),('pitch',1.2)]):
        tree=ast.parse(extract_code(row['completion']))
        change=Perturb(kind,delta)
        code=ast.unparse(ast.fix_missing_locations(change.visit(tree)))
        if len(change.edits)!=1: raise RuntimeError((row['tier'],row['spec_id'],kind,change.edits))
        filename=f"{row['tier']}-{row['spec_id']}-{kind}-{delta:g}.py"
        (mdir/filename).write_text(code+'\n',encoding='utf-8')
        rep=score(code,specs[row['spec_id']])
        expected={'diameter':'R4b:hole_diameter','length':'R1:length','pitch':'R5:hole_pattern'}[kind]
        check_map={c.name:c.passed for c in rep.checks}
        mutants.append(dict(tier=row['tier'],spec_id=row['spec_id'],kind=kind,delta=delta,edits=change.edits,
            code_file=str((mdir/filename).relative_to(ROOT)).replace('\\','/'),reward=rep.reward,
            caught=rep.reward!=1,expected_check=expected,expected_failed=check_map.get(expected) is False,
            failed=[k for k,v in check_map.items() if not v],details={c.name:c.detail for c in rep.checks},error=rep.error))
    shutdown_worker()
    summary=dict(geometry_rows=len(data),recorded_passes=sum(r['recorded_pass'] for r in data),
        export_score_mismatches=[r for r in data if not r['export_score_equal']],
        independent_pass_agreement=sum(r['recorded_pass'] and r['pass_exact'] for r in data),
        independent_pass_mismatches=[r for r in data if r['recorded_pass'] and not r['pass_exact']],
        all_failures=[r for r in data if not r['pass_exact']],
        max_missing_volume=max(abs(r['missing_volume']) for r in data if r['recorded_pass']),
        max_extra_volume=max(abs(r['extra_volume']) for r in data if r['recorded_pass']),
        max_position_error=max(r['max_position_error'] for r in data if r['recorded_pass']),
        sensitivity={f'{kind}+{delta:g}':dict(n=len(sub),caught=sum(r['caught'] for r in sub),expected_failed=sum(r['expected_failed'] for r in sub),
            failed_checks=dict(collections.Counter(k for r in sub for k in r['failed'])))
            for kind,delta in [('diameter',0.5),('length',1.0),('pitch',1.0),('pitch',1.2)]
            for sub in [[r for r in mutants if r['kind']==kind and r['delta']==delta]]})
    (OUT/'run1-geometry.json').write_text(json.dumps(dict(summary=summary,results=data),indent=2),encoding='utf-8')
    (OUT/'run1-perturbations.json').write_text(json.dumps(mutants,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':
    main()
