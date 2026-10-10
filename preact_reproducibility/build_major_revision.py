"""Build scientific revision figures, report, and empirical manuscript.

Read saved original and revision results; does not choose models or thresholds.
"""
import json
import re
import shutil
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parent
PAPER=ROOT.parent/'paper_mosicom2026'
R=json.loads((ROOT/'results/major_revision_results.json').read_text())
plt.rcParams.update({'font.size':11,'axes.labelsize':12,'legend.fontsize':10,'pdf.fonttype':42,
                     'axes.spines.top':False,'axes.spines.right':False})


def save(fig,name):
    fig.tight_layout()
    for ext in ['pdf','png']:
        fig.savefig(ROOT/'figures'/f'{name}.{ext}',bbox_inches='tight',dpi=220)
    shutil.copy2(ROOT/'figures'/f'{name}.pdf',PAPER/'figures'/f'{name}.pdf')
    plt.close(fig)


def figures():
    colors=['#246693','#c65b32','#39866e']
    fig,ax=plt.subplots(1,2,figsize=(7.1,3.1))
    for cp in [5,10,20,40]:
        main=next(c for c in R['checkpoints'] if c['checkpoint']==cp)['paired']
        lo,hi=main['percentile_95ci'];d=main['difference']
        ax[0].errorbar(cp,d,yerr=[[d-lo],[hi-d]],fmt='o',color=colors[0],capsize=3)
        cvs=[c['paired']['difference'] for c in R['repeated_grouped_cv'] if c['checkpoint']==cp]
        ax[0].scatter(np.array([cp]*3)+[-.6,0,.6],cvs,marker='x',s=35,color=colors[1])
    ax[0].axhline(0,color='black',lw=.8,ls='--');ax[0].set_xticks([5,10,20,40])
    ax[0].set_xlabel('Observed tool results');ax[0].set_ylabel('AUROC difference\n(target-trained - transfer)')
    ax[0].set_ylim(-.30,.68)
    ax[0].plot([],[],'o',color=colors[0],label='Hash split: paired 95% CI')
    ax[0].plot([],[],'x',color=colors[1],label='Three grouped CV seeds');ax[0].legend(loc='lower left',bbox_to_anchor=(0,1.02),fontsize=8)
    for agent,color,label in zip(['claude-code','gpt-5.6-luna','qwen3.6-27b'],colors,['Claude','Luna','Qwen']):
        for fail,ls in [(0,'-'),(1,'--')]:
            data=[s for s in R['survival'] if s['system']==agent and s['failure']==fail]
            ax[1].plot([s['checkpoint'] for s in data],[s['fraction'] for s in data],ls,marker='o',color=color,
                       label=label+(' success' if not fail else ' failure'))
    ax[1].set_xlabel('Observed tool results');ax[1].set_ylabel('Fraction eligible');ax[1].set_xticks([5,10,20,40]);ax[1].set_ylim(0,1.05)
    ax[1].legend(fontsize=8,ncol=2,loc='lower left',bbox_to_anchor=(0,1.02))
    save(fig,'revision_sensitivity')
    c=next(c for c in R['checkpoints'] if c['checkpoint']==20)
    fig,ax=plt.subplots(1,2,figsize=(7.1,3.0),layout='constrained')
    names=['Source','Target prior','Prior correction','Sigmoid','ECDF','Target trained']
    vals=[c['metrics'][k] for k in ['unchanged','target_validation_prior','prior_shift','target_validation_sigmoid','ecdf_normalized','target_trained']]
    pos=np.arange(6)
    for axis,metric,color,title in zip(ax,['auroc','brier'],colors,['AUROC (higher is better)','Brier (lower is better)']):
        axis.barh(pos,[v[metric] for v in vals],color=color)
        axis.set_yticks(pos,names,fontsize=10);axis.invert_yaxis()
        axis.set_xlabel(title,fontsize=11)
        axis.set_xlim(0,.8 if metric=='auroc' else .55)
    save(fig,'revision_shift')
    fig,axis=plt.subplots(figsize=(4.4,2.8))
    drift=sorted(c['drift'],key=lambda d:abs(d['standardized_mean_difference']),reverse=True)[:6]
    labels={'n_assistant_messages':'Assistant messages','error_rate':'Error rate','n_errors':'Error count','max_error_streak':'Max. error streak','repeat_action_rate':'Repetition rate','n_unique_actions':'Unique actions',
            'mean_result_chars':'Mean result length','recent_result_chars':'Recent result length','tool_switches':'Tool switches',
            'n_shell':'Shell calls','n_reads':'Read calls','n_searches':'Search calls','n_other':'Other calls'}
    axis.barh(range(len(drift)),[d['standardized_mean_difference'] for d in drift],color=colors[0])
    axis.set_yticks(range(len(drift)),[labels.get(d['feature'],d['feature'].replace('_',' ')) for d in drift]);axis.invert_yaxis()
    axis.axvline(0,color='black',lw=.8);axis.set_xlabel('Standardized mean difference',fontsize=10)
    save(fig,'revision_feature_shift')
    fig,axes=plt.subplots(1,3,figsize=(7.1,2.6))
    cases=json.loads((ROOT/'results/visualization_results.json').read_text())
    for axis,case in zip(axes,cases):
        matrix=np.array(case['confusion_matrix_rows_actual_columns_predicted'])
        fractions=matrix/matrix.sum(axis=1,keepdims=True)
        axis.imshow(fractions,cmap='Blues',vmin=0,vmax=1)
        for i in range(2):
            for j in range(2):axis.text(j,i,str(matrix[i,j]),ha='center',va='center',fontsize=14,color='white' if fractions[i,j]>.5 else 'black')
        axis.set_xticks([0,1],['Continue','Alarm']);axis.set_yticks([0,1],['Success','Failure'])
        axis.set_xlabel(case['case'].replace('Qwen own training','Qwen target-trained')+'\nthreshold '+f"{case['threshold']:.4f}",fontsize=10)
    axes[0].set_ylabel('Terminal outcome')
    save(fig,'revision_confusion')


def report():
    lines=['# Major revision: complete exploratory results','',
           'All new analyses follow reviewer feedback on 10 October 2026. Neither checkpoint 20 nor these comparisons were preregistered. Original four-checkpoint reporting is retained. No target test labels fit transformations, calibration, models, or thresholds.','',
           '## Paired task-cluster differences on the original split','',
           '| Checkpoint | Target n | Own minus transfer AUROC | Paired 95% interval |','|---|---:|---:|---|']
    for c in R['checkpoints']:
        p=c['paired'];lo,hi=p['percentile_95ci']
        lines.append(f"|{c['checkpoint']}|{p['n']}|{p['difference']:.3f}|[{lo:.3f}, {hi:.3f}]|")
    lines+=['','Intervals condition on fitted models and test tasks; they do not include full training uncertainty. No multiplicity-adjusted tests or acceptance probabilities are claimed.','',
            '## Repeated grouped five-fold cross-validation','',
            'Each outer fold holds out whole tasks across all systems. A random 20% subset of the remaining tasks is validation; the rest trains the candidates. Target-trained and transferred scores are evaluated on identical target runs. Pooled out-of-fold AUROC mixes fold-specific score scales; results are sensitivity analyses, not independent replications. The paired intervals condition on the fold models.','',
            '| Checkpoint | Seed | Transfer AUROC | Own AUROC | Difference [paired 95% interval] |','|---|---|---:|---:|---|']
    for c in R['repeated_grouped_cv']:
        p=c['paired'];lo,hi=p['percentile_95ci']
        lines.append(f"|{c['checkpoint']}|{c['seed']}|{c['transfer']['auroc']:.3f}|{c['own']['auroc']:.3f}|{p['difference']:.3f} [{lo:.3f}, {hi:.3f}]|")
    lines+=['','## Target adaptation on the original split','',
            'Prior-shift correction adjusts log odds using source-training and target-validation failure prevalence; label-shift assumptions are unverified. Sigmoid regression uses target-validation labels only and allows negative slope, which reverses ranking at some checkpoints. ECDF baseline fits source feature ranks on source training and target ranks on target validation, then selects source classifiers using source validation. It does not use target test labels.','',
            '| Checkpoint | Method | AUROC | AP | Brier |','|---|---|---:|---:|---:|']
    for c in R['checkpoints']:
        for name,m in c['metrics'].items():lines.append(f"|{c['checkpoint']}|{name}|{m['auroc']:.3f}|{m['auprc']:.3f}|{m['brier']:.3f}|")
    lines+=['','## Eligibility by system and terminal outcome','',
            'Denominators use all 555 trajectories per system, stratified by terminal outcome. Eligibility means a prefix can be extracted; these are not event-time failure labels.','',
            '| Checkpoint | System | Outcome | Eligible / total | Fraction |','|---|---|---|---|---:|']
    for s in R['survival']:lines.append(f"|{s['checkpoint']}|{s['system']}|{'failure' if s['failure'] else 'success'}|{s['eligible']}/{s['total']}|{s['fraction']:.3f}|")
    lines+=['','## Cohort sensitivities','',
            'Common eligibility matches the same task/run index across all three systems, not the same stochastic trajectory. Conditioning on future eligibility is a descriptive sensitivity analysis, never a deployable selection rule. It can introduce collider selection and does not identify a causal selection-adjusted population effect. Fixed-target cohort uses Qwen runs reaching checkpoint 40, evaluated at earlier checkpoints. Missing-prefix inverse weighting is not identifiable here because completed short runs have no features at later checkpoints.','',
            '| Checkpoint | Common n | Common transfer / own AUROC | Fixed-target n | Fixed transfer / own AUROC |','|---|---:|---|---:|---|']
    for c in R['checkpoints']:
        a=c['common_all_systems_cohort'];b=c['fixed_target_cp40_cohort']
        lines.append(f"|{c['checkpoint']}|{a['n']}|{a['transfer'].get('auroc','NA')} / {a['own'].get('auroc','NA')}|{b['transfer']['n']}|{b['transfer']['auroc']} / {b['own']['auroc']}|")
    lines+=['','## Validation-only feature-shift diagnostics','',
            'These compare source versus target validation cohorts, whose outcome mixtures and harnesses differ. Standardized mean differences and KS distances are descriptive; they do not isolate a model-weight effect. No KS p-values or causal interpretation are used.','',
            '| Checkpoint | Feature | Standardized mean difference | KS distance |','|---|---|---:|---:|']
    for c in R['checkpoints']:
        for d in c['drift']:lines.append(f"|{c['checkpoint']}|{d['feature']}|{d['standardized_mean_difference']:.3f}|{d['ks_distance']:.3f}|")
    (ROOT/'MAJOR_REVISION_RESULTS.md').write_text('\n'.join(lines),encoding='utf8')


def manuscript():
    source=PAPER/'preact_mosicom2026.tex'
    old=source.read_text(encoding='utf8')
    backup=PAPER/'history/preact_before_major_revision.tex'
    backup.parent.mkdir(exist_ok=True)
    if not backup.exists():backup.write_text(old,encoding='utf8')
    bibliography=old[old.index(r'\begin{thebibliography}'):old.index(r'\end{thebibliography}')+len(r'\end{thebibliography}')]
    text=r'''\documentclass[conference]{IEEEtran}
\usepackage{amsmath,amssymb,booktabs,array,url,graphicx}
\graphicspath{{figures/}}
\title{Cross-System Transfer in Prefix-Based Software-Agent Failure Prediction}
\author{\IEEEauthorblockN{Anonymous review manuscript}}
\begin{document}
\maketitle
\begin{abstract}
Prefix-based monitors may identify unsuccessful software-agent runs, but their reliability can depend on the agent system, task partition, and which trajectories reach the prediction checkpoint. We audit inexpensive structural monitors on 1,665 public trajectories from three systems attempting the same 111 repository tasks. On one task-grouped partition at 20 tool results, source-system AUROC is 0.700, unchanged transfer to Qwen yields 0.456, and target-specific training yields 0.691. However, the paired target-trained minus transferred AUROC difference is 0.235 with a task-bootstrap 95\% interval of $[-0.071,0.459]$. Three repeated five-fold grouped evaluations produce transfer AUROC 0.463--0.562 and target-trained AUROC 0.497--0.558 at that checkpoint; the advantage changes sign. Eligibility is strongly system- and outcome-dependent. Target-validation adaptation improves Brier from 0.300 to 0.229 without improving ranking or outperforming a constant target-validation prior (0.223). These sensitivity analyses qualify the original finding: one favorable partition does not establish target-training superiority or isolate a model-weight effect. We provide pinned provenance and complete multi-checkpoint results. This observational study measures no prevention or intervention benefit.
\end{abstract}
\begin{IEEEkeywords}
software agents, failure prediction, cross-system transfer, grouped evaluation, calibration
\end{IEEEkeywords}

\section{Introduction}
Tool-using language-model agents interleave reasoning, actions and observations~\cite{react}. Long unsuccessful runs can expend considerable execution resources, motivating early outcome monitoring. Reflection~\cite{reflexion}, process feedback~\cite{sweprm}, and recovery architectures~\cite{selfhealing} address related reliability problems. Nevertheless, predicting eventual failure is distinct from preventing it: an accurate critic can disrupt runs that would succeed~\cite{interventionparadox}.

Early prediction, transfer, calibration and executed repair already have substantial precedents. The relevant empirical question here is narrower: \emph{how stable are inexpensive structural outcome predictors across task partitions, checkpoint populations, and a change of agent system?} We use ``system'' because the public traces vary model and scaffold jointly. We do not identify a model-only effect or present a completed predictive intervention controller.

The PreAct analysis package initially showed a sizable single-partition transfer contrast. We extend that pilot with paired task-cluster inference, repeated grouped evaluation, outcome-stratified checkpoint eligibility, common-cohort sensitivities, prior adjustment, target-validation calibration and feature-shift diagnostics. These additions are exploratory analyses following review. All four checkpoints are reported; the emphasis on 20 results was chosen after the original test results and is not a preregistered primary endpoint. The contribution is an auditable reliability and sensitivity study, not a novel warning architecture, universal transfer-failure claim, or state-of-the-art comparison.

\section{Related Work and Positioning}
PrefixGuard learns event sequences for horizon-specific risk~\cite{prefixguard}; weak supervision addresses sparse early evidence~\cite{sparse}. AgentForesight audits decisive-error prefixes~\cite{agentforesight}, ProMAS forecasts semantic transitions~\cite{promas}, and trajectory graphs supply pre-execution diagnostics~\cite{graphcopilot}. Early termination and model switching also precede this study~\cite{agentstop,atropos}. Table~\ref{tab:position} contrasts the closest settings. Their different targets and budgets prevent direct numerical ranking against our monitor.

FailFast--RestartSmart uses a 0.6B prefix monitor on SWE-bench Verified, transfers from Qwen to other policies, and executes artifact-preserving restart~\cite{failfast}. EarlyEval uses LightGBM behavior/text/reference-solution features across three benchmarks, with leave-one-agent-out prediction for cheaper evaluation~\cite{earlyeval}. Dubey studies telemetry detection, serving-specific transfer/recalibration, and matched-checkpoint repair~\cite{sentinel}. We instead audit 20 structural features on a separate 111-task SWE-Rebench cohort, use task-grouped repeated evaluation, and separate ranking, probability adaptation and checkpoint selection. We do not claim that transfer failure or recalibration was first discovered here.

Outcome labels also have limits: AgentLens finds defects in passing runs~\cite{agentlens}; evaluator disagreements appear in AgentRewardBench~\cite{agentrewardbench}; early error onset need not coincide with visible evidence~\cite{failureprocess}. Cao's target-specific calibration audit is another predecessor~\cite{calibrationaudit}. ProbGuard and AgentSpec respectively predict unsafe reachability and enforce runtime rules~\cite{probguard,agentspec}. Executed debugging interventions in DoVer differ from imagined counterfactual corrections in A2P~\cite{dover,a2p}. The inspected self-healing paper says its experiments are ongoing; we treat it as a proposal~\cite{selfhealing}. The supplementary 40-paper evidence map retains source locations and qualified classifications; it is a targeted extraction, not independently double-screened synthesis.

\begin{table*}[t]
\centering\footnotesize
\caption{Closest-study comparison. Prior-study findings are author-reported, not reproduced by our experiments.}
\label{tab:position}
\begin{tabular}{@{}p{.18\textwidth}p{.26\textwidth}p{.27\textwidth}p{.22\textwidth}@{}}
\toprule Study & Data / representation & Evaluation purpose & Distinction from this audit \\
\midrule
FailFast~\cite{failfast} & SWE-bench Verified; learned 0.6B prefix monitor & Cross-policy warning and executed restart & Different dataset; task/budget success and resource effects \\
EarlyEval~\cite{earlyeval} & Three benchmarks; behavior, text, reference features & Held-out-agent verdict prediction and halting & Benchmark-cost objective; richer features \\
Telemetry~\cite{sentinel} & Synthetic/external telemetry and booking cohorts & Transfer, recalibration, executed checkpoint repair & Different event targets and injected/live populations \\
This study & SWE-Rebench; 111 tasks, three systems; 20 structural features & Terminal outcome; paired and repeated task-grouped prediction audit & Partition/eligibility sensitivity; no executed intervention \\
\bottomrule
\end{tabular}
\end{table*}

\section{Data and Prediction Protocol}
\subsection{Source, Target and Eligibility}
We use five attempts per task from Claude Code, GPT-5.6-Luna and Qwen3.6-27B in the public SWE-Rebench July 2026 trajectories~\cite{rebench}. The 111 shared tasks produce 1,665 traces: 750 resolved and 915 unresolved, with 81,534 calls and 82,079 tool-result events. Source-shard decompressed SHA-256 digests are checked against the pinned index. Let $Y=1$ mean unresolved terminal evaluation. A monitor predicts
\begin{equation}
 r_t=P(Y=1\mid h_t),\qquad t\in\{5,10,20,40\},
\end{equation}
from prefix $h_t$ after the first $t$ matched call/result pairs are observed. Parallel calls can delay this boundary; counts are not comparable semantic progress across harnesses. Runs without a complete prefix leave that checkpoint's risk set. This is eventual-outcome prediction, not an error-time or next-$k$-step hazard label.

\subsection{Features, Models and Original Split}
Twenty features cover error counts/rates/streaks, exact action repetition, unique actions, edit/read/search/test/shell/other counts, category switches, result lengths, assistant-message counts, and final prefix action type. Recent summaries use five actions; result length is capped at 65,536 characters. Fingerprints concatenate tool name and the first 500 characters of sorted JSON arguments; collisions and harness shortcuts are possible. Future events, terminal answers, reference patches and evaluated outcomes are excluded from features. An executable fixture checks invariance to future suffixes and terminal labels; real-data checks verify split disjointness, without certifying every possible leakage mode.

The first 12 hexadecimal digits of SHA-256(task ID), modulo 10, allocate residues 0--5 to training, 6--7 to validation and 8--9 to testing. Actual counts are 78/16/17 tasks; repeated attempts remain together. Pooled source training/validation excludes Qwen entirely. Target-specific controls instead use Qwen training/validation tasks, never target test labels. Standard-scaled logistic regression uses $C=0.3$ and 1,000 maximum iterations. Histogram gradient boosting uses 90 iterations, seven maximum leaves, learning rate 0.04, L2 penalty 2 and seed 2026. Validation average precision (AP) selects a candidate independently at each checkpoint; test outcomes select neither models nor thresholds. Baselines are a constant training prior and the published error/repetition heuristic.

\subsection{Statistics and Repeated Grouped Evaluation}
We report AUROC, AP against failure prevalence, Brier score and exact confusion matrices. Alarms strictly exceed the validation-success 90th percentile. A paired bootstrap resamples whole target-test tasks with replacement 2,000 times, applying each sampled index to both models. Its percentile interval is for target-trained minus transferred AUROC on identical Qwen examples and conditions on fitted models; it omits full training uncertainty. It replaces interpreting overlap of separate intervals as a difference test.

Three additional seeds (20261010--20261012) generate five outer task folds. Within each outer training partition, 20\% of its tasks form validation, shared across systems; the remainder trains the candidates. No outer-test tasks fit any model or transformation. We pool cross-fitted target predictions per seed, report all checkpoints, and retain fold selections in the archive. These pooled AUROCs combine fold-specific score scales and are sensitivity measures. Seeds share the same tasks, so they are not independent replications; corresponding task-bootstrap intervals condition on fold fits. No multiplicity-adjusted hypothesis tests are claimed.

\subsection{Selection, Calibration and Shift Checks}
Eligibility is tabulated by system and terminal outcome using all 555 runs per system. A common cohort retains task/run indices reaching the checkpoint in all three systems; it matches attempts, not stochastic paths. A second sensitivity fixes the Qwen cohort reaching 40 results and evaluates it at earlier checkpoints. Both condition on future trajectory duration and are descriptive, with possible collider selection. Missing later prefixes of completed short runs prevent identifying a full-population inverse-weighted estimate.

Prior correction adds the difference between target-validation and source-training failure log odds to source scores. Label-shift assumptions are unverified. A sigmoid logistic calibrator fits target-validation score logits and labels only; its unconstrained slope can reverse ranking, so it is not always monotone calibration. The stronger normalization baseline uses empirical feature ranks: source training defines source ECDFs, target validation defines target ECDFs, and source validation selects the classifier. Validation-only standardized mean differences and KS distances diagnose feature drift without test-label access or causal interpretation. No semantic monitor is evaluated.

\section{Results}
\subsection{Original Partition and Paired Evidence}
Table~\ref{tab:original} retains all original checkpoints. At 20 results, source-system AUROC is 0.700 (task-bootstrap interval [0.549,0.837]), AP 0.730 and Brier 0.214; constant-prior and error/repetition AUROCs are 0.500 and 0.576. Qwen transfer gives AUROC 0.456, AP 0.647 and Brier 0.300; AP is below its 0.671 prevalence. Target-trained AUROC is 0.691, AP 0.795 and Brier 0.200. However, the paired AUROC advantage is 0.235 [${-}0.071$,0.459], which includes zero. The original partition supports a possible reliability difference, not robustly established superiority.

\begin{table}[t]
\centering\footnotesize
\caption{Original split. S: source systems; T: unchanged Qwen transfer; O: Qwen-trained. $\Delta$: O minus T, paired task-bootstrap 95\% interval.}
\label{tab:original}
\begin{tabular}{@{}rrrrrl@{}}\toprule
$t$ & $n_S/n_T$ & S AUROC & T & O & $\Delta$ [interval] \\
\midrule
5 & 170/85 & .585 & .475 & .369 & ${-}.106$ [${-}.228$,.005] \\
10 & 158/85 & .610 & .422 & .571 & .149 [${-}.003$,.311] \\
20 & 92/85 & .700 & .456 & .691 & .235 [${-}.071$,.459] \\
40 & 50/74 & .588 & .551 & .613 & .062 [${-}.055$,.184] \\
\bottomrule\end{tabular}
\end{table}

Original checkpoint-20 alarms identify 13 of 44 source failures with two false alarms (29.5\% recall, 4.2\% false-alarm rate); unchanged transfer identifies five of 57 Qwen failures with three false alarms (8.8\%,10.7\%). Target-trained alarms identify 12 failures with three false alarms (Fig.~\ref{fig:confusion}). These are eventual-outcome alarms, not prevented errors. The supplementary archive retains ROC/PR/reliability curves, prior controls and all original LR/HGB feature ablations.

\begin{figure*}[t]
\centering\includegraphics[width=\textwidth]{revision_confusion.pdf}
\caption{Original checkpoint-20 confusion matrices: actual terminal outcome by continue/alarm decision. Counts are exact; shading is row-normalized. The source-validation threshold transfers unchanged to Qwen; target-trained thresholds use target validation. No calibration adaptation is applied in these matrices.}
\label{fig:confusion}
\end{figure*}

\subsection{Partition Sensitivity}
Table~\ref{tab:cv} and Fig.~\ref{fig:sensitivity} show that the single-partition contrast is unstable. At 20 results, repeated grouped transfer AUROC ranges from 0.463 to 0.562, while target-trained AUROC ranges from 0.497 to 0.558. The advantage reverses for one seed; all three paired intervals include zero. Original within-Qwen signal therefore does not establish robust target-training superiority. Full four-checkpoint scores and conditional intervals are retained, including checkpoints where target training performs worse.

\begin{table}[t]
\centering\footnotesize
\caption{Checkpoint-20 repeated grouped five-fold evaluation. Seed suffixes: 20261010--20261012. Same target examples within each pair.}
\label{tab:cv}
\begin{tabular}{@{}rrrrl@{}}\toprule
Seed & $n$ & Transfer & Own & $\Delta$ [paired 95\% interval] \\
\midrule
10 & 553 & .463 & .558 & .094 [${-}.001$,.187] \\
11 & 553 & .562 & .497 & ${-}.065$ [${-}.151$,.021] \\
12 & 553 & .472 & .506 & .034 [${-}.054$,.119] \\
\bottomrule\end{tabular}
\end{table}

\begin{figure*}[t]
\centering\includegraphics[width=\textwidth]{revision_sensitivity.pdf}
\caption{Left: original paired task-bootstrap intervals and repeated grouped-CV differences, all checkpoints. Intervals condition on fitted models. Right: outcome-stratified prefix eligibility over all runs; solid denotes success and dashed failure. The moving risk sets are strongly system-dependent.}
\label{fig:sensitivity}
\end{figure*}

\subsection{Checkpoint Eligibility and Common Cohorts}
At 20 results, 300/335 successful and 218/220 failed Claude runs are eligible, versus only 24/242 successful and 84/313 failed Luna runs. Qwen retains 173/173 successes and 380/382 failures. Thus the pooled source cohort at later checkpoints becomes heavily reweighted toward Claude and long Luna failures. Differences in counts, duration and task composition can contribute to apparent transfer effects.

On the common all-system task/run cohort at 20 results, only 16 target-test runs remain: transfer/own AUROC is 0.564/0.691, versus 0.456/0.691 on the original 85 Qwen runs. No all-system common test runs remain at 40 results. Restricting instead to the fixed 74 Qwen runs reaching 40 results gives checkpoint-20 AUROC 0.480/0.665. These conditional results demonstrate sensitivity without eliminating selection bias, isolating harness effects, or supporting a deployable future-duration rule.

\subsection{Target Adaptation and Feature Drift}
At 20 results, prior adjustment improves Brier from 0.300 to 0.245 and target-validation sigmoid adaptation to 0.229; neither changes AUROC 0.456 because both maps are increasing. A constant target-validation failure prior has Brier 0.223, better than either adapted score; adaptation does not establish predictive benefit beyond this control. The ECDF baseline yields AUROC 0.446 and Brier 0.463. Table~\ref{tab:adapt} retains AP. Adaptation is not consistently beneficial: checkpoint-40 sigmoid slope is negative and AUROC falls from 0.551 to 0.449, with Brier rising from 0.229 to 0.265. Target validation cannot guarantee test calibration.

\begin{table}[t]
\centering\footnotesize
\caption{Checkpoint-20 Qwen test metrics. Target adaptation fits only the 16 validation tasks; no test-label fitting.}
\label{tab:adapt}
\begin{tabular}{@{}lrrr@{}}\toprule Method & AUROC & AP & Brier \\
\midrule
Unchanged source & .456 & .647 & .300 \\
Target-validation prior & .500 & .671 & .223 \\
Prior correction & .456 & .647 & .245 \\
Validation sigmoid & .456 & .647 & .229 \\
ECDF normalization & .446 & .672 & .463 \\
Target-trained & .691 & .795 & .200 \\
\bottomrule\end{tabular}
\end{table}

\begin{figure*}[t]
\centering\includegraphics[width=\textwidth]{revision_shift.pdf}
\caption{Checkpoint-20 adaptation and validation-only shift diagnostics. Brier is lower-is-better; AUROC is higher-is-better. Right shows the six largest absolute standardized mean differences. Drift can reflect harness and outcome-mixture differences; it does not identify their causes.}
\label{fig:shift}
\end{figure*}

Validation feature distributions differ substantially (Fig.~\ref{fig:shift}); all 20 standardized differences and KS distances are supplied. They establish covariate differences between observed cohorts, not model-weight causality or stable conditional-label relations. Rank normalization and prevalence correction test limited alternatives; richer semantic monitors, more systems and independent model/scaffold factorial comparisons remain unperformed.

\section{Reproducibility and Limitations}
The accompanying anonymous archive includes task IDs/splits, selected source-index records, compressed/decompressed hashes, dependency versions, scripts, aggregate JSONs and complete reports. Downloads use the verified Hub commit; raw traces remain at the source and are excluded from redistribution. A clean pinned Python 3.13.5 environment (NumPy 2.2.6, SciPy 1.15.3, scikit-learn 1.6.1) reproduced the four original analyses exactly and all revision numerical fields within $10^{-8}$. This verifies environment portability on the same data/code, not independent-data replication. Regeneration requires no language-model API or GPU. The archive is prepared locally; upload to the existing submission remains pending. Evidence-map judgments remain single-reviewer extraction.

A previous one-thread CPU audit (Windows 11, Python 3.13.5, scikit-learn 1.6.1) extracted 5,271 prefix rows in 2.85 s and fit two checkpoint-20 candidates in 0.035 s; median warmed batch inference over 92 rows was 0.763 ms. These timings exclude downloads, agent execution and orchestration, establishing neither energy savings nor online latency. The prior environment's NumPy metadata discrepancy and non-fatal optimizer warning are documented; the clean rerun eliminates these issues.

This study uses one dataset, only three jointly changing model/scaffold systems, terminal labels, and reused tasks across sensitivity seeds. Checkpoint selection and new analyses are exploratory. Outcome-stratified eligibility and common cohorts do not identify missing-prefix population performance. Conditional bootstrap intervals omit full training uncertainty, and pooled cross-fitted scores can differ in scale. A monitor that performs near chance after transfer should not control unsupported systems automatically. Source traces may contain sensitive repository content; aggregates avoid redistributing raw content. Subgroup fairness and intervention safety are unmeasured.

Future work should independently vary model and scaffold, evaluate another dataset, and compare structural with semantic/event monitors under shared tasks and budgets. Establishing prevention requires observable-error-time annotations and randomized continuation/verification/restart branches with matched total budgets and a resampling control~\cite{sentinel,dover}. Measure both recovery and disruption, not classifier accuracy alone. The complete proposed intervention protocol is supplementary and is not an implemented system.

\section{Conclusion}
The original task partition suggests a cross-system reliability problem, but paired uncertainty and repeated grouped evaluation do not establish a stable target-training advantage. Checkpoint eligibility changes the compared populations. Target-validation adaptation can improve probability error without recovering ranking or beating a constant target prior, and can degrade later performance. These findings support reporting task partitions, risk sets, paired uncertainty and baseline-adjusted adaptation alongside headline metrics. They demonstrate neither prevention nor a model-only transfer effect.

'''
    source.write_text(text+'\\IEEEtriggeratref{9}\n'+bibliography+'\n\\end{document}\n',encoding='utf8')


if __name__=='__main__':
    figures();report();manuscript()
