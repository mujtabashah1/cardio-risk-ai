"""Serve the existing API and static QA frontend on loopback; no training."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runpy

if __name__ == '__main__':
    print('Local model testing website: http://127.0.0.1:8000/testing/')
    runpy.run_module('api', run_name='__main__')
