param (
    [string]$action
)

$pidFile = "pid"
$command = "python main.py"

function Start-Service {
    Write-Host "Starting Python service..."
    $commandArray = $command -split " "
    $tool = $commandArray[0]
    $params = $commandArray[1..($commandArray.Length - 1)]
    $process = Start-Process -FilePath $tool -ArgumentList $params -PassThru -WindowStyle Hidden
    $process.Id | Out-File -FilePath $pidFile -Force
    Write-Host "Python service started with PID $($process.Id)." -ForegroundColor Green
}

function Check-Service {
    if (-not (Test-Path $pidFile)) {
        Write-Host "PID file not found." -ForegroundColor Red
        return $false
    }

    $service_pid = Get-Content $pidFile
    if ($service_pid -eq $null -or $service_pid.Length -eq 0) {
        Write-Host "PID file is empty." -ForegroundColor Red
        return $false
    }

    $process = Get-Process -Id $service_pid -ErrorAction SilentlyContinue
    if (-not $process) {
        Write-Host "Service with PID $service_pid is not running." -ForegroundColor Red
        return $false
    }
    
    Write-Host "Service is running with PID $service_pid." -ForegroundColor Green
    return $true
}

function Kill-Service {
    if (-not (Test-Path $pidFile)) {
        Write-Host "PID file not found." -ForegroundColor Red
        return $false
    }

    $service_pid = Get-Content $pidFile
    if ($service_pid -eq $null -or $service_pid.Length -eq 0) {
        Write-Host "PID file is empty." -ForegroundColor Red
        return $false
    }

    $process = Get-Process -Id $service_pid -ErrorAction SilentlyContinue
    if (-not $process) {
        Write-Host "Service with PID $service_pid is not running." -ForegroundColor Red
        return $false
    }

    $process.Kill()
    Write-Host "Service with PID $service_pid has been killed." -ForegroundColor Green
    Remove-Item $pidFile -Force
    return $true
}

switch ($action) {
    "--help" {
        Write-Host ("
            Script Arguement
            --restart  restart service
            --config   install requirement.txt package 
            --check    check service alive
            --kill     kill service
        ")
    }
    "--restart" {
        Kill-Service
        Start-Service
    }
    "--check" {
        Check-Service
    }
    "--kill" {
        Kill-Service
    }
    "--config" {
        python -m pip install -r .\requirement.txt
    }
    default {
        Write-Host "Invalid action.`nUse --help, --restart, --config, --check, --kill"
    }
}