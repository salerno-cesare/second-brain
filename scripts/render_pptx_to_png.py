"""Render each slide of a PPTX to PNG using PowerPoint COM automation."""
import os
import sys
import shutil
from pathlib import Path

pptx_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    r"c:\Users\Cesare\OneDrive - NTT DATA EMEAL\Second Brain\reports\Wolters Kluwer - TCF - One Fiscale Integration.pptx"
)
out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(
    r"c:\Users\Cesare\OneDrive - NTT DATA EMEAL\Second Brain\reports\assets\preview"
)

# Copy to temp to avoid OneDrive reparse-point issues
tmp = Path(os.environ["TEMP"]) / "render_input.pptx"
shutil.copyfile(pptx_path, tmp)

out_dir.mkdir(parents=True, exist_ok=True)
# Clean previous
for f in out_dir.glob("*.png"):
    f.unlink()

try:
    import win32com.client
except ImportError:
    print("pywin32 not installed – installing"); os.system(f"{sys.executable} -m pip install pywin32")
    import win32com.client

app = win32com.client.Dispatch("PowerPoint.Application")
try:
    # ReadOnly=True, Untitled=False, WithWindow=True; PowerPoint on many
    # installs refuses WithWindow=False.
    pres = app.Presentations.Open(str(tmp), ReadOnly=True, Untitled=False,
                                  WithWindow=True)
    n = pres.Slides.Count
    for i in range(1, n + 1):
        target = out_dir / f"slide_{i:02d}.png"
        # width scaled to keep aspect; slide is 13.333x7.5in
        pres.Slides.Item(i).Export(str(target), "PNG", 1600, 900)
        print(f"  slide {i}: {target}")
    pres.Close()
finally:
    app.Quit()
