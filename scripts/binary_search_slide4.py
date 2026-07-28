"""Binary-search which part of slide 4 breaks PowerPoint."""
import os, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_tfc_deck_v2 as m
from pptx import Presentation
import win32com.client

src_template = Path(r"c:\Users\Cesare\OneDrive - NTT DATA EMEAL\Second Brain\reports\Template.pptx")

# Patch build_slide_4_architecture to accept a "cutoff" and run only the first N shapes.
# Simplest: monkeypatch add_line, add_rect, add_text_box to count calls and stop.

app = win32com.client.Dispatch("PowerPoint.Application")


def try_open(path):
    try:
        pres = app.Presentations.Open(str(path), ReadOnly=True)
        pres.Close()
        return True, None
    except Exception as e:
        return False, str(e)


def run_with_limit(limit):
    """Rebuild the pptx, patching add_line/add_rect/add_text_box to skip after `limit` total shape adds."""
    counter = {"n": 0}
    orig_line = m.add_line
    orig_rect = m.add_rect
    orig_text = m.add_text_box

    def guarded(fn, *a, **kw):
        counter["n"] += 1
        if counter["n"] > limit:
            return None
        return fn(*a, **kw)

    m.add_line = lambda *a, **kw: guarded(orig_line, *a, **kw)
    m.add_rect = lambda *a, **kw: guarded(orig_rect, *a, **kw)
    m.add_text_box = lambda *a, **kw: guarded(orig_text, *a, **kw)
    try:
        out = Path(os.environ["TEMP"]) / f"iso_bs_{limit}.pptx"
        shutil.copyfile(src_template, out)
        prs = Presentation(out)
        m.clear_slides(prs)
        m.build_slide_4_architecture(prs)
        prs.save(out)
        return out, counter["n"]
    finally:
        m.add_line = orig_line
        m.add_rect = orig_rect
        m.add_text_box = orig_text


# Binary search
lo, hi = 0, 200
# First find full count
_, full_count = run_with_limit(10_000)
print(f"Total calls: {full_count}")
hi = full_count

# Confirm full fails
p_full, _ = run_with_limit(full_count)
ok_full, err_full = try_open(p_full)
print(f"Full (limit={full_count}): ok={ok_full}, err={err_full}")

# Search for smallest limit that fails
last_ok = 0
first_fail = full_count
while lo <= hi:
    mid = (lo + hi) // 2
    p, _ = run_with_limit(mid)
    ok, err = try_open(p)
    print(f"limit={mid}: ok={ok}")
    if ok:
        last_ok = mid
        lo = mid + 1
    else:
        first_fail = mid
        hi = mid - 1

print(f"\nLast OK limit: {last_ok}")
print(f"First failing limit: {first_fail}")

app.Quit()
