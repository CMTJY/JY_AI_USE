#!/usr/bin/env python3
"""Behavior tests for bootstrap_memory; uses only temporary local projects.

Run: python -B -m unittest discover -s Skills/teampnew/scripts -p test_bootstrap_memory.py -v
"""

import importlib.util
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().with_name("bootstrap_memory.py")
SPEC = importlib.util.spec_from_file_location("bootstrap_memory_under_test", SCRIPT)
bootstrap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bootstrap)
SOURCE_SKILL = SCRIPT.parents[1]
DAY = "2026-10-15"


def snapshot(root):
    """Record temp-fixture entries and bytes without following directory links."""
    entries = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(directory) / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                entries[relative] = ("link", os.readlink(path))
            elif path.is_dir():
                entries[relative] = ("directory",)
            else:
                entries[relative] = ("file", path.read_bytes(), path.stat().st_mtime_ns)
    return entries


class BootstrapMemoryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="teampnew-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.project = self.root / "project"
        self.project.mkdir()
        self.skill = self.root / "skill"
        shutil.copytree(SOURCE_SKILL / "assets", self.skill / "assets")

    def install(self, **kwargs):
        return bootstrap.install(self.project, self.skill, DAY, **kwargs)

    def original_protocol(self):
        return (self.skill / "assets/wiki-memory-agent/template/AGENTS.md").read_bytes()

    def make_link(self, link, target, directory=False):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except OSError as error:
            if isinstance(error, PermissionError) or getattr(error, "winerror", None) == 1314:
                self.skipTest("Creating symlinks requires unavailable OS privileges")
            raise

    def test_fresh_install_preserves_complete_original_protocol_and_bundle(self):
        bundle_before = snapshot(self.skill / "assets/wiki-memory-agent")
        original = self.original_protocol()

        result = self.install()

        agent = (self.project / "AGENTS.md").read_bytes()
        self.assertTrue(agent.startswith(original))
        self.assertEqual(agent.count(original), 1)
        self.assertEqual(snapshot(self.skill / "assets/wiki-memory-agent"), bundle_before)
        self.assertTrue((self.project / "memory/INDEX.md").is_file())
        policy = (self.project / "memory/workflows/route-first.md").read_bytes()
        self.assertIn(DAY.encode("ascii"), policy)
        self.assertNotIn(b"{{DATE}}", policy)
        self.assertEqual(result["status"], "memory_scaffold_ready")
        self.assertEqual({item["action"] for item in result["files"]}, {"created"})

    def test_existing_agent_case_variants_keep_name_and_original_bytes(self):
        for number, name in enumerate(("agents.md", "AgEnTs.Md", "AGENTS.md")):
            with self.subTest(name=name):
                project = self.root / f"case-{number}"
                project.mkdir()
                old = b"\xef\xbb\xbf# Existing user rules\r\n" + "保留用户规则。\r\n".encode("utf-8")
                (project / name).write_bytes(old)

                bootstrap.install(project, self.skill, DAY)

                matches = [path for path in project.iterdir() if path.name.casefold() == "agents.md"]
                self.assertEqual([path.name for path in matches], [name])
                current = matches[0].read_bytes()
                self.assertTrue(current.startswith(old))
                self.assertIn(self.original_protocol(), current)

    def test_existing_index_and_memory_contents_are_preserved(self):
        index = self.project / "memory/INDEX.md"
        index.parent.mkdir()
        old_index = b"\xef\xbb\xbf# Existing index\r\n\r\n[Existing](projects/existing.md)\r\n"
        index.write_bytes(old_index)
        existing = self.project / "memory/projects/existing.md"
        existing.parent.mkdir()
        old_memory = "# 已有记忆\n飞书链接和用户项目知识。\n".encode("utf-8")
        existing.write_bytes(old_memory)
        policy = self.project / "memory/workflows/route-first.md"
        policy.parent.mkdir()
        old_policy = b"# Existing project-specific routing policy\r\n"
        policy.write_bytes(old_policy)

        self.install()

        self.assertTrue(index.read_bytes().startswith(old_index))
        self.assertEqual(existing.read_bytes(), old_memory)
        self.assertEqual(policy.read_bytes(), old_policy)
        self.assertIn(b"(workflows/route-first.md)", index.read_bytes())

    def test_existing_complete_original_protocol_is_not_duplicated(self):
        original = self.original_protocol()
        old = b"# User heading\n\n" + original + b"\n# User footer\n"
        (self.project / "AGENTS.md").write_bytes(old)

        self.install()

        current = (self.project / "AGENTS.md").read_bytes()
        self.assertTrue(current.startswith(old))
        self.assertEqual(current.count(original), 1)

    def test_repeated_install_changes_neither_bytes_nor_timestamps(self):
        self.install()
        before = snapshot(self.project)

        result = bootstrap.install(self.project, self.skill, "2026-10-16")

        self.assertEqual(snapshot(self.project), before)
        self.assertEqual({item["action"] for item in result["files"]}, {"preserved"})

    def test_dry_run_empty_project_creates_no_entries(self):
        before = snapshot(self.project)

        result = self.install(dry_run=True)

        self.assertEqual(snapshot(self.project), before)
        self.assertEqual(result["status"], "dry_run")
        self.assertEqual({item["action"] for item in result["files"]}, {"created"})

    def test_dry_run_existing_project_changes_nothing(self):
        (self.project / "agents.md").write_bytes(b"# Existing\r\n")
        (self.project / "memory").mkdir()
        (self.project / "memory/INDEX.md").write_bytes(b"# Existing index\n")
        before = snapshot(self.project)

        result = self.install(dry_run=True)

        self.assertEqual(snapshot(self.project), before)
        self.assertEqual(result["status"], "dry_run")

    def test_corrupt_bundle_is_rejected_without_project_writes(self):
        for corruption in ("changed", "missing", "extra", "invalid_manifest"):
            with self.subTest(corruption=corruption):
                skill = self.root / ("corrupt-" + corruption)
                shutil.copytree(self.skill, skill)
                original = skill / "assets/wiki-memory-agent/template/AGENTS.md"
                if corruption == "changed":
                    original.write_bytes(original.read_bytes() + b"\ncorruption\n")
                elif corruption == "missing":
                    original.unlink()
                elif corruption == "extra":
                    (skill / "assets/wiki-memory-agent/unexpected.txt").write_bytes(b"extra")
                else:
                    (skill / "assets/wiki-memory-agent.manifest.json").write_text("{", encoding="utf-8")
                (self.project / "agents.md").write_bytes(b"# Existing user instructions\n")
                before = snapshot(self.project)

                with self.assertRaises((ValueError, OSError, KeyError)):
                    bootstrap.install(self.project, skill, DAY)

                self.assertEqual(snapshot(self.project), before)

    def test_directory_symlink_escape_is_rejected_without_any_writes(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "existing.md").write_bytes(b"Do not change\n")
        self.make_link(self.project / "memory", outside, directory=True)
        project_before = snapshot(self.project)
        outside_before = snapshot(outside)

        with self.assertRaises(ValueError):
            self.install()

        self.assertEqual(snapshot(self.project), project_before)
        self.assertEqual(snapshot(outside), outside_before)

    def test_agent_symlink_escape_is_rejected_without_any_writes(self):
        outside = self.root / "outside-AGENTS.md"
        outside.write_bytes(b"# External instructions\n")
        self.make_link(self.project / "agents.md", outside)
        before = snapshot(self.project)
        outside_bytes = outside.read_bytes()

        with self.assertRaises(ValueError):
            self.install()

        self.assertEqual(snapshot(self.project), before)
        self.assertEqual(outside.read_bytes(), outside_bytes)

    def test_bundled_symlink_is_rejected_without_project_writes(self):
        bundled = self.skill / "assets/wiki-memory-agent/template/AGENTS.md"
        outside = self.root / "external-template.md"
        outside.write_bytes(bundled.read_bytes())
        bundled.unlink()
        self.make_link(bundled, outside)
        before = snapshot(self.project)

        with self.assertRaises(ValueError):
            self.install()

        self.assertEqual(snapshot(self.project), before)

    def test_skill_nested_inside_target_project_is_supported(self):
        nested_skill = self.project / "Skills/teampnew"
        shutil.copytree(self.skill, nested_skill)
        skill_before = snapshot(nested_skill)

        result = bootstrap.install(self.project, nested_skill, DAY)

        self.assertEqual(result["status"], "memory_scaffold_ready")
        self.assertIn(self.original_protocol(), (self.project / "AGENTS.md").read_bytes())
        self.assertEqual(snapshot(nested_skill), skill_before)

    def test_target_inside_skill_package_is_rejected_without_writes(self):
        project = self.skill / "nested-project"
        project.mkdir()
        before = snapshot(self.skill)

        with self.assertRaises(ValueError):
            bootstrap.install(project, self.skill, DAY)

        self.assertEqual(snapshot(self.skill), before)

    def test_invalid_date_is_rejected_before_project_writes(self):
        before = snapshot(self.project)

        with self.assertRaises(ValueError):
            bootstrap.install(self.project, self.skill, "2026-02-30")

        self.assertEqual(snapshot(self.project), before)


if __name__ == "__main__":
    unittest.main()
