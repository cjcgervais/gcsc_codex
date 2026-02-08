[CmdletBinding()]
param(
    [string]$Preset = "gcsc_default",
    [string]$OutputName = "gcsc_hull.stl"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$toolsDir = if ([string]::IsNullOrWhiteSpace($PSScriptRoot)) {
    Split-Path -Parent $MyInvocation.MyCommand.Path
} else {
    $PSScriptRoot
}
$labRoot = Split-Path -Parent $toolsDir
$presetPath = Join-Path $labRoot ("presets/{0}.scad" -f $Preset)

if (-not (Test-Path -LiteralPath $presetPath)) {
    throw "Preset not found: $presetPath"
}

$openscad = Get-Command openscad -ErrorAction SilentlyContinue
if (-not $openscad) {
    throw "OpenSCAD CLI not found in PATH."
}

$outDir = Join-Path $labRoot "exports/stl"
if (-not (Test-Path -LiteralPath $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

$tempEntryName = "_tmp_export_entry.scad"
$tempEntryPath = Join-Path $labRoot $tempEntryName
$outputPath = Join-Path $outDir $OutputName

$entryText = @"
include <presets/$Preset.scad>
include <src/gcsc_hull_core.scad>

gcsc_hull_build();
"@

Set-Content -LiteralPath $tempEntryPath -Value $entryText -NoNewline
$pushed = $false
try {
    Push-Location $labRoot
    $pushed = $true
    & $openscad.Source -o $outputPath $tempEntryName
}
finally {
    if ($pushed) {
        Pop-Location
    }
    Remove-Item -LiteralPath $tempEntryPath -Force -ErrorAction SilentlyContinue
}

Write-Host ("Exported STL: {0}" -f $outputPath)
