"""Add validation-only constant-prior control to an existing revision result.

No predictor refit or model selection changes. The complete revision script also
generates this control directly on future reruns.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from preact_pilot import load_data,metrics


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--results',type=Path,default=Path(__file__).resolve().parent/'results/major_revision_results.json')
    args=parser.parse_args()
    rows=load_data()
    result=json.loads(args.results.read_text())
    for case in result['checkpoints']:
        selected=[r for r in rows if r['checkpoint']==case['checkpoint'] and r['participant']=='qwen3.6-27b']
        validation=[r for r in selected if r['split']=='val'];test=[r for r in selected if r['split']=='test']
        prior=np.mean([r['failure'] for r in validation])
        case['metrics']['target_validation_prior']=metrics(test,np.full(len(test),prior))
    args.results.write_text(json.dumps(result,indent=2),encoding='utf8')
    print('Validation-only constant controls added:',args.results)


if __name__=='__main__':main()
