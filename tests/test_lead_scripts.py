import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_script(name):
    path = ROOT / "skills" / "lead-enrichment" / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lead_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


find = load_script("find")
enrich = load_script("enrich")


class LeadScriptSafetyTests(unittest.TestCase):
    def test_skip_host_matching_requires_a_domain_boundary(self):
        self.assertTrue(find.host_matches("reddit.com", "reddit.com"))
        self.assertTrue(find.host_matches("www.reddit.com", "reddit.com"))
        self.assertFalse(find.host_matches("notreddit.com", "reddit.com"))
        self.assertFalse(find.host_matches("reddit.com.evil.example", "reddit.com"))

    def test_csv_formula_prefixes_are_escaped(self):
        for module in (find, enrich):
            for value in ("=1+1", "+cmd", "-2+3", "@SUM(A1)", "\t=1", "\r=1"):
                with self.subTest(module=module.__name__, value=value):
                    self.assertEqual(module.csv_safe(value), "'" + value)
            self.assertEqual(module.csv_safe("https://example.com"), "https://example.com")
            self.assertEqual(module.csv_safe(None), "")


if __name__ == "__main__":
    unittest.main()
