import subprocess
import sys
import unittest
from pathlib import Path

class ProjectTests(unittest.TestCase):
    def test_reproduction(self):
        project=Path(__file__).resolve().parents[1]
        result=subprocess.run(
            [sys.executable,str(project/"reproduce.py")],
            capture_output=True,text=True
        )
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("PASS:",result.stdout)

    def test_chart_exists(self):
        project=Path(__file__).resolve().parents[1]
        chart=(project/"visualization.svg").read_text()
        self.assertIn("<svg",chart)
        self.assertIn("</svg>",chart)

if __name__=="__main__":
    unittest.main()
