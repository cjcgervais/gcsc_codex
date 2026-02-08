[CmdletBinding()]
param(
    [string]$RepoRoot,
    [switch]$MoveTempFiles,
    [switch]$FailOnFind,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $scriptDirectory = if ([string]::IsNullOrWhiteSpace($PSScriptRoot)) {
        Split-Path -Parent $MyInvocation.MyCommand.Path
    }
    else {
        $PSScriptRoot
    }
    $RepoRoot = Split-Path -Parent $scriptDirectory
}

$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$ArchiveRoot = Join-Path $RepoRoot "_codex/archive"
$BackupArchive = Join-Path $ArchiveRoot "backups"
$JunkArchive = Join-Path $ArchiveRoot "junk"

$Moved = New-Object System.Collections.Generic.List[object]
$Flagged = New-Object System.Collections.Generic.List[object]

function Ensure-Directory {
    param([string]$Path)
    if ($DryRun) {
        return
    }
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Get-UniqueDestinationPath {
    param(
        [string]$DestinationDirectory,
        [string]$Name
    )

    $target = Join-Path $DestinationDirectory $Name
    if (-not (Test-Path -LiteralPath $target)) {
        return $target
    }

    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($Name)
    $extension = [System.IO.Path]::GetExtension($Name)
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $counter = 1

    do {
        $candidateName = "{0}_{1}_{2}{3}" -f $baseName, $timestamp, $counter, $extension
        $target = Join-Path $DestinationDirectory $candidateName
        $counter++
    } while (Test-Path -LiteralPath $target)

    return $target
}

function Move-Candidate {
    param(
        [System.IO.FileSystemInfo]$Item,
        [string]$DestinationDirectory,
        [string]$Reason
    )

    Ensure-Directory -Path $DestinationDirectory
    $destinationPath = Get-UniqueDestinationPath -DestinationDirectory $DestinationDirectory -Name $Item.Name

    if ($DryRun) {
        Write-Host ("[DRY-RUN] MOVE {0} -> {1} ({2})" -f $Item.FullName, $destinationPath, $Reason)
    }
    else {
        Move-Item -LiteralPath $Item.FullName -Destination $destinationPath
        Write-Host ("MOVED {0} -> {1} ({2})" -f $Item.FullName, $destinationPath, $Reason)
    }

    $Moved.Add([PSCustomObject]@{
            Path   = $Item.FullName
            Action = "moved"
            Reason = $Reason
        })
}

Write-Host ("Repo root: {0}" -f $RepoRoot)

$bakFiles = @(Get-ChildItem -LiteralPath $RepoRoot -File -Filter "*.bak" -Force -ErrorAction SilentlyContinue)
$rootPycacheDirs = @(Get-ChildItem -LiteralPath $RepoRoot -Directory -Filter "__pycache__" -Force -ErrorAction SilentlyContinue)

$tempFiles = @(
    Get-ChildItem -LiteralPath $RepoRoot -File -Force -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -in @(".DS_Store", "Thumbs.db") -or
        $_.Name -match '\.tmp$' -or
        $_.Name -match '\.temp$' -or
        $_.Name -match '~$' -or
        $_.Name -match '^(tmp|temp|scratch|debug)[._-]'
    } |
    Sort-Object -Property FullName -Unique
)

$violationsFound = $bakFiles.Count + $rootPycacheDirs.Count + $tempFiles.Count

if ($bakFiles.Count -gt 0) {
    foreach ($file in $bakFiles) {
        Move-Candidate -Item $file -DestinationDirectory $BackupArchive -Reason "root .bak"
    }
}

if ($rootPycacheDirs.Count -gt 0) {
    foreach ($dir in $rootPycacheDirs) {
        Move-Candidate -Item $dir -DestinationDirectory $JunkArchive -Reason "root __pycache__"
    }
}

if ($tempFiles.Count -gt 0) {
    foreach ($file in $tempFiles) {
        if ($MoveTempFiles) {
            Move-Candidate -Item $file -DestinationDirectory $JunkArchive -Reason "root temp file"
        }
        else {
            Write-Host ("FLAGGED {0} (root temp file)" -f $file.FullName)
            $Flagged.Add([PSCustomObject]@{
                    Path   = $file.FullName
                    Action = "flagged"
                    Reason = "root temp file"
                })
        }
    }
}

if ($Moved.Count -eq 0 -and $Flagged.Count -eq 0) {
    Write-Host "No root hygiene artifacts found."
}
else {
    Write-Host ""
    Write-Host ("Summary: moved={0}, flagged={1}" -f $Moved.Count, $Flagged.Count)
}

if ($FailOnFind -and $violationsFound -gt 0) {
    Write-Host ("Failing because {0} hygiene artifact(s) were detected." -f $violationsFound)
    exit 1
}
