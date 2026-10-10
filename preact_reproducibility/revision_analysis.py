"""Exploratory major-revision analyses; no target test labels used for fitting.

Original hash split is retained. Repeated 5-fold task splits use a separate task
validation subset inside each outer training fold. Target adaptation uses only
the corresponding target validation tasks. Checkpoint 20 is exploratory.
"""
import gzip
import hashlib
import json
import os
import warnings
from pathlib import Path

import numpy as np
from scipy.special import expit, logit
from scipy.stats import ks_2samp
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from preact_pilot import DATA_ROOT, FEATURES, load_data, metrics
from preact_pilot_audit import fit_and_select

ROOT = Path(__file__).resolve().parent
TARGET = 'qwen3.6-27b'
SEEDS = [20261010, 20261011, 20261012]


def x(rows): return np.asarray([r['features'] for r in rows])
def y(rows): return np.asarray([r['failure'] for r in rows])
def key(row): return (row['instance'], row['run'])
def score(model, rows): return model.predict_proba(x(rows))[:, 1]


def paired_bootstrap(rows, transferred, own, reps=2000, seed=20261010):
    tasks = sorted({r['instance'] for r in rows})
    idx = {t: np.array([i for i,r in enumerate(rows) if r['instance']==t]) for t in tasks}
    labels = y(rows)
    rng = np.random.default_rng(seed)
    delta = []
    for _ in range(reps):
        indices = np.concatenate([idx[t] for t in rng.choice(tasks, len(tasks), replace=True)])
        if len(np.unique(labels[indices])) < 2: continue
        delta.append(roc_auc_score(labels[indices],own[indices])-roc_auc_score(labels[indices],transferred[indices]))
    point = roc_auc_score(labels,own)-roc_auc_score(labels,transferred) if len(np.unique(labels))==2 else None
    return {'direction':'target-trained minus transferred AUROC', 'difference':point,
            'percentile_95ci':np.quantile(delta,[.025,.975]).tolist() if delta else None,
            'valid_resamples':len(delta), 'requested_resamples':reps, 'tasks':len(tasks), 'n':len(rows)}


def ecdf(reference, values):
    return np.column_stack([np.searchsorted(np.sort(reference[:,j]), values[:,j], side='right') / len(reference)
                            for j in range(reference.shape[1])])


def fit_case(rows):
    train = [r for r in rows if r['participant'] != TARGET and r['split']=='train']
    val = [r for r in rows if r['participant'] != TARGET and r['split']=='val']
    target_train = [r for r in rows if r['participant']==TARGET and r['split']=='train']
    target_val = [r for r in rows if r['participant']==TARGET and r['split']=='val']
    test = [r for r in rows if r['participant']==TARGET and r['split']=='test']
    _, source_name, source = fit_and_select(train,val)
    _, own_name, own = fit_and_select(target_train,target_val)
    p = score(source,test); po = score(own,test); pv = score(source,target_val)
    # Label-shift assumption is unverified; prevalence estimated only from val.
    prior_delta = logit(np.clip(y(target_val).mean(),1e-6,1-1e-6))-logit(np.clip(y(train).mean(),1e-6,1-1e-6))
    corrected = expit(logit(np.clip(p,1e-6,1-1e-6))+prior_delta)
    sigmoid = LogisticRegression(C=1e6, max_iter=1000)
    sigmoid.fit(logit(np.clip(pv,1e-6,1-1e-6)).reshape(-1,1),y(target_val))
    calibrated = sigmoid.predict_proba(logit(np.clip(p,1e-6,1-1e-6)).reshape(-1,1))[:,1]
    # Rank-normalized baseline uses source train ECDF and target val ECDF only.
    def mapped(rows, ref):
        arr = ecdf(ref,x(rows))
        return [{**r,'features':v.tolist()} for r,v in zip(rows,arr)]
    _, rank_name, rank_model = fit_and_select(mapped(train,x(train)),mapped(val,x(train)))
    pr = score(rank_model,mapped(test,x(target_val)))
    drift=[]
    for j,name in enumerate(FEATURES):
        a=x(val)[:,j]; b=x(target_val)[:,j]
        scale=np.sqrt((np.var(a)+np.var(b))/2)
        drift.append({'feature':name,'source_validation_mean':float(a.mean()),'target_validation_mean':float(b.mean()),
                      'standardized_mean_difference':float((b.mean()-a.mean())/scale) if scale else 0.,
                      'ks_distance':float(ks_2samp(a,b).statistic)})
    return {'test':test,'p':p,'own':po,'models':{'source':source_name,'own':own_name,'rank':rank_name},
            'metrics':{name:metrics(test,prob) for name,prob in [('unchanged',p),('target_validation_prior',np.full(len(test),y(target_val).mean())),('prior_shift',corrected),
                ('target_validation_sigmoid',calibrated),('ecdf_normalized',pr),('target_trained',po)]},
            'target_validation_n':len(target_val),'prior_delta':float(prior_delta),
            'sigmoid_slope':float(sigmoid.coef_[0,0]),'sigmoid_intercept':float(sigmoid.intercept_[0]),'drift':drift}


def main():
    rows=load_data()
    assert rows
    output={'protocol':{'date':'2026-10-10','status':'Exploratory revisions after review; checkpoints and new analyses not preregistered.',
              'target':TARGET,'cv_seeds':SEEDS,'outer_folds':5,'inner_validation':'20% of outer-training tasks, shared across all systems',
              'paired_bootstrap':'2000 task-cluster resamples, target-trained minus transfer on identical rows',
              'calibration':'All target labels for fitting are validation-only; sigmoid permits slope reversal.',
              'survival':'Eligibility follows extractor availability, not a biological survival model; no identifiable missing-prefix IPW estimate.'},
            'checkpoints':[], 'repeated_grouped_cv':[], 'survival':[], 'manifest':[]}
    traces=[]
    for path in sorted((DATA_ROOT/'rebench').glob('*/*.jsonl.gz')):
        raw=gzip.decompress(path.read_bytes())
        output['manifest'].append({'relative_path':str(path.relative_to(DATA_ROOT)).replace('\\','/'),
                                   'compressed_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                                   'decompressed_sha256':hashlib.sha256(raw).hexdigest()})
        # Split only JSONL newlines; str.splitlines also splits Unicode content.
        traces.extend(json.loads(line) for line in raw.decode('utf8').split('\n') if line.strip())
    all_tasks=sorted({r['instance'] for r in rows})
    (ROOT/'results/task_manifest.json').write_text(json.dumps({'tasks':[{ 'task_id':t,'split':next(r['split'] for r in rows if r['instance']==t)} for t in all_tasks],
           'shards':output['manifest']},indent=2),encoding='utf8')
    for cp in [5,10,20,40]:
        cp_rows=[r for r in rows if r['checkpoint']==cp]
        result=fit_case(cp_rows)
        case={k:v for k,v in result.items() if k not in ('test','p','own')}
        case['checkpoint']=cp
        case['paired']=paired_bootstrap(result['test'],result['p'],result['own'])
        eligible={a:{key(r) for r in cp_rows if r['participant']==a} for a in sorted({r['participant'] for r in rows})}
        common=set.intersection(*eligible.values())
        mask=np.array([key(r) in common for r in result['test']])
        case['common_all_systems_cohort']={'n':int(mask.sum()),'transfer':metrics([r for r,m in zip(result['test'],mask) if m],result['p'][mask]),
                                          'own':metrics([r for r,m in zip(result['test'],mask) if m],result['own'][mask])}
        longest={key(r) for r in rows if r['participant']==TARGET and r['checkpoint']==40}
        fixed=np.array([key(r) in longest for r in result['test']])
        case['fixed_target_cp40_cohort']={'transfer':metrics([r for r,m in zip(result['test'],fixed) if m],result['p'][fixed]),
                                        'own':metrics([r for r,m in zip(result['test'],fixed) if m],result['own'][fixed])}
        output['checkpoints'].append(case)
        for agent in eligible:
            for failure in [0,1]:
                denominator=[t for t in traces if t['participant']['key']==agent and int(not t['evaluation']['resolved'])==failure]
                count=sum((t['instance_id'],t['run']['index']) in eligible[agent] for t in denominator)
                output['survival'].append({'checkpoint':cp,'system':agent,'failure':failure,'total':len(denominator),'eligible':count,'fraction':count/len(denominator)})
        print('Original split',cp,case['paired'],flush=True)
        for seed in SEEDS:
            rng=np.random.default_rng(seed)
            tasks=np.array(all_tasks); rng.shuffle(tasks)
            folds=np.array_split(tasks,5)
            collected=[]; pt=[]; po=[]; selections=[]
            for fold,held in enumerate(folds):
                remain=np.array([t for t in tasks if t not in set(held)])
                rng.shuffle(remain); nval=max(1,round(.2*len(remain)))
                validations=set(remain[:nval]); tests=set(held)
                fresh=[{**r,'split':'test' if r['instance'] in tests else ('val' if r['instance'] in validations else 'train')} for r in cp_rows]
                fitted=fit_case(fresh)
                collected+=fitted['test']; pt.extend(fitted['p']); po.extend(fitted['own']); selections.append(fitted['models'])
            output['repeated_grouped_cv'].append({'checkpoint':cp,'seed':seed,'transfer':metrics(collected,np.array(pt)),
                'own':metrics(collected,np.array(po)),'paired':paired_bootstrap(collected,np.array(pt),np.array(po),seed=seed),
                'models_by_fold':selections})
        (ROOT/'results/major_revision_results.json').write_text(json.dumps(output,indent=2),encoding='utf8')
    print('Completed revision analyses',flush=True)


if __name__=='__main__':
    main()
