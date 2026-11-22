"""Regression tests for lib.url_parser and lib.youtube_client._extract_video_id."""
from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _ensure_lib_modules():
    try:
        from lib import url_parser, youtube_client  # type: ignore
        return url_parser, youtube_client
    except Exception:
        fake_requests = SimpleNamespace(
            RequestException=Exception,
            Session=object,
            get=None,
            put=None,
            Response=object,
        )
        sys.modules["requests"] = fake_requests  # type: ignore[assignment]
        lib_pkg = types.ModuleType("lib")
        lib_pkg.__path__ = [str(ROOT / "lib")]
        sys.modules["lib"] = lib_pkg

        def load_mod(mod_name: str):
            spec = importlib.util.spec_from_file_location(mod_name, ROOT / "lib" / f"{mod_name.split('.')[-1]}.py")
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load {mod_name}")
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        load_mod("lib._env")
        up = load_mod("lib.url_parser")
        yc = load_mod("lib.youtube_client")
        return up, yc


url_parser, youtube_client = _ensure_lib_modules()
parse_youtube_url = url_parser.parse_youtube_url


class TestUrlParserAndClient(unittest.TestCase):
    def test_preserves_legacy_user_canonical_url(self):
        parsed = parse_youtube_url("https://www.youtube.com/user/GoogleDevelopers")
        self.assertEqual(parsed["url_type"], "channel")
        self.assertEqual(parsed["handle"], "GoogleDevelopers")
        self.assertEqual(parsed["canonical_url"], "https://www.youtube.com/user/GoogleDevelopers")

    def test_preserves_c_canonical_url(self):
        parsed = parse_youtube_url("https://www.youtube.com/c/CreatorStudio")
        self.assertEqual(parsed["canonical_url"], "https://www.youtube.com/c/CreatorStudio")

    def test_unicode_arabic_handle(self):
        parsed = parse_youtube_url("https://www.youtube.com/@محمد_لبد")
        self.assertEqual(parsed["url_type"], "channel")
        self.assertEqual(parsed["handle"], "محمد_لبد")
        self.assertEqual(parsed["canonical_url"], "https://www.youtube.com/@محمد_لبد")

    def test_extract_video_id_all_url_shapes(self):
        expected = "dQw4w9WgXcQ"
        cases = [
            f"https://www.youtube.com/watch?v={expected}&t=42s",
            f"https://m.youtube.com/watch?app=desktop&v={expected}",
            f"https://www.youtube.com/watch?v={expected}#t=10",
            f"https://youtu.be/{expected}?si=abc",
            f"https://www.youtube.com/shorts/{expected}",
            f"https://www.youtube.com/live/{expected}?feature=share",
            f"https://www.youtube.com/embed/{expected}",
            expected,
        ]
        for url in cases:
            with self.subTest(url=url):
                self.assertEqual(youtube_client._extract_video_id(url), expected)


if __name__ == "__main__":
    unittest.main()
