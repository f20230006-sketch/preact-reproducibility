"""Populate the paper's empirical visual section from stored results."""
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
paper=ROOT.parent/'paper_mosicom2026/preact_mosicom2026.tex'
s=paper.read_text(encoding='utf8')
if '\\usepackage{graphicx}' not in s:
    s=s.replace('\\usepackage{url}', '\\usepackage{url}\n\\usepackage{graphicx}\n\\graphicspath{{figures/}}')
# Apply reference checklist without copying its example authors or prose.
s=re.sub(r'(\\section\{([^}]+)\})(?!\n\\label)', lambda m:m[1]+'\n\\label{sec:'+re.sub('[^a-z]+','-',m[2].lower()).strip('-')+'}',s)
s=s.replace('Table~\\ref{tab:main} shows', 'Table~\\ref{tab:main} summarizes')
if 'Section~\\ref{sec:data-and-methods}' not in s:
    s=s.replace('We release the analysis code and aggregate results separately from the downloaded trajectories.', 'We release the analysis code and aggregate results separately from the downloaded trajectories. Section~\\ref{sec:data-and-methods} describes the experiment, Section~\\ref{sec:results} reports its findings, and Section~\\ref{sec:toward-an-intervention-aware-preact} develops the next study.')
def figure(name, caption, label):
    return '\n\\begin{figure*}[t]\n\\centering\n\\includegraphics[width=\\textwidth]{'+name+'.pdf}\n\\caption{'+caption+'}\n\\label{fig:'+label+'}\n\\end{figure*}\n'
block='\n% BEGIN GENERATED EMPIRICAL VISUALS\n'
block+=figure('checkpoint_metrics', 'Checkpoint-wise discrimination and probability error. Solid lines denote selected monitors; dotted lines denote constant training-prior controls. Risk sets differ across checkpoints, so these are not longitudinal improvements on a fixed cohort.', 'checkpoints')
block+=figure('confusion_matrices', 'Exact alarm confusion matrices after 20 tool results. Rows denote actual terminal success/failure; columns denote continue/alarm. Shading is normalized within each row; annotations are counts. The source validation threshold transfers unchanged to Qwen; the own-training control uses its own validation threshold.', 'confusion')
block+=figure('discrimination_calibration', 'Receiver-operating-characteristic, precision--recall, and reliability curves at 20 results. Reliability uses five equal-width bins, omitting empty bins; small-bin estimates are descriptive. The diagonal is the chance ranking or perfect-calibration reference. Precision baselines are 0.478 for source agents and 0.671 for Qwen.', 'curves')
block+='\\subsection{Complete Controls and Operating Points}\n'
block+='Fig.~\\ref{fig:checkpoints} compares all four checkpoints with prior controls. Fig.~\\ref{fig:confusion} gives exact alarm counts; Fig.~\\ref{fig:curves} distinguishes ranking from calibration. At 20 results, source alarms contain 13 failures and two successful runs, while transferred alarms contain five failures and three successful runs. The own-training Qwen control detects 12 failures with three false alarms. These counts concern eventual outcomes, not prevented errors.\n'
audit=json.loads((ROOT/'results/preact_pilot_audit_results.json').read_text())
block+='\\begin{table}[t]\n\\caption{Within-agent controls on unseen tasks. Intervals are 95\\% task-bootstrap AUROC intervals. C: Claude Code; L: GPT-5.6-Luna; Q: Qwen3.6-27B.}\n\\label{tab:within}\n\\centering\\scriptsize\n\\begin{tabular}{@{}rlrrrr@{}}\\toprule\n$t$ & Agent & $n$ & AUROC [interval] & AUPRC & Brier \\\\\n\\midrule\n'
for r in audit['cases']:
    v=r['test']; ci=r['auroc_task_bootstrap_95pct']; agent={'claude-code':'C','gpt-5.6-luna':'L','qwen3.6-27b':'Q'}[r['participant']]
    block+=f"{r['checkpoint']} & {agent} & {v['n']} & {v['auroc']:.3f} [{ci[0]:.3f}, {ci[1]:.3f}] & {v['auprc']:.3f} & {v['brier']:.3f} \\\\\n"
block+='\\bottomrule\\end{tabular}\n\\end{table}\n'
block+=figure('feature_ablation', 'Feature ablation at 20 tool results. LR denotes logistic regression and HGB histogram gradient boosting. Normalizing counts into rates does not yield useful transfer discrimination. All variants are reported, without selecting a variant on test outcomes.', 'ablation')
block+='\\begin{table}[t]\n\\caption{Ablation probability metrics at 20 results. Each cell reports AUPRC/Brier. All: full features; mix: tool-category fractions.}\n\\label{tab:ablation}\n\\centering\\footnotesize\n\\begin{tabular}{@{}llrr@{}}\\toprule\nFeatures & Model & Source & Transfer \\\\\n\\midrule\n'
for r in json.loads((ROOT/'results/preact_invariance_ablation_results.json').read_text()):
    name={'all':'All','rates':'Rates','rates_plus_tool_mix':'Rates + mix'}[r['features']]; model='LR' if r['model']=='logistic' else 'HGB'
    a=r['source_test']; b=r['new_agent_test']
    block+=f"{name} & {model} & {a['auprc']:.3f}/{a['brier']:.3f} & {b['auprc']:.3f}/{b['brier']:.3f} \\\\\n"
block+='\\bottomrule\\end{tabular}\n\\end{table}\n'
block+='\\begin{table}[t]\n\\caption{Independent-repeat statistics over all 111 tasks per agent. $p_1$: mean success fraction among other attempts conditional on failure; $p_{\\mathrm{any}}$: at least one other success. Steps are provider-reported, with tool-call fallback, and are not comparable across agents.}\n\\label{tab:repeats}\n\\centering\\footnotesize\n\\begin{tabular}{@{}lrrrrr@{}}\\toprule\nAgent & Failed & $p_1$ & $p_{\\mathrm{any}}$ & Steps (S) & Steps (F) \\\\\n\\midrule\n'
for name,r in json.loads((ROOT/'results/preact_retry_opportunity_results.json').read_text()).items():
    name={'claude-code':'Claude','gpt-5.6-luna':'Luna','qwen3.6-27b':'Qwen'}[name]
    block+=f"{name} & {r['failed_runs']} & {r['other_attempt_success_rate_given_failure']:.3f} & {r['share_failed_runs_with_at_least_one_other_success']:.3f} & {r['mean_steps_success']:.1f} & {r['mean_steps_failure']:.1f} \\\\\n"
block+='\\bottomrule\\end{tabular}\n\\end{table}\n'
block+='Table~\\ref{tab:within} reports every within-agent checkpoint control; Fig.~\\ref{fig:ablation} and Table~\\ref{tab:ablation} report all ablations. Table~\\ref{tab:repeats} summarizes repeat opportunities and run lengths. The accompanying \\texttt{COMPLETE\\_RESULTS.md} provides every baseline, validation metric, operating point, and curve coordinate. Token savings, prevented failures, and causal early-warning horizons remain unmeasured because the source lacks controlled branches and event-time labels.\n'
block+='% END GENERATED EMPIRICAL VISUALS\n'
s=re.sub(r'\n% BEGIN GENERATED EMPIRICAL VISUALS.*?% END GENERATED EMPIRICAL VISUALS\n','',s,flags=re.S)
s=s.replace('\\section{Toward an Intervention-Aware PreAct}',block+'\n\\section{Toward an Intervention-Aware PreAct}')
import shutil
(paper.parent/'figures').mkdir(exist_ok=True)
for path in (ROOT/'figures').glob('*.pdf'):
    shutil.copy2(path, paper.parent/'figures'/path.name)
s=s.replace('\\graphicspath{{../preact_reproducibility/figures/}}', '\\graphicspath{{figures/}}')
paper.write_text(s,encoding='utf8')
