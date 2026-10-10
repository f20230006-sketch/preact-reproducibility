"""Report within-outer-fold AUROC, avoiding cross-fold score-scale comparisons.

Recreates the exact seeded task splits in revision_analysis. No new model or
threshold selection occurs; fold variability is descriptive, not an SE or CI.
"""
import json
from pathlib import Path
import numpy as np
from preact_pilot import load_data,metrics
from revision_analysis import fit_case,SEEDS

ROOT=Path(__file__).resolve().parent


def main():
    rows=load_data();tasks_all=sorted({r['instance'] for r in rows});results=[]
    for cp in [5,10,20,40]:
        selected=[r for r in rows if r['checkpoint']==cp]
        for seed in SEEDS:
            rng=np.random.default_rng(seed);tasks=np.array(tasks_all);rng.shuffle(tasks)
            folds=np.array_split(tasks,5);reports=[];pooled=[];pt=[];po=[]
            for i,held in enumerate(folds):
                remaining=np.array([t for t in tasks if t not in set(held)]);rng.shuffle(remaining)
                validations=set(remaining[:max(1,round(.2*len(remaining)))]);test_tasks=set(held)
                fresh=[{**r,'split':'test' if r['instance'] in test_tasks else ('val' if r['instance'] in validations else 'train')} for r in selected]
                fitted=fit_case(fresh)
                reports.append({'fold':i+1,'test_tasks':sorted(test_tasks),'n':len(fitted['test']),
                    'transfer':metrics(fitted['test'],fitted['p']),'own':metrics(fitted['test'],fitted['own'])})
                pooled+=fitted['test'];pt.extend(fitted['p']);po.extend(fitted['own'])
            aggregate={}
            for name in ['transfer','own']:
                values=[r[name]['auroc'] for r in reports if 'auroc' in r[name]]
                aggregate[name]={'defined_folds':len(values),'unweighted_mean':float(np.mean(values)) if values else None,
                    'sample_sd':float(np.std(values,ddof=1)) if len(values)>1 else None,'min':min(values) if values else None,'max':max(values) if values else None}
            results.append({'checkpoint':cp,'seed':seed,'folds':reports,'summary':aggregate,
                            'pooled_transfer':metrics(pooled,np.array(pt)),'pooled_own':metrics(pooled,np.array(po))})
    original=json.loads((ROOT/'results/major_revision_results.json').read_text())
    for result in results:
        expected=next(r for r in original['repeated_grouped_cv'] if r['checkpoint']==result['checkpoint'] and r['seed']==result['seed'])
        assert result['pooled_transfer']==expected['transfer'] and result['pooled_own']==expected['own'],'Split recreation does not match published pooled metrics'
    output={'protocol':'Unweighted mean and sample SD of defined fold AUROCs; SD describes fold variation, not inferential uncertainty. Same tasks/seeds and outer-fold models as pooled sensitivity. Three seeds are not independent datasets.',
            'label':'failure=1 means unresolved; resolved=0','results':results}
    (ROOT/'results/per_fold_results.json').write_text(json.dumps(output,indent=2),encoding='utf8')
    lines=['# Individual outer-fold AUROC audit','',output['protocol'],'','| Checkpoint | Seed | Transfer mean (SD) | Own mean (SD) | Defined folds T/O |','|---|---|---|---|---|']
    for r in results:
        a=r['summary']['transfer'];b=r['summary']['own']
        lines.append(f"|{r['checkpoint']}|{r['seed']}|{a['unweighted_mean']:.3f} ({a['sample_sd']:.3f})|{b['unweighted_mean']:.3f} ({b['sample_sd']:.3f})|{a['defined_folds']}/{b['defined_folds']}|")
    lines+=['','Every fold score, task ID, sample count, and pooled consistency check is in `results/per_fold_results.json`. Undefined single-class folds would be excluded and counted explicitly.']
    (ROOT/'PER_FOLD_RESULTS.md').write_text('\n'.join(lines),encoding='utf8')
    print('\n'.join(lines[:12]))


if __name__=='__main__':main()
