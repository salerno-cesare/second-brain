"""Build one slide at a time and try to open in PowerPoint COM."""
import os, shutil, sys, importlib
from pathlib import Path

# Ensure we import the module fresh
sys.path.insert(0, str(Path(__file__).parent))
import build_tfc_deck_v2 as m

src = Path(r"c:\Users\Cesare\OneDrive - NTT DATA EMEAL\Second Brain\reports\Template.pptx")
tmp_src = Path(os.environ["TEMP"]) / "template_probe.pptx"
if not tmp_src.exists() or tmp_src.stat().st_size != src.stat().st_size:
    shutil.copyfile(src, tmp_src)

builders = [
    m.build_slide_1_cover,
    m.build_slide_2_context,
    m.build_slide_3_objective,
    m.build_slide_4_architecture,
    m.build_slide_5_use_cases_detail,
    m.build_slide_6_identity,
    m.build_slide_7_poc,
    m.build_slide_8_costs,
    m.build_slide_9_end,
]

import win32com.client
app = win32com.client.Dispatch("PowerPoint.Application")

from pptx import Presentation
for i, fn in enumerate(builders, 1):
    out = Path(os.environ["TEMP"]) / f"iso_{i}.pptx"
    shutil.copyfile(tmp_src, out)
    prs = Presentation(out)
    m.clear_slides(prs)
    fn(prs)
    prs.save(out)
    try:
        pres = app.Presentations.Open(str(out), ReadOnly=True)
        n = pres.Slides.Count
        pres.Close()
        print(f"slide {i} ({fn.__name__}): OK ({n})")
    except Exception as e:
        print(f"slide {i} ({fn.__name__}): FAIL – {e}")

app.Quit()
