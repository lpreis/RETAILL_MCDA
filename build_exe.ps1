$ErrorActionPreference = "Stop"

$AppName = "RETAILL_MCDA"
$AddData = @(
    "app.py;.",
    "requirements.txt;.",
    "core;core",
    "data;data",
    "logos;logos",
    "exports;exports",
    ".streamlit;.streamlit"
)

$Args = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--onefile",
    "--name", $AppName,
    "--collect-all", "streamlit",
    "--collect-all", "plotly",
    "--collect-all", "reportlab",
    "--hidden-import", "openpyxl",
    "--hidden-import", "pydantic",
    "--hidden-import", "pyarrow"
)

foreach ($Item in $AddData) {
    $Args += @("--add-data", $Item)
}

$Args += "run_app.py"

py @Args

Write-Host ""
Write-Host "Executable created at: dist\$AppName.exe"
