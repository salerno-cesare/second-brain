"""Log each shape-adding call to identify call #36 in slide 4."""
import os, shutil, sys, traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_tfc_deck_v2 as m
from pptx import Presentation

src_template = Path(r"c:\Users\Cesare\OneDrive - NTT DATA EMEAL\Second Brain\reports\Template.pptx")

counter = {"n": 0}
orig_line = m.add_line
orig_rect = m.add_rect
orig_text = m.add_text_box

def wrap(kind, fn):
    def wrapper(*a, **kw):
        counter["n"] += 1
        # Grab caller line
        frames = traceback.extract_stack(limit=6)
        caller = None
        for f in reversed(frames[:-1]):
            if "build_tfc_deck_v2" in f.filename and "build_slide_4" in f.name:
                caller = f
                break
        print(f"[{counter['n']:3d}] {kind}  line={caller.lineno if caller else '?'}  args[2:6]={a[1:5]}")
        return fn(*a, **kw)
    return wrapper

m.add_line = wrap("line", orig_line)
m.add_rect = wrap("rect", orig_rect)
m.add_text_box = wrap("text", orig_text)

out = Path(os.environ["TEMP"]) / "log_slide4.pptx"
shutil.copyfile(src_template, out)
prs = Presentation(out)
m.clear_slides(prs)
m.build_slide_4_architecture(prs)
prs.save(out)
print("done")
