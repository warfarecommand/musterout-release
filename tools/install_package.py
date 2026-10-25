#!/usr/bin/env python3
"""Stage the reviewed public install set. Never signs or publishes implicitly."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'docs'))
from _build_zip import files, release_entry
spec = importlib.util.spec_from_file_location('musterout_verify', ROOT / 'npm/musterout/verify.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)

# Folder releases keep their full source/build layout. The signed npm install
# needs the prebuilt boards and guides, not authoring tools or deployed servers.
INSTALL_BUILD_ONLY = frozenset({
    'board/template.html',
    'board/build_seed.py',
    'board/seed_copy.py',
    'board/va115_copy.py',
    'board/step_dependencies.py',
    'board/ides_seed.py',
    'board/build_board.py',
    'tools/install_package.py',
    'packs/usmc/check_w6.py',
})


def public_files(root=ROOT):
    # Derived from the reviewed public builder allowlist, never a tree copy.
    paths = list(files()) + [ROOT / 'board/board.publish.html', ROOT / 'board/update_client.js']
    result = {}
    for source in paths:
        p = source.relative_to(ROOT).as_posix()
        if p.startswith('my/'):
            continue  # Even the public folder scaffolding is excluded from install authority.
        if p in INSTALL_BUILD_ONLY or p.startswith('supabase/'):
            continue
        verify.safe_path(p)
        actual = root / p
        if any(x.is_symlink() for x in [actual, *actual.parents]) or not actual.is_file():
            raise ValueError('unsafe_public_file: ' + p)
        raw = actual.read_bytes()
        if len(raw) > verify.MAX_BYTES:
            raise ValueError('public_file_too_large: ' + p)
        result[p] = raw
    if len(result) > verify.MAX_FILES or sum(map(len, result.values())) > verify.MAX_TOTAL:
        raise ValueError('public_set_exceeds_bounds')
    return result


def manifest(release_raw, config=None, product=None):
    config = config or json.loads((ROOT / 'config.json').read_text())
    product = product or public_files()
    released, notes = release_entry(config['version'])
    verify.notes(notes)
    release = verify.wrapper(release_raw, 'release')
    e = release['envelope']
    if e['version'] != config['version'] or e['pack'] != config['pack'] or e['notes'] != notes:
        raise ValueError('release_metadata_differs')
    return dict(schema_version=1, product='Muster Out', version=config['version'], released=released,
                pack=config['pack'], notes=notes,
                files={p: hashlib.sha256(raw).hexdigest() for p, raw in sorted(product.items())},
                release=dict(path='release.js', sha256=verify.digest(release_raw), size=len(release_raw),
                             html_sha256=e['sha256'], html_size=e['size']))


def stage_package(destination, install_raw, release_raw, product=None):
    product = product or public_files()
    config = json.loads(product['config.json'])
    verify.package_check(install_raw, release_raw, config['version'], product, config['pack'])
    destination = Path(destination)
    if destination.is_symlink() or destination.exists():
        raise ValueError('package_destination_must_be_new')
    destination.mkdir(mode=0o700, parents=True)
    for name in ['package.json','LICENSE','NOTICE.md','README.md','verify.cjs','verify.py']:
        (destination/name).write_bytes((ROOT/'npm/musterout'/name).read_bytes())
    for name, raw in [('install.json',install_raw),('release.js',release_raw)]:
        (destination/name).write_bytes(raw)
    for p, raw in product.items():
        target = destination/'install'/p
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    return destination
