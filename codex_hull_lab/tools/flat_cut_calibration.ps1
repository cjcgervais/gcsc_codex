[CmdletBinding()]
param(
    [string]$Preset = "gcsc_default",
    [string]$OutputName = "",
    [double]$SliceWidthMm = 20,
    [double]$FlatCutZ = [double]::NaN
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

if ($SliceWidthMm -le 0) {
    throw "SliceWidthMm must be > 0."
}

if ([string]::IsNullOrWhiteSpace($OutputName)) {
    $OutputName = ("flat_cut_calibration_{0}.stl" -f $Preset)
}

$outDir = Join-Path $labRoot "exports/stl"
if (-not (Test-Path -LiteralPath $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

$tempEntryName = "_tmp_flat_cut_calibration.scad"
$tempEntryPath = Join-Path $labRoot $tempEntryName
$outputPath = Join-Path $outDir $OutputName

$flatCutOverride = if ([double]::IsNaN($FlatCutZ)) {
    ""
}
else {
    "flat_cut_z = $FlatCutZ;"
}

$entryText = @"
include <presets/$Preset.scad>
$flatCutOverride
include <src/gcsc_hull_core.scad>

slice_width_mm = $SliceWidthMm;

intersection() {
    gcsc_hull_build();
    translate([
        -slice_width_mm / 2,
        -(beam_mm + 40),
        -(depth_mm + keel_depth_mm + 60)
    ])
        cube([
            slice_width_mm,
            2 * (beam_mm + 40),
            depth_mm + keel_depth_mm + 120
        ], center = false);
}
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

Write-Host ("Exported flat-cut calibration STL: {0}" -f $outputPath)
