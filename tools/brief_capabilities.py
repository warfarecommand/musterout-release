"""Pure native manifest adapter. No service calls, board writes, or grants."""
from copy import deepcopy


def prepare(manifest):
    if not isinstance(manifest, dict) or not manifest.get('url') or not isinstance(manifest.get('capabilities'), dict):
        raise ValueError('Read the actual artifact manifest first')
    for field in ('html', 'sharing', 'title', 'icon'):
        if field not in manifest:
            raise ValueError('The native manifest is incomplete')
    result = deepcopy(manifest)
    result['capabilities']['downloads'] = True
    return result


def verify(before, actual):
    if actual != prepare(before):
        raise ValueError('Readback must preserve the address, page, rules, sharing, and every existing grant')
    return True
