"""Offline regression checks; does not open a browser or download from a site."""
import json
import os
import pathlib
import tempfile
import types
import unittest
from unittest import mock

import edge_cdp as helper


class HelperTests(unittest.TestCase):
    def test_loopback_and_redaction(self):
        for url in ["https://127.0.0.1:9222", "http://example.com:9222", "http://user:password@127.0.0.1:9222", "http://127.0.0.1:9222/path"]:
            with self.assertRaises(ValueError):
                helper.endpoint(url)
        self.assertEqual(helper.endpoint("http://[::1]:9222"), "http://[::1]:9222")
        self.assertEqual(helper.sanitize_url("https://user:password@example.com/page?token=secret#private"), "https://example.com/page")

    def test_destination_guards(self):
        with self.assertRaises(ValueError):
            helper.task_destination("../escape", "paper.pdf")
        for name in ["../escape.pdf", "CON.pdf", "file.", "sub/file.pdf"]:
            with self.assertRaises(ValueError):
                helper.task_destination("2026-10-12-test", name)

    def exercise_download(self, canceled=False):
        previous = pathlib.Path.cwd()
        with tempfile.TemporaryDirectory(prefix="cdp-offline-") as folder:
            workspace = pathlib.Path(folder).resolve()
            os.chdir(workspace)
            try:
                args = types.SimpleNamespace(task_id="2026-10-12-test", name="paper.pdf", selector="a.download", format="pdf", timeout=10)
                task, dest = helper.task_destination(args.task_id, args.name)
                pdf = b"%PDF-1.4\nfixture, format checks only\n%%EOF\n"
                guid = "test-download-guid"
                calls = []
                events = [
                    {"method": "Browser.downloadWillBegin", "params": {"frameId": "unrelated", "url": "https://foreign.example/file", "guid": "other-download"}},
                    # No openerId: modern target=_blank links can use noopener.
                    {"method": "Target.targetCreated", "params": {"targetInfo": {"targetId": "popup"}}},
                    {"method": "Browser.downloadWillBegin", "params": {"frameId": "popup", "url": "https://files.example/redirect?token=secret", "guid": guid}},
                    {"method": "Browser.downloadProgress", "params": {"guid": guid, "state": "canceled" if canceled else "completed", "receivedBytes": len(pdf)}},
                ]

                class FakeConnection:
                    def __init__(self, url):
                        self.closed = False
                        self.socket = self

                    def call(self, method, params=None):
                        calls.append(method)
                        if method == "Browser.setDownloadBehavior":
                            self.output = pathlib.Path(params["downloadPath"])
                        if method == "Page.getFrameTree":
                            return {"frameTree": {"frame": {"id": "source"}}}
                        if method == "Runtime.evaluate":
                            return {"result": {"value": "https://files.example/start?token=secret" if "e.href" in params["expression"] else True}}
                        return {}

                    def recv(self):
                        if self.closed:
                            raise AssertionError("Browser session closed before completion")
                        event = events.pop(0)
                        if event["method"] == "Browser.downloadProgress" and not canceled:
                            (self.output / guid).write_bytes(pdf)
                        return json.dumps(event)

                    def settimeout(self, value):
                        pass

                    def close(self):
                        self.closed = True

                target = {"id": "source", "url": "https://site.example/article?token=secret", "webSocketDebuggerUrl": "ws://127.0.0.1:9222/page"}
                with mock.patch.object(helper, "Connection", FakeConnection), mock.patch.object(helper, "fetch_json", return_value={"webSocketDebuggerUrl": "ws://127.0.0.1:9222/browser"}):
                    if canceled:
                        with self.assertRaisesRegex(RuntimeError, "canceled"):
                            helper.download("http://127.0.0.1:9222", target, args)
                        self.assertFalse(dest.exists())
                        self.assertFalse((task / "index.md").exists())
                        self.assertIn("Browser.cancelDownload", calls)
                    else:
                        record = helper.download("http://127.0.0.1:9222", target, args)
                        self.assertEqual(dest.read_bytes(), pdf)
                        self.assertTrue(record["format_verified"])
                        self.assertTrue(record["byte_count_matches"])
                        self.assertFalse(record["content_parsed"])
                        self.assertNotIn("secret", (task / "index.md").read_text(encoding="utf-8"))
                        with self.assertRaises(FileExistsError):
                            helper.download("http://127.0.0.1:9222", target, args)
                        self.assertEqual(dest.read_bytes(), pdf)
                bad = workspace / "login.pdf"
                bad.write_bytes(b"<html>login required</html>")
                self.assertFalse(helper.file_checks(bad, "pdf")["format_verified"])
                self.assertTrue(workspace.is_relative_to(pathlib.Path(tempfile.gettempdir()).resolve()))
            finally:
                os.chdir(previous)

    def test_download_completion_and_overwrite(self):
        self.exercise_download()

    def test_canceled_download_is_not_success(self):
        self.exercise_download(canceled=True)


if __name__ == "__main__":
    unittest.main()
