import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/high-agency"
SKILL = PLUGIN / "skills/high-agency-coding/SKILL.md"
ROUTING = PLUGIN / "skills/high-agency-coding/references/model-routing.md"
DOCTOR = PLUGIN / "skills/high-agency-doctor/SKILL.md"


class ModelFreshnessTests(unittest.TestCase):
    def test_non_direct_preflight_requires_current_catalog(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("Before a non-DIRECT preflight", text)
        self.assertIn("current runtime catalog", text)
        self.assertIn("Refresh once per task", text)
        self.assertIn("DIRECT tasks do not need a model lookup", text)

    def test_exact_id_overrides_alias_when_supported(self):
        skill = SKILL.read_text(encoding="utf-8")
        routing = ROUTING.read_text(encoding="utf-8")
        self.assertIn("per-invocation `model` parameter", skill)
        self.assertIn("same-family inheritance", routing)
        self.assertIn("exact current catalog ID", routing)
        self.assertIn("Keep the role's tool restrictions", routing)

    def test_alias_only_schema_does_not_accept_arbitrary_model_ids(self):
        for path in (SKILL, ROUTING, DOCTOR):
            text = path.read_text(encoding="utf-8")
            self.assertIn("alias-only", text)
            self.assertIn("schema", text)
        self.assertIn("exact model ID only when the schema allows it", ROUTING.read_text(encoding="utf-8"))

    def test_missing_inventory_is_not_claimed_as_latest(self):
        text = ROUTING.read_text(encoding="utf-8")
        self.assertIn("latest availability unverified", text)
        self.assertIn("do not prove access", text)
        self.assertIn("cannot guarantee the globally newest release", text)

    def test_pins_and_force_are_respected(self):
        for path in (ROUTING, DOCTOR):
            text = path.read_text(encoding="utf-8")
            for family in ("HAIKU", "SONNET", "OPUS", "FABLE"):
                self.assertIn("ANTHROPIC_DEFAULT_" + family + "_MODEL", text)
            self.assertIn("CLAUDE_CODE_SUBAGENT_MODEL_FORCE", text)
            self.assertIn("availableModels", text)
            self.assertIn("main model", text)

    def test_no_versioned_routing_pins(self):
        for path in (SKILL, ROUTING):
            self.assertNotRegex(path.read_text(encoding="utf-8"), r"claude-(?:haiku|sonnet|opus|fable)-\d")

    def test_retry_and_effort_are_bounded(self):
        text = ROUTING.read_text(encoding="utf-8")
        self.assertIn("at most one catalog refresh", text)
        self.assertIn("one supported fallback attempt", text)
        self.assertIn("only effort levels supported", text)

    def test_no_paid_discovery_or_config_rewrite(self):
        text = ROUTING.read_text(encoding="utf-8")
        self.assertIn("No API key, new SDK installation, paid model probe", text)
        self.assertIn("not write a discovered version", text)
        self.assertIn("never fabricate a full ID", text)

    def test_manifest_versions_match_marketplace(self):
        plugin = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text())
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        self.assertEqual(plugin["version"], market["version"])
        self.assertEqual(plugin["version"], market["plugins"][0]["version"])


if __name__ == "__main__":
    unittest.main()
