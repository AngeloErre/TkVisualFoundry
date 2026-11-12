from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime_requirements import supported,validate_interpreter,ensure_current,format_version

class RuntimePolicyTests(unittest.TestCase):
    def test_stable_315_and_future_stable(self):
        self.assertTrue(supported((3,15,0,'final',0)));self.assertTrue(supported((3,15,2,'final',0)));self.assertTrue(supported((3,16,0,'final',0)))
    def test_old_and_prerelease_rejected(self):
        for version in [(3,14,8,'final',0),(3,13,1,'final',0),(3,15,0,'alpha',7),(3,15,0,'beta',4),(3,15,0,'candidate',2),(3,16,0,'alpha',2)]:
            self.assertFalse(supported(version),version)
    def test_external_interpreter_final(self):
        with patch('runtime_requirements.subprocess.run',return_value=subprocess.CompletedProcess([],0,'[3,15,0,"final",0]','')):
            self.assertEqual(validate_interpreter('/path/python3.15')[:2],[3,15])
    def test_external_interpreter_alpha_rejected(self):
        with patch('runtime_requirements.subprocess.run',return_value=subprocess.CompletedProcess([],0,'[3,16,0,"alpha",2]','')):
            with self.assertRaisesRegex(ValueError,'stabile'):validate_interpreter('/path/python3.16')
    def test_missing_tk_and_timeout_actionable(self):
        with patch('runtime_requirements.subprocess.run',return_value=subprocess.CompletedProcess([],1,'','No module named tkinter')):
            with self.assertRaisesRegex(ValueError,'tkinter'):validate_interpreter('/path/python')
        with patch('runtime_requirements.subprocess.run',side_effect=subprocess.TimeoutExpired([],10)):
            with self.assertRaisesRegex(ValueError,'Interprete non utilizzabile'):validate_interpreter('/path/python')
    def test_ensure_current_uses_policy(self):
        with patch('runtime_requirements.sys.version_info',(3,15,0,'final',0)):ensure_current()
        with patch('runtime_requirements.sys.version_info',(3,16,0,'alpha',2)):
            with self.assertRaisesRegex(RuntimeError,'3.15'):ensure_current()

    def test_release_candidate_reported_exactly(self):
        self.assertEqual(format_version([3,15,0,'candidate',3]),'3.15.0rc3')
        with patch('runtime_requirements.subprocess.run',return_value=subprocess.CompletedProcess([],0,'[3,15,0,"candidate",3]','')):
            with self.assertRaisesRegex(ValueError,'3.15.0rc3'):validate_interpreter('/path/python3.15')
