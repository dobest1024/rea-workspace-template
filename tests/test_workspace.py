import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts import workspace


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "analysis"
        for name in ("target", "work", "notes"):
            (self.root / name).mkdir(parents=True)
        self.source = self.base / "sample.bin"
        self.source.write_bytes(b"original bytes")

    def run_import(self):
        with contextlib.redirect_stdout(io.StringIO()):
            workspace.import_target(self.root, self.source)

    def test_import_stage_and_verify(self):
        self.run_import()
        with contextlib.redirect_stdout(io.StringIO()):
            workspace.stage(self.root)
            workspace.verify(self.root)
        original = self.root / "target/sample.bin"
        copy = self.root / "work/input/sample.bin"
        copy.write_bytes(b"renamed analysis")
        self.assertEqual(original.read_bytes(), b"original bytes")
        self.assertEqual(original.stat().st_mode & 0o777, 0o444)
        with self.assertRaises(ValueError):
            workspace.stage(self.root)

    def test_reimport_refuses_to_replace_evidence(self):
        self.run_import()
        self.source.write_bytes(b"replacement")
        with self.assertRaises(ValueError):
            workspace.import_target(self.root, self.source)
        self.assertEqual((self.root / "target/sample.bin").read_bytes(), b"original bytes")

    def test_detects_changed_file(self):
        self.run_import()
        original = self.root / "target/sample.bin"
        original.chmod(0o600)
        original.write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError, "变化"):
            workspace.verify(self.root)

    def test_detects_added_and_missing_files(self):
        self.run_import()
        (self.root / "target/sample.bin").unlink()
        (self.root / "target/extra").write_text("extra")
        with self.assertRaises(ValueError) as caught:
            workspace.verify(self.root)
        self.assertIn("新增", str(caught.exception))
        self.assertIn("丢失", str(caught.exception))

    def test_no_baseline_is_not_a_pass(self):
        with self.assertRaisesRegex(ValueError, "基线"):
            workspace.verify(self.root)

    def test_rejects_nested_symlinks_before_copy(self):
        directory = self.base / "repo"
        directory.mkdir()
        (directory / "linked").symlink_to(self.source)
        with self.assertRaisesRegex(ValueError, "软链接"):
            workspace.import_target(self.root, directory)
        self.assertEqual(list((self.root / "target").iterdir()), [])

    def test_directory_inventory_includes_hidden_files(self):
        directory = self.base / "repo"
        directory.mkdir()
        (directory / ".hidden").write_text("hidden")
        (directory / "nested").mkdir()
        (directory / "nested/a.txt").write_text("nested")
        (directory / "nested/.gitkeep").write_text("sample content")
        workspace.import_target(self.root, directory)
        manifest = json.loads((self.root / "notes/target-manifest.json").read_text())
        self.assertEqual(set(manifest["files"]), {"repo/.hidden", "repo/nested/a.txt", "repo/nested/.gitkeep"})
        workspace.stage(self.root)
        self.assertEqual((self.root / "work/input/repo/nested/.gitkeep").read_text(), "sample content")

    def test_new_workspace_has_clean_templates_and_no_sample(self):
        destination = self.base / "new project"
        workspace.new_workspace(destination)
        self.assertTrue((destination / ".codex/config.toml").is_file())
        self.assertTrue((destination / "scripts/sanitize_har.py").is_file())
        self.assertFalse((destination / "notes/target-manifest.json").exists())
        self.assertEqual([p.name for p in (destination / "target").iterdir()], [".gitkeep"])
        self.assertIn("尚未导入目标", (destination / "notes/HANDOFF.md").read_text())
        with self.assertRaises(ValueError):
            workspace.new_workspace(destination)


if __name__ == "__main__":
    unittest.main()
