"""Copy source into a fresh workspace for an explicitly requested future reproduction."""
import argparse
import shutil
from pathlib import Path

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--destination',required=True,type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    destination=args.destination.resolve()
    if destination.exists() or destination==root or destination.is_relative_to(root):
        parser.error('Use a new directory outside the existing project; nothing will be overwritten.')
    destination.mkdir(parents=True)
    for name in ['src','docs']:
        shutil.copytree(root/name,destination/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for name in ['models','data/raw','data/processed','reports','tests/models']:
        (destination/name).mkdir(parents=True,exist_ok=True)
    shutil.copytree(root/'tests/models',destination/'tests/models',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copy2(root/'tests/test_pipeline.py',destination/'tests/test_pipeline.py')
    for name in ['requirements.txt','data/processed/data_dictionary.csv']:
        shutil.copy2(root/name,destination/name)
    print('Source-only reproduction workspace:',destination)
    print('No dataset or model copied. Place the official XPT in data/raw before any future training.')

if __name__=='__main__':main()
