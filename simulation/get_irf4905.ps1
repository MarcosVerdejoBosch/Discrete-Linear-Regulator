param([Parameter(Mandatory=$true)][string]$Destination)
$ErrorActionPreference = 'Stop'
$url = 'https://www.infineon.com/assets/row/public/documents/24/50/irf4905.spi?fileId=5546d462533600a4015356faeff336bb'
$expected = 'D6363459B4A5086A3F91CD0C973636CA1A4E38215D85DF5D3463C37AF85849F0'
$target = Join-Path $Destination 'irf4905.spi'
if (Test-Path -LiteralPath $target) {
    if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $expected) { throw 'Existing IRF4905 model differs from the reviewed version; it was not overwritten.' }
    return
}
$temporary = [IO.Path]::GetTempFileName()
try {
    Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $temporary
    if ((Get-FileHash -LiteralPath $temporary -Algorithm SHA256).Hash -ne $expected) { throw 'IRF4905 download does not match the reviewed model. Check supplier changes before proceeding.' }
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Copy-Item -LiteralPath $temporary -Destination $target
} finally { Remove-Item -LiteralPath $temporary -ErrorAction SilentlyContinue }
