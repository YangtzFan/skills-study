"""Bounded local CDP inspection and source downloads; no credential export."""
import argparse
import hashlib
import ipaddress
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request


def endpoint(value):
    parts = urllib.parse.urlsplit(value)
    try:
        local = parts.hostname == "localhost" or ipaddress.ip_address(parts.hostname).is_loopback
    except (ValueError, TypeError):
        local = False
    if not local or parts.scheme != "http" or parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError("CDP endpoint must be a credential-free loopback HTTP address")
    if parts.path not in ("", "/"):
        raise ValueError("CDP endpoint must not include a path")
    return value.rstrip("/")


def sanitize_url(value):
    parts = urllib.parse.urlsplit(value)
    # All query parameters are omitted; preserve a public article ID separately.
    if parts.scheme not in ("http", "https"):
        return parts.scheme + ":"
    host = parts.hostname or ""
    if ":" in host:
        host = "[" + host + "]"
    if parts.port:
        host += ":" + str(parts.port)
    return urllib.parse.urlunsplit((parts.scheme, host, parts.path, "", ""))


def fetch_json(base, path):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(base + path, timeout=10) as response:
        return json.load(response)


class Connection:
    def __init__(self, url, timeout=30):
        try:
            import websocket
        except ImportError as exc:
            raise RuntimeError("Missing local dependency: websocket-client; no packages installed") from exc
        parsed = urllib.parse.urlsplit(url)
        endpoint(urllib.parse.urlunsplit(("http", parsed.netloc, "", "", "")))
        if parsed.scheme != "ws":
            raise ValueError("Expected a loopback WebSocket endpoint")
        self.socket = websocket.create_connection(url, timeout=timeout, suppress_origin=True)
        self.sequence = 0

    def call(self, method, params=None):
        self.sequence += 1
        self.socket.send(json.dumps({"id": self.sequence, "method": method, "params": params or {}}))
        while True:
            message = json.loads(self.socket.recv())
            if message.get("id") == self.sequence:
                if "error" in message:
                    raise RuntimeError("CDP command failed: " + method)
                return message.get("result", {})

    def close(self):
        self.socket.close()


def task_destination(task_id, name):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*", task_id):
        raise ValueError("Use a date-prefixed task slug")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,99}", name):
        raise ValueError("Use a short ASCII filename without path separators")
    if name.endswith(".") or name.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)], *[f"LPT{i}" for i in range(1, 10)]}:
        raise ValueError("Reserved Windows filename")
    workspace = pathlib.Path.cwd().resolve()
    task = (workspace / ".agents-work" / task_id).resolve()
    if not task.is_relative_to(workspace):
        raise ValueError("Task directory escapes the workspace")
    dest = (task / "downloads" / name).resolve()
    if not dest.is_relative_to(task):
        raise ValueError("Download directory escapes the task")
    if dest.exists():
        raise FileExistsError("Destination already exists; choose a new name or reuse the existing file")
    return task, dest


def file_checks(path, expected):
    data = path.read_bytes()
    pdf = data.startswith(b"%PDF-") and b"%%EOF" in data[-2048:]
    caj = data.startswith((b"KDH", b"CAJ", b"NH"))
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "format": "pdf" if pdf else "caj/kdh" if caj else "unrecognized",
            "format_verified": pdf if expected == "pdf" else caj,
            "content_parsed": False}


def download(base, target, args):
    task, dest = task_destination(args.task_id, args.name)
    if (args.format == "pdf" and dest.suffix.lower() != ".pdf") or (args.format == "caj" and dest.suffix.lower() != ".caj"):
        raise ValueError("Filename extension must match the requested format")
    dest.parent.mkdir(parents=True, exist_ok=True)
    browser = Connection(fetch_json(base, "/json/version")["webSocketDebuggerUrl"])
    page = None
    guid = None
    saved = None
    try:
        browser.call("Browser.setDownloadBehavior", {"behavior": "allowAndName", "downloadPath": str(dest.parent), "eventsEnabled": True})
        browser.call("Target.setDiscoverTargets", {"discover": True})
        page = Connection(target["webSocketDebuggerUrl"])
        frames = {target["id"]}
        def collect_frames(tree):
            frames.add(tree["frame"]["id"])
            for child in tree.get("childFrames", []):
                collect_frames(child)
        collect_frames(page.call("Page.getFrameTree")["frameTree"])
        selector = json.dumps(args.selector)
        link = page.call("Runtime.evaluate", {"expression": f"(()=>{{const e=document.querySelector({selector});return e ? (e.href || e.closest('a')?.href || location.href) : null;}})()", "returnByValue": True})["result"].get("value")
        if not link:
            raise RuntimeError("Download selector did not match an element")
        origins = {urllib.parse.urlsplit(value).netloc for value in (target["url"], link) if urllib.parse.urlsplit(value).scheme in ("http", "https")}
        action = page.call("Runtime.evaluate", {"expression": f"(()=>{{const e=document.querySelector({selector});if(!e)throw new Error('Selector not found');e.click();return true;}})()", "returnByValue": True, "userGesture": True})
        if action.get("exceptionDetails"):
            raise RuntimeError("Selected download element was not usable")
        deadline = time.monotonic() + args.timeout
        while time.monotonic() < deadline:
            browser.socket.settimeout(max(0.1, deadline - time.monotonic()))
            message = json.loads(browser.socket.recv())
            params = message.get("params", {})
            if message.get("method") == "Target.targetCreated":
                info = params.get("targetInfo", {})
                if info.get("openerId") in frames:
                    frames.add(info["targetId"])
            if message.get("method") == "Browser.downloadWillBegin":
                # target=_blank links can use noopener, so no openerId is exposed.
                # A dedicated browser with no concurrent downloads is required.
                event_url = params.get("url", "")
                if event_url.startswith("blob:"):
                    event_url = event_url[5:]
                event_origin = urllib.parse.urlsplit(event_url).netloc
                if params.get("frameId") not in frames and event_origin not in origins:
                    continue
                if guid:
                    raise RuntimeError("Action triggered multiple downloads; inspect browser state")
                guid = params["guid"]
                if not re.fullmatch(r"[A-Za-z0-9-]+", guid):
                    raise RuntimeError("Unexpected browser download identifier")
            if message.get("method") == "Browser.downloadProgress" and guid and params.get("guid") == guid:
                if params.get("state") == "canceled":
                    raise RuntimeError("Browser canceled the download")
                if params.get("state") == "completed":
                    received = params.get("receivedBytes")
                    staged = dest.parent / guid
                    if not staged.is_file():
                        raise RuntimeError("Completion event arrived but no file exists at the configured destination")
                    if dest.exists():
                        raise FileExistsError("Destination was created during the download; refusing overwrite")
                    staged.rename(dest)
                    saved = dest
                    checks = file_checks(dest, args.format)
                    if received is not None and checks["bytes"] != received:
                        checks["byte_count_matches"] = False
                    else:
                        checks["byte_count_matches"] = True
                    record = {"path": str(dest), "source": sanitize_url(target["url"]), "state": "completed", **checks}
                    index = task / "index.md"
                    if not index.exists():
                        index.write_text("# Task download verification\n", encoding="utf-8")
                    with index.open("a", encoding="utf-8") as handle:
                        handle.write(f"\n## Download {args.name}\n\nSource: {record['source']}\n\nFile: [downloads/{args.name}](downloads/{args.name})\n\n```json\n" + json.dumps(record, ensure_ascii=False, indent=2) + "\n```\n")
                    return record
        raise TimeoutError("No completed download within the configured timeout")
    finally:
        if guid and saved is None:
            try:
                browser.socket.settimeout(5)
                browser.call("Browser.cancelDownload", {"guid": guid})
            except Exception:
                pass
        if page:
            page.close()
        browser.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["list", "inspect", "download"])
    parser.add_argument("--endpoint", default="http://127.0.0.1:9222")
    parser.add_argument("--target")
    parser.add_argument("--selector")
    parser.add_argument("--task-id")
    parser.add_argument("--name")
    parser.add_argument("--format", choices=["pdf", "caj"], default="pdf")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    try:
        base = endpoint(args.endpoint)
        pages = [p for p in fetch_json(base, "/json/list") if p.get("type") == "page"]
        if args.command == "list":
            result = [{"id": p["id"], "title": p.get("title"), "url": sanitize_url(p.get("url", ""))} for p in pages]
        else:
            target = next((p for p in pages if p["id"] == args.target), None)
            if target is None:
                raise ValueError("Select a current page target ID")
            if args.command == "inspect":
                conn = Connection(target["webSocketDebuggerUrl"])
                try:
                    result = conn.call("Runtime.evaluate", {"expression": "document.body ? document.body.innerText.slice(0,12000) : ''", "returnByValue": True})["result"].get("value", "")
                finally:
                    conn.close()
            else:
                if not all([args.selector, args.task_id, args.name]) or not 1 <= args.timeout <= 120:
                    raise ValueError("Download requires selector, task ID, filename, and timeout from 1 to 120 seconds")
                result = download(base, target, args)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        if isinstance(result, dict) and result.get("format_verified") is False:
            return 2
        if isinstance(result, dict) and result.get("byte_count_matches") is False:
            return 2
        return 0
    except Exception as exc:
        # Error strings may contain authenticated URLs; emit only a safe category.
        safe = str(exc) if type(exc) in (RuntimeError, ValueError, FileExistsError, TimeoutError) else "Local operation failed; inspect browser state and local prerequisites without repeating blindly"
        print(json.dumps({"status": "failed", "error_category": type(exc).__name__, "message": safe}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
