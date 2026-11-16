import unittest

from test_unit_skill import DELEGATE, DIRECTION, ROUTING, UNIT


class UnitTierTests(unittest.TestCase):
    def test_unit_skill_defines_four_tiers_and_names_them_in_the_report(self):
        text = UNIT.read_text(encoding="utf-8")
        for tier in ("T1 mechanical", "T2 standard", "T3 hard", "T4 frontier"):
            self.assertIn(tier, text)
        self.assertLess(text.index("## Difficulty tier"), text.index("## Playbooks"))
        self.assertIn("Unit: <one line: what changed> [T1–T4]", text)
        self.assertIn("stays on the main thread whatever its tier", text)

    def test_routing_maps_tiers_to_sonnet_opus_fable(self):
        text = ROUTING.read_text(encoding="utf-8")
        section = text[text.index("### Unit tiers"):]
        for needle in ("Sonnet / low", "Sonnet / medium", '`model: "opus"`', "Opus / high", "Fable / medium", "Fable never writes code"):
            self.assertIn(needle, section)
        self.assertIn("Never run two tiers on the same question", section)

    def test_direction_and_builder_reference_tiers(self):
        self.assertIn("Unit tiers", DIRECTION.read_text(encoding="utf-8"))
        builder = DELEGATE.read_text(encoding="utf-8")
        self.assertIn("T3, on Opus", builder)
        self.assertIn("[T1–T4]", builder)


if __name__ == "__main__":
    unittest.main()
