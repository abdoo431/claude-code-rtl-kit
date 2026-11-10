"""Tests for claude_code_rtl_kit.py. Run with: python -m unittest"""

import contextlib
import io
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

import claude_code_rtl_kit as rtl

LEGACY_START, LEGACY_END = rtl.CSS_MARKERS[1]
LEGACY_BLOCK = "\n" + LEGACY_START + "\n.old { direction: rtl; }\n" + LEGACY_END + "\n"
ORIGINAL = "body{color:red}\r\n.a{b:c}\n"


def quietly(fn, *args):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args)


class InjectRemoveTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "index.css")
        self.bak = self.path + ".bak"

    def tearDown(self):
        shutil.rmtree(self.dir)

    def write(self, content, path=None):
        rtl._write(path or self.path, content)

    def read(self, path=None):
        return rtl._read(path or self.path)

    def inject(self):
        return quietly(rtl._inject, self.path, rtl.RTL_CSS_RULES, rtl.CSS_MARKERS, "CSS:", "t")

    def remove(self):
        return quietly(rtl._remove, self.path, rtl.CSS_MARKERS, "CSS:", "t")

    def state(self):
        return rtl._install_state(self.path, rtl.RTL_CSS_RULES, rtl.CSS_MARKERS)

    def test_apply_then_remove_restores_original_exactly(self):
        self.write(ORIGINAL)
        self.assertTrue(self.inject())
        self.assertEqual(self.read(self.bak), ORIGINAL)
        self.assertEqual(self.state(), "installed")
        self.assertTrue(self.remove())
        self.assertEqual(self.read(), ORIGINAL)
        self.assertFalse(os.path.exists(self.bak))

    def test_remove_without_backup_strips_block(self):
        for original in (ORIGINAL, "no newline", "two\n\n"):
            self.write(original)
            self.inject()
            os.remove(self.bak)
            self.assertTrue(self.remove())
            self.assertEqual(self.read(), original)

    def test_second_apply_changes_nothing(self):
        self.write(ORIGINAL)
        self.inject()
        once = self.read()
        self.assertTrue(self.inject())
        self.assertEqual(self.read(), once)

    def test_legacy_install_is_detected_and_upgraded(self):
        self.write(ORIGINAL + LEGACY_BLOCK)
        self.assertTrue(rtl._file_holds_block(self.path, rtl.CSS_MARKERS))
        self.assertEqual(self.state(), "outdated")

        self.assertTrue(self.inject())
        content = self.read()
        self.assertNotIn(LEGACY_START, content)
        self.assertEqual(content.count(rtl.RTL_START_MARKER), 1)
        self.assertEqual(self.state(), "installed")
        # The backup made during the upgrade holds no patch.
        self.assertNotIn(LEGACY_START, self.read(self.bak))

        self.assertTrue(self.remove())
        self.assertNotIn(LEGACY_START, self.read())
        self.assertNotIn(rtl.RTL_START_MARKER, self.read())

    def test_patched_backup_is_replaced_and_not_restored(self):
        # State an earlier version could leave: both the file and its backup
        # hold the legacy block, plus a duplicate current block.
        self.write(ORIGINAL + LEGACY_BLOCK, self.bak)
        self.write(ORIGINAL + LEGACY_BLOCK + "\n" + rtl.RTL_CSS_RULES)
        self.assertTrue(self.inject())
        self.assertNotIn(LEGACY_START, self.read(self.bak))
        self.assertTrue(self.remove())
        self.assertNotIn(LEGACY_START, self.read())
        self.assertNotIn(rtl.RTL_START_MARKER, self.read())

    def test_remove_skips_patched_backup(self):
        self.write(ORIGINAL + LEGACY_BLOCK, self.bak)
        self.write(ORIGINAL + LEGACY_BLOCK)
        self.assertTrue(self.remove())
        self.assertNotIn(LEGACY_START, self.read())
        self.assertFalse(os.path.exists(self.bak))

    def test_damaged_block_is_left_alone(self):
        damaged = ORIGINAL + "\n" + rtl.RTL_START_MARKER + "\n.x{}\n"
        self.write(damaged)
        self.assertFalse(self.inject())
        self.assertEqual(self.read(), damaged)
        self.assertFalse(self.remove())
        self.assertEqual(self.read(), damaged)

    def test_not_installed(self):
        self.write(ORIGINAL)
        self.assertEqual(self.state(), "missing")
        self.assertTrue(self.remove())
        self.assertEqual(self.read(), ORIGINAL)


class LegacyMarkerTests(unittest.TestCase):
    """Blocks written by every earlier version are upgraded and removed."""

    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def check(self, name, block, markers, start, end):
        path = os.path.join(self.dir, name)
        old = "\n" + start + "\n/* old */\n" + end + "\n"
        # Every version appended "\n" + block, as _inject still does
        rtl._write(path, ORIGINAL + "\n" + old)
        self.assertEqual(rtl._install_state(path, block, markers), "outdated")
        quietly(rtl._inject, path, block, markers, "x", "t")
        content = rtl._read(path)
        self.assertNotIn(start, content)
        self.assertEqual(rtl._install_state(path, block, markers), "installed")
        quietly(rtl._remove, path, markers, "x", "t")
        self.assertEqual(rtl._read(path), ORIGINAL)

    def test_every_legacy_css_pair(self):
        for i, (start, end) in enumerate(rtl.CSS_MARKERS[1:]):
            self.check(f"css{i}.css", rtl.RTL_CSS_RULES, rtl.CSS_MARKERS, start, end)

    def test_every_legacy_js_pair(self):
        for i, (start, end) in enumerate(rtl.JS_MARKERS[1:]):
            self.check(f"js{i}.js", rtl.RTL_JS_CODE, rtl.JS_MARKERS, start, end)


class AutoApplyTests(unittest.TestCase):
    def test_command_runs_this_script_with_apply(self):
        command = rtl._auto_apply_command()
        self.assertEqual(command[1], os.path.abspath(rtl.__file__))
        self.assertEqual(command[2], "--apply")
        self.assertTrue(os.path.exists(command[0]))

    def test_cron_line_is_hourly_silent_and_tagged(self):
        line = rtl._cron_line(["/usr/bin/python3", "/home/a b/x.py", "--apply"])
        self.assertTrue(line.startswith("@hourly "))
        self.assertIn("'/home/a b/x.py'", line)
        self.assertIn(">/dev/null 2>&1", line)
        self.assertTrue(line.endswith(rtl.CRON_TAG))

    def test_cron_edit_keeps_other_jobs_and_never_duplicates(self):
        others = "0 5 * * * backup.sh\n@daily cleanup.sh\n"
        line = rtl._cron_line(["py", "x.py", "--apply"])
        once = rtl._cron_with(others, line)
        twice = rtl._cron_with(once, line)
        self.assertEqual(once, twice)
        self.assertEqual(once.count(rtl.CRON_TAG), 1)
        self.assertEqual(rtl._cron_without(twice), others)
        self.assertEqual(rtl._cron_with("", line), line + "\n")


class OldNameTests(unittest.TestCase):
    """Things saved by versions named Claude Code Arabic RTL keep working."""

    def test_old_cron_line_is_replaced(self):
        old = "@hourly py claude_code_arabic_rtl.py --apply " + rtl.LEGACY_CRON_TAG
        crontab = "0 5 * * * backup.sh\n" + old + "\n"
        line = rtl._cron_line(["py", "x.py", "--apply"])
        self.assertEqual(rtl._cron_with(crontab, line), "0 5 * * * backup.sh\n" + line + "\n")

    def test_old_settings_file_is_read(self):
        with tempfile.TemporaryDirectory() as d:
            new, old = os.path.join(d, "new.json"), os.path.join(d, "old.json")
            rtl._write(old, '{"language": "he"}')
            with mock.patch.object(rtl, "SETTINGS_PATH", new), \
                    mock.patch.object(rtl, "LEGACY_SETTINGS_PATH", old):
                self.assertEqual(rtl.load_language(), "he")
                rtl.save_language("fa")
                self.assertEqual(rtl.load_language(), "fa")

    def test_old_markers_are_known(self):
        self.assertIn("/* End Claude Code Arabic RTL: styles */", dict(rtl.CSS_MARKERS).values())
        self.assertIn("/* End Claude Code Arabic RTL: toggle and translation */",
                      dict(rtl.JS_MARKERS).values())
        self.assertIn("'ccar-rtl-enabled'", rtl.RTL_JS_CODE)


class DiscoveryTests(unittest.TestCase):
    def test_finds_extension_in_every_editor(self):
        with tempfile.TemporaryDirectory() as home:
            for editor in rtl.EDITOR_DIRS:
                webview = os.path.join(home, editor, "extensions",
                                       "anthropic.claude-code-2.1.0-win32-x64", "webview")
                os.makedirs(webview)
                rtl._write(os.path.join(webview, "index.css"), ORIGINAL)
            with mock.patch.object(rtl.platform, "system", return_value="Darwin"), \
                    mock.patch.object(rtl.Path, "home", return_value=rtl.Path(home)):
                found = rtl.find_installs()
        labels = {ext.name.split(" - ")[0] for ext in found}
        self.assertEqual(labels, set(rtl.EDITOR_LABELS.values()))
        for name in ("Cursor", "Trae", "Trae CN", "Trae (Remote)"):
            self.assertIn(name, labels)

    def homes(self, system, tree, **env):
        with mock.patch.object(rtl.platform, "system", return_value=system), \
                mock.patch.object(rtl, "running_in_wsl", return_value=True), \
                mock.patch.object(rtl.Path, "home", return_value=rtl.Path("/home/me")), \
                mock.patch.object(rtl, "_child_dirs", side_effect=lambda p: tree.get(p, [])), \
                mock.patch.dict(os.environ, env):
            return rtl._homes_to_search()

    def test_linux_searches_other_accounts_and_windows_drives(self):
        users = os.path.join("/mnt/d", "Users")
        tree = {
            "/home": ["/home/other"],
            "/mnt": ["/mnt/c", "/mnt/d", "/mnt/wsl"],
            users: [os.path.join(users, "Public"), os.path.join(users, "me")],
        }
        homes = self.homes("Linux", tree)
        self.assertEqual(homes[0], str(rtl.Path("/home/me")))
        self.assertIn("/home/other", homes)
        self.assertIn(os.path.join(users, "me"), homes)
        self.assertNotIn(os.path.join(users, "Public"), homes)
        self.assertEqual(len(homes), len(set(homes)))

    def test_windows_searches_wsl_once(self):
        distro = os.path.join("\\\\wsl.localhost", "Ubuntu")
        tree = {
            "\\\\wsl.localhost": [distro],
            "\\\\wsl$": [os.path.join("\\\\wsl$", "Ubuntu")],
            os.path.join(distro, "home"): [os.path.join(distro, "home", "me")],
        }
        homes = self.homes("Windows", tree, USERPROFILE="C:\\Users\\me")
        self.assertEqual(homes, ["C:\\Users\\me", os.path.join(distro, "home", "me")])


class LanguageTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        settings = mock.patch.object(rtl, "SETTINGS_PATH", os.path.join(self.dir, "settings.json"))
        settings.start()
        self.addCleanup(settings.stop)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_choice_is_saved_and_defaults_to_auto(self):
        self.assertEqual(rtl.load_language(), "auto")
        self.assertTrue(rtl.save_language("fa"))
        self.assertEqual(rtl.load_language(), "fa")
        rtl._write(rtl.SETTINGS_PATH, "not json")
        self.assertEqual(rtl.load_language(), "auto")

    def test_js_block_fixes_the_language(self):
        self.assertEqual(rtl.RTL_JS_CODE.count(rtl.FIXED_LANG_LINE), 1)
        self.assertEqual(rtl.js_block("auto"), rtl.RTL_JS_CODE)
        for lang in ("ar", "fa", "he", "en"):
            block = rtl.js_block(lang)
            self.assertIn(f"var FIXED_LANG = '{lang}';", block)
            self.assertNotIn(rtl.FIXED_LANG_LINE, block)

    def test_changing_language_replaces_the_installed_block(self):
        path = os.path.join(self.dir, "index.js")
        rtl._write(path, ORIGINAL)
        quietly(rtl._inject, path, rtl.js_block("ar"), rtl.JS_MARKERS, "JS:", "t")
        self.assertEqual(rtl._install_state(path, rtl.js_block("ar"), rtl.JS_MARKERS), "installed")
        self.assertEqual(rtl._install_state(path, rtl.js_block("fa"), rtl.JS_MARKERS), "outdated")
        quietly(rtl._inject, path, rtl.js_block("fa"), rtl.JS_MARKERS, "JS:", "t")
        self.assertEqual(rtl._install_state(path, rtl.js_block("fa"), rtl.JS_MARKERS), "installed")
        self.assertEqual(rtl._read(path).count(rtl.JS_START_MARKER), 1)
        self.assertEqual(rtl._read(path + ".bak"), ORIGINAL)

    def test_command_line(self):
        parse = rtl._parse_args
        self.assertEqual(parse([]), (None, None))
        self.assertEqual(parse(["--apply"]), ("--apply", None))
        self.assertEqual(parse(["--apply", "--lang", "fa"]), ("--apply", "fa"))
        self.assertEqual(parse(["--lang=he", "--apply"]), ("--apply", "he"))
        for bad in (["--apply", "--lang", "xx"], ["--status", "--lang", "fa"],
                    ["--lang", "fa"], ["--apply", "--lang"], ["--apply", "--remove"]):
            self.assertIsNone(parse(bad), bad)


class JsBlockTests(unittest.TestCase):
    def test_markers_wrap_block(self):
        block = rtl.RTL_JS_CODE.strip()
        self.assertTrue(block.startswith(rtl.JS_START_MARKER))
        self.assertTrue(block.endswith(rtl.JS_END_MARKER))
        css = rtl.RTL_CSS_RULES.strip()
        self.assertTrue(css.startswith(rtl.RTL_START_MARKER))
        self.assertTrue(css.endswith(rtl.RTL_END_MARKER))

    def test_every_language_translates_the_same_strings(self):
        js = rtl.RTL_JS_CODE
        body = js[js.index("var STRINGS = {"):js.index("var PERMISSION")]
        sections = re.split(r"\n        (ar|he|fa): \{", body)[1:]
        keys = {}
        for lang, text in zip(sections[0::2], sections[1::2]):
            keys[lang] = set(re.findall(r"^\s*(['\"])(.+?)\1:\s", text, re.M))
        self.assertEqual(set(keys), {"ar", "he", "fa"})
        self.assertEqual(keys["fa"], keys["ar"])
        self.assertEqual(keys["he"], keys["ar"])
        self.assertIn("fa: '", js[js.index("var BUTTON_TITLES"):])

    @unittest.skipUnless(shutil.which("node"), "node not installed")
    def test_js_block_parses(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "block.js")
            for lang in ("auto", "fa"):
                rtl._write(path, rtl.js_block(lang))
                result = subprocess.run(["node", "--check", path], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
