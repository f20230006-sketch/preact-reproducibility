$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:OMP_NUM_THREADS = '1'
$env:OPENBLAS_NUM_THREADS = '1'
function Invoke-Analysis([string]$ScriptName) {
    python $ScriptName
    if ($LASTEXITCODE -ne 0) { throw "Analysis failed: $ScriptName" }
}
Invoke-Analysis 'download_pilot.py'
Invoke-Analysis 'preact_pilot.py'
Invoke-Analysis 'preact_pilot_audit.py'
Invoke-Analysis 'preact_invariance_ablation.py'
Invoke-Analysis 'preact_retry_opportunity.py'
Invoke-Analysis 'visualize_results.py'
Invoke-Analysis 'reviewer_audit.py'
Invoke-Analysis 'revision_analysis.py'
Invoke-Analysis 'per_fold_audit.py'
Invoke-Analysis 'build_major_revision.py'
Invoke-Analysis 'final_editor_revision.py'
