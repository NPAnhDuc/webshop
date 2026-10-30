# Import the Kaggle-trained GGUF into the local Ollama as a separate model.
# The current model (qwen3:4b-instruct-2507-q4_K_M) is not touched; .env is not changed.
# Usage: .\scripts\import_qwen_sft_ollama.ps1 -Gguf D:\Downloads\shopbot_qwen_sft.Q4_K_M.gguf
param(
    [Parameter(Mandatory=$true)][string]$Gguf,
    [string]$Name='shopbot-qwen-sft-20261026',
    [string]$Base='qwen3:4b-instruct-2507-q4_K_M'
)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$env:OLLAMA_HOST='127.0.0.1:11435'
$env:OLLAMA_MODELS="$root\models\ollama"
if (-not (Test-Path $Gguf)) { throw "GGUF not found: $Gguf" }
$hash=(Get-FileHash $Gguf -Algorithm SHA256).Hash.ToLower()
# Reuse the base model's chat template and stop tokens so prompts render identically.
$show=Invoke-RestMethod -Method Post -Uri "http://$($env:OLLAMA_HOST)/api/show" -Body (@{model=$Base}|ConvertTo-Json) -ContentType 'application/json'
$lines=$show.modelfile -split "`n" | Where-Object { $_ -notmatch '^FROM ' -and $_ -notmatch '^#' }
$dir="$root\runtime\qwen_sft_import"
New-Item -ItemType Directory -Force $dir | Out-Null
$modelfile=@("FROM $((Resolve-Path $Gguf).Path)")+$lines
Set-Content -Path "$dir\Modelfile" -Value $modelfile -Encoding utf8
& "$root\runtime\ollama\ollama.exe" create $Name -f "$dir\Modelfile"
if ($LASTEXITCODE -ne 0) { throw 'ollama create failed' }
@{name=$Name;gguf=(Resolve-Path $Gguf).Path;sha256=$hash;base_template=$Base;created=(Get-Date).ToString('s')} |
    ConvertTo-Json | Set-Content "$dir\import.json" -Encoding utf8
Write-Host "Imported $Name (sha256 $hash)."
Write-Host "Evaluate without changing .env:"
Write-Host "  `$env:OLLAMA_MODEL='$Name'; `$env:RAG_EVIDENCE_RERANK='1'; .venv\Scripts\python.exe scripts\run_quality_loop_kb3_20261024.py --round kb3_sft_r1 --split development"
