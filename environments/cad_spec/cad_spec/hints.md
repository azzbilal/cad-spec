CadQuery notes (general API facts, not specific to this part):
- Operations act on what is on the stack. `.hole(d)` drills one hole at each point on the stack; with no points it drills once at the workplane origin, and calling `.hole()` again drills the same place again.
- To drill several holes, make a workplane on the part's face, place the points, then drill once: `.faces(">Z").workplane().pushPoints([(x1, y1), (x2, y2)]).hole(d)`, or `.rect(a, b, forConstruction=True).vertices().hole(d)` for the four corners of an a x b rectangle centred on the origin.
- `.translate()` moves the solid, not the drilling point. `.center(x, y)` shifts the workplane origin relative to its current position.
- Signatures: `box(length, width, height, centered=True)` (centred on the origin in X, Y and Z by default); `hole(diameter, depth=None)` (a diameter, not a radius; no depth means through); `rect(xLen, yLen, centered=True, forConstruction=False)`; `rarray(xSpacing, ySpacing, xCount, yCount)` (the counts are integers).
- There is no `.holes()`, `.centered()`, `.rectArray()` or `.rectangularPattern()` method.
- Holes need a solid underneath: drill from a workplane on a face of the part, not from a fresh `cq.Workplane("XY")`.
