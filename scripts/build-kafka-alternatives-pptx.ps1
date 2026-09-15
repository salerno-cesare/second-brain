#Requires -Version 5.1
<#
.SYNOPSIS
    Converte reports/kafka-alternatives-slides.md in un file .pptx usando python-pptx.

.DESCRIPTION
    - Assicura la venv locale via scripts/ensure-venv.ps1
    - Installa python-pptx se mancante
    - Esegue lo script Python inline che parsa il markdown e produce il .pptx

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-kafka-alternatives-pptx.ps1
#>

[CmdletBinding()]
param(
    [string]$MarkdownPath = "reports/kafka-alternatives-slides.md",
    [string]$OutputPath   = "reports/kafka-alternatives.pptx"
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$ensureVenv = Join-Path $repoRoot 'scripts\ensure-venv.ps1'
if (Test-Path $ensureVenv) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $ensureVenv | Out-Null
}

$venvPython = Join-Path $repoRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    $venvPython = (Get-Command python).Source
}

$uvExe = Join-Path $repoRoot 'tools\uv\uv.exe'
$pptxCheck = & $venvPython -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('pptx') else 1)" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installo python-pptx nella venv..." -ForegroundColor Cyan
    if (Test-Path $uvExe) {
        & $uvExe pip install --python $venvPython python-pptx
    } else {
        & $venvPython -m pip install --quiet python-pptx
    }
    if ($LASTEXITCODE -ne 0) { throw "Installazione python-pptx fallita" }
}

$mdFull  = Join-Path $repoRoot $MarkdownPath
$outFull = Join-Path $repoRoot $OutputPath

if (-not (Test-Path $mdFull)) {
    throw "Markdown non trovato: $mdFull"
}

$py = @"
import re, sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt

md_path = Path(r'''$mdFull''')
out_path = Path(r'''$outFull''')

text = md_path.read_text(encoding='utf-8')
# Split per slide: sezioni che iniziano con '## Slide'
raw_slides = re.split(r'(?m)^## Slide\s+\d+\s*$', text)
raw_slides = [s.strip() for s in raw_slides[1:] if s.strip()]

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)

title_layout   = prs.slide_layouts[0]
content_layout = prs.slide_layouts[1]

def parse_block(block):
    title, subtitle, bullets = '', '', []
    for line in block.splitlines():
        s = line.strip()
        if not s: continue
        if s.startswith('Titolo:'):
            title = s[len('Titolo:'):].strip()
        elif s.startswith('Sottotitolo:'):
            subtitle = s[len('Sottotitolo:'):].strip()
        elif s.startswith('- '):
            bullets.append(('main', s[2:].strip()))
        elif s.startswith('  - '):
            bullets.append(('sub', s.strip()[2:].strip()))
    return title, subtitle, bullets

for idx, block in enumerate(raw_slides):
    title, subtitle, bullets = parse_block(block)
    if idx == 0 and not bullets:
        slide = prs.slides.add_slide(title_layout)
        slide.shapes.title.text = title or 'Presentazione'
        if len(slide.placeholders) > 1:
            slide.placeholders[1].text = subtitle
        continue

    slide = prs.slides.add_slide(content_layout)
    slide.shapes.title.text = title or f'Slide {idx+1}'
    body = slide.placeholders[1].text_frame
    body.word_wrap = True

    first = True
    if subtitle:
        p = body.paragraphs[0]
        p.text = subtitle
        p.font.size = Pt(16)
        p.font.italic = True
        first = False

    for level, txt in bullets:
        if first:
            p = body.paragraphs[0]
            first = False
        else:
            p = body.add_paragraph()
        p.text = txt
        p.level = 0 if level == 'main' else 1
        p.font.size = Pt(18) if level == 'main' else Pt(14)

out_path.parent.mkdir(parents=True, exist_ok=True)
prs.save(out_path)
print(f'OK -> {out_path}')
"@

$tmp = New-TemporaryFile
try {
    $tmpPy = [System.IO.Path]::ChangeExtension($tmp.FullName, '.py')
    Rename-Item -Path $tmp.FullName -NewName ([System.IO.Path]::GetFileName($tmpPy))
    Set-Content -Path $tmpPy -Value $py -Encoding UTF8
    & $venvPython $tmpPy
    if ($LASTEXITCODE -ne 0) { throw "Generazione PPTX fallita (exit $LASTEXITCODE)" }
    Write-Host "Presentazione creata: $OutputPath" -ForegroundColor Green
}
finally {
    if (Test-Path $tmpPy) { Remove-Item $tmpPy -Force }
}
