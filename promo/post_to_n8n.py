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

THE PAYLOAD IS CONFIRMED, NOT GUESSED. Read off the live workflow
(u32k553be5vakrce, "Manus - Viral Shorts -> YouTube Auto Upload"):

    {"video_url": "...", "title": "...", "description": "...", "tags": [...]}

The workflow does not receive the file. It receives a URL and FETCHES the video
itself, then hands it to the YouTube node (public, region AE, category 28) and
mirrors it to Google Drive.

    THAT URL MUST BE PUBLICLY FETCHABLE. The "Download Video File" node has no
    credentials attached, so it gets exactly what an anonymous curl gets. The
    repo these videos live in is PRIVATE — every raw.githubusercontent URL for
    it returns 404 unauthenticated, SHA-pinned or not. Until that is fixed the
    workflow will fail at the download step.

    It fails safely: the HTTP node raises on a 404 rather than passing an error
    page downstream, so a bad URL means no upload rather than a broken upload.
    But it does mean nothing can be posted until the videos are reachable.

Three ways out, in order of least friction:
    1. attach a GitHub credential to the "Download Video File" node
       (there is already an "Observer World - Pull from GitHub & Upload"
       workflow, so a credential very likely exists)
    2. make the repo public
    3. host the finished videos somewhere anonymous fetch works
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
    """The exact shape the live workflow reads. Confirmed by reading
    workflow u32k553be5vakrce, not guessed:

        Check Payload          gates on  $json.body.video_url  isNotEmpty
        Download Video File    GETs      $json.body.video_url  as a file
        Upload to YouTube      reads     body.title
                                         body.description
                                         body.tags.join(',')   <- must be a LIST

    tags MUST be a JSON array: the node calls .join(',') on it, so a string
    there throws at runtime, after the video has already been downloaded."""
    payload = {
        "video_url": entry["url"],
        "title": entry["title"],
        "description": entry["description"] or "",
        "tags": entry["tags"],
    }
    assert payload["video_url"], "the workflow drops any payload with no video_url"
    assert isinstance(payload["tags"], list), "tags.join(',') needs a list"
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
    ap.add_argument("--mode", choices=("multipart", "json"), default="json",
                    help="json is the confirmed contract; multipart is kept "
                         "only in case the workflow is ever rebuilt to take "
                         "the file directly")
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
        print(f"    url:   {v['url']}")
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
