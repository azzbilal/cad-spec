export PATH="/usr/bin:$PATH"
source "$HOME/cadspec.sh"
export PYTHONIOENCODING=utf-8 PRIME_DISABLE_VERSION_CHECK=1
python audit/scratch/reconstruct_cost.py
