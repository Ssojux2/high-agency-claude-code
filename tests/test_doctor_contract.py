import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCTOR = ROOT / "plugins/high-agency/skills/high-agency-doctor/SKILL.md"
COMMAND = ROOT / "plugins/high-agency/commands/doctor.md"
ROUTING = ROOT / "plugins/high-agency/skills/high-agency-coding/references/model-routing.md"
MANIFEST = ROOT / "plugins/high-agency/.claude-plugin/plugin.json"


class ClaudeDoctorContractTests(unittest.TestCase):
    def test_doctor_is_read_only_and_safe(self):
        text = DOCTOR.read_text(encoding="utf-8")
        self.assertIn("Do not run model probes unless the user explicitly asks", text)
        self.assertIn("Do **not** print full settings", text)
        self.assertIn("UNVERIFIED", text)

    def test_doctor_detects_model_force_and_agent_teams(self):
        text = DOCTOR.read_text(encoding="utf-8")
        self.assertIn("CLAUDE_CODE_SUBAGENT_MODEL_FORCE", text)
        self.assertIn("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS", text)

    def test_slash_command_is_cheap(self):
        text = COMMAND.read_text(encoding="utf-8")
        self.assertRegex(text, r"model:\s*haiku")
        self.assertRegex(text, r"effort:\s*low")
        self.assertIn("CLAUDE_CODE_SUBAGENT_MODEL_FORCE", text)
        self.assertIn("--probe-models", text)
        self.assertIn("Task", text)
        self.assertIn("Do not modify project files or settings", text)

    def test_explicit_fallbacks_exist(self):
        text = ROUTING.read_text(encoding="utf-8")
        self.assertIn("Explicit fallback chains", text)
        for model in ("Haiku", "Sonnet", "Opus", "Fable", "current main model"):
            self.assertIn(model, text)

    def test_manifest_uses_standard_component_discovery(self):
        text = MANIFEST.read_text(encoding="utf-8")
        self.assertNotIn('"commands"', text)
        self.assertNotIn('"agents"', text)


if __name__ == "__main__":
    unittest.main()
