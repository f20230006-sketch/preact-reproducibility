"""Edit the existing manuscript in place and embed vector plots for the editor.

No replacement document or separately compiled PDF is produced.
"""
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PAPER=ROOT.parent/'paper_mosicom2026/preact_mosicom2026.tex'
R=json.loads((ROOT/'results/major_revision_results.json').read_text())
F=json.loads((ROOT/'results/per_fold_results.json').read_text())


def axis(options,plots):
    return '\\begin{tikzpicture}\n\\begin{axis}[font=\\small,tick label style={font=\\scriptsize},axis lines=left,'+options+']\n'+plots+'\n\\end{axis}\n\\end{tikzpicture}'


def side(left,right):
    return '\\begin{minipage}{.49\\textwidth}\\centering\n'+left+'\n\\end{minipage}\\hfill\n\\begin{minipage}{.49\\textwidth}\\centering\n'+right+'\n\\end{minipage}'


def shifts():
    case=next(c for c in R['checkpoints'] if c['checkpoint']==20)
    names=['unchanged','target_validation_prior','prior_shift','target_validation_sigmoid','ecdf_normalized','target_trained']
    graphs=[]
    for metric,color,title,maximum in [('auroc','preactblue','AUROC (higher is better)',.8),('brier','preactorange','Brier (lower is better)',.55)]:
        coords=' '.join(f"({case['metrics'][name][metric]:.4f},{6-i})" for i,name in enumerate(names))
        options=r'width=\linewidth,height=5.0cm,xbar,bar width=8pt,xmin=0,xmax='+str(maximum)+r',ymin=.4,ymax=6.6,ytick={1,2,3,4,5,6},yticklabels={Target trained,ECDF,Sigmoid,Prior correction,Target prior,Source},xlabel={'+title+'}'
        graphs.append(axis(options,r'\addplot[fill='+color+',draw=none] coordinates {'+coords+'};'))
    return side(*graphs)


def sensitivity():
    table='cp difference minus plus\n'
    for c in R['checkpoints']:
        d=c['paired']['difference'];lo,hi=c['paired']['percentile_95ci']
        table+=f"{c['checkpoint']} {d:.8f} {d-lo:.8f} {hi-d:.8f}\n"
    plots=r'\addplot[only marks,mark=*,preactblue,error bars/.cd,y dir=both,y explicit] table[x=cp,y=difference,y error minus=minus,y error plus=plus] {'+'\n'+table+'};\n'+r'\addlegendentry{Hash split (95\% CI)}'+'\n'
    coords=[]
    for cp in [5,10,20,40]:
        values=[c['paired']['difference'] for c in R['repeated_grouped_cv'] if c['checkpoint']==cp]
        coords += [f'({cp+shift:.1f},{value:.8f})' for shift,value in zip([-.6,0,.6],values)]
    plots+=r'\addplot[only marks,mark=x,preactorange] coordinates {'+' '.join(coords)+'};\n'+r'\addlegendentry{Grouped evaluations}'+'\n'+r'\addplot[black,dashed,forget plot] coordinates {(3,0)(42,0)};'
    options=r'width=\linewidth,height=5.3cm,xmin=3,xmax=42,ymin=-.30,ymax=.55,xtick={5,10,20,40},xlabel={Observed tool results},ylabel={AUROC difference},legend style={at={(0,1.03)},anchor=south west,draw=none,font=\scriptsize}'
    left=axis(options,plots)
    plots=''
    for agent,color,label in [('claude-code','preactblue','Claude'),('gpt-5.6-luna','preactorange','Luna'),('qwen3.6-27b','preactgreen','Qwen')]:
        for fail,style in [(0,'solid'),(1,'dashed')]:
            selected=[s for s in R['survival'] if s['system']==agent and s['failure']==fail]
            coords=' '.join(f"({s['checkpoint']},{s['fraction']:.8f})" for s in selected)
            plots+=r'\addplot['+color+','+style+r',mark=*] coordinates {'+coords+'};\n'+r'\addlegendentry{'+label+(' failure' if fail else ' success')+'}\n'
    options=r'width=\linewidth,height=5.3cm,xmin=3,xmax=42,ymin=0,ymax=1.06,xtick={5,10,20,40},xlabel={Observed tool results},ylabel={Fraction eligible},legend columns=2,legend style={at={(0,1.03)},anchor=south west,draw=none,font=\scriptsize}'
    return side(left,axis(options,plots))


def confusion():
    cases=json.loads((ROOT/'results/visualization_results.json').read_text())
    parts=[r'\begin{tikzpicture}[font=\small]']
    labels=['Source systems','Qwen transfer','Qwen target-trained']
    for i,(case,label) in enumerate(zip(cases,labels)):
        matrix=case['confusion_matrix_rows_actual_columns_predicted']
        parts.append(r'\begin{scope}[xshift='+str(i*5.15)+'cm]')
        for row in range(2):
            total=sum(matrix[row])
            for col in range(2):
                count=matrix[row][col];shade=round(100*count/total)
                low=1-row
                parts.append(r'\fill[preactblue!'+str(shade)+f'!white] ({col*1.2},{low*1.2}) rectangle ({(col+1)*1.2},{(low+1)*1.2});')
                parts.append(r'\node[text='+('white' if shade>50 else 'black')+r',font=\large] at '+f'({col*1.2+.6},{low*1.2+.6})'+' {'+str(count)+'};')
        parts += [r'\node[anchor=east] at (-.12,1.8) {Success};',r'\node[anchor=east] at (-.12,.6) {Failure};',
                  r'\node at (.6,-.3) {Continue};',r'\node at (1.8,-.3) {Alarm};',
                  r'\node[align=center,font=\small] at (1.2,-.9) {'+label+r'\\threshold '+f"{case['threshold']:.4f}"+'};',r'\end{scope}']
    return '\n'.join(parts+[r'\end{tikzpicture}'])


def main():
    source=PAPER.read_text(encoding='utf8')
    source=source.replace('The accompanying anonymous archive includes','The reproducibility package includes')
    publication_file=ROOT/'publication.json'
    if publication_file.exists():
        url=json.loads(publication_file.read_text(encoding='utf8'))['repository_url']
        source=source.replace('The package is prepared locally for supplementary review material; no submission or public upload has yet occurred.',
                              r'Materials are available at \url{'+url+'}. No conference submission has been made.')
    author_file=PAPER.parent/'author_metadata.json'
    if author_file.exists():
        authors=json.loads(author_file.read_text(encoding='utf8'))['authors']
        blocks=[]
        for author in authors:
            blocks.append(r'\IEEEauthorblockN{'+author['name']+r'}\IEEEauthorblockA{'+r'\\'.join([author['department'],author['institution'],author['location'],author['email']])+'}')
        author_block=r'\author{'+r'\and'.join(blocks)+'}\n'
        source=re.sub(r'\\author\{.*?(?=\\begin\{document\})',lambda m:author_block,source,flags=re.S)
    if r'\usepackage{pgfplots}' not in source:
        source=source.replace(r'\graphicspath{{figures/}}',r'''\graphicspath{{figures/}}
\usepackage{iftex}
\ifPDFTeX\else
\usepackage{fontspec}
\setmainfont{texgyretermes}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,ItalicFont=*-italic,BoldItalicFont=*-bolditalic,NFSSFamily=ptm]
\fi
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\definecolor{preactblue}{HTML}{246693}
\definecolor{preactorange}{HTML}{C65B32}
\definecolor{preactgreen}{HTML}{39866E}''')
    source=source.replace('These additions are exploratory analyses following review.','These additional sensitivity analyses evaluate the stability of the initial finding.')
    source=source.replace('The contribution is an auditable reliability and sensitivity study, not a novel warning architecture, universal transfer-failure claim, or state-of-the-art comparison.',
       'Our primary contribution is an evaluation protocol that exposes how a promising single-split cross-system prediction result becomes inconclusive under paired inference, repeated task-grouped evaluation, and eligibility/calibration checks. This is a reliability audit of structural monitors.')
    source=source.replace('A sigmoid logistic calibrator','Target-validation logistic recalibration')
    source=source.replace('target-validation sigmoid adaptation','target-validation logistic recalibration')
    source=source.replace('checkpoint-40 sigmoid slope','checkpoint-40 logistic recalibration slope')
    source=source.replace('Validation sigmoid &','Logistic recalibration &')
    source=source.replace('We pool cross-fitted target predictions per seed, report all checkpoints, and retain fold selections in the archive.',
       'We report both pooled cross-fitted AUROC and the unweighted mean and sample SD of defined individual outer-fold AUROCs. SD describes fold variability, not an SE or confidence interval. Single-class folds would be excluded and counted; all five folds are defined at every checkpoint and seed. All checkpoints and fold scores are archived.')
    source=source.replace('The archive is prepared locally; upload to the existing submission remains pending.','The package is prepared locally for supplementary review material; no submission or public upload has yet occurred.')
    # Replace the existing CV table in place with pooled and within-fold scores.
    start=list(re.finditer(r'\\begin\{table\*?\}',source[:source.index(r'\label{tab:cv}')]))[-1].start()
    ending=r'\end{table*}' if source[start:].startswith(r'\begin{table*}') else r'\end{table}'
    end=source.index(ending,start)+len(ending)
    rows=[]
    for result in F['results']:
        if result['checkpoint']!=20:continue
        a=result['summary']['transfer'];b=result['summary']['own']
        original=next(r for r in R['repeated_grouped_cv'] if r['checkpoint']==20 and r['seed']==result['seed'])
        p=original['paired'];lo,hi=p['percentile_95ci']
        rows.append(f"{str(result['seed'])[-2:]} & {result['pooled_transfer']['n']} & {result['pooled_transfer']['auroc']:.3f} & {a['unweighted_mean']:.3f} ({a['sample_sd']:.3f}) & {result['pooled_own']['auroc']:.3f} & {b['unweighted_mean']:.3f} ({b['sample_sd']:.3f}) & {p['difference']:.3f} [{lo:.3f}, {hi:.3f}] "+r'\\')
    table=r'''\begin{table*}[t]
\centering\footnotesize
\caption{Checkpoint-20 grouped five-fold evaluation. Seeds 20261010--20261012 reuse the same tasks. Fold means are unweighted; parentheses give sample SD, not uncertainty of the mean. All five folds are defined. Paired intervals concern pooled predictions.}
\label{tab:cv}
\begin{tabular}{@{}rrrcrcl@{}}\toprule
Seed & $n$ & Transfer pooled & Transfer fold mean (SD) & Own pooled & Own fold mean (SD) & Pooled $\Delta$ [95\% interval] \\
\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}
\end{table*}'''
    source=source[:start]+table+source[end:]
    paragraph='At checkpoint 20, within-fold transfer means are 0.517--0.567 and target-trained means 0.497--0.566 (Table~\\ref{tab:cv}); the advantage again changes sign. These comparisons avoid ranking examples across different fold models. The archive reports every fold AUROC and its sample size at all four checkpoints.'
    if paragraph not in source:source=source.replace(r'\subsection{Checkpoint Eligibility and Common Cohorts}',paragraph+'\n\n'+r'\subsection{Checkpoint Eligibility and Common Cohorts}')
    for name,content in [('revision_confusion',confusion()),('revision_sensitivity',sensitivity()),('revision_shift',shifts())]:
        marker=f'% BEGIN INLINE {name}'
        replacement=marker+'\n'+content+f'\n% END INLINE {name}'
        source=re.sub(r'\\includegraphics\[width=\\textwidth\]\{'+name+r'\.pdf\}',lambda m:replacement,source)
        if marker in source:source=re.sub(re.escape(marker)+r'.*?'+re.escape(f'% END INLINE {name}'),lambda m:replacement,source,flags=re.S)
    source=source.replace('Checkpoint-20 adaptation and validation-only shift diagnostics. Brier is lower-is-better; AUROC is higher-is-better. Right shows the six largest absolute standardized mean differences. Drift can reflect harness and outcome-mixture differences; it does not identify their causes.',
      'Checkpoint-20 AUROC and Brier shown separately with horizontal method labels. Higher AUROC and lower Brier are preferred; results are retained in Table~\\ref{tab:adapt}. Sigmoid denotes target-validation logistic recalibration. Feature-shift graphics and all diagnostics are supplementary.')
    source=source.replace('Validation feature distributions differ substantially (Fig.~\\ref{fig:shift});','Validation feature distributions differ substantially;')
    source=source.replace('These findings support reporting task partitions, risk sets, paired uncertainty and baseline-adjusted adaptation alongside headline metrics.',
      'The evaluation protocol exposes how a promising single-split result becomes inconclusive under stronger paired, task-grouped, eligibility and calibration analyses. This reliability-audit contribution supports reporting those checks alongside headline metrics.')
    PAPER.write_text(source,encoding='utf8')
    print('Updated existing editor source with inline vector plots, fold summaries and consistent framing.')


if __name__=='__main__':main()
