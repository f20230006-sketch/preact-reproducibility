"""Fresh publication gate: real-data prediction checks and release hygiene.

No saved experimental outputs or manuscript source are changed.
"""
import ast
import json
import re
from pathlib import Path
import numpy as np
from preact_pilot import extract,load_data,metrics
from preact_pilot_audit import fit_and_select
from revision_analysis import fit_case

ROOT=Path(__file__).resolve().parent


def main():
    scripts=list(ROOT.rglob('*.py'))
    for path in scripts:
        if '__pycache__' not in path.parts:ast.parse(path.read_text(encoding='utf8'),filename=str(path))
    events=[]
    for i in range(20):
        events.extend([{'type':'tool_call','tool':'read','tool_call_id':str(i),'input':{'path':str(i)}},
                       {'type':'tool_result','tool_call_id':str(i),'status':'success','content':'prefix'}])
    trace={'events':events,'evaluation':{'resolved':True}}
    baseline=extract(trace,20)
    changed={'events':events+[{'type':'assistant_message','content':'future final answer'},
                              {'type':'tool_result','tool_call_id':'future','status':'error','content':'future failure'}],
             'evaluation':{'resolved':False}}
    assert extract(changed,20)==baseline
    assert extract({'events':events[:10]},20) is None
    rows=load_data();assert rows
    groups={}
    for row in rows:groups.setdefault(row['instance'],set()).add(row['split'])
    assert len(groups)==111 and all(len(v)==1 for v in groups.values())
    selected=[r for r in rows if r['checkpoint']==20]
    target=fit_case(selected)
    assert abs(target['metrics']['unchanged']['auroc']-.4561)<1e-4
    assert abs(target['metrics']['target_trained']['auroc']-.6911)<1e-4
    assert abs(target['metrics']['target_validation_prior']['brier']-.2227)<1e-4
    training=[r for r in selected if r['participant']!='qwen3.6-27b' and r['split']=='train']
    validation=[r for r in selected if r['participant']!='qwen3.6-27b' and r['split']=='val']
    testing=[r for r in selected if r['participant']!='qwen3.6-27b' and r['split']=='test']
    _,_,model=fit_and_select(training,validation)
    m=metrics(testing,model.predict_proba(np.array([r['features'] for r in testing]))[:,1])
    saved=json.loads((ROOT/'results/preact_pilot_results.json').read_text())
    expected=next(r['monitor'] for r in saved['results'] if r['checkpoint']==20 and r['group']=='held_out_tasks')
    assert m==expected,('Recomputed source metrics differ from stored precision',m,expected)
    folds=json.loads((ROOT/'results/per_fold_results.json').read_text())
    for result in folds['results']:
        tasks=[task for fold in result['folds'] for task in fold['test_tasks']]
        assert len(tasks)==len(set(tasks))==111
        for kind in ['transfer','own']:
            values=[f[kind]['auroc'] for f in result['folds']]
            summary=result['summary'][kind]
            assert np.isclose(summary['unweighted_mean'],np.mean(values))
            assert np.isclose(summary['sample_sd'],np.std(values,ddof=1))
    manuscript=ROOT.parent/'paper_mosicom2026/preact_mosicom2026.tex'
    source=manuscript.read_text(encoding='utf8')
    keys=set(re.findall(r'\\bibitem\{([^}]+)\}',source))
    cites={key for group in re.findall(r'\\cite\{([^}]+)\}',source) for key in group.split(',')}
    assert keys==cites and len(keys)==24
    assert 'Yuvaraj Nayak' in source and 'f20230006@dubai.bits-pilani.ac.in' in source
    assert source.count('BEGIN INLINE')==3
    sensitive=[]
    credential=re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|AKIA[0-9A-Z]{16})')
    for path in ROOT.parent.rglob('*'):
        if not path.is_file() or '.git' in path.parts:continue
        if path.suffix in {'.py','.md','.json','.tex','.txt','.ps1'}:
            text=path.read_text(encoding='utf-8-sig',errors='replace')
            if credential.search(text) or re.search(r'(?i)c:[\\/]users[\\/]',text):sensitive.append(str(path.relative_to(ROOT.parent)))
    assert not sensitive,sensitive
    assert not (ROOT/'data').exists() and not (ROOT/'review/sources').exists()
    print(f'PASS: {len(scripts)} Python sources parsed; prefix invariance and task grouping; real-data source AUROC {m["auroc"]}; transfer .4561/own .6911; fold summaries; citations; publication hygiene.')


if __name__=='__main__':main()
