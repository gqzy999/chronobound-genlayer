"""Share the official linter's pinned runner archive with Direct Mode."""
from pathlib import Path
import shutil
name='genvm-universal-v0.3.0-rc7.tar.xz'
a=Path.home()/'.cache/genvm-linter'/name
b=Path.home()/'.cache/gltest-direct'/name
if not a.exists():raise SystemExit('Run genvm-lint check on the contract first.')
b.parent.mkdir(parents=True,exist_ok=True)
if not b.exists():shutil.copyfile(a,b)
print('Pinned SDK archive ready.')
