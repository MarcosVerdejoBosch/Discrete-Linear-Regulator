param([string]$Scenario, [switch]$NoOpen)
$ErrorActionPreference = 'Stop'
try {
    $catalog = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'scenario_catalog.json') -Raw | ConvertFrom-Json
    if (!$Scenario) {
        Write-Host 'Elegir una simulacion (resultados numericos; no mediciones de la placa):'
        for ($i=0; $i -lt $catalog.Count; $i++) { Write-Host (('{0,2}. ' -f ($i+1)) + $catalog[$i].label) }
        $answer = Read-Host 'Numero'
        $index = 0
        if (![int]::TryParse($answer,[ref]$index) -or $index -lt 1 -or $index -gt $catalog.Count) { throw 'Seleccion invalida.' }
        $entry = $catalog[$index-1]
    } else {
        $entry = @($catalog | Where-Object {$_.stem -eq $Scenario})
        if ($entry.Count -ne 1) { throw 'El escenario no figura en el catalogo.' }
        $entry = $entry[0]
    }
    if ($entry.stem -notmatch '^[A-Za-z0-9_.-]+$' -or $entry.solver -notin 'norm','alt') { throw 'Catalogo invalido.' }
    $exe = if ($env:LTSPICE_EXE) { $env:LTSPICE_EXE } else { Join-Path $env:LOCALAPPDATA 'Programs\ADI\LTspice\LTspice.exe' }
    if (!(Test-Path -LiteralPath $exe)) { throw 'LTspice no encontrado. Instalarlo o definir LTSPICE_EXE.' }
    $stem = Join-Path $PSScriptRoot $entry.stem
    if (!(Test-Path -LiteralPath ($stem+'.asc'))) { throw 'Falta el esquema. Ejecutar primero PREPARAR_LTSPICE.cmd.' }
    $previous = @('.raw','.log','.op.raw') | Where-Object {Test-Path -LiteralPath ($stem+$_)}
    if ($previous) {
        $archive = Join-Path $PSScriptRoot ('previous-runs\'+[guid]::NewGuid().ToString())
        New-Item -ItemType Directory -Path $archive -Force | Out-Null
        foreach ($suffix in $previous) { Move-Item -LiteralPath ($stem+$suffix) -Destination $archive }
    }
    Write-Host $entry.label
    Write-Host ('Solver: '+$entry.solver+'. Esperar hasta la finalizacion; algunos ensayos tardan varios minutos.')
    $process = Start-Process -FilePath $exe -ArgumentList ('-'+$entry.solver+' -b -Run "'+$stem+'.asc"') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru -Wait
    if ($process.ExitCode -ne 0) { throw ('LTspice termino con codigo '+$process.ExitCode) }
    $bytes = [IO.File]::ReadAllBytes($stem+'.log')
    $encoding = [Text.Encoding]::GetEncoding(1252)
    if ($bytes.Length -gt 1 -and $bytes[1] -eq 0) { $encoding = [Text.Encoding]::Unicode }
    $log = $encoding.GetString($bytes)
    if ($log -notmatch 'Total elapsed time:' -or $log -match 'Fatal Error' -or !(Test-Path -LiteralPath ($stem+'.raw'))) { throw 'No se confirmo una corrida completa. Revisar el .log.' }
    Write-Host 'Corrida completa. Revisar las curvas contra las condiciones y resultados documentados.'
    if (!$NoOpen) { Start-Process -FilePath $exe -ArgumentList ('"'+$stem+'.raw"') }
} catch { Write-Host $_ -ForegroundColor Red; exit 1 }
