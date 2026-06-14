$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$Separator = [System.IO.Path]::PathSeparator
$env:PYTHONPATH = if ($env:PYTHONPATH) { "src$Separator$env:PYTHONPATH" } else { "src" }
$PythonBin = if ($env:PYTHON) {
  $env:PYTHON
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  'python'
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
  'python3'
} else {
  'python'
}

Write-Host "== Doctor =="
& $PythonBin -m repo_harness_creator doctor

Write-Host "== Compile =="
& $PythonBin -m compileall src tests

Write-Host "== Tests =="
& $PythonBin -m unittest discover -s tests

Write-Host "== Pin check =="
& $PythonBin scripts/check_pins.py --root .

Write-Host "== Self audit =="
& $PythonBin -m repo_harness_creator audit --target . --min-score 85
