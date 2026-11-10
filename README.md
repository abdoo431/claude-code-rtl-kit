# Claude Code RTL Kit

[![Tests](https://github.com/abdoo431/claude-code-rtl-kit/actions/workflows/tests.yml/badge.svg)](https://github.com/abdoo431/claude-code-rtl-kit/actions/workflows/tests.yml)

<p><b>Right-to-left support and translated menus for the Claude Code extension in VS Code, Cursor, Kiro and Trae, for Arabic, Persian and Hebrew.</b></p>

<p dir="rtl"><b>دعم الكتابة من اليمين لليسار وترجمة القوائم في إضافة Claude Code على VS Code و Cursor و Kiro و Trae، للعربية والفارسية والعبرية.</b></p>

<p dir="rtl"><b>پشتیبانی از نوشتن راست‌به‌چپ و ترجمهٔ منوها در افزونهٔ Claude Code در VS Code، Cursor، Kiro و Trae، برای فارسی، عربی و عبری.</b></p>

<p dir="rtl"><b>תמיכה בכתיבה מימין לשמאל ותרגום תפריטים בתוסף Claude Code ב-VS Code, Cursor, Kiro ו-Trae, לעברית, ערבית ופרסית.</b></p>

| 🇸🇦 العربية | 🇬🇧 English | 🇮🇱 עברית |
|:---:|:---:|:---:|
| [اقرأ بالعربية ↓](#arabic) | [Read in English ↓](#english) | [לקרוא בעברית ↓](#hebrew) |

> MIT licensed &nbsp;·&nbsp; © 2026 Abdullah Hassan

---

<a name="arabic"></a>

<div dir="rtl" lang="ar">

## 🇸🇦 العربية

### ما المشكلة؟

إضافة **"Claude Code in VS Code"** لا تدعم اتجاه الكتابة من اليمين لليسار. فتظهر النصوص العربية والعبرية في المحادثة بمحاذاة خاطئة، ويختلط ترتيب الكلمات عند خلطها بالإنجليزية، وتظهر قوائم الواجهة بالإنجليزية فقط.

### ماذا تفعل الأداة؟

- **زر ⇄ أعلى المحادثة** يقلب المحادثة إلى وضع RTL ويعيدها، ويتذكّر اختيارك حتى بعد إعادة تحميل النافذة.
- **اختصار لوحة المفاتيح `Ctrl+Alt+R`** (و`Ctrl+Option+R` على macOS) يفعل نفس الشيء، ويعمل مع لوحة المفاتيح العربية أيضًا.
- **محاذاة صحيحة** لرسائلك وردود Claude والقوائم والفقرات.
- **الكود يبقى من اليسار لليمين**: كتل الكود، والأدوات ونتائجها، وكتلة Thinking، وأوامر slash.
- **تعريب القوائم والنوافذ وطلبات الإذن** عند تفعيل RTL (التفاصيل بالأسفل).
- **إعادة تطبيق تلقائية** بعد كل تحديث لـ Claude Code، إن فعّلتها.
- **نسخ احتياطية تلقائية** قبل أي تعديل، وإزالة كاملة تعيد الملفات الأصلية كما كانت.
- **ترقية آمنة**: يتعرّف على التثبيتات التي تمت بإصدارات أقدم، وبأدوات RTL أخرى سبقتها، ويستبدلها دون تكرار.
- يبحث تلقائيًا عن الإضافة في **VS Code و Cursor و Kiro و Trae** على Windows و macOS و Linux، وداخل WSL.

### المتطلبات

- **Python 3.6** أو أحدث
- إضافة **"Claude Code in VS Code"** مثبتة في VS Code أو Cursor أو Kiro أو Trae

### التثبيت

```bash
git clone https://github.com/abdoo431/claude-code-rtl-kit.git
cd claude-code-rtl-kit
python claude_code_rtl_kit.py
```

على macOS و Linux استخدم `python3` بدل `python`.

ستظهر قائمة:

```
Claude Code RTL Kit - for VS Code, Cursor, Kiro and Trae
--------------------------------------------------------
  [1] Install or update RTL support
  [2] Uninstall RTL support
  [3] Show status
  [4] Turn automatic re-apply ON
  [5] Quit
```

اختر `1` لإضافة الدعم، ثم اختر لغة القوائم المترجمة:

| الخيار | النتيجة |
|---|---|
| Automatic | اللغة تتبع رسائلك (الافتراضي) |
| Arabic / Persian / Hebrew | لغة ثابتة دائمًا |
| English | RTL فقط، بدون ترجمة |

يُحفظ اختيارك في `~/.claude-code-rtl-kit.json`، فيُستخدم عند إعادة التطبيق بعد التحديث. ثم أعد تحميل النافذة: `Ctrl+Shift+P` ← `Developer: Reload Window`.

#### بدون قائمة (سطر الأوامر)

```bash
python claude_code_rtl_kit.py --apply          # إضافة RTL لكل التثبيتات (أو تحديث تثبيت قديم)
python claude_code_rtl_kit.py --apply --lang fa  # مع لغة ثابتة: auto أو ar أو fa أو he أو en
python claude_code_rtl_kit.py --remove         # إزالة RTL واستعادة الملفات الأصلية
python claude_code_rtl_kit.py --status         # INSTALLED / OUTDATED / Not installed
python claude_code_rtl_kit.py --auto-apply     # تشغيل إعادة التطبيق التلقائية
python claude_code_rtl_kit.py --no-auto-apply  # إيقافها
```

رمز الخروج `0` عند النجاح، و`1` إذا فشل شيء أو لم يُعثر على الإضافة، و`2` لمعامل غير معروف.

### الاستخدام

1. افتح محادثة Claude Code.
2. اضغط الزر **⇄** بجانب زرّي السجل والمحادثة الجديدة أعلى المحادثة، أو اضغط `Ctrl+Alt+R`.
3. عندما يكون RTL مفعّلًا تظهر خلفية الزر مظللة.
4. اضغط مرة أخرى للعودة إلى LTR.

**مربع الكتابة:** كل سطر يأخذ اتجاهه من أول حرف فيه، فالسطر الذي يبدأ بكلمة عربية يُكتب من اليمين. هذا سلوك الإضافة نفسها، ولا يتغير بالزر.

### تعريب القوائم

عند تفعيل RTL تُترجم النصوص الإنجليزية الثابتة في:

| المكان | مثال |
|---|---|
| قائمة الرسالة | *Fork conversation from here* ← تفريع المحادثة من هنا |
| نافذة تأكيد الإرجاع (Rewind) | العنوان والأزرار والملاحظات وعدد الأسطر |
| نافذة Agent map | ‏Agent map ← خريطة الوكلاء، وعدد الوكلاء والمهام، والتوكنات، وتفاصيل الوكيل: حالته وأقسامها وأزرارها |
| طلب الإذن | ‏Yes ← نعم، ‏No ← لا، ‏Yes, and don't ask again ← نعم، ولا تسألني مرة أخرى، وكذلك الموافقة على الخطة وأسئلة WebFetch و WebSearch |
| تلميح زر ⇄ | تبديل اتجاه الكتابة (Ctrl+Alt+R) |

- **اللغة تُختار عند التثبيت**، والافتراضي أن تُستنتج من رسائلك: العربية إذا كنت تكتب بالعربية، والفارسية إذا كنت تكتب بالفارسية، والعبرية إذا كنت تكتب بالعبرية.
- النصوص التي يكتبها Claude، مثل أسماء مهام الوكلاء، **لا تُترجم**. وكذلك أزرار الإذن التي تذكر ملفًا أو قاعدة بعينها.
- إيقاف RTL يعيد النصوص الإنجليزية.
- إذا غيّر تحديث من Claude Code صياغة نص ما، يظهر بالإنجليزية دون أي عطل.

### بعد تحديث Claude Code

كل تحديث للإضافة يُثبَّت في مجلد جديد بدون RTL، فيختفي الزر. لديك طريقتان:

- **تلقائيًا (موصى به):** شغّل `--auto-apply` مرة واحدة. يُسجَّل في النظام أمر يشغّل `--apply` كل ساعة (Task Scheduler على Windows، و cron على macOS و Linux). إذا لم يكن هناك تحديث جديد فلا يغيّر شيئًا. بعد أن يعيد التطبيق، أعد تحميل النافذة. لا تنقل مجلد المشروع بعد تفعيله، لأن الأمر يشير إلى مكانه الحالي.
- **يدويًا:** شغّل `--apply` بعد كل تحديث ثم أعد تحميل النافذة.

يعرض `--status` التثبيتات القديمة بالحالة `OUTDATED`، ويعرض حالة إعادة التطبيق التلقائية.

### الإزالة

شغّل `python claude_code_rtl_kit.py --remove` (أو الخيار `2` من القائمة)، ثم أعد تحميل النافذة. تُستعاد الملفات الأصلية من النسخة الاحتياطية، وتُوقَف إعادة التطبيق التلقائية حتى لا تعيد RTL لاحقًا.

### حل المشاكل

- **الزر لا يظهر:** غالبًا تحدّثت الإضافة. شغّل `--status`، ثم `--apply`، ثم أعد تحميل النافذة. ولتجنّب ذلك مستقبلًا فعّل `--auto-apply`.
- **لا يجد البرنامج الإضافة:** تأكد أنها مثبتة: Extensions ← ابحث عن "Claude Code".
- **لا توجد صلاحية لتعديل ملف (no permission to change):** على Windows شغّل الطرفية كمسؤول، وعلى macOS و Linux استخدم `sudo python3 claude_code_rtl_kit.py`.

### المساهمة والتواصل

يسعدنا تلقّي ملاحظاتكم واقتراحاتكم، ونرحّب بمساهماتكم في تطوير الأداة.

- **الإبلاغ عن مشكلة أو اقتراح ميزة:** افتح [Issue](https://github.com/abdoo431/claude-code-rtl-kit/issues) جديدًا مع وصف واضح لما حدث. ويساعدنا ذكر المحرر، ونسخة Claude Code، ونظام التشغيل.
- **المساهمة بالكود أو الترجمة:** نرحّب بطلبات الدمج ([Pull Requests](https://github.com/abdoo431/claude-code-rtl-kit/pulls)) لإصلاح خطأ، أو تحسين ميزة، أو إضافة لغة جديدة. يُرجى تشغيل `python -m unittest` قبل الإرسال.

### الترخيص

مرخّص بـ MIT، © 2026 Abdullah Hassan. انظر [LICENSE](LICENSE).

</div>

---

<a name="english"></a>

## 🇬🇧 English

### The problem

The **"Claude Code in VS Code"** extension has no right-to-left support. Arabic, Persian and Hebrew messages are misaligned, word order breaks when they are mixed with English, and the UI menus are English only.

### What it does

- **A ⇄ button at the top of the chat** switches the conversation to RTL and back, and remembers your choice across window reloads.
- **Keyboard shortcut `Ctrl+Alt+R`** (`Ctrl+Option+R` on macOS) does the same, and works with an Arabic or Hebrew keyboard layout too.
- **Correct alignment** for your messages, Claude's replies, lists and paragraphs.
- **Code stays left-to-right**: code blocks, tools and their output, the Thinking block, slash commands.
- **Translated menus, dialogs and permission prompts** while RTL is on (details below).
- **Automatic re-apply** after every Claude Code update, if you turn it on.
- **Automatic backups** before any change; removal restores the original files exactly.
- **Safe upgrades**: installs made by older versions, and by earlier RTL patches, are detected and replaced, never duplicated.
- Finds the extension in **VS Code, Cursor, Kiro and Trae** on Windows, macOS and Linux, including WSL.

### Requirements

- **Python 3.6** or newer
- The **"Claude Code in VS Code"** extension, installed in VS Code, Cursor, Kiro or Trae

### Installation

```bash
git clone https://github.com/abdoo431/claude-code-rtl-kit.git
cd claude-code-rtl-kit
python claude_code_rtl_kit.py
```

On macOS and Linux use `python3`. The interactive menu offers add, remove, status and automatic re-apply. When adding, it asks for the language of the translated menus: **Automatic** (follows your messages, the default), **Arabic**, **Persian**, **Hebrew**, or **English** (RTL only, no translation). The choice is saved in `~/.claude-code-rtl-kit.json` and reused when RTL is re-applied after an update. After adding, reload the window: `Ctrl+Shift+P` → `Developer: Reload Window`.

#### Command line

```bash
python claude_code_rtl_kit.py --apply          # add RTL to every install (or update an older one)
python claude_code_rtl_kit.py --apply --lang fa  # with a fixed language: auto, ar, fa, he or en
python claude_code_rtl_kit.py --remove         # remove RTL and restore the original files
python claude_code_rtl_kit.py --status         # INSTALLED / OUTDATED / Not installed
python claude_code_rtl_kit.py --auto-apply     # turn automatic re-apply on
python claude_code_rtl_kit.py --no-auto-apply  # turn it off
```

Exit code is `0` on success, `1` on failure or when no extension is found, `2` on an unknown flag.

### Usage

Click **⇄** next to the history and new-chat buttons at the top of the chat, or press `Ctrl+Alt+R`. The button is shaded while RTL is on. Do it again to go back to LTR.

**Input box:** each line takes its direction from its first letter, so a line starting with an Arabic word is written right-to-left. This is the extension's own behaviour and the toggle does not change it.

### Translated menus

While RTL is on, the fixed English strings of these parts are translated:

| Where | Example |
|---|---|
| Message menu | *Fork conversation from here* → تفريع المحادثة من هنا / انشعاب گفتگو از اینجا / פיצול השיחה מכאן |
| Rewind confirmation dialog | title, buttons, notes, line counts |
| Agent map dialog | title, agent and task counts, token counts, agent details (status, sections, buttons) |
| Permission prompt | *Yes*, *No*, *Yes, and don't ask again*, the question and the Esc hint, plan approval, WebFetch and WebSearch questions |
| ⇄ button tooltip | in the conversation's language |

- **The language is chosen when installing**; by default it is picked from your messages: Arabic if you write in Arabic, Persian (Farsi) if you write in Persian, Hebrew if you write in Hebrew.
- Text written by Claude, such as agent task names, is **never translated**; neither are permission buttons that name a specific file or rule.
- Turning RTL off brings the English back.
- If a Claude Code update rewords a string, it simply stays in English.

### After a Claude Code update

Every extension update installs into a new folder without RTL, so the button disappears. Two options:

- **Automatic (recommended):** run `--auto-apply` once. It schedules `--apply` every hour (Task Scheduler on Windows, cron on macOS and Linux); when nothing changed it does nothing. Reload the window after it re-applies. Keep the project folder where it is, since the schedule points to it.
- **Manual:** run `--apply` after each update and reload the window.

`--status` shows installs from older versions as `OUTDATED`, and whether automatic re-apply is on.

### Removal

Run `python claude_code_rtl_kit.py --remove` (or option `2` in the menu) and reload the window. The original files are restored from the backup, and automatic re-apply is turned off so RTL does not come back.

### Troubleshooting

- **The button is missing:** the extension most likely updated. Run `--status`, then `--apply`, then reload the window. Turn on `--auto-apply` to avoid this next time.
- **The extension is not found:** check it is installed: Extensions → search "Claude Code".
- **No permission to change a file:** on Windows run the terminal as administrator; on macOS and Linux use `sudo python3 claude_code_rtl_kit.py`.

### Development

```bash
python -m unittest
```

Tests run on every push and pull request on Windows, macOS and Linux. The injected CSS and JavaScript live as strings in `claude_code_rtl_kit.py`. Translations are in the `STRINGS` table of the JavaScript block; adding a string is one line.

### Contributing

Feedback, suggestions and contributions are always welcome.

- **Found a problem or have an idea?** Open an [issue](https://github.com/abdoo431/claude-code-rtl-kit/issues) with a clear description. Your editor, Claude Code version and operating system help us reproduce it.
- **Want to contribute?** [Pull requests](https://github.com/abdoo431/claude-code-rtl-kit/pulls) are welcome, whether a fix, an improvement or a new language. Please run `python -m unittest` before submitting.

### License

MIT licensed, © 2026 Abdullah Hassan. See [LICENSE](LICENSE).

---

<a name="hebrew"></a>

<div dir="rtl" lang="he">

## 🇮🇱 עברית

### מה הבעיה?

לתוסף **"Claude Code in VS Code"** אין תמיכה בכתיבה מימין לשמאל. הודעות בעברית ובערבית מיושרות לא נכון, סדר המילים משתבש כשמשלבים אנגלית, ותפריטי הממשק מוצגים באנגלית בלבד.

### מה הכלי עושה?

- **כפתור ⇄ בראש הצ'אט** מעביר את השיחה למצב RTL וחזרה, וזוכר את הבחירה גם אחרי טעינה מחדש של החלון.
- **קיצור מקלדת `Ctrl+Alt+R`** (`Ctrl+Option+R` ב-macOS) עושה את אותו הדבר, ועובד גם עם פריסת מקלדת עברית.
- **יישור נכון** להודעות שלך, לתשובות של Claude, לרשימות ולפסקאות.
- **קוד נשאר משמאל לימין**: בלוקי קוד, כלים ותוצאותיהם, בלוק Thinking ופקודות slash.
- **תרגום תפריטים, חלונות ובקשות הרשאה** כשמצב RTL פעיל (פרטים בהמשך).
- **החלה אוטומטית מחדש** אחרי כל עדכון של Claude Code, אם תפעיל אותה.
- **גיבויים אוטומטיים** לפני כל שינוי, והסרה שמשחזרת את הקבצים המקוריים בדיוק.
- **שדרוג בטוח**: התקנות מגרסאות קודמות, ומתיקוני RTL קודמים, מזוהות ומוחלפות, בלי כפילויות.
- מאתר את התוסף ב-**VS Code, Cursor, Kiro ו-Trae** על Windows, macOS ו-Linux, כולל WSL.

### דרישות מערכת

- **Python 3.6** ומעלה
- התוסף **"Claude Code in VS Code"** מותקן ב-VS Code, ב-Cursor, ב-Kiro או ב-Trae

### התקנה

```bash
git clone https://github.com/abdoo431/claude-code-rtl-kit.git
cd claude-code-rtl-kit
python claude_code_rtl_kit.py
```

ב-macOS וב-Linux השתמש ב-`python3`. בתפריט בחר `1` להוספת התמיכה, ובחר את שפת התפריטים המתורגמים: **Automatic** (לפי ההודעות שלך, ברירת המחדל), **Arabic**, **Persian**, **Hebrew**, או **English** (RTL בלבד, בלי תרגום). הבחירה נשמרת ב-`~/.claude-code-rtl-kit.json` ומשמשת גם בהחלה מחדש אחרי עדכון. אחר כך טען את החלון מחדש: `Ctrl+Shift+P` → `Developer: Reload Window`.

#### שורת פקודה

```bash
python claude_code_rtl_kit.py --apply          # הוספת RTL לכל ההתקנות (או עדכון התקנה ישנה)
python claude_code_rtl_kit.py --apply --lang fa  # עם שפה קבועה: auto, ar, fa, he או en
python claude_code_rtl_kit.py --remove         # הסרת RTL ושחזור הקבצים המקוריים
python claude_code_rtl_kit.py --status         # INSTALLED / OUTDATED / Not installed
python claude_code_rtl_kit.py --auto-apply     # הפעלת החלה אוטומטית מחדש
python claude_code_rtl_kit.py --no-auto-apply  # כיבוי שלה
```

קוד היציאה הוא `0` בהצלחה, `1` אם משהו נכשל או שהתוסף לא נמצא, ו-`2` לפרמטר לא מוכר.

### שימוש

לחץ על **⇄** ליד כפתורי ההיסטוריה והשיחה החדשה בראש הצ'אט, או הקש `Ctrl+Alt+R`. כשמצב RTL פעיל, הכפתור מודגש. חזור על הפעולה כדי לחזור ל-LTR.

**תיבת הכתיבה:** כל שורה מקבלת את הכיוון שלה מהאות הראשונה בה, כך ששורה שמתחילה במילה בעברית נכתבת מימין לשמאל. זו התנהגות של התוסף עצמו, והכפתור לא משנה אותה.

### תרגום תפריטים

כשמצב RTL פעיל, הטקסטים הקבועים באנגלית בחלקים הבאים מתורגמים:

| איפה | דוגמה |
|---|---|
| התפריט של הודעה | *Fork conversation from here* ← פיצול השיחה מכאן |
| חלון אישור ההחזרה (Rewind) | כותרת, כפתורים, הערות ומספר השורות |
| חלון Agent map | ‏Agent map ← מפת סוכנים, מספר הסוכנים והמשימות, הטוקנים, ופרטי הסוכן: מצב, מקטעים וכפתורים |
| בקשת הרשאה | ‏Yes ← כן, ‏No ← לא, ‏Yes, and don't ask again ← כן, ואל תשאל שוב, וגם אישור תוכנית ושאלות WebFetch ו-WebSearch |
| הסבר הכפתור ⇄ | בשפת השיחה |

- **השפה נבחרת בהתקנה**; כברירת מחדל היא נקבעת לפי ההודעות שלך: עברית אם אתה כותב בעברית, ערבית אם בערבית, פרסית אם בפרסית.
- טקסט ש-Claude כתב, כמו שמות המשימות של הסוכנים, **לא מתורגם**; גם לא כפתורי הרשאה שמזכירים קובץ או כלל מסוים.
- כיבוי מצב RTL מחזיר את האנגלית.
- אם עדכון של Claude Code משנה ניסוח של טקסט, הוא פשוט יישאר באנגלית.

### אחרי עדכון של Claude Code

כל עדכון של התוסף מותקן בתיקייה חדשה ללא RTL, ולכן הכפתור נעלם. יש שתי דרכים:

- **אוטומטית (מומלץ):** הרץ `--auto-apply` פעם אחת. נקבעת משימה שמריצה `--apply` כל שעה (Task Scheduler ב-Windows, cron ב-macOS וב-Linux); אם אין עדכון, היא לא משנה כלום. אחרי שהיא מחילה מחדש, טען את החלון מחדש. אל תעביר את תיקיית הפרויקט, כי המשימה מצביעה עליה.
- **ידנית:** הרץ `--apply` אחרי כל עדכון וטען את החלון מחדש.

`--status` מציג התקנות מגרסאות קודמות כ-`OUTDATED`, ואם ההחלה האוטומטית פעילה.

### הסרה

הרץ `python claude_code_rtl_kit.py --remove` (או אפשרות `2` בתפריט) וטען את החלון מחדש. הקבצים המקוריים משוחזרים מהגיבוי, וההחלה האוטומטית נכבית כדי ש-RTL לא יחזור.

### פתרון בעיות

- **הכפתור לא מופיע:** כנראה התוסף התעדכן. הרץ `--status`, אחר כך `--apply`, וטען את החלון מחדש. הפעל `--auto-apply` כדי למנוע את זה בפעם הבאה.
- **התוסף לא נמצא:** ודא שהוא מותקן: Extensions → חפש "Claude Code".
- **אין הרשאה לשנות קובץ (no permission to change):** ב-Windows הרץ את הטרמינל כמנהל; ב-macOS וב-Linux השתמש ב-`sudo python3 claude_code_rtl_kit.py`.

### תרומה ומשוב

נשמח לקבל משוב והצעות, ונקבל בברכה תרומות לפיתוח הכלי.

- **מצאתם בעיה או יש לכם רעיון?** פתחו [Issue](https://github.com/abdoo431/claude-code-rtl-kit/issues) עם תיאור ברור. ציון העורך, גרסת Claude Code ומערכת ההפעלה יעזור לנו לשחזר אותה.
- **רוצים לתרום?** [Pull Requests](https://github.com/abdoo431/claude-code-rtl-kit/pulls) יתקבלו בברכה, בין אם תיקון, שיפור או שפה חדשה. אנא הריצו `python -m unittest` לפני השליחה.

### רישיון

מופץ תחת רישיון MIT, © 2026 Abdullah Hassan. ראה [LICENSE](LICENSE).

</div>
