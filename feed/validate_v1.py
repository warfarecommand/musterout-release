"""Installed-feed validator preserved from sync-feed.yml."""
import datetime, re
def validate_feed(feed, now=None, require_complete=True):
    # Scan every key and value, including unknown nested fields, before use.
    def clean(value):
        if isinstance(value, str) and re.search(r"[\x00-\x1f\x7f-\x9f]", value):
            raise ValueError("control character in feed")
        if isinstance(value, dict):
            for key, item in value.items():
                clean(key)
                clean(item)
        elif isinstance(value, list):
            for item in value:
                clean(item)
    clean(feed)
    if not isinstance(feed, dict):
        raise ValueError("feed must be a JSON object")
    required = {"schema_version", "source", "generated_at", "checked_from", "checked_to", "coverage",
                "checked_count", "unclassified_count", "truncated", "capture_replay", "notices"}
    if not required <= feed.keys() or type(feed["schema_version"]) is not int or feed["schema_version"] != 1 or feed["source"] != "MARADMIN":
        raise ValueError("missing or invalid expected feed keys")
    if not isinstance(feed["generated_at"], str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})", feed["generated_at"]):
        raise ValueError("invalid generated_at")
    stamp = datetime.datetime.fromisoformat(feed["generated_at"].replace("Z", "+00:00"))
    now = now or datetime.datetime.now(datetime.timezone.utc)
    if stamp > now or (require_complete and now - stamp > datetime.timedelta(hours=72)):
        raise ValueError("stale or future feed")
    dates = {}
    for key in ("checked_from", "checked_to"):
        if not isinstance(feed[key], str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", feed[key]):
            raise ValueError("invalid feed date")
        dates[key] = datetime.date.fromisoformat(feed[key])
    if dates["checked_to"] < dates["checked_from"] or dates["checked_to"] - dates["checked_from"] > datetime.timedelta(days=7) or dates["checked_to"] > now.date():
        raise ValueError("invalid feed window")
    if not isinstance(feed["coverage"], str) or not feed["coverage"].strip():
        raise ValueError("coverage must be a nonempty string")
    if not isinstance(feed["notices"], list) or len(feed["notices"]) > 100:
        raise ValueError("invalid notices or more than 100 items")
    if type(feed["checked_count"]) is not int or feed["checked_count"] < len(feed["notices"]):
        raise ValueError("invalid checked_count")
    if type(feed["unclassified_count"]) is not int or feed["unclassified_count"] < 0:
        raise ValueError("invalid unclassified_count")
    for key in ("truncated", "capture_replay"):
        if type(feed[key]) is not bool:
            raise ValueError("invalid feed flag")
    if require_complete and (feed["unclassified_count"] != 0 or feed["truncated"] or feed["capture_replay"]):
        raise ValueError("incomplete feed")
    if "body_available" in feed and type(feed["body_available"]) is not bool:
        raise ValueError("invalid body_available")
    numbers = set()
    for notice in feed["notices"]:
        if not isinstance(notice, dict):
            raise ValueError("notice must be an object")
        number = notice.get("number")
        if not isinstance(number, str) or not re.fullmatch(r"[0-9]{1,3}/[0-9]{2}", number) or number in numbers:
            raise ValueError("invalid or duplicate notice number")
        numbers.add(number)
        for key, limit in (("title", 300), ("summary", 1000)):
            value = notice.get(key)
            if not isinstance(value, str) or not value.strip() or len(value.encode("utf-16-le")) // 2 > limit or re.search(r"[<>]", value):
                raise ValueError("invalid or oversized notice text")
        url = notice.get("url")
        # Exact origin, no credentials or ports; retain the digest's message path.
        if not isinstance(url, str) or len(url) > 500 or not re.fullmatch(r"https://www\.marines\.mil/News/Messages/Messages-Display/[^\s<>\\]+", url):
            raise ValueError("invalid official message URL")
        posted = notice.get("posted")
        if not isinstance(posted, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", posted):
            raise ValueError("invalid notice date")
        datetime.date.fromisoformat(posted)
        if not feed["checked_from"] <= posted <= feed["checked_to"]:
            raise ValueError("notice outside checked window")
        for key, allowed in (("lines", {"separation", "retirement", "va", "skillbridge", "reserve", "leave", "family"}),
                             ("paths", {"resign", "retire", "eas", "all"})):
            value = notice.get(key)
            if not isinstance(value, list) or not value or any(not isinstance(v, str) or v not in allowed for v in value) or len(value) != len(set(value)):
                raise ValueError("invalid notice classification")
        if type(notice.get("body_available")) is not bool:
            raise ValueError("invalid notice body_available")
        if "action" in notice and notice["action"] not in ("required", "informational"):
            raise ValueError("invalid action")
        if "confidence" in notice and notice["confidence"] not in ("high", "medium", "low"):
            raise ValueError("invalid confidence")
        if "relevant" in notice and notice["relevant"] is not True:
            raise ValueError("invalid relevance")
        if notice.get("deadline") is not None:
            if not isinstance(notice["deadline"], str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", notice["deadline"]):
                raise ValueError("invalid deadline")
            datetime.date.fromisoformat(notice["deadline"])
    return feed
