import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = ROOT / "plugins/high-agency/agents"

EXPECTED = {
    "high-agency-scout.md": ("haiku", "low"),
    "high-agency-planner.md": ("opus", "high"),
    "high-agency-advisor.md": ("fable", "medium"),
    "high-agency-builder.md": ("sonnet", "medium"),
    "high-agency-verifier.md": ("haiku", "low"),
    "high-agency-deep-critic.md": ("fable", "xhigh"),
}


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---", text, re.S)
    if not match:
        raise AssertionError(f"missing frontmatter: {path}")
    data = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data


class ClaudeRoutingProfileTests(unittest.TestCase):
    def test_expected_role_model_effort_pairs(self):
        for filename, expected in EXPECTED.items():
            data = frontmatter(AGENT_DIR / filename)
            self.assertEqual((data.get("model"), data.get("effort")), expected)

    def test_only_builder_has_write_tools(self):
        for filename in EXPECTED:
            data = frontmatter(AGENT_DIR / filename)
            tools = data.get("tools", "")
            if filename == "high-agency-builder.md":
                self.assertIn("Edit", tools)
                self.assertIn("Write", tools)
            else:
                self.assertNotIn("Edit", tools)
                self.assertNotIn("Write", tools)

    def test_fable_roles_are_tool_free(self):
        for filename in ("high-agency-advisor.md", "high-agency-deep-critic.md"):
            data = frontmatter(AGENT_DIR / filename)
            self.assertEqual(data.get("model"), "fable")
            self.assertEqual(data.get("tools"), "[]")


if __name__ == "__main__":
    unittest.main()
