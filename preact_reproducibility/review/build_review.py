"""Build the review, CSV/BibTeX library and categorical evidence map.

Requires matplotlib, requests and beautifulsoup4. No benchmark results change.
"""
import csv, json, re, shutil
from pathlib import Path
from collections import Counter
from bs4 import BeautifulSoup
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from curated_notes import NOTES

ROOT=Path(__file__).resolve().parent
WORK=ROOT.parents[1]
HEADERS=['Unseen tasks','Held-out agent','Scaffold/domain','Calibration','Intervention','Replay/control']

def main():
    metadata=json.loads((ROOT/'source_metadata.json').read_text(encoding='utf8'))
    assert set(NOTES)=={r['arxiv_id'] for r in metadata}, 'All 40 sources must be retrieved before building.'
    records=[]
    raw=ROOT/'sources/raw_metadata.json'
    if any('abstract' in r for r in metadata):
        raw.parent.mkdir(exist_ok=True)
        raw.write_text(json.dumps(metadata,indent=2),encoding='utf8')
    for m in metadata:
        m.pop('abstract',None)
        cached=ROOT/'sources'/f"{m['arxiv_id']}.html"
        if cached.exists():
            soup=BeautifulSoup(cached.read_text(encoding='utf8'),'html.parser')
            area=soup.select_one('.leftcolumn') or soup
            m['artifact_links']=sorted(set(a.get('href') for a in area.find_all('a',href=True)
                if any(x in a['href'] for x in ['github.com','huggingface.co','aka.ms','sites.google','agents','react-lm','reflexion'])))
            status=soup.select_one('td.tablecell.jref')
            m['journal_reference']=status.get_text(' ',strip=True) if status else ''
        m.setdefault('artifact_links',[])
        m['status']='arXiv preprint; peer review not independently confirmed'
        if m['comments'] or m.get('journal_reference'):
            m['status']+='; source record: '+(m.get('journal_reference') or m['comments'])
        m.update(NOTES[m['arxiv_id']]); m['verification']='Primary metadata plus full-text method/results reading; not independently reproduced'
        assert m['fulltext_available']
        records.append(m)
    records.sort(key=lambda r:(r['category'],list(NOTES).index(r['arxiv_id'])))
    for i,r in enumerate(records,1):r['review_id']=f'P{i:02d}'
    (ROOT/'extracted_papers.json').write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding='utf8')
    (ROOT/'source_metadata.json').write_text(json.dumps([{k:v for k,v in r.items() if k not in NOTES[r['arxiv_id']] and k!='review_id'} for r in records],indent=2,ensure_ascii=False),encoding='utf8')
    fields=['review_id','arxiv_id','category','title','authors','date','version','status','source_url','fulltext_url','domain','target','summary','findings','design','gap','future','role','evidence_location','artifact_links']
    with (ROOT/'extracted_papers.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
        for r in records:w.writerow({**r,'authors':'; '.join(r['authors']),'artifact_links':'; '.join(r['artifact_links'])})
    with (ROOT/'evidence_map.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.writer(f);w.writerow(['review_id','short','category',*HEADERS,'source_location','source_url'])
        for r in records:w.writerow([r['review_id'],r['short'],r['category'],*r['matrix'],r['evidence_location'],r['source_url']])
    bib=[]
    for r in records:
        title=r['title'].replace('&',r'\&')
        bib.append('@misc{preact_'+r['arxiv_id'].replace('.','_')+',\n  title={'+title+'},\n  author={'+ ' and '.join(r['authors'])+'},\n  year={'+r['date'][:4]+'},\n  eprint={'+r['arxiv_id']+'},\n  archivePrefix={arXiv},\n  note={Inspected '+r['version']+' on 4 October 2026},\n  url={'+r['source_url']+'}\n}')
    (ROOT/'references.bib').write_text('\n\n'.join(bib),encoding='utf8')
    counts=Counter(r['category'] for r in records)
    intro='''# PreAct: Expanded Literature Review and Evidence Map

**Updated:** 4 October 2026 (Asia/Dubai). **Corpus:** 40 verified paper identifiers, expanding the original 22. Every included source has primary metadata and an inspected full text. Verification means source checking, not reproduction or endorsement. This is a targeted literature mapping review, not an exhaustive or registered systematic review. Search protocol, queries, extraction data, bibliography and code are in `preact_reproducibility/review/`.

## Executive synthesis

The basic idea of predicting failure from an unfinished agent trajectory is established. So are pre-action correction, restart, stronger-model switching, probabilistic safety monitoring, calibration-transfer auditing and matched-prefix repair. PreAct must not claim these individually as new. The defensible present contribution is a reproducible, task-grouped structural-monitor pilot on three software-agent systems, including a negative transfer result and within-agent controls. It is independent evidence under a different dataset and monitor, not a universal transfer theorem.

The strongest future direction is **calibrated intervention selection under separately controlled model and scaffold shift**, on organic failures, with action-specific gains and harms evaluated at a common total budget. That is a research hypothesis, not a contribution already demonstrated by the current data. Before claiming novelty, compare to telemetry sentinel, FailFast–RestartSmart, the intervention-paradox study, SWE-PRM, graph copilot, ProbGuard and DoVer.

### Corrections from full-text verification

- **Self-healing (2605.06737):** Section 4.4 says experiments are ongoing. Retain as a framework proposal; do not cite it as a completed quantitative recovery demonstration.
- **PrefixGuard v2:** held-out tasks are represented in training. Its result is held-out trajectory performance; unseen tasks and agents remain unmeasured.
- **Telemetry sentinel:** matched-checkpoint repair and recalibration are already studied. The headline 0.872 AUROC is from its synthetic study; live, external-corpus and repair evaluations have separate denominators. Paper and current repository differ on some p-values/counts. We use the inspected paper for reported results.
- **A2P:** counterfactual outcomes are imagined within one LLM inference, not established by executing an environment branch. Keep it distinct from DoVer's active intervention verification.
- **Plan compliance:** the inspected v3 has 21,120 trajectories, superseding an older bibliography's 16,991 figure.
- **Cao audit:** two target-specific calibration errors persist, but broad heterogeneity and cross-benchmark replication are not established. Cite both the positive and negative findings.

## Search, eligibility and evidence strength

Primary public arXiv records and full texts were checked, using web discovery and reference chaining from the inherited review and an author-maintained trajectory-analysis bibliography. No authenticated Scopus/Web of Science/ACM/IEEE database export or independent second screening was performed. There is no defensible PRISMA retrieval denominator, so none is fabricated. One inherited conceptual paper is explicitly retained as a documented eligibility exception. Preprints are distinguished from source-record claims of conference acceptance; unchecked venue labels from curated lists are not adopted.

**Category 1** contains direct forecasting, online intervention and transfer/calibration work. **Category 2** contains adjacent diagnosis, process analysis, enforcement and recovery. **Category 3** contains architecture, evaluation and methodological foundations. Relevance is not a quality rank.

Evidence codes: **R** = reported evidence in the extracted setting; **Q** = qualified evidence, partial comparison or a different estimand; **NR** = not extracted/established for this column, not proof of absence. Multiple tested backbones are not automatically held-out-agent transfer; multiple benchmarks are not automatically frozen cross-domain transfer. Calibration includes explicit probability/threshold analysis, not simply an accuracy number. Intervention denotes downstream task/safety/resource-policy evaluation; Q may indicate stopping or process outcomes rather than recovered tasks. Replay/control identifies executed control comparisons, not imagined counterfactual text. Consult each study's design before interpreting a cell.

No cross-benchmark metric pooling is performed. The 40 papers reuse environments and traces, and do not constitute 40 independent intervention estimates. All quantitative findings below are authors' reports. **Gap** and **future work** are reviewer assessments and proposals unless identified otherwise.

## Evidence map

![Direct-monitor evidence map](preact_reproducibility/review/outputs/evidence_map.png)

'''
    lines=[intro, '|ID / paper|Cat.|Unseen tasks|Held-out agent|Scaffold/domain|Calibration|Intervention|Replay/control|','|---|---|---|---|---|---|---|---|']
    for r in records:lines.append('|'+f"[{r['review_id']} {r['short']}]({r['source_url']})|{r['category']}|"+'|'.join(r['matrix'])+'|')
    titles={1:'Closest: Forecasting, Online Intervention and Transfer',2:'Adjacent: Diagnosis, Process Evidence, Enforcement and Recovery',3:'Foundations: Agents, Benchmarks, Evaluation and Calibration'}
    for cat in [1,2,3]:
        lines.extend(['',f'## Category {cat} - {titles[cat]} ({counts[cat]} papers)',''])
        for r in records:
            if r['category'] != cat:
                continue
            lines.extend([f"### {r['review_id']}. [{r['title']}]({r['source_url']})",'',
                '**Citation:** '+ '; '.join(r['authors'])+'. '+r['title']+'. arXiv:'+r['arxiv_id']+', '+r['date'][:4]+'.',
                '',f"**Version/status:** {r['version']}; first posted {r['date']}. {r['status']}.",
                '',f"**Domain / prediction or evaluation target:** {r['domain']} / {r['target']}.",
                '', '**Detailed method summary:** '+r['summary'],
                '', '**Reported findings and sample context:** '+r['findings'],
                '', '**Evaluation design and validity:** '+r['design'],
                '', '**Research gap / practical limitation (reviewer assessment):** '+r['gap'],
                '', '**Possible future work (proposed experiment):** '+r['future'],
                '', '**Relationship to PreAct:** '+r['role'],
                '', '**Evidence location:** '+r['evidence_location']+' Inspected full text: '+f"[{r['version']}]({r.get('fulltext_url',r['source_url'])}).",
                '', '**Artifacts:** '+('; '.join(f'[author-linked resource]({u})' for u in r['artifact_links']) or 'No external artifact link extracted from the primary landing page; this is not a claim that code is unavailable.'), ''])
    lines.append(SYNTHESIS)
    (WORK/'PreAct_literature_review.md').write_text('\n'.join(lines),encoding='utf8')
    (ROOT/'LITERATURE_REVIEW.md').write_text('\n'.join(lines).replace('preact_reproducibility/review/outputs/','outputs/'),encoding='utf8')
    OUT=ROOT/'outputs';OUT.mkdir(exist_ok=True)
    core=[r for r in records if r['category']==1]
    values={'NR':0,'Q':1,'R':2}
    matrix=[[values[v] for v in r['matrix']] for r in core]
    plt.rcParams.update({'font.size':8,'pdf.fonttype':42})
    fig,ax=plt.subplots(figsize=(7.1,3.7))
    ax.imshow(matrix,cmap=ListedColormap(['#f1f3f5','#f1dba7','#246a89']),vmin=0,vmax=2,aspect='auto')
    ax.set_yticks(range(len(core)),[r['short'] for r in core])
    ax.set_xticks(range(6),['Unseen\ntasks','Held-out\nagent','Scaffold/\ndomain','Calibration','Intervention','Replay/\ncontrol'])
    for i,row in enumerate(core):
        for j,v in enumerate(row['matrix']):ax.text(j,i,v,ha='center',va='center',color='white' if v=='R' else '#222',fontsize=7)
    ax.tick_params(length=0)
    for spine in ax.spines.values():spine.set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT/'evidence_map.pdf',bbox_inches='tight');fig.savefig(OUT/'evidence_map.png',dpi=220,bbox_inches='tight');plt.close(fig)
    print('Built',len(records),'records; category counts',dict(counts))

SYNTHESIS='''
## Cross-paper synthesis and the remaining research gap

### What existing evidence supports

1. **Partial traces carry predictive information**, but the target and usable warning time vary. PrefixGuard estimates horizons; Sparse Evidence finds late evidence; ProMAS localizes errors from reduced logs; the CLI anatomy study finds early errors that may remain hidden. These observations are compatible: causal onset and observable warning time differ.
2. **Transfer is conditional.** FailFast and EarlyEval report successful unseen-agent evaluation. Cao finds persistent errors only for some target/head cells. Telemetry sentinel requires a serving-specific healthy null. PreAct's pooled structural monitor falls from 0.700 to 0.456 AUROC at 20 results, while own-agent training reaches 0.691. Together these motivate identifying when transfer holds, not asserting universal failure.
3. **Downstream intervention is already measured.** SWE-PRM, graph copilot, FailFast, Atropos, ProbGuard and telemetry sentinel all evaluate interventions under different goals. DoVer validates debugging through actual interventions. A2P instead uses imagined counterfactual reasoning. Neither classification accuracy nor causal vocabulary establishes an executable policy effect.
4. **Intervention can harm.** The intervention-paradox study gives direct negative evidence; safety monitors can also trade completion for fewer unsafe actions. A useful outcome report must count recovered failures, disrupted successes and complete monitor/action costs.
5. **Labels are not interchangeable.** AgentLens process defects can coexist with passing tests. AgentRewardBench exposes evaluator disagreement. Who&When/AgentRx label retrospective critical steps; injected-provenance labels differ from organic causality. ToolPRMBench ranks local actions. Each can contribute evidence without supplying the same target.

### Evidence-supported gap, phrased conservatively

The reviewed evidence does not establish a general, prospectively validated rule for selecting among feasible interventions on organic tool-agent failures under independently varied model and scaffold shifts, while maintaining task success at a shared budget and a prespecified disruption constraint. This is a bounded conclusion about the extracted corpus, not proof that no such paper exists. Calibrated prediction, counterfactual branching and action selection each have predecessors. The contribution must come from the controlled combination and a reproducible result.

## Strengthened PreAct concept and experiment

### Present paper: a negative transfer study

Keep the title focused on early failure prediction and transfer. State the main claim as: a cheap prefix-only structural monitor can rank eventual outcomes on held-out tasks from its training systems, but its ranking and validation-derived alarm threshold fail in one fully held-out software-agent system. Own-agent training helps; simple rate normalization does not repair the tested shift. The data do not identify whether model weights or scaffold caused the shift, nor compare faithfully reproduced state-of-the-art monitors. The current pilot therefore supports a limited empirical transfer finding, not state-of-the-art superiority.

### Follow-up question

At a prefix and proposed action, can a monitor select **continue, verify, or restart** to improve task resolution after counting monitor overhead and interruption harm, and can that policy retain utility when model and scaffold are changed independently?

For potential outcome Y(m), total cost C(m) and side-effect D(m), define Q_m(h,a)=E[Y(m)-lambda C(m)-mu D(m)|h,a]. A failure score estimates P(Y(continue)=0|h,a); it does not identify Q_m-Q_continue. The controller continues unless a supported estimate of net advantage exceeds the prespecified decision threshold. Safety constraints remain separate and can forbid an action irrespective of task-value estimates.

### Controlled design

- Use a **factorial model × scaffold design**. Train/calibrate on one cell, then evaluate same-model/new-scaffold, new-model/same-scaffold, and jointly new cells. Freeze tools, budgets, prompts where the comparison requires them. Compare raw, normalized, semantic and event-based features on identical prefixes.
- Annotate **observable evidence, consequential error and budget-dependent recoverability** separately. A detector after onset may help recovery but must not count as pre-error prevention. Keep adjudication uncertainty and success-run controls.
- Branch on stratified low- and high-risk prefixes, rather than alarms alone. Replay environment and conversation states, then execute continue/verify/restart under repeated seeds. Stop claiming matched counterfactuals when external effects cannot be replayed. Final task checks and budget accounting apply to every branch.
- Start with **organic failures**; injected failures are a separate robustness arm. Include task/repository grouped splits and a target calibration set disjoint from target testing. Report new-agent data requirements and an abstention/coverage frontier.
- Compare base agent, reactive recovery, error/repeat heuristics, reference-free EarlyEval, PrefixGuard-style risk thresholds, FailFast restart, SWE-PRM feedback, deterministic checks, and telemetry-sentinel/located-repair where task semantics permit faithful implementation. List non-reproducible baselines rather than silently substituting a weaker version.
- Online randomization should compare the complete prespecified monitor policies. Use task-cluster uncertainty; if randomization is adaptive, preserve assignment probabilities and overlap. Do not treat correlated prefixes as independent trials.

### Primary endpoints and interpretation

Report absolute task-resolution difference at matched total budget; failure recovery and successful-run disruption; tokens, tool calls, wall time and monitor inference; calibration and decision coverage per model/scaffold; and lead time relative to verified onset. Budget should include tokens consumed after restart and abandoned work. AUROC, AUPRC and Brier remain descriptive predictor endpoints. No pooled literature-wide AUROC or effect size is justified here.

### Priority sequence

1. Reproduce the pilot and core baseline comparisons on the same traces.
2. Run the factorial transfer study to distinguish representation shortcuts from agent change.
3. Collect replayable organic-prefix branches and identify intervention benefit.
4. Freeze a calibrated abstaining policy, then run the randomized budget-matched trial.

## Availability and limits

The review protocol, search log, screening notes, extracted JSON/CSV, 40-entry BibTeX library, matrix CSV and plotting script form the auditable review package. Primary full-text reading copies stay local and are excluded from redistribution. The existing 1,665-trace empirical results are unchanged. The manuscript is an unpublished pilot; it is not counted as external peer-reviewed evidence. Independent human extraction checks and a comprehensive database search remain necessary before labeling this a systematic review.
'''

if __name__=='__main__':main()
