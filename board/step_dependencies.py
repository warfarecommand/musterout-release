"""Informational task prerequisites. Date rules never consume this field."""

def validate_dependencies(items, edges):
    errors = []
    by_id = {item["id"]: item for item in items}
    explained = set()
    for edge in edges:
        if not isinstance(edge, dict):
            errors.append("dependency source: edge must be an object")
            continue
        dependent, prerequisite = edge.get("dependent"), edge.get("prerequisite")
        if not isinstance(dependent, str) or dependent not in by_id:
            errors.append(f"dependency source: unknown dependent {dependent!r}")
            continue
        if not isinstance(prerequisite, str) or prerequisite not in by_id:
            errors.append(f"{dependent}: unknown prerequisite {prerequisite!r}")
            continue
        if not any(isinstance(edge.get(key), str) and edge[key].strip() for key in ("reason", "citation")):
            errors.append(f"{dependent} after {prerequisite}: missing reason or citation")
        pair = (dependent, prerequisite)
        if pair in explained:
            errors.append(f"{dependent}: duplicate dependency source {prerequisite}")
        explained.add(pair)
    graph = {}
    for item in items:
        refs = item.get("after", [])
        if not isinstance(refs, list):
            errors.append(f"{item['id']}: after must be an array")
            continue
        graph[item["id"]] = []
        seen = set()
        for ref in refs:
            if not isinstance(ref, str) or not ref.strip():
                errors.append(f"{item['id']}: after requires nonempty string IDs")
                continue
            if ref not in by_id:
                errors.append(f"{item['id']}: unknown prerequisite {ref}")
            if ref == item["id"]:
                errors.append(f"{item['id']}: self dependency")
            if ref in seen:
                errors.append(f"{item['id']}: duplicate prerequisite {ref}")
            if (item["id"], ref) not in explained:
                errors.append(f"{item['id']} after {ref}: missing pack source reason or citation")
            seen.add(ref)
            graph[item["id"]].append(ref)
    visiting, visited = set(), set()
    def walk(item_id):
        if item_id in visiting:
            errors.append(f"dependency cycle at {item_id}")
            return
        if item_id in visited:
            return
        visiting.add(item_id)
        for ref in graph.get(item_id, []):
            walk(ref)
        visiting.remove(item_id)
        visited.add(item_id)
    for item_id in graph:
        walk(item_id)
    return errors


def apply_dependencies(items, source):
    if not isinstance(source, dict) or source.get("schema") != 1 or not isinstance(source.get("edges"), list):
        raise ValueError("dependency source: expected schema 1 and edges array")
    # Check declarations before attaching them; malformed sources never write a seed.
    edges = source["edges"]
    by_id = {item["id"]: item for item in items}
    for edge in edges:
        if isinstance(edge, dict) and isinstance(edge.get("dependent"), str) and edge["dependent"] in by_id:
            refs = by_id[edge["dependent"]].setdefault("after", [])
            if isinstance(refs, list):
                refs.append(edge.get("prerequisite"))
    errors = validate_dependencies(items, edges)
    if errors:
        raise ValueError("\n".join(errors))
