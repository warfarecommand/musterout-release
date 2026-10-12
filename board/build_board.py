#!/usr/bin/env python3
"""Inject seed.json into template.html and write board.html, the page Claude Code publishes.
Run from board/: python3 build_seed.py && python3 build_board.py"""
import hashlib, json, re, subprocess, sys
from pathlib import Path
here = Path(__file__).resolve().parent

# Copied byte for byte from _cook/research/update-test.html buildDoc.
RESET = ':root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,-apple-system,sans-serif;background:#fafaf9}img{max-width:100%}[hidden]{display:none!important}'
DOCUMENT_PREFIX = '<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><style>' + RESET + '</style></head><body>'
DOCUMENT_SUFFIX = '</body></html>'

def complete_document(fragment):
    return DOCUMENT_PREFIX + fragment + DOCUMENT_SUFFIX

def update_config(root=here.parent):
    config = json.loads((root / 'config.json').read_text())
    keys = config.get('update_keys', {})
    return dict(product=config['product'], version=config['version'], pack=config['pack'],
                release_keys=keys.get('release_keys', {}), feed_keys=keys.get('feed_keys', {}))

def embed_updates(fragment, root=here.parent):
    config = canonical(update_config(root)).replace('</', '<\\/')
    engine = (root / 'board/update_client.js').read_text()
    # The template can opt into markers without changing the fragment contract.
    has_engine = '/*UPDATE_ENGINE*/' in fragment
    fragment = fragment.replace('/*UPDATE_CONFIG*/', config)
    if has_engine:
        fragment = fragment.replace('/*UPDATE_ENGINE*/', 'window.MusterOutUpdateConfig=' + config + ';\n' + engine)
    else:
        fragment += '\n<script>window.MusterOutUpdateConfig=' + config + ';\n' + engine + '</script>\n'
    return fragment

def embed_trust(fragment, root=here.parent):
    """Inline the trust components; templates may opt into explicit markers."""
    for marker, filename, tag in (("/*TRUST_CSS*/", "trust.css", "style"),
                                   ("/*TRUST_JS*/", "trust.js", "script")):
        content = (root / "board" / filename).read_text()
        if marker in fragment:
            fragment = fragment.replace(marker, content)
        else:
            fragment += "\n<" + tag + ">" + content + "</" + tag + ">\n"
    return fragment

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
    # Budget raised from 100 KB to 150 KB for 0.2.0 (label and brief changed every current hash).
    # Compact the map (shared digest table) before it reaches this bound; each release adds about 15 KB.
    if len(canonical(result).encode()) >= 150000:
        raise SystemExit("seed fingerprint map exceeds 150 KB")
    return result


def embed(template, seed, fingerprints, root=here.parent):
    escape = lambda value: canonical(value).replace("</", "<\\/")
    return embed_trust(embed_updates(template.replace("/*SEED*/", escape(seed)).replace("/*SEED_FINGERPRINTS*/", escape(fingerprints)), root), root)

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
    document = complete_document(out)
    assert document.encode()[len(DOCUMENT_PREFIX.encode()):-len(DOCUMENT_SUFFIX.encode())] == out.encode()
    # syntax check the inline script
    for js in re.findall(r"<script>(.*?)</script>", out, re.S):
        r = subprocess.run(["node", "--check"], input=js, capture_output=True, text=True)
        if r.returncode: sys.exit("script does not parse:\n" + r.stderr)
    (here / "board.html").write_bytes(out.encode())
    (here / "board.publish.html").write_bytes(document.encode())
    print(f"board.html {len(out.encode())//1024} KB; board.publish.html {len(document.encode())} bytes; fragment identical; fingerprints {len(canonical(fingerprints).encode())} bytes; scripts parse")

if __name__ == "__main__":
    build_page()
