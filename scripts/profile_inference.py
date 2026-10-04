"""Diagnose serving overhead using synthetic profiles; no model or data changes."""
import cProfile,io,json,pstats,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from api.config import Settings
from src.inference.service import InferenceService
service=InferenceService(Settings());profile=json.loads((ROOT/'tests/fixtures/golden_predictions.json').read_text())[0]['input']
profiler=cProfile.Profile();profiler.enable()
for _ in range(30):service.predict_batch([profile]*100)
profiler.disable();output=io.StringIO();pstats.Stats(profiler,stream=output).sort_stats('cumulative').print_stats(18)
(ROOT/'reports/deployment/inference_profile.txt').write_text(output.getvalue(),encoding='utf-8')
print(output.getvalue())
