#!/usr/bin/env python3
"""Inject seed.json into template.html and write board.html, the page Claude Code publishes.
Run from board/: python3 build_seed.py && python3 build_board.py"""
import hashlib, json, os, re, subprocess, sys
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

# MTN-94, TRS ruling 18 OCT 2026: 125 copy revisions measured 121,039 bytes
# in format 2; the full publication measured 1,158,488 bytes. The old 120,000
# soft target was a page budget, not a database or wire limit. Allow growth
# to 160,000 without dropping history; retain the 200,000-byte hard ceiling.
FINGERPRINT_SOFT_TARGET_BYTES = 160000
FINGERPRINT_HARD_LIMIT_BYTES = 200000

def decode_fingerprints(value):
    if "format" not in value:
        return value
    if value["format"] != 2:
        raise ValueError("unknown fingerprint format")
    digests = value["digests"]
    if len(set(digests)) != len(digests) or any(not re.fullmatch(r"[a-f0-9]{64}", h) for h in digests) or len(value["shapes"]) != len(digests):
        raise ValueError("invalid fingerprint dictionary")
    def digest(n):
        if type(n) is not int or not 0 <= n < len(digests):
            raise ValueError("invalid fingerprint index")
        return digests[n]
    result = {k: v for k, v in value.items() if k not in ("format", "digests", "versions", "shapes", "variants")}
    result.update(versions={v: {i: digest(n) for i, n in rows.items()} for v, rows in value["versions"].items()},
                  shapes=dict(zip(digests, value["shapes"])),
                  variants={i: [digest(n) for n in rows] for i, rows in value["variants"].items()})
    return result


def pack_fingerprints(value):
    digests = sorted(value["shapes"])
    indices = {h: n for n, h in enumerate(digests)}
    packed = {k: v for k, v in value.items() if k not in ("versions", "shapes", "variants")}
    packed.update(format=2, digests=digests,
                  versions={v: {i: indices[h] for i, h in rows.items()} for v, rows in value["versions"].items()},
                  shapes=[value["shapes"][h] for h in digests],
                  variants={i: [indices[h] for h in rows] for i, rows in value["variants"].items()})
    if canonical(decode_fingerprints(packed)) != canonical(value):
        raise ValueError("fingerprint compaction lost data")
    if len(canonical(packed).encode()) >= FINGERPRINT_SOFT_TARGET_BYTES:
        raise ValueError("compact fingerprint map exceeds TEL1 target")
    return packed


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

    def legacy_browser_decode(value):
        # Historical L2 captures omitted charset; reproduce only the exact UTF-8/Windows-1252 transform.
        if isinstance(value, str):
            decoded = value.encode("utf-8").decode("cp1252", errors="surrogateescape")
            return "".join(chr(ord(c)-0xDC00) if 0xDC80 <= ord(c) <= 0xDCFF else c for c in decoded)
        if isinstance(value, list):
            return [legacy_browser_decode(v) for v in value]
        if isinstance(value, dict):
            return {k: legacy_browser_decode(v) for k, v in value.items()}
        return value

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
            damaged = legacy_browser_decode(fields)
            if damaged != fields and any(any(ord(c) > 127 for c in citation.get("quote", "")) for citation in item.get("cite", [])):
                damaged_hash = hashlib.sha256(canonical(damaged).encode()).hexdigest()
                variants = result["variants"].setdefault(item["id"], [])
                if damaged_hash not in variants:
                    variants.append(damaged_hash)
                result["shapes"][damaged_hash] = result["shapes"][digest]
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
            # Tags identify published bytes even when a later feed sync carries
            # the same config version. Untagged releases use publication commits.
            tags = git(repo, "tag", "--list").splitlines()
            commits = []
            for version in sorted(missing):
                for tag in ("v" + version, version):
                    if tag in tags:
                        commit = git(repo, "rev-parse", tag + "^{commit}").strip()
                        commits.append((commit, version))
                        break
            for row in git(repo, "log", "--format=%H %s").splitlines():
                commit, subject = row.split(" ", 1)
                match = re.match(r"^Muster Out (\d+\.\d+\.\d+)(?:$|[ :])", subject)
                if match:
                    commits.append((commit, match[1]))
        except subprocess.CalledProcessError:
            continue
        for commit, published_version in commits:
            if published_version not in missing:
                continue
            try:
                version = json.loads(git(repo, "show", commit + ":config.json"))["version"]
            except (subprocess.CalledProcessError, KeyError, json.JSONDecodeError):
                continue
            if version != published_version:
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
        previous = decode_fingerprints(json.loads(match[1])) if match else {}
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
    # add() may append current variants after the history sort; keep every list ordered.
    for hashes in result["variants"].values():
        hashes.sort()
    # Claim data belongs to the owner. Admit only the exact traced encoding
    # damage of a canonical seeded quotation, scoped by row and source identity.
    result["claimQuoteRepairs"] = []
    for row in current.get("claim", {}).get("benefits", {}).get("rows", []):
        if not row.get("id"):
            continue
        for cite in row.get("cite", []):
            quote = cite.get("quote", "")
            damaged = legacy_browser_decode(quote)
            if damaged != quote:
                result["claimQuoteRepairs"].append(dict(
                    row=row["id"], ref=cite.get("ref"), para=cite.get("para"),
                    url=cite.get("url"), before=damaged, after=quote))
    # Content updates also run on boards already at this product version.
    revision_content = dict(items=result["versions"]["current"], claimQuoteRepairs=result["claimQuoteRepairs"])
    # This exact-default correction must also reach already-current boards.
    revision_content["enlistedRetirementDesk"] = next((c for c in current.get("contacts", []) if c.get("id") == "c-mmsr2-re"), None)
    result["revision"] = hashlib.sha256(canonical(revision_content).encode()).hexdigest()
    result["version"] = config["version"]
    # Budget raised from 100 KB to 150 KB for 0.2.0 (label and brief changed every current hash),
    # then to 200 KB for 0.2.4 (one more released seed version, no seed change). Compact the map
    # (shared digest table) before it reaches this bound; each release adds about 15 KB. Tracked in MTN-55.
    # TEL1 compaction and MTN-94 retain a separate 200 KB hard ceiling.
    if len(canonical(pack_fingerprints(result)).encode()) >= FINGERPRINT_HARD_LIMIT_BYTES:
        raise SystemExit("seed fingerprint map exceeds 200 KB")
    return result


def embed(template, seed, fingerprints, root=here.parent):
    escape = lambda value: canonical(value).replace("</", "<\\/")
    if "/*HELP_LINES*/" in template:
        template = template.replace("/*HELP_LINES*/", escape(json.loads((root / "packs/usmc/help-lines.json").read_text())))
    if "/*COACH_SETUP*/" in template:
        project = (root / "PROJECT.md").read_text(encoding="utf-8")
        block = re.search(r"## Instructions to paste\s+```text\n(.*?)\n```", project, re.S)
        if not block:
            raise SystemExit("PROJECT.md lacks the complete coach setup block")
        template = template.replace("/*COACH_SETUP*/", escape(block[1]))
    if "/*COACH_JS*/" in template:
        template = template.replace("/*COACH_JS*/", (root / "board/coach.js").read_text(encoding="utf-8"))
    workflows = []
    for file in sorted((root / "workflows").glob("*.md")):
        text = file.read_text(encoding="utf-8")
        title = re.search(r"^# (.+)$", text, re.M)
        if not title or "## Paste this" not in text:
            raise SystemExit(f"workflow lacks title or prompt: {file}")
        prompt = re.search(r"## Paste this\s+```text\n(.*?)\n```", text, re.S)
        if not prompt or not prompt[1].strip():
            raise SystemExit(f"workflow lacks a plain text prompt: {file}")
        workflows.append({"file": file.name, "title": title[1], "text": prompt[1].strip()})
    if "/*WORKFLOWS*/" in template:
        if len(workflows) != 10:
            raise SystemExit("expected ten starter workflow prompts")
        template = template.replace("/*WORKFLOWS*/", escape(workflows))
    libraries = "<script>" + (root / "board/fingerprints.js").read_text() + "</script>\n"
    libraries += "<script>" + (root / "supabase/functions/_shared/telemetry_contract.js").read_text() + "</script>\n"
    libraries += "<script>" + (root / "supabase/functions/_shared/registration_v3.js").read_text() + "</script>\n"
    telemetry_config = json.loads((root / "config.json").read_text()).get("telemetry", {})
    template = template.replace("/*RG3_JS*/", (root / "board/registration_v3.js").read_text())
    template = template.replace("/*TEL_JS*/", (root / "board/telemetry.js").read_text()).replace("/*TEL_CONFIG*/", escape(telemetry_config))
    title = re.match(r"<title>[^<]*</title>\n?", template)
    if not title:
        raise SystemExit("template must start with its <title>")
    template = template[title.end():]
    # The gallery reads the name from the first 8 KB only, so the title leads.
    return title[0].rstrip("\n") + "\n" + libraries + embed_trust(embed_updates(template.replace("/*SEED*/", escape(seed)).replace("/*SEED_FINGERPRINTS*/", escape(pack_fingerprints(fingerprints))), root), root)

def build_page():
    seed = json.loads((here / "seed.json").read_text())
    def _leak_words():
        if os.environ.get("MUSTEROUT_PUBLIC_BUILD") == "1":
            print("private word-list check not run: public build forbids private-file access")
            return []
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
    contract = (here.parent / "supabase/functions/_shared/telemetry_contract.js").read_text()
    (here.parent / "docs/assets/telemetry_contract.js").write_text(contract)
    (here.parent / "docs/assets/registration_v3.js").write_text((here.parent / "supabase/functions/_shared/registration_v3.js").read_text())
    telemetry_config = json.loads((here.parent / "config.json").read_text()).get("telemetry", {})
    (here.parent / "docs/assets/telemetry_config.js").write_text("window.MusterOutTelemetryConfig=" + canonical(telemetry_config) + ";\n")
    (here / "board.html").write_bytes(out.encode())
    (here / "board.publish.html").write_bytes(document.encode())
    print(f"board.html {len(out.encode())//1024} KB; board.publish.html {len(document.encode())} bytes; fragment identical; fingerprints {len(canonical(pack_fingerprints(fingerprints)).encode())} bytes; scripts parse")

if __name__ == "__main__":
    build_page()
