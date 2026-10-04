"""Run or resume modeling without rewriting data or re-evaluating the test set."""
import argparse,json,subprocess,sys
from .config import ROOT

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['all','train','select','evaluate','report'],default='all');parser.add_argument('--device',choices=['auto'],default='auto');args=parser.parse_args()
    out=ROOT/'reports/modeling'
    if args.stage in ['all','train'] and not (out/'training_complete.json').exists():
        from .train_models import run
        run()
    if args.stage in ['all','select'] and not (ROOT/'models/model_freeze.json').exists():
        from .model_selection import select_and_export
        select_and_export()
    if args.stage in ['all','evaluate']:
        result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests/models')],capture_output=True,text=True)
        (out/'automated_tests.txt').write_text(result.stdout+'\n'+result.stderr)
        (out/'automated_tests.json').write_text(json.dumps(dict(passed=result.returncode==0,command='python -m unittest discover -s tests/models',output=result.stdout+'\n'+result.stderr),indent=2))
        if result.returncode:raise RuntimeError('Model tests failed; test evaluation remains locked. See automated_tests.txt')
        from .evaluate import evaluate
        evaluate()
    if args.stage in ['all','report'] and (out/'final_test_metrics.json').exists():
        from .reporting import generate
        generate()

if __name__=='__main__':main()
