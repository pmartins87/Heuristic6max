# OH G1/G6 -- local file identity ONLY. Does NOT launch, connect or automate OH.
# Run in PowerShell on the OFFLINE VM. Keep output private until redacted.
param(
    [Parameter(Mandatory=$true)][string]$OpenHoldemExe,
    [Parameter(Mandatory=$true)][string]$OpenPPLFormula,
    [Parameter(Mandatory=$true)][string]$TableMap,
    [Parameter(Mandatory=$true)][string]$OutputJson
)
$ErrorActionPreference = 'Stop'
$files = @($OpenHoldemExe, $OpenPPLFormula, $TableMap)
foreach ($f in $files) {
    if (-not (Test-Path -LiteralPath $f -PathType Leaf)) {
        throw "Missing input file. No changes performed: $f"
    }
}
$version = (Get-Item -LiteralPath $OpenHoldemExe).VersionInfo.FileVersion
$identity = [ordered]@{
    protocol = 'OH-G1G6-1'
    openholdem_version = [string]$version
    openholdem_exe_sha256 = (Get-FileHash -LiteralPath $OpenHoldemExe -Algorithm SHA256).Hash.ToLowerInvariant()
    loaded_oppl_sha256 = (Get-FileHash -LiteralPath $OpenPPLFormula -Algorithm SHA256).Hash.ToLowerInvariant()
    tablemap_sha256 = (Get-FileHash -LiteralPath $TableMap -Algorithm SHA256).Hash.ToLowerInvariant()
    observation = 'FILE_HASHES_ONLY_NOT_PROOF_OF_ACTUAL_FORMULA_LOADED'
}
$json = $identity | ConvertTo-Json -Depth 3
[System.IO.File]::WriteAllText(
    [System.IO.Path]::GetFullPath($OutputJson),
    $json + [Environment]::NewLine,
    [System.Text.UTF8Encoding]::new($false)
)
Write-Host "Fingerprints saved locally. No application launched, no autoplayer action, no upload."
