param([ValidateSet('5V','33V')][string]$Mode = '5V', [switch]$NoOpen)
$ErrorActionPreference = 'Stop'
try {
    $exe = Join-Path $env:LOCALAPPDATA 'Programs\ADI\LTspice\LTspice.exe'
    if ($env:LTSPICE_EXE) { $exe = $env:LTSPICE_EXE }
    if (!(Test-Path -LiteralPath $exe)) { throw 'LTspice no encontrado. Instalarlo o definir LTSPICE_EXE con su ruta.' }
    $stem = Join-Path $PSScriptRoot "SIM-01_calibrated_startup_$Mode"
    # Preserve previous outputs instead of mistaking them for a completed new run.
    $previous = @('.log','.raw','.op.raw') | Where-Object { Test-Path -LiteralPath ($stem+$_) }
    if ($previous) {
        $archive = Join-Path $PSScriptRoot ('previous-runs\' + [guid]::NewGuid().ToString())
        New-Item -ItemType Directory -Path $archive -Force | Out-Null
        foreach ($suffix in $previous) { Move-Item -LiteralPath ($stem+$suffix) -Destination $archive }
    }
    $solver = if ($Mode -eq "33V") { "-alt" } else { "-norm" }
    Write-Host "Ejecutando SIM-01 $Mode con solver $solver..."
    $process = Start-Process -FilePath $exe -ArgumentList ($solver+' -b -Run "' + $stem + '.asc"') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -Wait -PassThru
    if ($process.ExitCode -ne 0) { throw "LTspice termino con codigo $($process.ExitCode)." }
    $bytes = [IO.File]::ReadAllBytes($stem+'.log')
    $encoding = [Text.Encoding]::GetEncoding(1252)
    if ($bytes.Length -gt 1 -and $bytes[1] -eq 0) { $encoding = [Text.Encoding]::Unicode }
    $log = $encoding.GetString($bytes)
    if ($log -notmatch 'Total elapsed time:' -or $log -match 'Fatal Error' -or !(Test-Path -LiteralPath ($stem+'.raw'))) { throw 'No se confirmo la finalizacion; revisar el .log.' }
    Write-Host 'Simulacion completa. El preset muestra las senales de encendido y apagado.'
    if (!$NoOpen) { Start-Process -FilePath $exe -ArgumentList ('"'+$stem+'.raw"') }
} catch { Write-Host $_ -ForegroundColor Red; exit 1 }
