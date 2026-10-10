#!/usr/bin/env python3
"""Inject seed.json into template.html and write board.html, the page Claude Code publishes.
Run from board/: python3 build_seed.py && python3 build_board.py"""
import hashlib, json, re, subprocess, sys
from pathlib import Path
here = Path(__file__).resolve().parent

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def seed_fingerprints(root=here.parent):
    """Read released snapshots, never approximate a release with today's seed.

    The release repo begins at 0.1.2. Earlier folder releases are commits
    that wrote the shipped archive on the CHANGELOG release date.
    A release export carries the embedded map so folder rebuilds need no git.
    """
    template = (root / "board/template.html").read_text()
    owned = json.loads(re.search(r"var SEED_OWNED_FIELDS = (\[[^;]+\]);", template)[1])
    personal = json.loads(re.search(r"var PERSON_OWNED_FIELDS = (\[[^;]+\]);", template)[1])
    versions = dict(re.findall(r"^## (\d+\.\d+\.\d+) \((\d{4}-\d{2}-\d{2})\)$", (root / "CHANGELOG.md").read_text(), re.M))
    current = json.loads((root / "board/seed.json").read_text())
    config = json.loads((root / "config.json").read_text())
    result = {"versions": {}, "shapes": {}, "sources": {}, "variants": {}, "reissues": {}}

    def add(label, snapshot):
        hashes = {}
        for item in snapshot["items"]:
            unknown = set(item) - set(owned) - set(personal) - {"id"}
            if unknown:
                raise SystemExit(f"item ownership missing: {sorted(unknown)}")
            fields = {key: item[key] for key in owned if key in item}
            digest = hashlib.sha256(canonical(fields).encode()).hexdigest()
            hashes[item["id"]] = digest
            result["shapes"][digest] = {"when": item.get("when", []), "setup": item.get("due", {}).get("date") == "SETUP" if item.get("due") else False}
        result["versions"][label] = hashes

    def git(repo, *args):
        top = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "--show-toplevel"], stderr=subprocess.DEVNULL).decode().strip()
        if Path(top).resolve() != repo.resolve():
            raise subprocess.CalledProcessError(1, ["git", "rev-parse"])
        return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.DEVNULL).decode()

    # The version being built is the working seed ("current"), not a past release.
    missing = set(versions) - {config["version"]}
    # Early versions shipped more than once at the same version number.
    # Preserve all actually shipped seeds, including the original pilot.
    for version in sorted(versions):
        if tuple(map(int, version.split("."))) >= (0, 1, 2):
            continue
        try:
            rows = git(root, "log", "--reverse", "--diff-filter=AM", "--format=%H %as", "--", f"docs/dl/musterout-{version}.zip").splitlines()
        except subprocess.CalledProcessError:
            continue
        for row in rows:
            commit, date = row.split()
            if date != versions[version]:
                continue
            snapshot = json.loads(git(root, "show", commit + ":board/seed.json"))
            if version in missing:
                add(version, snapshot)
                result["sources"][version] = commit
                missing.remove(version)
            else:
                add("reissue", snapshot)
                for item_id, digest in result["versions"].pop("reissue").items():
                    if digest != result["versions"][version].get(item_id):
                        variants = result["variants"].setdefault(item_id, [])
                        if digest not in variants:
                            variants.append(digest)
                result["reissues"].setdefault(version, []).append(commit)
    for repo in (root.parent / "musterout-release", root):
        try:
            commits = git(repo, "log", "--format=%H %as").splitlines()
        except subprocess.CalledProcessError:
            continue
        for row in commits:
            commit, date = row.split()
            try:
                version = json.loads(git(repo, "show", commit + ":config.json"))["version"]
            except (subprocess.CalledProcessError, KeyError, json.JSONDecodeError):
                continue
            if version not in missing or date != versions[version]:
                continue
            try:
                snapshot = json.loads(git(repo, "show", commit + ":board/seed.json"))
            except (subprocess.CalledProcessError, json.JSONDecodeError):
                continue
            add(version, snapshot)
            result["sources"][version] = commit
            missing.remove(version)
            if not missing:
                break
    if missing:
        # A shipped folder has no private product history. Use only the map
        # shipped in its verified page, and fail closed if it lacks a release.
        page = (root / "board/board.html").read_text()
        match = re.search(r'<script type="application/json" id="seed-fingerprints">(.*?)</script>', page, re.S)
        previous = json.loads(match[1]) if match else {}
        for version in sorted(missing):
            if version not in previous.get("versions", {}):
                raise SystemExit(f"released seed history unavailable: {version}")
            result["versions"][version] = previous["versions"][version]
            result["sources"][version] = previous["sources"][version]
        result["shapes"].update(previous.get("shapes", {}))
        for item_id, hashes in previous.get("variants", {}).items():
            result["variants"][item_id] = sorted(set(result["variants"].get(item_id, []) + hashes))
        result["reissues"].update(previous.get("reissues", {}))
    for hashes in result["variants"].values():
        hashes.sort()
    add("current", current)
    result["revision"] = hashlib.sha256(canonical(result["versions"]["current"]).encode()).hexdigest()
    result["version"] = config["version"]
    if len(canonical(result).encode()) >= 100000:
        raise SystemExit("seed fingerprint map exceeds 100 KB")
    return result


def embed(template, seed, fingerprints):
    escape = lambda value: canonical(value).replace("</", "<\\/")
    return template.replace("/*SEED*/", escape(seed)).replace("/*SEED_FINGERPRINTS*/", escape(fingerprints))

def build_page():
    seed = json.loads((here / "seed.json").read_text())
    def _leak_words():
        p = Path.home() / ".musterout" / "leak_words.txt"
        if not p.exists():
            print("leak guard skipped: no private word list at ~/.musterout/leak_words.txt")
            return []
        return [w for w in p.read_text(encoding="utf-8").splitlines() if w]
    tpl = (here / "template.html").read_text()
    assert "/*SEED*/" in tpl and "MUSTEROUT_PATCHED" in tpl
    fingerprints = seed_fingerprints()
    out = embed(tpl, seed, fingerprints)
    for d in (chr(0x2014), chr(0x2013)):
        if d in out: sys.exit("dash found in page")
    # The exact, source-verified enlisted counseling quote uses generic pronouns.
    privacy_text = out.replace('Counsel the Marine concerning his or her potential for recall to active duty and/or mobilization.', '')
    for bad in _leak_words():
        if bad in privacy_text: sys.exit(f"personal string in page: {bad}")
    (here / "board.html").write_text(out)
    # syntax check the inline script
    js = re.findall(r"<script>(.*?)</script>", out, re.S)[-1]
    chk = here / "_dev" / "_board_check.js"; chk.write_text(js)
    r = subprocess.run(["node", "--check", str(chk)], capture_output=True, text=True)
    chk.unlink()
    if r.returncode: sys.exit("script does not parse:\n" + r.stderr)
    print(f"board.html {len(out)//1024} KB, fingerprints {len(canonical(fingerprints).encode())} bytes, script parses")

if __name__ == "__main__":
    build_page()
