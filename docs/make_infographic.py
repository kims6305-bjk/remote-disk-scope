"""Regenerate docs/infographic.{ko,en}.png. The mutation count is measured, not typed: runs tests/mutation_test.py first.
Run: python3 docs/make_infographic.py   (needs Google Chrome)"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

r = subprocess.run([sys.executable, os.path.join(HERE, "..", "tests", "mutation_test.py")], capture_output=True, text=True)
m = re.search(r"(\d+)/(\d+) mutants killed", r.stdout)
assert r.returncode == 0 and m, "mutation test failed:\n" + r.stdout + r.stderr
mut = "%s/%s" % m.groups()
for lang in ("ko", "en"):
    out = os.path.join(HERE, "infographic.%s.png" % lang)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                    "--window-size=1200,548", "--screenshot=" + out,
                    "file://%s?lang=%s&mut=%s" % (os.path.join(HERE, "infographic.html"), lang, mut)],
                   check=True, capture_output=True)
    print(out, mut)
