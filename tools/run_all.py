"""Execute every notebook in place (nbclient), up to N in parallel. Token comes from env APIFY_TOKEN."""
import sys, pathlib, concurrent.futures as cf, traceback
import nbformat
from nbclient import NotebookClient

ROOT = pathlib.Path(__file__).resolve().parent.parent
only = set(sys.argv[1:])


def run(p):
    nb = nbformat.read(p, as_version=4)
    try:
        NotebookClient(nb, timeout=400, kernel_name="python3", allow_errors=False,
                       resources={"metadata": {"path": str(ROOT)}}).execute()
        res = "ok"
    except Exception as e:  # keep partial outputs for diagnosis but report failure
        res = "FAIL " + type(e).__name__ + ": " + str(e)[-300:].replace("\n", " ")
    nbformat.write(nb, p)
    return p.stem, res


paths = [p for p in sorted((ROOT / "notebooks").glob("*.ipynb")) if not only or p.stem in only]
with cf.ThreadPoolExecutor(6) as ex:
    for slug, res in ex.map(run, paths):
        print(slug, res, flush=True)
