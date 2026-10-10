"""Recompute held-out predictions and generate publication figures and full tables.

No thresholds or models are selected using test outcomes. Run with PREACT_DATA_ROOT
pointing at the downloaded source shards. Outputs contain aggregate statistics only.
"""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, roc_curve, precision_recall_curve
from sklearn.calibration import calibration_curve
from preact_pilot import load_data
from preact_pilot_audit import fit_and_select

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'figures'
COLORS = ['#1764ab', '#cf552d', '#268466']
plt.rcParams.update({'font.size': 9, 'axes.spines.top': False,
                     'axes.spines.right': False, 'pdf.fonttype': 42})

def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / (name + '.pdf'), bbox_inches='tight')
    fig.savefig(OUT / (name + '.png'), dpi=200, bbox_inches='tight')
    plt.close(fig)

def main():
    OUT.mkdir(exist_ok=True)
    data = [r for r in load_data() if r['checkpoint'] == 20]
    cases = []
    for label, training_agent, test_agent in [
        ('Source agents', None, None), ('Qwen transfer', None, 'qwen3.6-27b'),
        ('Qwen own training', 'qwen3.6-27b', 'qwen3.6-27b')]:
        def training(r):
            return r['participant'] == training_agent if training_agent else r['participant'] != 'qwen3.6-27b'
        train = [r for r in data if training(r) and r['split'] == 'train']
        val = [r for r in data if training(r) and r['split'] == 'val']
        test = [r for r in data if r['split'] == 'test' and
                (r['participant'] == test_agent if test_agent else training(r))]
        _, model_name, model = fit_and_select(train, val)
        pv = model.predict_proba(np.array([r['features'] for r in val]))[:, 1]
        p = model.predict_proba(np.array([r['features'] for r in test]))[:, 1]
        y = np.array([r['failure'] for r in test])
        threshold = float(np.quantile(pv[np.array([r['failure'] for r in val]) == 0], .9))
        cm = confusion_matrix(y, p > threshold, labels=[0, 1])
        cases.append((label, y, p, threshold, cm, model_name))
    fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.25))
    for ax, (label, y, p, threshold, cm, _) in zip(axes, cases):
        ax.imshow(cm / cm.sum(axis=1, keepdims=True), vmin=0, vmax=1, cmap='Blues')
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(cm[i, j]), ha='center', va='center',
                        color='white' if cm[i, j]/cm[i].sum() > .5 else 'black', fontsize=12)
        ax.set_xticks([0, 1], ['Continue', 'Alarm'])
        ax.set_yticks([0, 1], ['Success', 'Failure'])
        ax.set_xlabel(label + '\n' + f'threshold = {threshold:.4f}')
    axes[0].set_ylabel('Observed terminal outcome')
    save(fig, 'confusion_matrices')
    fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.35))
    aggregate = []
    for color, (label, y, p, threshold, cm, model_name) in zip(COLORS, cases):
        fpr, tpr, _ = roc_curve(y, p)
        precision, recall, _ = precision_recall_curve(y, p)
        observed, predicted = calibration_curve(y, p, n_bins=5, strategy='uniform')
        axes[0].plot(fpr, tpr, color=color, label=label)
        axes[1].plot(recall, precision, color=color)
        axes[2].plot(predicted, observed, 'o-', color=color)
        aggregate.append({'case': label, 'selected_model': model_name, 'threshold': threshold,
                          'confusion_matrix_rows_actual_columns_predicted': cm.tolist(),
                          'labels': ['success/continue', 'failure/alarm'],
                          'roc_fpr': fpr.tolist(), 'roc_tpr': tpr.tolist(),
                          'pr_recall': recall.tolist(), 'pr_precision': precision.tolist(),
                          'calibration_predicted': predicted.tolist(), 'calibration_observed': observed.tolist()})
    axes[0].plot([0,1], [0,1], 'k--', lw=.7)
    axes[2].plot([0,1], [0,1], 'k--', lw=.7)
    for ax, xlabel, ylabel in zip(axes, ['False-positive rate', 'Failure recall', 'Mean predicted risk'],
                                ['True-positive rate', 'Precision', 'Observed failure fraction']):
        ax.set(xlabel=xlabel, ylabel=ylabel, xlim=(0,1), ylim=(0,1.03))
    axes[0].legend(fontsize=6, loc='lower right')
    save(fig, 'discrimination_calibration')
    pilot = json.loads((ROOT/'results/preact_pilot_results.json').read_text())
    fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.25))
    for color, group, label in zip(COLORS, ['held_out_tasks', 'held_out_agent_and_tasks'], ['Source agents', 'Qwen transfer']):
        rows = [r for r in pilot['results'] if r['group'] == group]
        for ax, metric in zip(axes, ['auroc', 'auprc', 'brier']):
            ax.plot([r['checkpoint'] for r in rows], [r['monitor'][metric] for r in rows], 'o-', color=color, label=label)
            ax.plot([r['checkpoint'] for r in rows], [r['prior'][metric] for r in rows], ':', color=color, lw=1)
            ax.set(xlabel='Observed tool results', ylabel=metric.upper(), xticks=[5,10,20,40])
    axes[0].legend(fontsize=7)
    save(fig, 'checkpoint_metrics')
    ablation = json.loads((ROOT/'results/preact_invariance_ablation_results.json').read_text())
    fig, ax = plt.subplots(figsize=(7.1, 2.05))
    x = np.arange(len(ablation))
    ax.bar(x-.18, [r['source_test']['auroc'] for r in ablation], .36, color=COLORS[0], label='Source agents')
    ax.bar(x+.18, [r['new_agent_test']['auroc'] for r in ablation], .36, color=COLORS[1], label='Qwen transfer')
    ax.axhline(.5, color='black', linestyle='--', lw=.7)
    ax.set_xticks(x, ['All\nLR','All\nHGB','Rates\nLR','Rates\nHGB','Rates + mix\nLR','Rates + mix\nHGB'])
    ax.set_ylabel('AUROC'); ax.set_ylim(0, .9); ax.legend(fontsize=8)
    save(fig, 'feature_ablation')
    (ROOT/'results/visualization_results.json').write_text(json.dumps(aggregate, indent=2))
    # Complete tabular supplement includes every stored result, including controls.
    lines = ['# Complete empirical results', '', 'All figures use real held-out predictions. Positive class: eventual failure.', '',
             '## Pooled prediction and baseline controls', '', '|Checkpoint|Group|Predictor|n|Failure fraction|AUROC|AUPRC|Brier|', '|---|---|---|---|---|---|---|---|']
    for r in pilot['results']:
        for predictor in ['monitor','prior','error_repeat_heuristic']:
            v=r[predictor]
            lines.append(f"|{r['checkpoint']}|{r['group']}|{predictor}|{v['n']}|{v['failure_rate']:.4f}|{v['auroc']:.4f}|{v['auprc']:.4f}|{v['brier']:.4f}|")
    for name in ['preact_pilot_audit_results','preact_invariance_ablation_results','preact_retry_opportunity_results','visualization_results']:
        lines.extend(['', '## '+name.replace('_',' '), '', '```json', (ROOT/'results'/f'{name}.json').read_text(), '```'])
    (ROOT/'COMPLETE_RESULTS.md').write_text('\n'.join(lines), encoding='utf8')
    print(json.dumps([{k:v for k,v in a.items() if k in ['case','threshold','confusion_matrix_rows_actual_columns_predicted']} for a in aggregate], indent=2))

if __name__ == '__main__':
    main()
