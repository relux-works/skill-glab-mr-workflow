from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import setup_support as ss


class SetupSupportTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)

    def make_source_skill_dir(self) -> Path:
        skill_dir = self.root / "source" / "skill-glab-mr-workflow"
        (skill_dir / "agents").mkdir(parents=True, exist_ok=True)
        (skill_dir / "locales").mkdir(parents=True, exist_ok=True)
        (skill_dir / "scripts").mkdir(parents=True, exist_ok=True)
        (skill_dir / ".git").mkdir(parents=True, exist_ok=True)
        (skill_dir / ".venv").mkdir(parents=True, exist_ok=True)
        (skill_dir / "__pycache__").mkdir(parents=True, exist_ok=True)
        (skill_dir / "tests").mkdir(parents=True, exist_ok=True)

        (skill_dir / "README.md").write_text("readme\n", encoding="utf-8")
        (skill_dir / "dependencies.json").write_text(
            json.dumps(
                {
                    "supported_platforms": ["darwin"],
                    "dependencies": [
                        {"command": "glab", "install": "brew install glab"},
                        {"command": "direnv", "install": "brew install direnv"},
                    ]
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (skill_dir / "Makefile").write_text(".PHONY: skill\nskill:\n\t@true\n", encoding="utf-8")
        (skill_dir / "agents" / "runtime.json").write_text(
            '{"commands": {"gmr": "scripts/gmr"}}\n',
            encoding="utf-8",
        )
        (skill_dir / "SKILL.md").write_text(
            "---\n"
            "name: skill-glab-mr-workflow\n"
            "description: >\n"
            "  English source description\n"
            "  on multiple lines\n"
            "triggers:\n"
            '  - "my open merge requests"\n'
            '  - "gitlab mr status"\n'
            "---\n\n"
            "# Sample Skill\n",
            encoding="utf-8",
        )
        (skill_dir / "agents" / "openai.yaml").write_text(
            'interface:\n'
            '  display_name: "GitLab MR Workflow"\n'
            '  short_description: "English Short"\n'
            '  default_prompt: "Use $skill-glab-mr-workflow in English."\n',
            encoding="utf-8",
        )
        (skill_dir / "locales" / "metadata.json").write_text(
            json.dumps(
                {
                    "locales": {
                        "en": {
                            "description": "English localized description",
                            "display_name": "GitLab MR Workflow",
                            "short_description": "English Short",
                            "default_prompt": "Use $skill-glab-mr-workflow in English.",
                            "local_prefix": "[local] ",
                        },
                        "ru": {
                            "description": "Русское описание",
                            "display_name": "GitLab MR Workflow",
                            "short_description": "Русский Short",
                            "default_prompt": "Используй $skill-glab-mr-workflow по-русски.",
                            "local_prefix": "[локально] ",
                        },
                    }
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (skill_dir / ".skill_triggers").mkdir(parents=True, exist_ok=True)
        (skill_dir / ".skill_triggers" / "en.md").write_text(
            "- my open merge requests\n- merge requests assigned to me\n- my review queue\n- review this mr\n- create merge request\n- gitlab mr status\n- approve this mr\n",
            encoding="utf-8",
        )
        (skill_dir / ".skill_triggers" / "ru.md").write_text(
            "- мои открытые mr\n- что назначено мне\n- что у меня на ревью\n- проверь этот mr\n- создай merge request\n- статус mr\n- апрувни mr\n",
            encoding="utf-8",
        )
        (skill_dir / ".git" / "config").write_text("", encoding="utf-8")
        (skill_dir / ".venv" / "marker").write_text("", encoding="utf-8")
        (skill_dir / "__pycache__" / "cache.pyc").write_text("", encoding="utf-8")
        (skill_dir / "tests" / "test_dummy.py").write_text("pass\n", encoding="utf-8")
        return skill_dir

    def test_render_skill_metadata_dual_mode_merges_trigger_lists(self) -> None:
        skill_dir = self.make_source_skill_dir()

        ss.render_skill_metadata(skill_dir, "ru-en", "local")

        skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        openai_yaml = (skill_dir / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertIn('description: "Русское описание Триггеры: \\"мои открытые mr\\", \\"что назначено мне\\", \\"что у меня на ревью\\", \\"проверь этот mr\\", \\"создай merge request\\", \\"статус mr\\". / English localized description Triggers: \\"my open merge requests\\", \\"merge requests assigned to me\\", \\"my review queue\\", \\"review this mr\\", \\"create merge request\\", \\"gitlab mr status\\"."', skill_text)
        self.assertIn('  - "мои открытые mr"\n', skill_text)
        self.assertIn('  - "статус mr"\n', skill_text)
        self.assertIn('  - "my open merge requests"\n', skill_text)
        self.assertIn('  - "merge requests assigned to me"\n', skill_text)
        self.assertIn('display_name: "[локально] GitLab MR Workflow"', openai_yaml)
        self.assertIn('short_description: "[локально] Русский Short"', openai_yaml)

    def test_perform_local_install_requires_locale_for_first_install(self) -> None:
        source_dir = self.make_source_skill_dir()
        repo_root = self.root / "repo"
        repo_root.mkdir(parents=True, exist_ok=True)

        with mock.patch.object(ss, "resolve_repo_root", return_value=repo_root.resolve()):
            with self.assertRaises(ss.SetupError) as exc:
                ss.perform_install(
                    source_dir=source_dir,
                    install_mode="local",
                    requested_locale=None,
                    repo_root=repo_root,
                )

        self.assertIn("First local install requires --locale", str(exc.exception))

    def test_perform_local_install_uses_project_fixed_locale(self) -> None:
        source_dir = self.make_source_skill_dir()
        repo_root = self.root / "repo"
        repo_root.mkdir(parents=True, exist_ok=True)

        with mock.patch.object(ss, "resolve_repo_root", return_value=repo_root.resolve()):
            first_result = ss.perform_install(
                source_dir=source_dir,
                install_mode="local",
                requested_locale="ru",
                repo_root=repo_root,
            )

            with self.assertRaises(ss.SetupError) as exc:
                ss.perform_install(
                    source_dir=source_dir,
                    install_mode="local",
                    requested_locale="en",
                    repo_root=repo_root,
                )

        self.assertEqual(
            first_result.runtime_dir.resolve(),
            (repo_root / ".agents" / "skills" / "skill-glab-mr-workflow").resolve(),
        )
        self.assertIn("project-fixed", str(exc.exception))
        self.assertFalse((repo_root / ".claude" / "skills" / "skill-glab-mr-workflow").exists())
        self.assertFalse((repo_root / ".codex" / "skills" / "skill-glab-mr-workflow").exists())

    def test_perform_local_install_creates_committed_safe_runtime_copy(self) -> None:
        source_dir = self.make_source_skill_dir()
        repo_root = self.root / "repo"
        repo_root.mkdir(parents=True, exist_ok=True)

        with mock.patch.object(ss, "resolve_repo_root", return_value=repo_root.resolve()), mock.patch.object(
            ss.shutil,
            "which",
            return_value="/opt/homebrew/bin/present",
        ):
            result = ss.perform_install(
                source_dir=source_dir,
                install_mode="local",
                requested_locale="ru",
                repo_root=repo_root,
            )

        self.assertTrue((result.runtime_dir / "Makefile").exists())
        self.assertTrue((result.runtime_dir / "agents" / "runtime.json").exists())
        self.assertFalse((result.runtime_dir / "README.md").exists())
        self.assertFalse((result.runtime_dir / "locales" / "metadata.json").exists())
        self.assertFalse((result.runtime_dir / "scripts" / "setup_main.py").exists())
        self.assertFalse((result.runtime_dir / "scripts" / "setup_support.py").exists())
        self.assertFalse((result.runtime_dir / "tests").exists())
        self.assertTrue((result.runtime_dir / ".skill_triggers" / "en.md").exists())
        self.assertTrue((result.runtime_dir / ".skill_triggers" / "ru.md").exists())
        manifest = json.loads((result.runtime_dir / ss.MANIFEST_FILENAME).read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], 2)
        self.assertNotIn("source_dir", manifest)
        self.assertNotIn("runtime_dir", manifest)

    def test_perform_local_install_fails_when_declared_dependencies_are_missing(self) -> None:
        source_dir = self.make_source_skill_dir()
        repo_root = self.root / "repo"
        repo_root.mkdir(parents=True, exist_ok=True)

        def fake_which(command: str) -> str | None:
            if command == "glab":
                return None
            if command == "direnv":
                return "/opt/homebrew/bin/direnv"
            return None

        with mock.patch.object(ss, "resolve_repo_root", return_value=repo_root.resolve()), mock.patch.object(
            ss.shutil,
            "which",
            side_effect=fake_which,
        ):
            with self.assertRaises(ss.SetupError) as exc:
                ss.perform_install(
                    source_dir=source_dir,
                    install_mode="local",
                    requested_locale="ru",
                    repo_root=repo_root,
                )

        self.assertIn("dependencies.json", str(exc.exception))
        self.assertIn("glab", str(exc.exception))
        self.assertIn("brew install glab", str(exc.exception))
        self.assertFalse((repo_root / ".agents" / "skills" / "skill-glab-mr-workflow").exists())

    def test_perform_local_install_fails_on_unsupported_platform(self) -> None:
        source_dir = self.make_source_skill_dir()
        repo_root = self.root / "repo"
        repo_root.mkdir(parents=True, exist_ok=True)

        with mock.patch.object(ss, "resolve_repo_root", return_value=repo_root.resolve()), mock.patch.object(
            ss.platform,
            "system",
            return_value="Linux",
        ), mock.patch.object(
            ss.shutil,
            "which",
            return_value="/opt/homebrew/bin/present",
        ):
            with self.assertRaises(ss.SetupError) as exc:
                ss.perform_install(
                    source_dir=source_dir,
                    install_mode="local",
                    requested_locale="ru",
                    repo_root=repo_root,
                )

        self.assertIn("linux", str(exc.exception).lower())
        self.assertIn("dependencies.json", str(exc.exception))
        self.assertFalse((repo_root / ".agents" / "skills" / "skill-glab-mr-workflow").exists())

    def test_render_skill_metadata_uses_markdown_triggers_as_single_source(self) -> None:
        source_dir = self.make_source_skill_dir()

        ss.render_skill_metadata(source_dir, "en", "local")

        skill_text = (source_dir / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn('  - "my open merge requests"', skill_text)
        self.assertIn('  - "gitlab mr status"', skill_text)
        self.assertIn('description: "English localized description Triggers: \\"my open merge requests\\", \\"merge requests assigned to me\\", \\"my review queue\\", \\"review this mr\\", \\"create merge request\\", \\"gitlab mr status\\"."', skill_text)
        self.assertNotIn('[local] English localized description', skill_text)

    def test_load_metadata_catalog_rejects_trigger_lists_in_metadata_json(self) -> None:
        source_dir = self.make_source_skill_dir()
        metadata_path = source_dir / "locales" / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["locales"]["en"]["triggers"] = ["legacy trigger"]
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        with self.assertRaises(ss.SetupError) as exc:
            ss.load_metadata_catalog(source_dir)

        self.assertIn("must define triggers only in", str(exc.exception))

    def test_resolve_source_dir_prefers_manifest_source_dir(self) -> None:
        source_dir = self.make_source_skill_dir().resolve()
        installed_dir = self.root / "installed" / "skill-glab-mr-workflow"
        installed_dir.mkdir(parents=True, exist_ok=True)
        ss.write_install_manifest(
            skill_dir=installed_dir,
            skill_name="skill-glab-mr-workflow",
            install_mode="local",
            locale_mode="en",
            source_dir=source_dir,
        )

        self.assertEqual(ss.resolve_source_dir(installed_dir), source_dir)


if __name__ == "__main__":
    unittest.main()
