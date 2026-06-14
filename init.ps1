param(
  [switch] $NoEnv
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ScriptRoot = if ($PSScriptRoot) {
  $PSScriptRoot
} else {
  Split-Path -Parent $MyInvocation.MyCommand.Path
}
Set-Location -LiteralPath $ScriptRoot

function Invoke-Native {
  param(
    [Parameter(Mandatory = $true)]
    [string] $FilePath,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $ArgumentList
  )

  & $FilePath @ArgumentList
  if ($LASTEXITCODE -ne 0) {
    throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($ArgumentList -join ' ')"
  }
}

function Clear-HarnessEnvironment {
  $Names = @(
    'ANTHROPIC_API_KEY',
    'ANTHROPIC_OAUTH_TOKEN',
    'OPENAI_API_KEY',
    'GEMINI_API_KEY',
    'GROQ_API_KEY',
    'CEREBRAS_API_KEY',
    'XAI_API_KEY',
    'OPENROUTER_API_KEY',
    'ZAI_API_KEY',
    'MISTRAL_API_KEY',
    'MINIMAX_API_KEY',
    'MINIMAX_CN_API_KEY',
    'AI_GATEWAY_API_KEY',
    'OPENCODE_API_KEY',
    'COPILOT_GITHUB_TOKEN',
    'GH_TOKEN',
    'GITHUB_TOKEN',
    'HF_TOKEN',
    'GOOGLE_APPLICATION_CREDENTIALS',
    'GOOGLE_CLOUD_PROJECT',
    'GCLOUD_PROJECT',
    'GOOGLE_CLOUD_LOCATION',
    'AWS_PROFILE',
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_SESSION_TOKEN',
    'AWS_REGION',
    'AWS_DEFAULT_REGION',
    'AWS_BEARER_TOKEN_BEDROCK',
    'AWS_CONTAINER_CREDENTIALS_RELATIVE_URI',
    'AWS_CONTAINER_CREDENTIALS_FULL_URI',
    'AWS_WEB_IDENTITY_TOKEN_FILE',
    'AZURE_OPENAI_API_KEY',
    'AZURE_OPENAI_BASE_URL',
    'AZURE_OPENAI_RESOURCE_NAME'
  )
  foreach ($Name in $Names) {
    Remove-Item -LiteralPath "Env:$Name" -ErrorAction SilentlyContinue
  }
}

if ($NoEnv) {
  Clear-HarnessEnvironment
  Write-Host '== Running without common AI, cloud, or GitHub credentials =='
}

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
Invoke-Native $PythonBin -m harnessforge doctor

Write-Host "== Compile =="
Invoke-Native $PythonBin -m compileall src tests

Write-Host "== Tests =="
Invoke-Native $PythonBin -m unittest discover -s tests

Write-Host "== Pin check =="
Invoke-Native $PythonBin scripts/check_pins.py --root .

Write-Host "== Self audit =="
Invoke-Native $PythonBin -m harnessforge audit --target . --min-score 85
