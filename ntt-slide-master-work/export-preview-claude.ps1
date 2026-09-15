$ErrorActionPreference = 'Stop'
$deck = 'C:\Users\ESALERC1Y\OneDrive - NTT DATA EMEAL\Second Brain\reports\kafka-alternatives-claude.pptx'
$outDir = 'C:\Users\ESALERC1Y\OneDrive - NTT DATA EMEAL\Second Brain\ntt-slide-master-work\preview-claude'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
Get-ChildItem $outDir -Filter *.png -ErrorAction SilentlyContinue | Remove-Item -Force
Write-Host 'opening...'
$p = New-Object -ComObject PowerPoint.Application
$p.Visible = -1
$dest = $p.Presentations.Open($deck, -1, 0, -1)
Write-Host ('slides: ' + $dest.Slides.Count)
for ($i = 1; $i -le $dest.Slides.Count; $i++) {
  $num = "{0:D2}" -f $i
  $path = Join-Path $outDir "slide-$num.png"
  $dest.Slides.Item($i).Export($path, "PNG", 1600, 900)
  Write-Host ("exported $i")
}
$dest.Close()
$p.Quit()
Write-Host 'done'
