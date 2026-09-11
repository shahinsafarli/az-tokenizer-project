# Build the IEEE paper on Windows (MiKTeX). Regenerates figures and tables first.
# Uses the classic pdflatex -> bibtex -> pdflatex x2 sequence (no Perl/latexmk needed).
$ErrorActionPreference = 'Continue'
Set-Location $PSScriptRoot
$miktex = "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64"
if (Test-Path $miktex) { $env:PATH = "$miktex;$env:PATH" }
$env:PYTHONIOENCODING = 'utf-8'
$env:BIBINPUTS = "$PSScriptRoot;"
foreach ($s in Get-ChildItem figures\make_*.py) {
    python $s.FullName
    if ($LASTEXITCODE -ne 0) { throw "figure script failed: $($s.Name)" }
}
python tables\make_tables.py
if ($LASTEXITCODE -ne 0) { throw "make_tables.py failed" }
if (-not (Test-Path build)) { New-Item -ItemType Directory build | Out-Null }
function Run-Tex($cmd) {
    cmd /c "$cmd >> build\build.out 2>&1"
    if ($LASTEXITCODE -ne 0) { Get-Content build\build.out -Tail 40; throw "failed: $cmd" }
}
if (Test-Path build\build.out) { Remove-Item build\build.out }
Run-Tex "pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build report.tex"
Run-Tex "bibtex build\report"
Run-Tex "pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build report.tex"
Run-Tex "pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build report.tex"
Copy-Item build\report.pdf report.pdf -Force
$log = Get-Content build\report.log -Raw
$undef = ([regex]::Matches($log, "LaTeX Warning: (Reference|Citation) ``")).Count
Write-Host "built report.pdf  (undefined refs/cites: $undef)"
