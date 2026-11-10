"""Browser tests: the injected CSS and JS, run in Chromium on a small copy of
the Claude Code webview.

Needs Playwright:
    pip install playwright
    python -m playwright install chromium
Without it these tests are skipped. On CI they always run.
"""

import os
import re
import unittest

import claude_code_rtl_kit as rtl

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

URL = "http://ccrk.test/"

# The parts of the webview the kit touches. Class names follow the
# extension's CSS modules: name_ plus a hash, which the kit matches by prefix.
FIXTURE = """
<div class="header_h1">
  <div class="titleGroup_h1">Session title</div>
  <button class="iconButton_b1">H</button><button class="iconButton_b1">N</button>
</div>
<div class="messagesContainer_m1">
  <div class="userMessageContainer_u1"><div class="userMessage_u1" id="msg">MESSAGE</div></div>
  <div class="timelineMessage_t1"><div class="root_r1" id="reply"><p>Yes</p><p>Restore</p>
    <pre><code>print("No")</code></pre></div></div>
  <div class="timelineMessage_t1"><details class="thinking_k1">
    <summary class="thinkingSummary_k1"><span id="thinking">Thought for 12s</span></summary>
    <div class="thinkingContent_k1"><div class="root_r1"><p>thinking text</p></div></div></details></div>

  <div class="popup_p1" id="menu">
    <button class="popupOption_p1"><span class="optionText_p1">Fork conversation from here</span></button>
    <button class="popupOption_p1"><span class="optionText_p1">Rewind code to here</span></button>
    <button class="popupOption_p1"><span class="optionText_p1">Fork conversation and rewind code</span></button>
  </div>

  <div class="permissionRequestContainer_q1" id="perm">
    <div class="permissionRequestHeader_q1">Do you want to proceed with <strong>Bash</strong>?</div>
    <div class="permissionRequestDescription_q1"><details><summary><span>Details</span></summary>
      <pre>ls -la</pre></details></div>
    <div class="buttonContainer_q1">
      <button class="button_q1"><span class="shortcutNum_q1">1</span> Yes</button>
      <button class="button_q1"><span class="shortcutNum_q1">2</span> Yes, and don't ask again</button>
      <button class="button_q1"><span class="shortcutNum_q1">3</span> No</button>
    </div>
    <div class="keyboardHints_q1">Esc to cancel</div>
  </div>
  <div class="permissionRequestContainer_q1" id="plan">
    <div class="permissionRequestHeader_q1">Accept this plan?</div>
    <div class="buttonContainer_q1">
      <button class="button_q1"><span class="shortcutNum_q1">1</span> Yes, and use auto mode</button>
      <button class="button_q1"><span class="shortcutNum_q1">2</span> No, keep planning</button>
    </div>
  </div>
</div>

<div role="dialog" id="rewind"><h3>Rewind</h3>
  <p class="forkNote_r2">A new forked conversation will be created after rewinding.</p>
  <p class="warning_r2">Restored files go back whole, losing later changes by anyone. Bash changes to other files are not undone.</p>
  <div class="choiceGroup_r2">
    <button><span>Restore code and conversation</span><span>The conversation will be forked.</span></button>
    <button><span>Restore conversation</span><span>The conversation will be forked. The code will be unchanged.</span></button>
  </div>
  <p class="summary_r2"><span>3</span><span> line</span><span>s</span> <span>will be removed and</span>
    <span>1</span><span> line</span> <span>will be added across </span><span>2</span><span> file</span><span>s</span>:</p>
  <div class="actions_r2"><button>Restore</button><button>Never mind</button></div>
</div>

<div role="dialog" id="agentmap"><h3>Agent map</h3>
  <div class="subtitle_x1"><span>10</span> <span>agents</span><span> · click an agent for details</span></div>
  <div class="row_x1 rowMain_x1"><span class="rowTitle_x1">This session</span><span class="rowMeta_x1">345.6k tokens in context</span></div>
  <div class="tasksHeader_x1"><span>2</span><span> background </span><span>tasks</span><span> · click a task for details</span></div>
  <span class="cardTitle_x1">Running</span>
  <div class="meta_x1">Working · Explore · 1m 4s · background</div>
  <div class="meta_x1"><span>Spawned by </span><span>the main agent</span></div>
  <button class="sectionHeader_x1">Output</button>
  <div class="meta_x1">No output yet.</div>
  <div class="actions_x1"><button>Open transcript</button><button>Stop agent</button></div>
</div>

<div role="dialog" aria-label="Past conversations" id="history">
  <input class="searchInput_s1" placeholder="Search sessions…">
  <div class="sectionTitle_s1">Sessions</div>
  <div class="nullStateText_s1">No sessions yet</div>
  <div class="groupName_s1">Ungrouped</div>
</div>

<div role="dialog" id="slash"><h3>Slash commands</h3>
  <input placeholder="Filter commands…">
  <div class="emptyState_c1"><p>No matching commands.</p></div>
</div>

<fieldset class="inputContainer_i1">
  <div class="messageInput_i1" id="input" contenteditable="true" data-placeholder="Ask Claude to edit…"></div>
</fieldset>
"""

# Parts the kit translates, and English that is meant to stay: tool and
# product names, keys, units and a URL.
TRANSLATED = "#menu, #perm, #plan, #rewind, #agentmap, #history, #slash, #thinking"
KEPT_ENGLISH = re.compile(r"\b(Bash|Esc|Claude|Explore|KB|Ctrl|Alt)\b|claude\.ai/code|\d+(\.\d+)?k?|\b\d+m\b|\b\d+s\b")

MESSAGES = {
    "ar": "مرحبا، راجع الملفات التي كتبتها",
    "fa": "سلام، این فایل‌ها را بررسی کن",
    "ur": "براہ کرم ان فائلوں کو دیکھیں اور بتائیں کہ کیا ہے",
    "he": "שלום, תבדוק את הקבצים",
}
# How the first menu item reads in each language
FORK = {
    "ar": "تفريع المحادثة من هنا",
    "fa": "انشعاب گفتگو از اینجا",
    "ur": "یہاں سے گفتگو کی شاخ بنائیں",
    "he": "פיצול השיחה מכאן",
}
SCRIPT = {"ar": "[؀-ۿ]", "fa": "[؀-ۿ]", "ur": "[؀-ۿ]", "he": "[֐-׿]"}


def page_html(message="hello", lang="auto", storage=None):
    seed = ""
    if storage:
        seed = "<script>localStorage.setItem(%r, %r);</script>" % storage
    return ("<!doctype html><html><head><meta charset='utf-8'><style>body{width:640px}"
            + rtl.RTL_CSS_RULES + "</style>" + seed + "</head><body><div id='root'>"
            + FIXTURE.replace("MESSAGE", message) + "</div><script>" + rtl.js_block(lang)
            + "</script></body></html>")


@unittest.skipIf(sync_playwright is None, "Playwright is not installed")
class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        try:
            cls.browser = cls.pw.chromium.launch()
        except Exception as e:
            cls.pw.stop()
            if os.environ.get("CI"):
                raise
            raise unittest.SkipTest(f"Chromium is not available: {e}")

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def open(self, **kw):
        context = self.browser.new_context()
        self.addCleanup(context.close)
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        self.addCleanup(lambda: self.assertEqual(errors, [], "script errors"))
        html = page_html(**kw)
        page.route(URL, lambda route: route.fulfill(body=html, content_type="text/html"))
        page.goto(URL)
        self.settle(page)
        return page

    def settle(self, page):
        """Wait until the kit has handled the last change (it runs once per frame)."""
        page.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")

    def texts(self, page, selector):
        return page.evaluate("""sel => {
            const out = [];
            document.querySelectorAll(sel).forEach(root => {
                const walk = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
                let n;
                while ((n = walk.nextNode())) {
                    if (n.parentElement.closest('pre')) continue;
                    const t = n.nodeValue.trim();
                    if (t) out.push(t);
                }
            });
            return out;
        }""", selector)

    def placeholders(self, page):
        return page.evaluate("""() => [
            document.getElementById('input').getAttribute('data-placeholder'),
            ...[...document.querySelectorAll('[placeholder]')].map(e => e.placeholder)]""")

    def is_on(self, page):
        return page.evaluate("() => document.getElementById('root').classList.contains('ccrk-rtl')")

    # ------------------------------------------------------------------

    def test_every_translated_part_in_each_language(self):
        for lang in ("ar", "fa", "ur", "he"):
            with self.subTest(lang=lang):
                page = self.open(lang=lang, storage=("ccrk-rtl-enabled", "1"))
                left = [t for t in self.texts(page, TRANSLATED)
                        if re.search(r"[A-Za-z]{2,}", KEPT_ENGLISH.sub("", t))]
                self.assertEqual(left, [], "still in English")
                for text in self.placeholders(page):
                    self.assertRegex(text, SCRIPT[lang])
                self.assertEqual(page.inner_text("#menu .optionText_p1 >> nth=0"), FORK[lang])
                page.hover("#ccrk-rtl-btn")
                self.assertRegex(page.get_attribute("#ccrk-rtl-btn", "title"), SCRIPT[lang])

    def test_language_follows_the_messages(self):
        for lang, message in MESSAGES.items():
            with self.subTest(lang=lang):
                page = self.open(message=message, storage=("ccrk-rtl-enabled", "1"))
                self.assertEqual(page.inner_text("#menu .optionText_p1 >> nth=0"), FORK[lang])

    def test_text_claude_wrote_is_left_alone(self):
        page = self.open(lang="ar", storage=("ccrk-rtl-enabled", "1"))
        self.assertEqual(self.texts(page, "#reply"), ["Yes", "Restore"])
        self.assertEqual(page.inner_text("#reply pre"), 'print("No")')

    def test_toggle_brings_english_back(self):
        page = self.open(lang="fa", storage=("ccrk-rtl-enabled", "1"))
        english = self.texts(self.open(), TRANSLATED)
        english_placeholders = self.placeholders(self.open())

        page.click("#ccrk-rtl-btn")
        self.settle(page)
        self.assertFalse(self.is_on(page))
        self.assertEqual(self.texts(page, TRANSLATED), english)
        self.assertEqual(self.placeholders(page), english_placeholders)
        self.assertEqual(page.evaluate("() => document.querySelectorAll('[data-ccrk-dir]').length"), 0)
        self.assertEqual(page.evaluate("() => localStorage.getItem('ccrk-rtl-enabled')"), "0")

        page.keyboard.press("Control+Alt+KeyR")
        self.settle(page)
        self.assertTrue(self.is_on(page))
        self.assertEqual(page.inner_text("#menu .optionText_p1 >> nth=0"), FORK["fa"])
        self.assertEqual(page.evaluate("() => localStorage.getItem('ccrk-rtl-enabled')"), "1")

    def test_ui_rendered_later_is_translated(self):
        page = self.open(lang="ar", storage=("ccrk-rtl-enabled", "1"))
        page.evaluate("""() => {
            const option = document.createElement('button');
            option.className = 'popupOption_p1';
            option.id = 'late';
            option.textContent = 'Rewind code to here';
            document.getElementById('menu').appendChild(option);
            document.querySelector('#thinking').firstChild.nodeValue = 'Thinking...';
            document.getElementById('input').setAttribute('data-placeholder', 'Queue another message…');
            document.getElementById('input').setAttribute('data-placeholder', 'ctrl esc to attach selected text');
        }""")
        self.settle(page)
        self.assertEqual(page.inner_text("#late"), "إرجاع الكود إلى هذه النقطة")
        self.assertEqual(page.inner_text("#thinking"), "يفكّر...")
        self.assertEqual(page.get_attribute("#input", "data-placeholder"), "ctrl esc لإرفاق النص المحدد")

    def test_state_saved_by_older_versions_is_restored(self):
        for key in ("ccar-rtl-enabled", "yby-rtl-enabled"):
            with self.subTest(key=key):
                self.assertTrue(self.is_on(self.open(storage=(key, "1"))))

    def test_fixed_english_keeps_the_ui_in_english(self):
        page = self.open(message=MESSAGES["ar"], lang="en", storage=("ccrk-rtl-enabled", "1"))
        self.assertTrue(self.is_on(page))
        self.assertEqual(page.inner_text("#menu .optionText_p1 >> nth=0"), "Fork conversation from here")

    def test_layout(self):
        style = """sel => { const s = getComputedStyle(document.querySelector(sel));
                            return [s.direction, s.textAlign]; }"""
        page = self.open(message=MESSAGES["ar"], storage=("ccrk-rtl-enabled", "1"))
        self.assertEqual(page.evaluate(style, "#msg"), ["rtl", "right"])
        self.assertEqual(page.evaluate(style, "#reply p"), ["rtl", "right"])
        self.assertEqual(page.evaluate(style, "#reply pre"), ["ltr", "left"])
        self.assertEqual(page.evaluate(style, ".thinkingContent_k1 p")[0], "ltr")
        self.assertEqual(page.evaluate(style, "#input")[0], "ltr")
        self.assertEqual(page.evaluate(style, ".titleGroup_h1")[0], "ltr")
        self.assertEqual(page.get_attribute("#rewind", "dir"), "rtl")

        page.click("#ccrk-rtl-btn")
        self.settle(page)
        self.assertEqual(page.evaluate(style, "#msg")[0], "ltr")
        self.assertIsNone(page.get_attribute("#rewind", "dir"))


if __name__ == "__main__":
    unittest.main()
