[CmdletBinding()]
param(
    [string]$Preset = "",
    [string]$InputScad = "src/gcsc_hull_entry.scad",
    [string]$OutputName = "",
    [int]$ImageSize = 1400
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$toolsDir = if ([string]::IsNullOrWhiteSpace($PSScriptRoot)) {
    Split-Path -Parent $MyInvocation.MyCommand.Path
} else {
    $PSScriptRoot
}
$labRoot = Split-Path -Parent $toolsDir

$openscad = Get-Command openscad -ErrorAction SilentlyContinue
if (-not $openscad) {
    throw "OpenSCAD CLI not found in PATH."
}

$renderDir = Join-Path $labRoot "exports/renders"
if (-not (Test-Path -LiteralPath $renderDir)) {
    New-Item -ItemType Directory -Path $renderDir -Force | Out-Null
}

$sourceScad = $InputScad
$sourceScadPath = Join-Path $labRoot $InputScad
$tempEntryPath = $null

if (-not [string]::IsNullOrWhiteSpace($Preset)) {
    $presetPath = Join-Path $labRoot ("presets/{0}.scad" -f $Preset)
    if (-not (Test-Path -LiteralPath $presetPath)) {
        throw "Preset not found: $presetPath"
    }

    $sourceScad = "_tmp_preview_entry.scad"
    $tempEntryPath = Join-Path $labRoot $sourceScad

    $entryText = @"
include <presets/$Preset.scad>
include <src/gcsc_hull_core.scad>

gcsc_hull_build();
"@
    Set-Content -LiteralPath $tempEntryPath -Value $entryText -NoNewline
}
else {
    if (-not (Test-Path -LiteralPath $sourceScadPath)) {
        throw "Input SCAD not found: $sourceScadPath"
    }
}

if ([string]::IsNullOrWhiteSpace($OutputName)) {
    if (-not [string]::IsNullOrWhiteSpace($Preset)) {
        $OutputName = ("{0}_preview.png" -f $Preset)
    }
    else {
        $OutputName = "gcsc_hull_preview.png"
    }
}

$outputPath = Join-Path $renderDir $OutputName

$pushed = $false
try {
    Push-Location $labRoot
    $pushed = $true
    & $openscad.Source --imgsize "$ImageSize,$ImageSize" --autocenter --viewall -o $outputPath $sourceScad
}
finally {
    if ($pushed) {
        Pop-Location
    }
    if (-not [string]::IsNullOrWhiteSpace($tempEntryPath)) {
        Remove-Item -LiteralPath $tempEntryPath -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ("Rendered preview: {0}" -f $outputPath)
