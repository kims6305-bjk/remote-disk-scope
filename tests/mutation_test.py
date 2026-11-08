"""Proves the selftest is not a green light by accident: each mutant disables one rule and must FAIL selftest.
Run: python3 tests/mutation_test.py   (exit 1 if any mutant survives)"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "scripts")
MUTANTS = {
    "folder duplicate check off": ('            if all(o):', '            if False and all(o):'),
    "project folder detection off": ('            if any(fnmatch.fnmatch(p.lower(), m.lower()) for r in rels', '            if False and any(fnmatch.fnmatch(p.lower(), m.lower()) for r in rels'),
    "program folder detection off": ('            elif any(len(r) <= 2 and ext_of', '            elif False and any(len(r) <= 2 and ext_of'),
    "year subfolders off": ('if cat in R["by_year"] else ""', 'if False else ""'),
    "custom rules off": ('for c in R["custom"] if', 'for c in [] if'),
    "empty folder detection off": ('        elif not d["_fs"]:', '        elif False:'),
    "oldest copy survives off": ('and (l == "정리됨" or l in seen))', ')'),
    "kept folders counted as original": ('        elif d["folder"]:  #', '        else:  #'),
    "keep_dirs off": ('for g in R["keep_dirs"]', 'for g in []'),
    "junk files not ignored": ('real = [f for f in fs if f and os.path.basename(f[0]).lower() not in JUNK]', 'real = [f for f in fs if f]'),
    "inner duplicates list the original": ('        for p, l in live[1:]:', '        for p, l in live:'),
    "scan follows symlinks": ('                    st = e.stat(follow_symlinks=False)\n                except OSError as x:\n                    errs.append([r,',
                              '                    st = e.stat(follow_symlinks=True)\n                except OSError as x:\n                    errs.append([r,'),
    "control chars not escaped": ('    return _BAD.sub(lambda m:', '    return s or _BAD.sub(lambda m:'),
}


def run(d):
    return subprocess.run([sys.executable, os.path.join(d, "diskscope.py"), "selftest"], capture_output=True, timeout=120).returncode


def main():
    src = open(os.path.join(SRC, "diskscope.py"), encoding="utf-8").read()
    with tempfile.TemporaryDirectory() as d:
        shutil.copy(os.path.join(SRC, "rules.json"), d)
        open(os.path.join(d, "diskscope.py"), "w", encoding="utf-8").write(src)
        assert run(d) == 0, "unmutated selftest must pass"
        survived = []
        for name, (a, b) in MUTANTS.items():
            assert src.count(a) == 1, "mutation anchor not found (code changed?): " + name
            open(os.path.join(d, "diskscope.py"), "w", encoding="utf-8").write(src.replace(a, b))
            ok = run(d) != 0
            print(("killed   " if ok else "SURVIVED ") + name)
            if not ok:
                survived.append(name)
    print("%d/%d mutants killed" % (len(MUTANTS) - len(survived), len(MUTANTS)))
    sys.exit(1 if survived else 0)


if __name__ == "__main__":
    main()
