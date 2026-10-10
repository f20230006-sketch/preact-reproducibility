"""Apply the verified literature synthesis to the existing empirical draft.

Preserves experimental results and their original figure files. Idempotent.
"""
from pathlib import Path
import json,re,shutil
ROOT=Path(__file__).resolve().parent
PAPER=ROOT.parents[1]/'paper_mosicom2026/preact_mosicom2026.tex'

RELATED=r'''\section{Related Work and Research Gap}
\label{sec:related-work-and-research-gap}
\subsection{Scope and Evidence Targets}
Our accompanying targeted review checks primary records and full texts for 40 papers through 4 October 2026: 15 direct monitoring/intervention papers, 16 adjacent diagnosis or recovery papers, and nine foundations. It is not an exhaustive systematic review or independently double-screened synthesis. Fig.~\ref{fig:literature-map} summarizes the direct studies. We distinguish terminal failure, decisive error onset, unsafe reachability, process quality, and intervention value; their metrics cannot be pooled as one outcome.

\subsection{Prefix and Pre-Action Monitoring}
PrefixGuard learns events for horizon-specific risk and finite-state diagnosis~\cite{prefixguard}. Its inspected revision keeps held-out tasks represented in training; unseen-task and unseen-agent performance remain unmeasured. Sparse-evidence training addresses delayed diagnostic turns~\cite{sparse}. AgentForesight audits prefixes near decisive errors~\cite{agentforesight}; ProMAS forecasts error localization through Markov semantic transitions~\cite{promas}. Trajectory Graph Copilot already evaluates proposed actions before execution and supplies corrective feedback~\cite{graphcopilot}. Therefore, prefix classification and pre-execution warning are established objectives, not our novelty claims.

\subsection{Transfer and Intervention Predecessors}
Transfer can succeed: FailFast--RestartSmart transfers a Qwen-trained monitor to other policies and couples alarms with artifact-preserving restart~\cite{failfast}; EarlyEval evaluates leave-one-agent-out prediction for cheaper benchmarking~\cite{earlyeval}. Their representations, tasks, costs and endpoints differ from ours. AgentStop trades some utility for energy savings~\cite{agentstop}, and Atropos combines multi-path termination with stronger-model hotswap~\cite{atropos}. SWE-PRM evaluates online feedback~\cite{sweprm}. ProbGuard predicts unsafe reachability, reporting both safety improvement and completion cost~\cite{probguard}; AgentSpec enforces explicit runtime constraints~\cite{agentspec}.

Crucially, Dubey's telemetry monitor already reports serving-specific transfer failure and recalibration, plus executed matched-checkpoint repair with a resampling control~\cite{sentinel}. Its headline synthetic AUROC, external-corpus tests and live repair cohort have distinct denominators. DoVer validates debugging hypotheses through actual interventions~\cite{dover}; A2P instead imagines counterfactual corrections within an LLM inference~\cite{a2p}. Matched-prefix branching and causal-style diagnosis thus have predecessors. Vasudev et al. show that accurate prediction can still disrupt successful runs~\cite{interventionparadox}.

\subsection{Label Validity and the Present Contribution}
AgentLens finds process defects in passing software-agent runs~\cite{agentlens}, and AgentRewardBench exposes evaluator disagreement~\cite{agentrewardbench}. A CLI-trajectory study distinguishes early error onset from later visibility~\cite{failureprocess}; this is compatible with sparse observable evidence. The self-healing framework's inspected Section 4.4 says experiments are ongoing, so we cite it as a proposal rather than completed recovery evidence~\cite{selfhealing}. Cao's audit finds persistent calibration errors in specific target/head cells, without establishing broad heterogeneity or cross-benchmark replication~\cite{calibrationaudit}.

Our present contribution is a task-grouped, prefix-only structural-monitor pilot and a negative transfer finding in a different software-agent dataset. It does not establish state-of-the-art superiority or a universal transfer failure. The remaining research question is whether calibrated intervention selection retains net utility on organic failures when model and scaffold shifts are varied independently, including disruption and complete execution cost.

\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{evidence_map.pdf}
\caption{Evidence map of the 15 direct papers in the targeted review. R denotes reported evidence; Q denotes a qualified comparison or different estimand; NR denotes evidence not extracted or established for that column, not proof of absence. Multiple tested models do not imply held-out-agent transfer. Intervention may target task, safety or resource outcomes; replay/control distinguishes executed comparisons from imagined counterfactuals. Cells are reviewer assessments, not quality scores.}
\label{fig:literature-map}
\end{figure*}

'''

FACTORIAL=r'''\subsection{Separating Model and Scaffold Shift}
The follow-up should independently vary model and scaffold. A factorial design trains on one combination and evaluates a new model with the original scaffold, the original model with a new scaffold, and their joint change. Raw structural, normalized, semantic and event-based monitors should share task splits and budgets. A target calibration set must remain separate from target testing. This distinguishes harness shortcuts from model change, which our current pooled transfer test cannot do. Organic failures should be the primary cohort; injected faults provide a separate robustness arm. Since matched-checkpoint repair and recalibration already exist~\cite{sentinel,dover}, the intended advance is a prospectively tested, cost-constrained policy under these controlled shifts, not branching alone.

'''

def main():
    s=PAPER.read_text(encoding='utf8')
    s=re.sub(r'\\section\{Related Work and Research Gap\}.*?(?=\\section\{Problem Definition\})',lambda m:RELATED,s,flags=re.S)
    s=s.replace('and recovering after detected errors~\\cite{selfhealing}', 'and proposing integrated recovery architectures~\\cite{selfhealing}')
    s=s.replace('Thus, merely building another binary predictor would offer a weak distinction.', 'Thus, another binary predictor alone would offer a weak distinction; prior work already studies transfer, calibration and checkpoint repair~\\cite{sentinel,calibrationaudit}.')
    s=s.replace('an empirical transfer finding that reverses the usefulness of a monitor trained on other agents', 'a negative transfer finding for a monitor trained on two other systems')
    s=s.replace('A subsequent online trial should randomize eligible prefixes', 'Following prior executed repair studies~\\cite{sentinel,dover}, a subsequent online trial should randomize eligible prefixes')
    s=re.sub(r'\\subsection\{Separating Model and Scaffold Shift\}.*?(?=\\subsection\{Calibrated Decision)', '',s,flags=re.S|re.I)
    s=re.sub(r'\\subsection\{Calibrated decision and abstention\}',lambda m: FACTORIAL+m.group(0),s,flags=re.I)
    # Repeated edits do not add repeated bibliographic entries.
    additions={
      'sentinel':('2608.02464', 'S. Dubey'),
      'probguard':('2508.00500','H. Wang, C. M. Poskitt, J. Wei, and J. Sun'),
      'agentspec':('2503.18666','H. Wang, C. M. Poskitt, and J. Sun'),
      'promas':('2603.20260','X. Zhao \\emph{et al.}'),
      'dover':('2512.06749','M. Ma \\emph{et al.}'),
      'a2p':('2509.10401',''),
      'agentlens':('2605.12925',''),
      'failureprocess':('2607.09510','')}
    records={r['arxiv_id']:r for r in json.loads((ROOT/'extracted_papers.json').read_text(encoding='utf8'))}
    refs=[]
    for key,(aid,author) in additions.items():
        if '\\bibitem{'+key+'}' in s:continue
        r=records[aid]
        if not author:
            last,first=r['authors'][0].split(', ',1)
            author=' '.join(x[0]+'.' for x in first.split())+' '+last+' \\emph{et al.}'
        title=r['title'].replace('&',r'\&')
        refs.append('\\bibitem{'+key+'} '+author+', ``'+title+',\'\' arXiv:'+aid+', '+r['date'][:4]+'.')
    s=s.replace('\\end{thebibliography}','\n'.join(refs)+'\n\\end{thebibliography}')
    s=s.replace('\\begin{thebibliography}{15}','\\begin{thebibliography}{99}')
    s=re.sub(r'(\\bibitem\{calibrationaudit\}.*?``).*?(,\'\' arXiv:2609\.25647)',lambda m:m[1]+records['2609.25647']['title']+m[2],s)
    # Title case and consistent labeled display equations, following the reference.
    s=re.sub(r'\\subsection\{([^}]+)\}',lambda m:'\\subsection{'+m[1].title().replace('Swe','SWE')+'}',s)
    for eq,label in [(r'h_t=(g,a_0,o_1,a_1,o_2,\ldots,a_{t-1},o_t).','eq:prefix'),
                     (r'r_t=P(Y=0\mid h_t,\pi_0).','eq:risk'),
                     (r'Q_m(h_t)=\mathbb{E}[Y(m)-\lambda C(m)-\mu D(m)\mid h_t].','eq:value')]:
        if '\\label{'+label+'}' not in s:s=s.replace(eq,'\\label{'+label+'}\n'+eq)
    PAPER.write_text(s,encoding='utf8')
    shutil.copy2(ROOT/'outputs/evidence_map.pdf',PAPER.parent/'figures/evidence_map.pdf')
    print('Strengthened paper with verified review and eight additional cited predecessors.')

if __name__=='__main__':main()
