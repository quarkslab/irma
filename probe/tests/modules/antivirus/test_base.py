from unittest import TestCase
from mock import patch, MagicMock
import re
import modules.antivirus.base as module


class TestAntivirusBase(TestCase):

    def test_scan_raises_tuple(self):
        a = module.Antivirus()
        with self.assertRaises(NotImplementedError):
            a.scan(tuple())

    def test_scan_raises_list(self):
        a = module.Antivirus()
        with self.assertRaises(NotImplementedError):
            a.scan(list())

    def test_scan_raises_set(self):
        a = module.Antivirus()
        with self.assertRaises(NotImplementedError):
            a.scan(set())

    @patch.object(module.Antivirus, "run_cmd")
    def test__run_and_parse_wrong_retcode(self, m_run_cmd):
        a = module.Antivirus()
        m_run_cmd.return_value = 1, "", ""
        with self.assertRaises(RuntimeError):
            a._run_and_parse()

    @patch.object(module.Antivirus, "run_cmd")
    def test__run_and_parse_no_regexp(self, m_run_cmd):
        a = module.Antivirus()
        m_run_cmd.return_value = 0, "stdout", ""
        res = a._run_and_parse()
        self.assertEquals(res, "stdout")

    @patch.object(module.Antivirus, "run_cmd")
    def test__run_and_parse_no_group(self, m_run_cmd):
        a = module.Antivirus()
        m_run_cmd.return_value = 0, "some text and figures 1 2 3 4", ""
        regexp = '(?P<num1>\\d+) (?P<num2>\\d+)'
        res = a._run_and_parse(regexp=regexp)
        self.assertEquals(res.group(), "1 2")

    @patch.object(module.Antivirus, "run_cmd")
    def test__run_and_parse_with_group(self, m_run_cmd):
        a = module.Antivirus()
        m_run_cmd.return_value = 0, "some text and figures 1 2 3 4", ""
        regexp = '(?P<num1>\\d+) (?P<num2>\\d+)'
        res = a._run_and_parse(regexp=regexp, group='num2')
        self.assertEquals(res, "2")

    @patch.object(module.Antivirus, "run_cmd")
    def test__run_and_parse_no_match(self, m_run_cmd):
        a = module.Antivirus()
        m_run_cmd.return_value = 0, "some text", ""
        regexp = '(?P<num1>\\d+) (?P<num2>\\d+)'
        with self.assertRaises(RuntimeError):
            a._run_and_parse(regexp=regexp, group='num2')

    def test__sanitize_str(self):
        res = module.Antivirus._sanitize(" a str with spaces  ")
        self.assertEquals(res, "a str with spaces")

    def test__sanitize_path(self):
        res = module.Antivirus._sanitize(module.Path("/a/random/path"))
        self.assertEquals(res, "/a/random/path")

    def test__sanitize_other(self):
        m = MagicMock()
        res = module.Antivirus._sanitize(m)
        self.assertEquals(res, m)

    def test_sanitize(self):
        res = module.Antivirus.sanitize([" first str  ", "   second str  "])
        self.assertEquals(list(res), ["first str", "second str"])

    @patch("modules.antivirus.base.Popen")
    def test_run_cmd_multiple_string(self, m_Popen):
        m_pd = MagicMock()
        m_pd.returncode = 0
        stdout = b"stdout"
        stderr = b"stderr"
        m_pd.communicate.return_value = stdout, stderr
        m_Popen.return_value = m_pd
        a = module.Antivirus()
        res = a.run_cmd("ls", "-la", "/tmp")
        m_Popen.assert_called_once_with(['ls', '-la', '/tmp'],
                                        env=None,
                                        stderr=module.PIPE,
                                        stdout=module.PIPE)
        self.assertEquals(res, (0, "stdout", "stderr"))

    @patch("modules.antivirus.base.Popen")
    def test_run_cmd_list(self, m_Popen):
        m_pd = MagicMock()
        m_pd.returncode = 0
        stdout = b"stdout"
        stderr = b"stderr"
        m_pd.communicate.return_value = stdout, stderr
        m_Popen.return_value = m_pd
        a = module.Antivirus()
        res = a.run_cmd(["ls", "-la", "/tmp"])
        m_Popen.assert_called_once_with(['ls', '-la', '/tmp'],
                                        env=None,
                                        stderr=module.PIPE,
                                        stdout=module.PIPE)
        self.assertEquals(res, (0, "stdout", "stderr"))

    @patch("modules.antivirus.base.Popen")
    def test_run_cmd_path(self, m_Popen):
        m_pd = MagicMock()
        m_pd.returncode = 0
        stdout = b"stdout"
        stderr = b"stderr"
        m_pd.communicate.return_value = stdout, stderr
        m_Popen.return_value = m_pd
        a = module.Antivirus()
        res = a.run_cmd(module.Path('/usr/bin/ls'))
        m_Popen.assert_called_once_with(['/usr/bin/ls'],
                                        env=None,
                                        stderr=module.PIPE,
                                        stdout=module.PIPE)
        self.assertEquals(res, (0, "stdout", "stderr"))

    @patch("modules.antivirus.base.Popen")
    def test_run_cmd_str(self, m_Popen):
        m_pd = MagicMock()
        m_pd.returncode = 0
        stdout = b"stdout"
        stderr = b"stderr"
        m_pd.communicate.return_value = stdout, stderr
        m_Popen.return_value = m_pd
        a = module.Antivirus()
        res = a.run_cmd("/usr/bin/ls")
        m_Popen.assert_called_once_with(['/usr/bin/ls'],
                                        env=None,
                                        stderr=module.PIPE,
                                        stdout=module.PIPE)
        self.assertEquals(res, (0, "stdout", "stderr"))

    def test_locate_unix(self):
        module.AntivirusUnix.locate("ls")

    @patch("modules.antivirus.base.os")
    def test_locate_unix_error(self, m_os):
        m_os.environ.__getitem__.side_effect = KeyError
        module.AntivirusUnix.locate("ls")

    def test_locate_windows(self):
        module.AntivirusWindows.locate("ls")

    @patch("modules.antivirus.base.os")
    def test_locate_windows_error(self, m_os):
        m_os.environ.__getitem__.side_effect = KeyError
        module.AntivirusWindows.locate("ls")

    @patch.object(module.Antivirus, "locate")
    def test_locate_one(self, m_locate):
        m_locate.return_value = ["/bin/azdzadzad"]
        a = module.AntivirusUnix()
        res = a.locate_one("azdzadzad")
        self.assertEquals(res, "/bin/azdzadzad")

    @patch.object(module.Antivirus, "locate")
    def test_locate_one_not_found(self, m_locate):
        m_locate.return_value = []
        a = module.AntivirusUnix()
        with self.assertRaises(RuntimeError):
            a.locate_one("azdzadzad")

    def test__locate(self):
        module.AntivirusUnix._locate("pattern", False, False)

    @patch.object(module.Antivirus, "identify_threat")
    def test_check_scan_results_infected(self, m_identify_threat):
        a = module.Antivirus()
        retcode = 1
        stdout = "stdout"
        stderr = "stderr"
        m_identify_threat.return_value = "threat"
        res = a.check_scan_results("/a/file/path", (retcode, stdout, stderr))
        self.assertEquals(res, 1)
        self.assertEquals(a.scan_results["/a/file/path"], "threat")

    @patch.object(module.Antivirus, "identify_threat")
    def test_check_scan_results_infected_error(self, m_identify_threat):
        a = module.Antivirus()
        retcode = 1
        stdout = "stdout"
        stderr = "stderr"
        m_identify_threat.return_value = ""
        res = a.check_scan_results("/a/file/path", (retcode, stdout, stderr))
        self.assertEquals(res, -1)

    @patch.object(module.Antivirus, "identify_threat")
    def test_check_scan_results_infected_error_no_stderr(self,
                                                         m_identify_threat):
        a = module.Antivirus()
        retcode = 1
        stdout = "stdout"
        stderr = ""
        m_identify_threat.return_value = ""
        res = a.check_scan_results("/a/file/path", (retcode, stdout, stderr))
        self.assertEquals(res, 0)

    def test_check_scan_results_error(self):
        a = module.Antivirus()
        retcode = -1
        stdout = "stdout"
        stderr = "stderr"
        res = a.check_scan_results("/a/file/path", (retcode, stdout, stderr))
        self.assertEquals(res, -1)
        self.assertEquals(a.scan_results["/a/file/path"], "stderr")

    def test_check_scan_results_clean(self):
        a = module.Antivirus()
        retcode = 0
        stdout = "stdout"
        stderr = "stderr"
        res = a.check_scan_results("/a/file/path", (retcode, stdout, stderr))
        self.assertEquals(res, 0)
        self.assertIsNone(a.scan_results["/a/file/path"])

    def test_check_scan_results_clean_raises(self):
        a = module.Antivirus()
        a._scan_retcodes[a.ScanResult.ERROR] = (lambda x: False)
        retcode = 2
        stdout = "stdout"
        stderr = "stderr"
        with self.assertRaises(RuntimeError):
            a.check_scan_results("/a/file/path", (retcode, stdout, stderr))
