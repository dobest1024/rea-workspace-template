import json
import tempfile
import unittest
from pathlib import Path

from scripts.sanitize_har import sanitize, write_sanitized


def sample_har():
    return {"log": {"entries": [{
        "request": {
            "method": "POST",
            "url": "https://user:URL_SECRET@example.com/api/search?token=QUERY_SECRET#FRAGMENT_SECRET",
            "headers": [{"name": "Authorization", "value": "Bearer HEADER_SECRET"},
                        {"name": "Cookie", "value": "sid=COOKIE_SECRET"}],
            "cookies": [{"name": "sid", "value": "COOKIE_SECRET"}],
            "queryString": [],
            "postData": {"mimeType": "application/json", "text": json.dumps({
                "password": "BODY_SECRET", "count": 42, "ok": True,
                "items": [{"email": "PRIVATE_EMAIL", "empty": None}],
            })},
        },
        "response": {
            "status": 200, "statusText": "STATUS_SECRET",
            "headers": [{"name": "Set-Cookie", "value": "RESPONSE_SECRET"}],
            "redirectURL": "https://example.com/REDIRECT_SECRET",
            "content": {"mimeType": "text/html", "text": "OPAQUE_SECRET"},
        },
        "_webSocketMessages": [{"data": "WEBSOCKET_SECRET"}],
        "comment": "COMMENT_SECRET",
    }], "pages": [{"title": "PAGE_SECRET"}]}}


class HarTests(unittest.TestCase):
    def test_removes_values_and_unknown_extensions(self):
        cleaned = sanitize(sample_har())
        serialized = json.dumps(cleaned)
        self.assertNotIn("SECRET", serialized)
        self.assertNotIn("PRIVATE_EMAIL", serialized)
        entry = cleaned["log"]["entries"][0]
        self.assertEqual(entry["request"]["url"], "https://example.com/api/search")
        self.assertEqual(entry["request"]["queryString"], [{"name": "token", "value": "[REDACTED]"}])
        self.assertEqual(entry["response"]["status"], 200)
        body = json.loads(entry["request"]["postData"]["text"])
        self.assertEqual(body["count"], 0)
        self.assertIs(body["ok"], False)
        self.assertIsNone(body["items"][0]["empty"])

    def test_encoded_bodies_and_form_file_names_are_removed(self):
        source = sample_har()
        entry = source["log"]["entries"][0]
        entry["response"]["content"] = {"mimeType": "application/json", "encoding": "base64", "text": "BASE64_SECRET"}
        entry["request"]["postData"] = {"mimeType": "multipart/form-data; boundary=BOUNDARY_SECRET",
            "params": [{"name": "upload", "value": "FORM_SECRET", "fileName": "FILE_SECRET"}]}
        self.assertNotIn("SECRET", json.dumps(sanitize(source)))

    def test_preserves_source_refuses_overwrite_and_private_permissions(self):
        with tempfile.TemporaryDirectory() as directory:
            source, destination = Path(directory) / "raw.har", Path(directory) / "clean.har"
            source.write_text(json.dumps(sample_har()))
            before = source.read_bytes()
            write_sanitized(source, destination)
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(destination.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(FileExistsError):
                write_sanitized(source, destination)
            with self.assertRaises(FileExistsError):
                write_sanitized(source, source)

    def test_refuses_empty_or_invalid_capture(self):
        with self.assertRaises(ValueError):
            sanitize({"log": {"entries": []}})
        source = sample_har()
        source["log"]["entries"][0]["request"]["url"] = "file:///private/data"
        with self.assertRaises(ValueError):
            sanitize(source)


if __name__ == "__main__":
    unittest.main()
