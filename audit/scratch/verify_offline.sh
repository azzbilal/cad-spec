export PATH="/usr/bin:$PATH"
source "$HOME/cadspec.sh"
export PYTHONIOENCODING=utf-8 PRIME_DISABLE_VERSION_CHECK=1
python audit/scratch/test_guard_offline.py
python audit/scratch/preflight_candidate.py --steps 104 --batch 128 --group 8 --flat 0.91 --input-tokens 587 --output-tokens 800 --trained-tokens 1552 --wallet 30 --ceiling 15 --prior-spend 0.6854 --reserve 2 --evaluation-reserve 0.15
