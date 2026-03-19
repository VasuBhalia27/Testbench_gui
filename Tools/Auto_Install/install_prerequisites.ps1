param(
    [switch]$SkipPip,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"

function Write-Section {
    param([string]$Title)
    if (-not $Quiet) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host " $Title" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
    }
}

function Write-Info {
    param([string]$Message)
    if (-not $Quiet) { Write-Host "[INFO] $Message" -ForegroundColor Gray }
}

function Write-Ok {
    param([string]$Message)
    Write-Host "[OK]   $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Fail {
    param([string]$Message)
    Write-Host "[FAIL] $Message" -ForegroundColor Red
}

$script:UsePyLauncher = $false

function Invoke-Python {
    param([string[]]$Args)
    if ($script:UsePyLauncher) {
        & py -3 @Args
    } else {
        & python @Args
    }
    return $LASTEXITCODE
}

function Test-Command {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\.." )).Path
$ConfigReq = Join-Path $RepoRoot "Config\requirements.txt"
$AutoReq = Join-Path $RepoRoot "AutomationScripts\requirements.txt"

Write-Section "SmartBU Prerequisite Installer"
Write-Info "Repository root: $RepoRoot"

Write-Section "Python Detection"
if (Test-Command "python") {
    Write-Ok "python found"
    $script:UsePyLauncher = $false
} elseif (Test-Command "py") {
    Write-Ok "py launcher found (using py -3)"
    $script:UsePyLauncher = $true
} else {
    Write-Fail "Python not found in PATH. Install Python 3.10+ and re-run."
    exit 1
}

$pyVersionCode = Invoke-Python -Args @("--version")
if ($pyVersionCode -ne 0) {
    Write-Fail "Unable to execute Python."
    exit 1
}

Write-Section "Python Package Installation"
if ($SkipPip) {
    Write-Warn "Skipping pip install because -SkipPip was provided."
} else {
    $pipUpgrade = Invoke-Python -Args @("-m", "pip", "install", "--upgrade", "pip")
    if ($pipUpgrade -eq 0) {
        Write-Ok "pip upgraded"
    } else {
        Write-Warn "pip upgrade failed (continuing with requirements install)"
    }

    if (Test-Path $ConfigReq) {
        Write-Info "Installing Config requirements"
        $rc1 = Invoke-Python -Args @("-m", "pip", "install", "-r", $ConfigReq)
        if ($rc1 -eq 0) {
            Write-Ok "Installed Config requirements"
        } else {
            Write-Fail "Failed to install Config requirements"
            exit 1
        }
    } else {
        Write-Warn "Missing file: $ConfigReq"
    }

    if (Test-Path $AutoReq) {
        Write-Info "Installing AutomationScripts requirements"
        $rc2 = Invoke-Python -Args @("-m", "pip", "install", "-r", $AutoReq)
        if ($rc2 -eq 0) {
            Write-Ok "Installed AutomationScripts requirements"
        } else {
            Write-Fail "Failed to install AutomationScripts requirements"
            exit 1
        }
    } else {
        Write-Warn "Missing file: $AutoReq"
    }
}

Write-Section "VISA Runtime / Driver Checks"
$visaCandidates = @(
    "$env:WINDIR\System32\visa64.dll",
    "$env:WINDIR\System32\visa32.dll",
    "$env:WINDIR\SysWOW64\visa32.dll"
)
$visaFound = $false
foreach ($candidate in $visaCandidates) {
    if (Test-Path $candidate) {
        Write-Ok "VISA runtime detected: $candidate"
        $visaFound = $true
        break
    }
}
if (-not $visaFound) {
    Write-Warn "NI-VISA runtime not detected. Install NI-VISA Runtime:"
    Write-Warn "https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html"
}

Write-Section "PyVISA Resource Check"
$pyvisaCheckCode = @"
import pyvisa
try:
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    print("RESOURCES:", resources)
except Exception as exc:
    print("PYVISA_ERROR:", exc)
"@
$rcPyvisa = Invoke-Python -Args @("-c", $pyvisaCheckCode)
if ($rcPyvisa -eq 0) {
    Write-Ok "PyVISA check executed"
} else {
    Write-Warn "PyVISA check failed"
}

Write-Section "Lauterbach / Trace32 Checks"
$trace32Exe = "C:\T32\bin\windows64\t32marm.exe"
if (Test-Path $trace32Exe) {
    Write-Ok "Trace32 executable found: $trace32Exe"
} else {
    Write-Warn "Trace32 executable not found at $trace32Exe"
}

try {
    $devices = Get-PnpDevice -PresentOnly -ErrorAction Stop |
        Where-Object { $_.FriendlyName -match "Lauterbach|PODBUS" }
    if ($devices) {
        Write-Ok "Lauterbach debugger device detected"
    } else {
        Write-Warn "No Lauterbach device detected (plug debugger if required)"
    }
} catch {
    Write-Warn "Could not query PnP devices. Run PowerShell as Administrator if needed."
}

Write-Section "Manual Next Steps"
Write-Host "1. If NI-VISA was missing, install it and reconnect PSU." -ForegroundColor White
Write-Host "2. For OWON runs: set PSU_TYPE=owon (optional if already default)." -ForegroundColor White
Write-Host "3. For KIKUSUI runs: set PSU_TYPE=kikusui before launch." -ForegroundColor White
Write-Host "4. Launch manual GUI: ManualTest\\SmartBuApp.bat" -ForegroundColor White
Write-Host "5. Launch automation GUI via your normal workflow." -ForegroundColor White

Write-Host "" 
Write-Host "Completed prerequisite setup/checks." -ForegroundColor Green
