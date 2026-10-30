param([switch]$SkipKev,[switch]$EnableKev,[switch]$SkipMonthly,[switch]$SkipVietnameseEmbedding)
$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
$env:OLLAMA_HOST='127.0.0.1:11435'
$env:OLLAMA_MODELS="$PSScriptRoot\models\ollama"
$env:OLLAMA_VULKAN='1'
$env:OLLAMA_NO_CLOUD='1'
$env:HF_HOME="$PSScriptRoot\models\huggingface"
$env:HF_HUB_DISABLE_TELEMETRY='1'
$env:DO_NOT_TRACK='1'
$env:HF_HUB_DISABLE_XET='1'
$env:KEV_DTYPE='bf16'
$env:OMP_NUM_THREADS='4'
$env:TOKENIZERS_PARALLELISM='false'
$env:KEV_PREFIX_CACHE='1'
$env:KEV_PREFIX_MAX_TOKENS='2048'
try { Invoke-RestMethod http://127.0.0.1:11435/api/tags -TimeoutSec 2 | Out-Null }
catch { Start-Process -FilePath "$PSScriptRoot\runtime\ollama\ollama.exe" -ArgumentList 'serve' -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput "$PSScriptRoot\runtime\ollama.out.log" -RedirectStandardError "$PSScriptRoot\runtime\ollama.err.log" }
if ($EnableKev -and -not $SkipKev) {
 try { Invoke-RestMethod http://127.0.0.1:8009/v1/models -TimeoutSec 2 | Out-Null }
 catch { Start-Process -FilePath "$PSScriptRoot\.venv-kev\Scripts\python.exe" -ArgumentList '-m kev.serve --run jaredpalmer/kev-0.8b --device cpu --port 8009 --host 127.0.0.1' -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput "$PSScriptRoot\runtime\kev.out.log" -RedirectStandardError "$PSScriptRoot\runtime\kev.err.log" }
}
if (-not $SkipVietnameseEmbedding -and (Test-Path -LiteralPath "$PSScriptRoot\models\vietnamese-embedding\source-manifest.json")) {
 try { Invoke-RestMethod http://127.0.0.1:8011/health -TimeoutSec 2 | Out-Null }
 catch { Start-Process -FilePath "$PSScriptRoot\.venv-kev\Scripts\python.exe" -ArgumentList 'scripts/vietnamese_embedding_service.py' -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput "$PSScriptRoot\runtime\vietnamese-embedding.out.log" -RedirectStandardError "$PSScriptRoot\runtime\vietnamese-embedding.err.log" }
}
if (-not $SkipMonthly) {
    $workerRunning=$false
    $workerState="$PSScriptRoot\runtime\monthly\worker-instance.json"
    if(Test-Path -LiteralPath $workerState){
        try {
            $instance=Get-Content -LiteralPath $workerState -Raw | ConvertFrom-Json
            $workerProcess=Get-CimInstance Win32_Process -Filter "ProcessId = $($instance.pid)" -ErrorAction Stop
            $workerRunning=($null -ne $workerProcess -and $workerProcess.CommandLine -like '*update_monthly.py*')
        } catch {}
    }
    if(-not $workerRunning){
        Start-Process -FilePath "$PSScriptRoot\.venv\Scripts\python.exe" -ArgumentList 'scripts/update_monthly.py --watch --refresh-references' -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput "$PSScriptRoot\runtime\monthly-worker.out.log" -RedirectStandardError "$PSScriptRoot\runtime\monthly-worker.err.log"
    }
}
try {
    $web=Invoke-WebRequest http://127.0.0.1:8501/_stcore/health -TimeoutSec 2
    if($web.StatusCode -eq 200){ Write-Host 'Shop AI: http://127.0.0.1:8501'; exit 0 }
} catch {}
& "$PSScriptRoot\start.ps1"

