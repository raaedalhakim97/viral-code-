"""
post_to_n8n.py — send queued videos to the n8n publishing webhook.

    python3 post_to_n8n.py --probe                 # what does the endpoint want?
    python3 post_to_n8n.py --count 1 --dry-run     # show exactly what would go
    python3 post_to_n8n.py --count 1               # send ONE, then stop
    python3 post_to_n8n.py --count 5               # a day's batch

Reads `youtube_queue.json` (built by build_youtube_queue.py) and posts the next
unsent entries. Every send is recorded in `youtube_posted.json`, so re-running
never double-posts — that log is the only thing standing between a retry and a
duplicate on a public channel, and it is written BEFORE the next send starts.

    IT SENDS ONE VIDEO AT A TIME, AND STOPS ON THE FIRST FAILURE. Posting is
    not idempotent and not reversible. A batch that half-worked is worth far
    less than a clear error and an untouched queue.

DEFAULT IS --dry-run OFF BUT --count 1. Publishing five things to a live
channel on the strength of a payload format nobody has confirmed is how a
channel ends up with five broken uploads. Send one, look at it, then raise the
count.

THE PAYLOAD IS A GUESS UNTIL THE ENDPOINT CONFIRMS IT. Two shapes are
supported because n8n workflows are commonly built either way:

    --mode multipart   (default)  file + fields, as a real upload
    --mode json                   metadata only, video as base64 or a URL

Run --probe first. If the workflow expects something else, the shape is one
function (`build_payload`) and the fields are one dict.
"""
import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
QUEUE = os.path.join(HERE, "youtube_queue.json")
POSTED = os.path.join(HERE, "youtube_posted.json")
URL = os.environ.get("N8N_WEBHOOK",
                     "https://n8n.thunderworkflow.com/webhook/manus-viral-shorts")


def load_posted():
    if not os.path.exists(POSTED):
        return {"sent": []}
    return json.load(open(POSTED))


def record(entry, status, detail):
    log = load_posted()
    log["sent"].append({"file": entry["file"], "title": entry["title"],
                        "status": status, "detail": detail,
                        "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    json.dump(log, open(POSTED, "w"), indent=2, ensure_ascii=False)


def multipart(entry):
    """A real file upload: boundary-delimited body, video plus metadata."""
    boundary = "----observercollapse" + str(int(time.time() * 1000))
    b = boundary.encode()
    parts = []
    fields = {
        "title": entry["title"],
        "description": entry["description"] or "",
        "tags": ",".join(entry["tags"]),
        "filename": entry["file"],
        "duration": str(entry["duration"]),
        "privacyStatus": "public",
    }
    for k, v in fields.items():
        parts += [b"--" + b,
                  f'Content-Disposition: form-data; name="{k}"'.encode(),
                  b"", v.encode()]
    ctype = mimetypes.guess_type(entry["file"])[0] or "video/mp4"
    parts += [b"--" + b,
              f'Content-Disposition: form-data; name="video"; '
              f'filename="{entry["file"]}"'.encode(),
              f"Content-Type: {ctype}".encode(), b""]
    body = b"\r\n".join(parts) + b"\r\n"
    body += open(entry["path"], "rb").read()
    body += b"\r\n--" + b + b"--\r\n"
    return body, f"multipart/form-data; boundary={boundary}"


def as_json(entry):
    payload = {
        "title": entry["title"],
        "description": entry["description"] or "",
        "tags": entry["tags"],
        "filename": entry["file"],
        "duration": entry["duration"],
        "privacyStatus": "public",
    }
    return json.dumps(payload).encode(), "application/json"


def send(entry, mode, timeout):
    body, ctype = (multipart if mode == "multipart" else as_json)(entry)
    req = urllib.request.Request(URL, data=body, method="POST",
                                 headers={"Content-Type": ctype,
                                          "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read(2000).decode("utf-8", "replace")


def probe():
    print(f"probing {URL}")
    for method in ("GET", "OPTIONS"):
        try:
            req = urllib.request.Request(URL, method=method)
            with urllib.request.urlopen(req, timeout=25) as r:
                print(f"  {method}: {r.status}  {r.read(400).decode('utf-8','replace')}")
        except urllib.error.HTTPError as e:
            print(f"  {method}: HTTP {e.code}  {e.read(400).decode('utf-8','replace')}")
        except Exception as e:
            print(f"  {method}: unreachable — {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=1,
                    help="how many to send (default 1 — raise it only once one "
                         "has landed correctly)")
    ap.add_argument("--mode", choices=("multipart", "json"), default="multipart")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--timeout", type=int, default=300)
    a = ap.parse_args()

    if a.probe:
        probe()
        return

    queue = json.load(open(QUEUE))["videos"]
    done = {s["file"] for s in load_posted()["sent"] if s["status"] == "ok"}
    todo = [v for v in queue if v["file"] not in done][:a.count]

    if not todo:
        print("queue is empty — everything has been sent")
        return

    print(f"{len(done)} already sent, {len(queue) - len(done)} left. "
          f"sending {len(todo)} to {URL}\n")
    for v in todo:
        size = v["bytes"] / 1e6
        print(f"  {v['file']}  ({size:.1f} MB, {v['duration']}s)")
        print(f"    title: {v['title']}")
        print(f"    tags:  {', '.join(v['tags'][:8])}")
        if a.dry_run:
            print("    [dry run — nothing sent]\n")
            continue
        try:
            status, resp = send(v, a.mode, a.timeout)
            record(v, "ok", f"HTTP {status}: {resp[:300]}")
            print(f"    -> HTTP {status}  {resp[:200]}\n")
        except Exception as e:
            record(v, "failed", repr(e))
            print(f"    -> FAILED: {e}")
            print("    stopping. the rest of the queue is untouched.")
            sys.exit(1)


if __name__ == "__main__":
    main()
