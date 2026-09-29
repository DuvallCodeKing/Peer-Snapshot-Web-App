"""Inline data/peers.json into scripts/template.html -> index.html (single self-contained page)."""
import json
data = json.dumps(json.load(open("data/peers.json")), separators=(",", ":"))
open("index.html", "w").write(open("scripts/template.html").read().replace("/*DATA*/", data))
