$ErrorActionPreference = "Stop"

function Emit-Section {
    param(
        [string]$Title,
        [string]$Path,
        [int]$MaxLines = 220
    )
    Write-Host ""
    Write-Host "===== BEGIN $Title :: $Path =====" -ForegroundColor Yellow
    if (Test-Path -LiteralPath $Path) {
        Get-Content -LiteralPath $Path -TotalCount $MaxLines
    } else {
        Write-Host "[missing]" -ForegroundColor Red
    }
    Write-Host "===== END $Title =====" -ForegroundColor Yellow
}

Set-Location "C:\Users\jacks\OneDrive\Desktop\CHEMIFRAME"

Write-Host ""
Write-Host "===== BEGIN REPO TREE =====" -ForegroundColor Yellow
Get-ChildItem -Recurse -File | ForEach-Object { $_.FullName.Replace((Get-Location).Path + "\", "") }
Write-Host "===== END REPO TREE =====" -ForegroundColor Yellow

Emit-Section -Title "MAIN" -Path ".\main.py"
Emit-Section -Title "UI_MAIN_WINDOW" -Path ".\chemiframe\ui\main_window.py" -MaxLines 500
Emit-Section -Title "DEMO_SUPPORT" -Path ".\chemiframe\demo_support.py"
Emit-Section -Title "WORKSPACE" -Path ".\chemiframe\workspace.py"
Emit-Section -Title "README" -Path ".\README.md" -MaxLines 180

Write-Host ""
Write-Host "===== BEGIN ARTIFACT SNAPSHOT =====" -ForegroundColor Yellow
$artifactDirs = @(
    ".\artifacts\compiled_xdl",
    ".\artifacts\contracts",
    ".\artifacts\traces",
    ".\artifacts\reports"
)
foreach ($dir in $artifactDirs) {
    Write-Host "--- $dir ---" -ForegroundColor Cyan
    if (Test-Path -LiteralPath $dir) {
        Get-ChildItem -LiteralPath $dir -File | Select-Object Name, Length, LastWriteTime
    } else {
        Write-Host "[missing]" -ForegroundColor Red
    }
}
Write-Host "===== END ARTIFACT SNAPSHOT =====" -ForegroundColor Yellow