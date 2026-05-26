param(
    [switch]$SkipPip,
    [switch]$Quiet
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$script:PythonLauncher = 'python'
$script:PythonLauncherArgs = @()
$script:LastPythonExitCode = 0

function Write-Section {
    param([string]$Title)
    if (-not $Quiet) {
        Write-Host ''
        Write-Host '========================================' -ForegroundColor Cyan
        Write-Host " $Title" -ForegroundColor Cyan
        Write-Host '========================================' -ForegroundColor Cyan
    }
}

function Write-Info { param([string]$Message) if (-not $Quiet) { Write-Host "[INFO]  $Message" -ForegroundColor Gray } }
function Write-Ok { param([string]$Message) Write-Host "[OK]    $Message" -ForegroundColor Green }
function Write-Warn { param([string]$Message) Write-Host "[WARN]  $Message" -ForegroundColor Yellow }
function Write-ErrorLine { param([string]$Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

function Invoke-Python {
    param([string[]]$PythonArgs)

    try {
        $output = & $script:PythonLauncher @($script:PythonLauncherArgs + $PythonArgs) 2>&1
        $script:LastPythonExitCode = $LASTEXITCODE
        return $output
    } catch {
        $script:LastPythonExitCode = -1
        return @($_.Exception.Message)
    }
}

function Test-Command {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function New-PythonTempFile {
    param([string[]]$Lines)
    $tmp = Join-Path $env:TEMP ("smartebu_py_{0}.py" -f ([guid]::NewGuid()))
    $Lines | Out-File -FilePath $tmp -Encoding utf8
    return $tmp
}

function Get-PythonVersion {
    $tmpFile = New-PythonTempFile -Lines @(
        'import sys',
        'print(f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}")'
    )
    $output = Invoke-Python -PythonArgs @($tmpFile)
    Remove-Item -Path $tmpFile -ErrorAction SilentlyContinue
    if ($script:LastPythonExitCode -ne 0) { return $null }
    return ($output | Select-Object -First 1).Trim()
}

function Compare-PythonVersion {
    param(
        [string]$VersionString,
        [int]$Major,
        [int]$Minor
    )
    if (-not $VersionString) { return $false }
    try {
        $parts = $VersionString.Split('.') | ForEach-Object {[int]$_}
        return ($parts[0] -gt $Major) -or ($parts[0] -eq $Major -and $parts[1] -ge $Minor)
    } catch {
        return $false
    }
}

function Run-PythonCheck {
    param(
        [string[]]$PythonLines,
        [string]$TempFileName
    )

    $tmpFile = Join-Path $env:TEMP $TempFileName
    $PythonLines | Out-File -FilePath $tmpFile -Encoding utf8
    $output = Invoke-Python -PythonArgs @($tmpFile)
    Remove-Item -Path $tmpFile -ErrorAction SilentlyContinue
    return $output
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$ConfigReq = Join-Path $RepoRoot 'Config\requirements.txt'
$AutoReq = Join-Path $RepoRoot 'AutomationScripts\requirements.txt'

Write-Section 'SmartBU Prerequisite Installer'
Write-Info "Repository root: $RepoRoot"

Write-Section 'Python Detection'
$pythonFound = $false
$pythonVersion = $null

if (Test-Command 'python') {
    $script:PythonLauncher = 'python'
    $script:PythonLauncherArgs = @()
    $pythonVersion = Get-PythonVersion
    if (Compare-PythonVersion -VersionString $pythonVersion -Major 3 -Minor 10) {
        Write-Ok "python found: $pythonVersion"
        $pythonFound = $true
    }
}

if (-not $pythonFound -and (Test-Command 'py')) {
    $script:PythonLauncher = 'py'
    $script:PythonLauncherArgs = @('-3')
    $pythonVersion = Get-PythonVersion
    if (Compare-PythonVersion -VersionString $pythonVersion -Major 3 -Minor 10) {
        Write-Ok "py launcher found: $pythonVersion"
        $pythonFound = $true
    }
}

if (-not $pythonFound) {
    Write-ErrorLine 'Python 3.10+ not found. Install Python 3.10+ and re-run.'
    exit 1
}

Write-Info "Using Python runtime: $script:PythonLauncher $($script:PythonLauncherArgs -join ' ')"
Invoke-Python -PythonArgs @('--version')
if ($script:LastPythonExitCode -ne 0) {
    Write-ErrorLine 'Unable to execute selected Python runtime.'
    exit 1
}

function Try-PipInstall {
    param([string[]]$CommandArgs)

    $output = Invoke-Python -PythonArgs $CommandArgs
    if ($script:LastPythonExitCode -eq 0) { return 0 }

    $userArgs = @()
    $inserted = $false
    foreach ($a in $CommandArgs) {
        $userArgs += $a
        if (-not $inserted -and $a -eq 'install') {
            $userArgs += '--user'
            $inserted = $true
        }
    }
    if (-not $inserted) { $userArgs += '--user' }

    $output = Invoke-Python -PythonArgs $userArgs
    if ($output) { foreach ($line in $output) { Write-Host $line } }
    return $script:LastPythonExitCode
}

Write-Section 'Python Package Installation'
if ($SkipPip) {
    Write-Warn 'Skipping pip install because -SkipPip was provided.'
} else {
    Write-Info 'Upgrading pip'
    Try-PipInstall -CommandArgs @('-m','pip','install','--upgrade','pip') | Out-Null

    if (Test-Path $ConfigReq) {
        Write-Info 'Installing Config requirements'
        $rc = Try-PipInstall -CommandArgs @('-m','pip','install','-r',$ConfigReq)
        if ($rc -eq 0) { Write-Ok 'Config requirements installed' } else { Write-Warn 'Config requirements install failed' }
    } else {
        Write-Warn 'Config requirements file missing'
    }

    if (Test-Path $AutoReq) {
        Write-Info 'Installing AutomationScripts requirements'
        $rc = Try-PipInstall -CommandArgs @('-m','pip','install','-r',$AutoReq)
        if ($rc -eq 0) { Write-Ok 'AutomationScripts requirements installed' } else { Write-Warn 'AutomationScripts requirements install failed' }
    } else {
        Write-Warn 'AutomationScripts requirements file missing'
    }

    Write-Info 'Installing MCP2221 support package'
    $rc = Try-PipInstall -CommandArgs @('-m','pip','install','mcp2221')
    if ($rc -eq 0) { Write-Ok 'mcp2221 installed' } else { Write-Warn 'mcp2221 install failed' }

    Write-Info 'Installing PyVISA support packages'
    $rc = Try-PipInstall -CommandArgs @('-m','pip','install','pyvisa','pyvisa-py')
    if ($rc -eq 0) { Write-Ok 'PyVISA support packages installed' } else { Write-Warn 'PyVISA support install failed' }
}

Write-Section 'VISA Runtime / Driver Checks'
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
if (-not $visaFound) { Write-Warn 'NI-VISA runtime not detected' }

Write-Section 'PyVISA Package / Backend Check'
$pyvisaLines = @(
    'import importlib.util',
    'print("PYVISA_IMPORT_OK" if importlib.util.find_spec("pyvisa") else "PYVISA_IMPORT_MISSING")',
    'try:',
    '    import pyvisa',
    '    print("PYVISA_VERSION", pyvisa.__version__)',
    '    try:',
    '        rm = pyvisa.ResourceManager()',
    '        print("PYVISA_BACKEND_DEFAULT_OK")',
    '        resources = rm.list_resources()',
    '        print(f"PyVISA resources found: {len(resources)}")',
    '    except Exception as exc_default:',
    '        print("PYVISA_BACKEND_DEFAULT_FAIL", exc_default)',
    '        try:',
    '            rm = pyvisa.ResourceManager("@py")',
    '            print("PYVISA_BACKEND_PY_OK")',
    '            resources = rm.list_resources()',
    '            print(f"PyVISA resources found: {len(resources)}")',
    '        except Exception as exc_py:',
    '            print("PYVISA_BACKEND_PY_FAIL", exc_py)',
    'except Exception as exc:',
    '    print("PYVISA_IMPORT_FAIL", exc)'
)
$pyvisaOut = Run-PythonCheck -PythonLines $pyvisaLines -TempFileName ('smartebu_pyvisa_check_{0}.py' -f ([guid]::NewGuid()))
foreach ($line in $pyvisaOut) { Write-Host $line }

$hasImportOk = $pyvisaOut | Where-Object { $_ -match 'PYVISA_IMPORT_OK' }
$hasBackendDefaultOk = $pyvisaOut | Where-Object { $_ -match 'PYVISA_BACKEND_DEFAULT_OK' }
$hasBackendPyOk = $pyvisaOut | Where-Object { $_ -match 'PYVISA_BACKEND_PY_OK' }

if ($hasImportOk) {
    Write-Ok 'PyVISA package available'
    if ($hasBackendDefaultOk) {
        Write-Ok 'PyVISA default backend available'
    } elseif ($hasBackendPyOk) {
        Write-Warn 'PyVISA default backend unavailable; pyvisa-py backend is available'
    } else {
        Write-Warn 'PyVISA package installed, but no backend is available'
    }
} else {
    Write-Warn 'PyVISA package missing or import failed'
}

Write-Section 'Adafruit Blinka / MCP2221 Support'
$blinkaLines = @(
    'import importlib.util',
    'print("BLINKA_OK" if importlib.util.find_spec("adafruit_blinka") else "BLINKA_MISSING")',
    'print("MCP2221_OK" if importlib.util.find_spec("MCP2221") else "MCP2221_MISSING")'
)
$blinkaOut = Run-PythonCheck -PythonLines $blinkaLines -TempFileName ('smartebu_blinka_check_{0}.py' -f ([guid]::NewGuid()))
foreach ($line in $blinkaOut) { Write-Host $line }

$hasCoreOk = $blinkaOut | Where-Object { $_ -match 'BLINKA_OK' }
$hasMcpOk = $blinkaOut | Where-Object { $_ -match 'MCP2221_OK' }

if ($hasCoreOk) { Write-Ok 'Adafruit Blinka package available' } else { Write-Warn 'Adafruit Blinka package missing' }
if ($hasMcpOk) { Write-Ok 'MCP2221 package available' } else { Write-Warn 'MCP2221 package missing' }

Write-Section 'Lauterbach / Trace32 Checks'
$trace32Exe = 'C:\T32\bin\windows64\t32marm.exe'
if (Test-Path $trace32Exe) { Write-Ok "Trace32 executable found: $trace32Exe" } else { Write-Warn 'Trace32 executable not found' }

try {
    $devices = Get-PnpDevice -PresentOnly -ErrorAction Stop | Where-Object { $_.FriendlyName -match 'Lauterbach|PODBUS' }
    if ($devices) { Write-Ok 'Lauterbach debugger device detected' } else { Write-Warn 'No Lauterbach debugger device detected' }
} catch {
    Write-Warn 'Unable to query PnP devices'
}

Write-Section 'Summary'
Write-Host 'Completed prerequisite checks.' -ForegroundColor Green
