import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "bin" / "update_scholar_citations.py"
SPEC = importlib.util.spec_from_file_location("update_scholar_citations", MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(module)


class UpdateScholarCitationsTests(unittest.TestCase):
    def test_missing_output_file_is_handled(self):
        mock_scholarly = MagicMock()
        mock_scholarly.search_author_id.return_value = {"id": "scholar-123"}
        mock_scholarly.fill.return_value = {
            "publications": [{
                "pub_id": "pub-1",
                "bib": {"title": "Example paper", "pub_year": "2024"},
                "num_citations": 7,
            }]
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "citations.yml"
            original_output_file = module.OUTPUT_FILE
            module.OUTPUT_FILE = str(output_path)
            try:
                with patch.object(module.os.path, "exists", return_value=False):
                    with patch.object(module, "scholarly", mock_scholarly):
                        module.get_scholar_citations()

                self.assertTrue(output_path.exists())
                data = module.yaml.safe_load(output_path.read_text())
                self.assertEqual(data["papers"]["pub-1"]["citations"], 7)
                self.assertEqual(data["papers"]["pub-1"]["title"], "Example paper")
            finally:
                module.OUTPUT_FILE = original_output_file


if __name__ == "__main__":
    unittest.main()
