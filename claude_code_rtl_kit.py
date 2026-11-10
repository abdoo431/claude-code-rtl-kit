#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code RTL Kit

Right-to-left layout and translated menus (Arabic, Persian, Urdu, Hebrew) for the
Claude Code extension in VS Code, Cursor, Kiro and Trae.

The extension's webview is patched in two places, each with one marked block
that can be taken out again:
  webview/index.css - styles that apply while the .ccrk-rtl class is set
  webview/index.js  - the toggle button, the shortcut and the translation
"""

import json
import os
import shlex
import subprocess
import sys
import platform
import glob
from collections import namedtuple
from pathlib import Path

RTL_CSS_RULES = """
/* Claude Code RTL Kit: styles - added by claude_code_rtl_kit.py */

/* ---------------------------------------------------------------
   The toggle button
   It takes the classes of the header's own icon buttons, so their
   rules give it its size and padding. Only the glyph and the on/off
   look are set here: a width of our own would make it wider than its
   neighbours and push them out of a narrow panel.
   --------------------------------------------------------------- */

#ccrk-rtl-btn {
    cursor: pointer;
    font-size: 13px;
    font-weight: 700;
    line-height: 1;
    opacity: 0.7;
    transition: opacity 0.15s, background 0.15s;
}

/* Its own box, used only when the header has no icon button to borrow
   from. It comes before the hover and pressed rules so they still win. */
#ccrk-rtl-btn.ccrk-standalone {
    display: flex;
    align-items: center;
    justify-content: center;
    inline-size: 24px;
    block-size: 24px;
    padding: 4px;
    border: 0 none;
    border-radius: 4px;
    background: transparent;
    color: var(--vscode-foreground);
    flex: 0 0 auto;
}

#ccrk-rtl-btn:is(:hover, .ccrk-active) {
    opacity: 1;
}

#ccrk-rtl-btn:hover {
    background: var(--app-hover-background, rgba(128, 128, 128, 0.15));
}

#ccrk-rtl-btn.ccrk-active {
    background: var(--app-secondary-background, rgba(128, 128, 128, 0.3));
    color: var(--app-primary-foreground, var(--vscode-foreground));
}

/* ---------------------------------------------------------------
   Right to left, while #root carries .ccrk-rtl
   --------------------------------------------------------------- */

.ccrk-rtl [class*="messagesContainer_"] {
    direction: rtl;
}

/* Your own messages line up on the right. Each paragraph still takes
   the direction of its first letter, so English stays readable. */
.ccrk-rtl :is([class*="userMessage_"], [class*="userMessageContainer_"]) {
    direction: rtl;
    unicode-bidi: plaintext;
    align-items: flex-end !important;
    text-align: right !important;
    margin-inline: 0 auto !important;
}

.ccrk-rtl :is([class*="expandableContainer_"] [class*="content_"], [class*="content_"] > span) {
    unicode-bidi: plaintext;
}

/* Claude's replies - but not its thinking, which stays as it is */
.ccrk-rtl [class*="root_"]:not([class*="thinkingContent_"] *) {
    direction: rtl;
    unicode-bidi: plaintext;
}

.ccrk-rtl [class*="root_"]:not([class*="thinkingContent_"] *) > :is(p, h1, h2, h3, h4, blockquote, ul, ol),
.ccrk-rtl [class*="root_"]:not([class*="thinkingContent_"] *) > :is(ul, ol) li {
    text-align: right;
}

.ccrk-rtl [class*="root_"]:not([class*="thinkingContent_"] *) a {
    unicode-bidi: plaintext;
}

/* Questions Claude asks, their options and your answers */
.ccrk-rtl :is([class*="questionBlock_"], [class*="questionHeader_"], [class*="answerText_"],
              [class*="optionText_"], [class*="optionContent_"]) {
    direction: rtl;
    unicode-bidi: plaintext;
}

/* ---------------------------------------------------------------
   What stays left to right
   --------------------------------------------------------------- */

/* Controls and status: the message box and its attachments, buttons,
   slash commands, progress dots, permission prompts, errors, the todo
   list and sign-in */
.ccrk-rtl :is(
    fieldset[class*="inputContainer_"], [class*="inputWrapper_"], [class*="messageInput_"],
    [class*="selectionAttachment_"], [class*="attachmentInfo_"], [class*="attachmentText_"],
    [class*="iconButton_"], [class*="copyButton_"], [class*="actionButton_"],
    [class*="sessionsButtonText_"],
    [class*="slashCommandMessage_"], [class*="slashCommandResultMessage_"],
    [class*="progressContent_"],
    [class*="dotSuccess_"], [class*="dotFailure_"], [class*="dotProgress_"], [class*="dotWarning_"],
    [class*="permissionRequest"], [class*="errorMessage_"], [class*="secondaryLine_"],
    [class*="todoListContainer_"], [class*="todoList_"], [class*="todoItem_"],
    [class*="auth_"], [class*="authUrl"]
) {
    direction: ltr !important;
}

/* The session header - the one holding the conversation title. A rule of
   its own: a selector list that contains :has() is dropped whole by an
   engine without it. */
.ccrk-rtl [class*="header_"]:has([class*="titleGroup_"], [class*="headerSpacer_"]) {
    direction: ltr !important;
}

/* Code, tool calls and Claude's thinking: isolated from the text around
   them and aligned left */
.ccrk-rtl :is(
    pre, code, [class*="codeBlockWrapper_"],
    [class*="toolUse_"], [class*="toolSummary_"], [class*="toolResult_"],
    [class*="toolNameText_"], [class*="toolReference_"],
    [class*="toolBody_"], [class*="toolBodyGrid_"], [class*="toolBodyRow_"],
    [class*="toolBodyRowContent_"], [class*="toolBodyRowLabel_"],
    [class*="thinking_"], [class*="thinkingContent_"], [class*="thinkingContainer_"],
    [class*="thinkingHeader_"], [class*="spinnerRow_"],
    [class*="timelineMessage_"]:has([class*="thinking_"])
) {
    direction: ltr !important;
    unicode-bidi: isolate !important;
    text-align: left !important;
}

/* Lists in the thinking block, which the reply rules would otherwise reach */
.ccrk-rtl [class*="thinkingContent_"] [class*="root_"] :is(ul, ol, li) {
    direction: ltr !important;
    text-align: left !important;
}

/* ---------------------------------------------------------------
   Translated menus and dialogs - the toggle script sets dir on them
   --------------------------------------------------------------- */

/* The extension hard-codes left alignment on menu items */
[class*="popupOption_"][dir="rtl"] {
    text-align: right;
}

/* Agent map rows: the extension hard-codes left alignment, and indents the
   meta line on the left to sit under the title text */
[role="dialog"] [class*="row_"][dir="rtl"] {
    text-align: right;
}

[role="dialog"] [class*="row_"][dir="rtl"] [class*="rowMeta_"] {
    padding-left: 0;
    padding-right: 14px;
}

/* Agent map tree: the connector lines are placed with left offsets - mirror
   them so they still join the main row to its agents */
[role="dialog"][dir="rtl"] [class*="children_"] {
    margin-left: 0;
    margin-right: 32px;
}

[role="dialog"][dir="rtl"] [class*="children_"]::before {
    left: auto;
    right: -32px;
}

[role="dialog"][dir="rtl"] [class*="child_"]::before,
[role="dialog"][dir="rtl"] [class*="child_"]::after {
    left: auto;
    right: -16px;
}

[role="dialog"][dir="rtl"] [class*="rowMain_"]::after {
    left: auto;
    right: calc(100% + 1px);
}

/* Permission prompt: the whole prompt is kept left-to-right above, so a
   translated header needs !important to turn back. The extension also
   hard-codes left alignment on its buttons. */
.ccrk-rtl [class*="permissionRequestHeader_"][dir="rtl"] {
    direction: rtl !important;
    text-align: right;
}

[class*="buttonContainer_"] > button[dir="rtl"] {
    text-align: right;
}

/* Rewind dialog: file paths stay left-to-right */
[role="dialog"][dir="rtl"] [class*="fileItem_"] {
    direction: ltr;
    text-align: left;
}

/* End Claude Code RTL Kit: styles */
"""

RTL_JS_CODE = r"""
/* Claude Code RTL Kit: toggle and translation - added by claude_code_rtl_kit.py */
(function() {
    var BTN_ID = 'ccrk-rtl-btn';
    var ROOT_CLASS = 'ccrk-rtl';
    var STORAGE_KEY = 'ccrk-rtl-enabled';
    /* Keys earlier versions and earlier RTL patches saved the state under */
    var LEGACY_STORAGE_KEYS = ['ccar-rtl-enabled', 'yby-rtl-enabled'];
    /* Translation language picked when installing: 'ar', 'fa', 'ur', 'he', or 'en'
       for no translation. null follows the conversation. Set by the installer. */
    var FIXED_LANG = null;

    /* ------------------------------------------------------------------
       Translation of fixed UI strings
       ------------------------------------------------------------------ */

    /* Applied only while RTL mode is on. The language follows the
       conversation: whichever of Arabic, Persian, Urdu or Hebrew the user writes in. A string
       missing here, or reworded by an extension update, stays in English.
       Each language has one table per scope (see SCOPES). */
    var STRINGS = {
        ar: {
            ui: {
                /* Message action menu */
                'Fork conversation from here': 'تفريع المحادثة من هنا',
                'Rewind code to here': 'إرجاع الكود إلى هذه النقطة',
                'Fork conversation and rewind code': 'تفريع المحادثة وإرجاع الكود',
                /* Rewind confirmation dialog */
                'Rewind': 'إرجاع',
                'Rewind code': 'إرجاع الكود',
                'Fork and rewind': 'تفريع وإرجاع',
                'Restore': 'استعادة',
                'Continue': 'متابعة',
                'Never mind': 'إلغاء',
                'A new forked conversation will be created after rewinding.': 'ستُنشأ محادثة مفرّعة جديدة بعد الإرجاع.',
                'Checking code changes…': 'جارٍ فحص تغييرات الكود…',
                'Restored files go back whole, losing later changes by anyone. Bash changes to other files are not undone.':
                    'تُستعاد الملفات كاملة، فتضيع أي تغييرات لاحقة عليها مهما كان مصدرها. ولا تُلغى تغييرات أوامر Bash على الملفات الأخرى.',
                'Restore code and conversation': 'استعادة الكود والمحادثة',
                'Restore conversation': 'استعادة المحادثة',
                'Restore code': 'استعادة الكود',
                'The conversation will be forked.': 'ستُفرَّع المحادثة.',
                'The conversation will be forked. The code will be unchanged.': 'ستُفرَّع المحادثة، ولن يتغير الكود.',
                'The conversation will be unchanged.': 'لن تتغير المحادثة.',
                'The code ': 'الكود ',
                'has not changed': 'لم يتغير',
                ', so no code will be restored.': '، لذلك لن يُستعاد أي كود.',
                /* Agent map dialog */
                'Agent map': 'خريطة الوكلاء',
                'This session': 'هذه الجلسة',
                /* Permission prompt */
                'Yes': 'نعم',
                'No': 'لا',
                "Yes, and don't ask again": 'نعم، ولا تسألني مرة أخرى',
                'Yes, allow all edits this session': 'نعم، اسمح بكل التعديلات في هذه الجلسة',
                'Yes, return to normal mode': 'نعم، عُد إلى الوضع العادي',
                'Yes, and manually approve edits': 'نعم، مع الموافقة اليدوية على التعديلات',
                'Esc to cancel': 'اضغط Esc للإلغاء',
                /* Plan approval, questions and Agent map actions */
                'Yes, and use auto mode': 'نعم، واستخدم الوضع التلقائي',
                'Yes, and auto-accept': 'نعم، مع القبول التلقائي',
                'Submit answers': 'إرسال الإجابات',
                'No, keep planning': 'لا، تابع التخطيط',
                'Send feedback and keep planning': 'أرسل ملاحظاتي وتابع التخطيط',
                'Open transcript': 'فتح السجل',
                'Stop agent': 'إيقاف الوكيل',
                'Stop': 'إيقاف',
                'Stopping…': 'جارٍ الإيقاف…',
                /* Slash commands dialog */
                'Slash commands': 'أوامر الشرطة المائلة',
                'No matching commands.': 'لا توجد أوامر مطابقة.',
                'No slash commands available.': 'لا توجد أوامر متاحة.'
            },
            /* "Do you want to proceed with <tool>?" */
            permHeader: {
                'Do you want to proceed with ': 'هل تريد المتابعة مع ',
                '?': '؟',
                'Accept this plan?': 'هل تقبل هذه الخطة؟',
                'Continue planning': 'متابعة التخطيط',
                'Allow fetching this url?': 'هل تسمح بجلب هذا الرابط؟',
                'Allow network connection to this host?': 'هل تسمح بالاتصال بهذا الخادم؟',
                'Allow searching for this query?': 'هل تسمح بالبحث عن هذا الاستعلام؟'
            },
            /* "3 lines will be removed and 5 lines will be added across 2 files:" -
               the extension builds it from fragments around the numbers. */
            summary: {
                ' line': ' سطر',
                's': '',
                'will be removed and': 'سيُحذف و',
                'will be added across ': 'سيُضاف في ',
                ' file': ' ملف'
            },
            /* "10 agents · click an agent for details" */
            agents: {
                'agent': 'وكيل',
                'agents': 'وكلاء',
                ' · click an agent for details': ' · اضغط على وكيل لعرض تفاصيله',
                /* "2 background tasks · click a task for details" */
                ' background ': ' ',
                'task': 'مهمة في الخلفية',
                'tasks': 'مهام في الخلفية',
                ' · click a task for details': ' · اضغط على مهمة لعرض تفاصيلها'
            },
            /* "2m 23s · 80.0k tokens", "345.6k tokens in context" */
            tokens: [
                [/ tokens in context$/, ' توكن في السياق'],
                [/ tokens$/, ' توكن']
            ],
            /* Agent and task details in the Agent map */
            detail: {
                'Working': 'يعمل',
                'Waiting for your permission': 'بانتظار إذنك',
                'Finished': 'اكتمل',
                'Failed': 'فشل',
                'Stopped': 'أُوقف',
                'Now': 'الآن',
                'Running': 'قيد التشغيل',
                'Ended': 'انتهى',
                'Stopping…': 'جارٍ الإيقاف…',
                'Prompt': 'الطلب',
                'Output': 'المخرجات',
                'Tool calls (': 'استدعاءات الأدوات (',
                'No output.': 'لا توجد مخرجات.',
                'No output yet.': 'لا توجد مخرجات بعد.',
                'Output is not available.': 'المخرجات غير متاحة.',
                'The agent could not be stopped. It may have finished already.': 'تعذّر إيقاف الوكيل. ربما انتهى بالفعل.',
                'The task could not be stopped. It may have finished already.': 'تعذّر إيقاف المهمة. ربما انتهت بالفعل.',
                'Spawned by ': 'أنشأه ',
                'the main agent': 'الوكيل الرئيسي',
                'Showing the end of ': 'يُعرض آخر جزء من ',
                ' of output.': ' من المخرجات.'
            },
            /* "Working · Explore · 1m 4s · background" */
            agentMeta: [
                [/^Working(?= · |$)/, 'يعمل'],
                [/^Waiting for your permission(?= · |$)/, 'بانتظار إذنك'],
                [/^Finished(?= · |$)/, 'اكتمل'],
                [/^Failed(?= · |$)/, 'فشل'],
                [/^Stopped(?= · |$)/, 'أُوقف'],
                [/ · background$/, ' · في الخلفية'],
                [/ · foreground$/, ' · في المقدمة']
            ],
            /* Permission prompt body */
            permDesc: {
                'Details': 'التفاصيل',
                'Scroll to the end of the message before approving it.': 'مرّر إلى نهاية الرسالة قبل الموافقة عليها.'
            },
            /* The Past conversations list */
            history: {
                'Sessions': 'الجلسات',
                'Archived sessions': 'الجلسات المؤرشفة',
                'Loading sessions…': 'جارٍ تحميل الجلسات…',
                'No sessions yet': 'لا توجد جلسات بعد',
                'No sessions found': 'لم يُعثر على جلسات',
                'No web sessions yet': 'لا توجد جلسات ويب بعد',
                'Start one at claude.ai/code': 'ابدأ واحدة على claude.ai/code',
                'Remote server is not connected': 'الخادم البعيد غير متصل',
                'Reconnect': 'إعادة الاتصال',
                'Connecting…': 'جارٍ الاتصال…',
                'Ungrouped': 'بدون مجموعة',
                'New group': 'مجموعة جديدة',
                'Unarchive session': 'إلغاء أرشفة الجلسة'
            },
            /* Placeholders of the message box and other inputs */
            placeholders: {
                'Queue another message…': 'أضف رسالة أخرى إلى قائمة الانتظار…',
                'Ask Claude to edit…': 'اطلب من Claude التعديل…',
                'Search sessions…': 'ابحث في الجلسات…',
                'Filter commands…': 'تصفية الأوامر…',
                'Type your answer…': 'اكتب إجابتك…',
                'Tell Claude what to do instead': 'أخبر Claude بما يفعله بدلًا من ذلك'
            },
            placeholderPatterns: [
                [/^(.+) to attach selected text$/, '$1 لإرفاق النص المحدد'],
                [/^(.+) to focus or unfocus Claude$/, '$1 للتركيز على Claude أو الخروج منه']
            ],
            /* "Thinking...", "Thought for 12s" */
            thinking: [
                [/^Thinking\.\.\.$/, 'يفكّر...'],
                [/^Thinking$/, 'تفكير'],
                [/^Thought for (\d+)s$/, 'فكّر لمدة $1 ث']
            ]
        },
        he: {
            ui: {
                'Fork conversation from here': 'פיצול השיחה מכאן',
                'Rewind code to here': 'החזרת הקוד לנקודה זו',
                'Fork conversation and rewind code': 'פיצול השיחה והחזרת הקוד',
                'Rewind': 'החזרה',
                'Rewind code': 'החזרת הקוד',
                'Fork and rewind': 'פיצול והחזרה',
                'Restore': 'שחזור',
                'Continue': 'המשך',
                'Never mind': 'ביטול',
                'A new forked conversation will be created after rewinding.': 'לאחר ההחזרה תיווצר שיחה מפוצלת חדשה.',
                'Checking code changes…': 'בודק שינויים בקוד…',
                'Restored files go back whole, losing later changes by anyone. Bash changes to other files are not undone.':
                    'קבצים משוחזרים חוזרים במלואם, וכל שינוי מאוחר יותר בהם יאבד, לא משנה מי ביצע אותו. שינויים של Bash בקבצים אחרים אינם מבוטלים.',
                'Restore code and conversation': 'שחזור הקוד והשיחה',
                'Restore conversation': 'שחזור השיחה',
                'Restore code': 'שחזור הקוד',
                'The conversation will be forked.': 'השיחה תפוצל.',
                'The conversation will be forked. The code will be unchanged.': 'השיחה תפוצל. הקוד לא ישתנה.',
                'The conversation will be unchanged.': 'השיחה לא תשתנה.',
                'The code ': 'הקוד ',
                'has not changed': 'לא השתנה',
                ', so no code will be restored.': ', ולכן שום קוד לא ישוחזר.',
                'Agent map': 'מפת סוכנים',
                'This session': 'הסשן הנוכחי',
                'Yes': 'כן',
                'No': 'לא',
                "Yes, and don't ask again": 'כן, ואל תשאל שוב',
                'Yes, allow all edits this session': 'כן, אפשר את כל העריכות בסשן הזה',
                'Yes, return to normal mode': 'כן, חזור למצב רגיל',
                'Yes, and manually approve edits': 'כן, ואשר עריכות ידנית',
                'Esc to cancel': 'הקש Esc לביטול',
                'Yes, and use auto mode': 'כן, והשתמש במצב אוטומטי',
                'Yes, and auto-accept': 'כן, ואשר אוטומטית',
                'Submit answers': 'שליחת התשובות',
                'No, keep planning': 'לא, המשך לתכנן',
                'Send feedback and keep planning': 'שלח משוב והמשך לתכנן',
                'Open transcript': 'פתיחת התמליל',
                'Stop agent': 'עצירת הסוכן',
                'Stop': 'עצירה',
                'Stopping…': 'עוצר…',
                'Slash commands': 'פקודות סלאש',
                'No matching commands.': 'אין פקודות תואמות.',
                'No slash commands available.': 'אין פקודות זמינות.'
            },
            permHeader: {
                'Do you want to proceed with ': 'להמשיך עם ',
                '?': '?',
                'Accept this plan?': 'לאשר את התוכנית?',
                'Continue planning': 'המשך תכנון',
                'Allow fetching this url?': 'לאפשר טעינה של הכתובת הזו?',
                'Allow network connection to this host?': 'לאפשר חיבור רשת לשרת הזה?',
                'Allow searching for this query?': 'לאפשר חיפוש של השאילתה הזו?'
            },
            summary: {
                ' line': ' שורות',
                's': '',
                'will be removed and': 'יוסרו ו-',
                'will be added across ': 'יתווספו ב-',
                ' file': ' קבצים'
            },
            agents: {
                'agent': 'סוכן',
                'agents': 'סוכנים',
                ' · click an agent for details': ' · לחצו על סוכן לפרטים',
                ' background ': ' ',
                'task': 'משימת רקע',
                'tasks': 'משימות רקע',
                ' · click a task for details': ' · לחצו על משימה לפרטים'
            },
            tokens: [
                [/ tokens in context$/, ' טוקנים בהקשר'],
                [/ tokens$/, ' טוקנים']
            ],
            detail: {
                'Working': 'עובד',
                'Waiting for your permission': 'ממתין לאישורך',
                'Finished': 'הסתיים',
                'Failed': 'נכשל',
                'Stopped': 'נעצר',
                'Now': 'עכשיו',
                'Running': 'פועל',
                'Ended': 'הסתיים',
                'Stopping…': 'עוצר…',
                'Prompt': 'הנחיה',
                'Output': 'פלט',
                'Tool calls (': 'קריאות לכלים (',
                'No output.': 'אין פלט.',
                'No output yet.': 'אין פלט עדיין.',
                'Output is not available.': 'הפלט אינו זמין.',
                'The agent could not be stopped. It may have finished already.': 'לא ניתן היה לעצור את הסוכן. ייתכן שהוא כבר סיים.',
                'The task could not be stopped. It may have finished already.': 'לא ניתן היה לעצור את המשימה. ייתכן שהיא כבר הסתיימה.',
                'Spawned by ': 'נוצר על ידי ',
                'the main agent': 'הסוכן הראשי',
                'Showing the end of ': 'מוצג סוף הפלט מתוך ',
                ' of output.': '.'
            },
            agentMeta: [
                [/^Working(?= · |$)/, 'עובד'],
                [/^Waiting for your permission(?= · |$)/, 'ממתין לאישורך'],
                [/^Finished(?= · |$)/, 'הסתיים'],
                [/^Failed(?= · |$)/, 'נכשל'],
                [/^Stopped(?= · |$)/, 'נעצר'],
                [/ · background$/, ' · ברקע'],
                [/ · foreground$/, ' · בחזית']
            ],
            permDesc: {
                'Details': 'פרטים',
                'Scroll to the end of the message before approving it.': 'גללו עד סוף ההודעה לפני שתאשרו אותה.'
            },
            history: {
                'Sessions': 'סשנים',
                'Archived sessions': 'סשנים בארכיון',
                'Loading sessions…': 'טוען סשנים…',
                'No sessions yet': 'אין עדיין סשנים',
                'No sessions found': 'לא נמצאו סשנים',
                'No web sessions yet': 'אין עדיין סשנים באינטרנט',
                'Start one at claude.ai/code': 'התחילו אחד ב-claude.ai/code',
                'Remote server is not connected': 'השרת המרוחק אינו מחובר',
                'Reconnect': 'התחברות מחדש',
                'Connecting…': 'מתחבר…',
                'Ungrouped': 'ללא קבוצה',
                'New group': 'קבוצה חדשה',
                'Unarchive session': 'הוצאת הסשן מהארכיון'
            },
            placeholders: {
                'Queue another message…': 'הוסיפו הודעה נוספת לתור…',
                'Ask Claude to edit…': 'בקשו מ-Claude לערוך…',
                'Search sessions…': 'חיפוש סשנים…',
                'Filter commands…': 'סינון פקודות…',
                'Type your answer…': 'הקלידו את תשובתכם…',
                'Tell Claude what to do instead': 'כתבו ל-Claude מה לעשות במקום'
            },
            placeholderPatterns: [
                [/^(.+) to attach selected text$/, '$1 לצירוף הטקסט המסומן'],
                [/^(.+) to focus or unfocus Claude$/, '$1 למיקוד או ליציאה מהמיקוד ב-Claude']
            ],
            thinking: [
                [/^Thinking\.\.\.$/, 'חושב...'],
                [/^Thinking$/, 'חשיבה'],
                [/^Thought for (\d+)s$/, 'חשב $1 שניות']
            ]
        },
        fa: {
            ui: {
                'Fork conversation from here': 'انشعاب گفتگو از اینجا',
                'Rewind code to here': 'بازگرداندن کد به این نقطه',
                'Fork conversation and rewind code': 'انشعاب گفتگو و بازگرداندن کد',
                'Rewind': 'بازگردانی',
                'Rewind code': 'بازگرداندن کد',
                'Fork and rewind': 'انشعاب و بازگردانی',
                'Restore': 'بازیابی',
                'Continue': 'ادامه',
                'Never mind': 'انصراف',
                'A new forked conversation will be created after rewinding.': 'پس از بازگردانی، یک گفتگوی انشعابی جدید ساخته می‌شود.',
                'Checking code changes…': 'در حال بررسی تغییرات کد…',
                'Restored files go back whole, losing later changes by anyone. Bash changes to other files are not undone.':
                    'فایل‌های بازیابی‌شده به‌طور کامل برمی‌گردند و هر تغییر بعدی روی آن‌ها، از هر کسی، از بین می‌رود. تغییرات Bash روی فایل‌های دیگر لغو نمی‌شود.',
                'Restore code and conversation': 'بازیابی کد و گفتگو',
                'Restore conversation': 'بازیابی گفتگو',
                'Restore code': 'بازیابی کد',
                'The conversation will be forked.': 'گفتگو منشعب می‌شود.',
                'The conversation will be forked. The code will be unchanged.': 'گفتگو منشعب می‌شود و کد تغییری نمی‌کند.',
                'The conversation will be unchanged.': 'گفتگو تغییری نمی‌کند.',
                'The code ': 'کد ',
                'has not changed': 'تغییری نکرده است',
                ', so no code will be restored.': '، بنابراین هیچ کدی بازیابی نمی‌شود.',
                'Agent map': 'نقشهٔ عامل‌ها',
                'This session': 'این نشست',
                'Yes': 'بله',
                'No': 'خیر',
                "Yes, and don't ask again": 'بله، و دیگر نپرس',
                'Yes, allow all edits this session': 'بله، همهٔ ویرایش‌ها در این نشست مجاز باشد',
                'Yes, return to normal mode': 'بله، بازگشت به حالت عادی',
                'Yes, and manually approve edits': 'بله، با تأیید دستی ویرایش‌ها',
                'Esc to cancel': 'برای لغو Esc را بزنید',
                'Yes, and use auto mode': 'بله، و از حالت خودکار استفاده کن',
                'Yes, and auto-accept': 'بله، با پذیرش خودکار',
                'Submit answers': 'ارسال پاسخ‌ها',
                'No, keep planning': 'خیر، برنامه‌ریزی را ادامه بده',
                'Send feedback and keep planning': 'ارسال بازخورد و ادامهٔ برنامه‌ریزی',
                'Open transcript': 'باز کردن رونوشت',
                'Stop agent': 'توقف عامل',
                'Stop': 'توقف',
                'Stopping…': 'در حال توقف…',
                'Slash commands': 'فرمان‌های اسلش',
                'No matching commands.': 'فرمان منطبقی پیدا نشد.',
                'No slash commands available.': 'فرمانی در دسترس نیست.'
            },
            permHeader: {
                'Do you want to proceed with ': 'ادامه با ',
                '?': '؟',
                'Accept this plan?': 'این برنامه را می‌پذیرید؟',
                'Continue planning': 'ادامهٔ برنامه‌ریزی',
                'Allow fetching this url?': 'دریافت این نشانی مجاز است؟',
                'Allow network connection to this host?': 'اتصال شبکه به این میزبان مجاز است؟',
                'Allow searching for this query?': 'جست‌وجوی این عبارت مجاز است؟'
            },
            /* Persian counts take a singular noun: "3 خط", "2 فایل" */
            summary: {
                ' line': ' خط',
                's': '',
                'will be removed and': 'حذف و',
                'will be added across ': 'اضافه می‌شود، در ',
                ' file': ' فایل'
            },
            agents: {
                'agent': 'عامل',
                'agents': 'عامل',
                ' · click an agent for details': ' · برای دیدن جزئیات روی یک عامل کلیک کنید',
                ' background ': ' ',
                'task': 'وظیفهٔ پس‌زمینه',
                'tasks': 'وظیفهٔ پس‌زمینه',
                ' · click a task for details': ' · برای دیدن جزئیات روی یک وظیفه کلیک کنید'
            },
            tokens: [
                [/ tokens in context$/, ' توکن در زمینه'],
                [/ tokens$/, ' توکن']
            ],
            detail: {
                'Working': 'در حال کار',
                'Waiting for your permission': 'در انتظار اجازهٔ شما',
                'Finished': 'تمام‌شده',
                'Failed': 'ناموفق',
                'Stopped': 'متوقف‌شده',
                'Now': 'اکنون',
                'Running': 'در حال اجرا',
                'Ended': 'پایان‌یافته',
                'Stopping…': 'در حال توقف…',
                'Prompt': 'دستور',
                'Output': 'خروجی',
                'Tool calls (': 'فراخوانی ابزارها (',
                'No output.': 'خروجی ندارد.',
                'No output yet.': 'هنوز خروجی ندارد.',
                'Output is not available.': 'خروجی در دسترس نیست.',
                'The agent could not be stopped. It may have finished already.': 'متوقف کردن عامل ممکن نشد. شاید کارش تمام شده باشد.',
                'The task could not be stopped. It may have finished already.': 'متوقف کردن وظیفه ممکن نشد. شاید تمام شده باشد.',
                'Spawned by ': 'ایجادشده توسط ',
                'the main agent': 'عامل اصلی',
                'Showing the end of ': 'بخش پایانی از ',
                ' of output.': ' خروجی نمایش داده شده است.'
            },
            agentMeta: [
                [/^Working(?= · |$)/, 'در حال کار'],
                [/^Waiting for your permission(?= · |$)/, 'در انتظار اجازهٔ شما'],
                [/^Finished(?= · |$)/, 'تمام‌شده'],
                [/^Failed(?= · |$)/, 'ناموفق'],
                [/^Stopped(?= · |$)/, 'متوقف‌شده'],
                [/ · background$/, ' · پس‌زمینه'],
                [/ · foreground$/, ' · پیش‌زمینه']
            ],
            permDesc: {
                'Details': 'جزئیات',
                'Scroll to the end of the message before approving it.': 'پیش از تأیید، تا انتهای پیام پایین بروید.'
            },
            history: {
                'Sessions': 'نشست‌ها',
                'Archived sessions': 'نشست‌های بایگانی‌شده',
                'Loading sessions…': 'در حال بارگذاری نشست‌ها…',
                'No sessions yet': 'هنوز نشستی وجود ندارد',
                'No sessions found': 'نشستی پیدا نشد',
                'No web sessions yet': 'هنوز نشست وبی وجود ندارد',
                'Start one at claude.ai/code': 'یکی را در claude.ai/code شروع کنید',
                'Remote server is not connected': 'سرور راه دور متصل نیست',
                'Reconnect': 'اتصال دوباره',
                'Connecting…': 'در حال اتصال…',
                'Ungrouped': 'بدون گروه',
                'New group': 'گروه جدید',
                'Unarchive session': 'خارج کردن نشست از بایگانی'
            },
            placeholders: {
                'Queue another message…': 'پیام دیگری به صف اضافه کنید…',
                'Ask Claude to edit…': 'از Claude بخواهید ویرایش کند…',
                'Search sessions…': 'جست‌وجوی نشست‌ها…',
                'Filter commands…': 'فیلتر فرمان‌ها…',
                'Type your answer…': 'پاسخ خود را بنویسید…',
                'Tell Claude what to do instead': 'به Claude بگویید به‌جای آن چه کند'
            },
            placeholderPatterns: [
                [/^(.+) to attach selected text$/, '$1 برای پیوست متن انتخاب‌شده'],
                [/^(.+) to focus or unfocus Claude$/, '$1 برای فوکوس روی Claude یا خروج از آن']
            ],
            thinking: [
                [/^Thinking\.\.\.$/, 'در حال فکر کردن...'],
                [/^Thinking$/, 'فکر کردن'],
                [/^Thought for (\d+)s$/, '$1 ثانیه فکر کرد']
            ]
        },
        ur: {
            ui: {
                'Fork conversation from here': 'یہاں سے گفتگو کی شاخ بنائیں',
                'Rewind code to here': 'کوڈ کو یہاں تک واپس لے جائیں',
                'Fork conversation and rewind code': 'گفتگو کی شاخ بنائیں اور کوڈ واپس لے جائیں',
                'Rewind': 'واپسی',
                'Rewind code': 'کوڈ کی واپسی',
                'Fork and rewind': 'شاخ اور واپسی',
                'Restore': 'بحال کریں',
                'Continue': 'جاری رکھیں',
                'Never mind': 'منسوخ کریں',
                'A new forked conversation will be created after rewinding.': 'واپسی کے بعد گفتگو کی ایک نئی شاخ بنائی جائے گی۔',
                'Checking code changes…': 'کوڈ کی تبدیلیاں جانچی جا رہی ہیں…',
                'Restored files go back whole, losing later changes by anyone. Bash changes to other files are not undone.': 'بحال کی گئی فائلیں پوری کی پوری واپس آتی ہیں، اور ان پر بعد میں کسی کی بھی کی گئی تبدیلیاں ضائع ہو جاتی ہیں۔ دوسری فائلوں پر Bash کی تبدیلیاں واپس نہیں ہوتیں۔',
                'Restore code and conversation': 'کوڈ اور گفتگو بحال کریں',
                'Restore conversation': 'گفتگو بحال کریں',
                'Restore code': 'کوڈ بحال کریں',
                'The conversation will be forked.': 'گفتگو کی شاخ بنائی جائے گی۔',
                'The conversation will be forked. The code will be unchanged.': 'گفتگو کی شاخ بنائی جائے گی اور کوڈ تبدیل نہیں ہوگا۔',
                'The conversation will be unchanged.': 'گفتگو تبدیل نہیں ہوگی۔',
                'The code ': 'کوڈ ',
                'has not changed': 'تبدیل نہیں ہوا',
                ', so no code will be restored.': '، اس لیے کوئی کوڈ بحال نہیں کیا جائے گا۔',
                'Agent map': 'ایجنٹ نقشہ',
                'This session': 'یہ سیشن',
                'Yes': 'ہاں',
                'No': 'نہیں',
                "Yes, and don't ask again": 'ہاں، اور دوبارہ نہ پوچھیں',
                'Yes, allow all edits this session': 'ہاں، اس سیشن میں تمام ترامیم کی اجازت دیں',
                'Yes, return to normal mode': 'ہاں، عام موڈ پر واپس جائیں',
                'Yes, and manually approve edits': 'ہاں، ترامیم کی دستی منظوری کے ساتھ',
                'Esc to cancel': 'منسوخ کرنے کے لیے Esc دبائیں',
                'Yes, and use auto mode': 'ہاں، اور خودکار موڈ استعمال کریں',
                'Yes, and auto-accept': 'ہاں، خودکار منظوری کے ساتھ',
                'Submit answers': 'جوابات بھیجیں',
                'No, keep planning': 'نہیں، منصوبہ بندی جاری رکھیں',
                'Send feedback and keep planning': 'رائے بھیجیں اور منصوبہ بندی جاری رکھیں',
                'Open transcript': 'ٹرانسکرپٹ کھولیں',
                'Stop agent': 'ایجنٹ روکیں',
                'Stop': 'روکیں',
                'Stopping…': 'روکا جا رہا ہے…',
                'Slash commands': 'سلیش کمانڈز',
                'No matching commands.': 'کوئی مماثل کمانڈ نہیں ملی۔',
                'No slash commands available.': 'کوئی کمانڈ دستیاب نہیں۔'
            },
            /* "کیا Bash کے ساتھ آگے بڑھیں؟" - the tool name sits between the two parts */
            permHeader: {
                'Do you want to proceed with ': 'کیا ',
                '?': ' کے ساتھ آگے بڑھیں؟',
                'Accept this plan?': 'کیا یہ منصوبہ قبول ہے؟',
                'Continue planning': 'منصوبہ بندی جاری رکھیں',
                'Allow fetching this url?': 'کیا یہ URL حاصل کرنے کی اجازت ہے؟',
                'Allow network connection to this host?': 'کیا اس ہوسٹ سے نیٹ ورک کنکشن کی اجازت ہے؟',
                'Allow searching for this query?': 'کیا اس سوال کی تلاش کی اجازت ہے؟'
            },
            summary: {
                ' line': ' لائن',
                's': '',
                'will be removed and': 'حذف ہوں گی اور',
                'will be added across ': 'شامل ہوں گی، ',
                ' file': ' فائل میں'
            },
            agents: {
                'agent': 'ایجنٹ',
                'agents': 'ایجنٹس',
                ' · click an agent for details': ' · تفصیلات کے لیے کسی ایجنٹ پر کلک کریں',
                ' background ': ' ',
                'task': 'بیک گراؤنڈ ٹاسک',
                'tasks': 'بیک گراؤنڈ ٹاسکس',
                ' · click a task for details': ' · تفصیلات کے لیے کسی ٹاسک پر کلک کریں'
            },
            tokens: [
                [/ tokens in context$/, ' ٹوکن سیاق میں'],
                [/ tokens$/, ' ٹوکن']
            ],
            detail: {
                'Working': 'کام جاری ہے',
                'Waiting for your permission': 'آپ کی اجازت کا انتظار',
                'Finished': 'مکمل',
                'Failed': 'ناکام',
                'Stopped': 'روک دیا گیا',
                'Now': 'ابھی',
                'Running': 'چل رہا ہے',
                'Ended': 'ختم',
                'Stopping…': 'روکا جا رہا ہے…',
                'Prompt': 'ہدایت',
                'Output': 'آؤٹ پٹ',
                'Tool calls (': 'ٹول کالز (',
                'No output.': 'کوئی آؤٹ پٹ نہیں۔',
                'No output yet.': 'ابھی کوئی آؤٹ پٹ نہیں۔',
                'Output is not available.': 'آؤٹ پٹ دستیاب نہیں۔',
                'The agent could not be stopped. It may have finished already.': 'ایجنٹ کو روکا نہیں جا سکا۔ ہو سکتا ہے یہ پہلے ہی ختم ہو چکا ہو۔',
                'The task could not be stopped. It may have finished already.': 'ٹاسک کو روکا نہیں جا سکا۔ ہو سکتا ہے یہ پہلے ہی ختم ہو چکا ہو۔',
                'Spawned by ': 'بنانے والا: ',
                'the main agent': 'مرکزی ایجنٹ',
                'Showing the end of ': 'آؤٹ پٹ کا آخری حصہ دکھایا جا رہا ہے، کل ',
                ' of output.': '۔'
            },
            agentMeta: [
                [/^Working(?= · |$)/, 'کام جاری ہے'],
                [/^Waiting for your permission(?= · |$)/, 'آپ کی اجازت کا انتظار'],
                [/^Finished(?= · |$)/, 'مکمل'],
                [/^Failed(?= · |$)/, 'ناکام'],
                [/^Stopped(?= · |$)/, 'روک دیا گیا'],
                [/ · background$/, ' · بیک گراؤنڈ'],
                [/ · foreground$/, ' · فور گراؤنڈ']
            ],
            permDesc: {
                'Details': 'تفصیلات',
                'Scroll to the end of the message before approving it.': 'منظوری سے پہلے پیغام کے آخر تک اسکرول کریں۔'
            },
            history: {
                'Sessions': 'سیشنز',
                'Archived sessions': 'آرکائیو شدہ سیشنز',
                'Loading sessions…': 'سیشنز لوڈ ہو رہے ہیں…',
                'No sessions yet': 'ابھی کوئی سیشن نہیں',
                'No sessions found': 'کوئی سیشن نہیں ملا',
                'No web sessions yet': 'ابھی کوئی ویب سیشن نہیں',
                'Start one at claude.ai/code': 'claude.ai/code پر ایک شروع کریں',
                'Remote server is not connected': 'ریموٹ سرور سے رابطہ نہیں',
                'Reconnect': 'دوبارہ جوڑیں',
                'Connecting…': 'جڑ رہا ہے…',
                'Ungrouped': 'بغیر گروپ',
                'New group': 'نیا گروپ',
                'Unarchive session': 'سیشن آرکائیو سے نکالیں'
            },
            placeholders: {
                'Queue another message…': 'قطار میں ایک اور پیغام شامل کریں…',
                'Ask Claude to edit…': 'Claude سے ترمیم کرنے کو کہیں…',
                'Search sessions…': 'سیشنز تلاش کریں…',
                'Filter commands…': 'کمانڈز فلٹر کریں…',
                'Type your answer…': 'اپنا جواب لکھیں…',
                'Tell Claude what to do instead': 'Claude کو بتائیں کہ اس کے بجائے کیا کرے'
            },
            placeholderPatterns: [
                [/^(.+) to attach selected text$/, '$1 منتخب متن منسلک کرنے کے لیے'],
                [/^(.+) to focus or unfocus Claude$/, '$1 Claude پر فوکس کرنے یا ہٹانے کے لیے']
            ],
            thinking: [
                [/^Thinking\.\.\.$/, 'سوچ رہا ہے...'],
                [/^Thinking$/, 'سوچ'],
                [/^Thought for (\d+)s$/, '$1 سیکنڈ سوچا']
            ]
        }
    };

    var PERMISSION = '[class*="permissionRequestContainer_"]';

    /* Tooltip of the toggle button */
    var BUTTON_TITLES = {
        en: 'Toggle RTL mode (Ctrl+Alt+R)',
        ar: 'تبديل اتجاه الكتابة (Ctrl+Alt+R)',
        he: 'החלפת כיוון הכתיבה (Ctrl+Alt+R)',
        fa: 'تغییر جهت نوشتار (Ctrl+Alt+R)',
        ur: 'لکھنے کی سمت بدلیں (Ctrl+Alt+R)'
    };

    /* The only places text is ever replaced, each with the table it uses.
       Messages, code and file names are outside all of them. */
    var SCOPES = [
        ['[class*="popupOption_"]', 'ui'],
        ['[role="dialog"] h3', 'ui'],
        ['[role="dialog"] [class*="actions_"] button', 'ui'],
        ['[role="dialog"] [class*="forkNote_"]', 'ui'],
        ['[role="dialog"] [class*="loading_"]', 'ui'],
        ['[role="dialog"] [class*="warning_"]', 'ui'],
        ['[role="dialog"] [class*="choiceGroup_"]', 'ui'],
        ['[role="dialog"] [class*="noChanges_"]', 'ui'],
        ['[role="dialog"] [class*="summary_"]', 'summary'],
        ['[role="dialog"] [class*="subtitle_"]', 'agents'],
        ['[role="dialog"] [class*="rowMain_"] [class*="rowTitle_"]', 'ui'],
        ['[role="dialog"] [class*="rowMeta_"]', 'tokens'],
        [PERMISSION + ' [class*="buttonContainer_"] > button', 'ui'],
        [PERMISSION + ' [class*="keyboardHints_"]', 'ui'],
        [PERMISSION + ' [class*="permissionRequestHeader_"]', 'permHeader'],
        [PERMISSION + ' [class*="permissionRequestDescription_"]', 'permDesc'],
        /* Agent map: background tasks and the details of an agent or task */
        ['[role="dialog"] [class*="tasksHeader_"]', 'agents'],
        ['[role="dialog"] [class*="activityLabel_"]', 'detail'],
        ['[role="dialog"] [class*="cardTitle_"]', 'detail'],
        ['[role="dialog"] [class*="failure_"]', 'detail'],
        ['[role="dialog"] [class*="sectionHeader_"]', 'detail'],
        ['[role="dialog"] [class*="meta_"]', ['detail', 'agentMeta']],
        /* The Past conversations list, the slash commands dialog and the
           "Thinking" label */
        ['[role="dialog"][aria-label="Past conversations"]', 'history'],
        ['[role="dialog"] [class*="emptyState_"]', 'ui'],
        ['[class*="thinkingSummary_"] > span', 'thinking']
    ];

    /* Attributes translated the same way: input placeholders. The message
       box shows its placeholder from data-placeholder. */
    var ATTR_SCOPES = [
        ['[data-placeholder]', 'data-placeholder', ['placeholders', 'placeholderPatterns']],
        ['[placeholder]', 'placeholder', ['placeholders', 'placeholderPatterns']]
    ];

    /* Dialogs whose layout follows the translation: right-to-left when
       translated, left-to-right otherwise (they would inherit RTL from the
       chat and scramble English text). Keyed by their English title. */
    var DIALOG_TITLES = {
        'Agent map': true,
        'Rewind': true,
        'Rewind code': true,
        'Fork and rewind': true
    };

    var WATCHED = '[class*="popupOption_"], [role="dialog"], ' + PERMISSION;

    /* Text node -> {en, tr}: the English it had and what we replaced it with.
       Lets a node be translated again, or restored, without losing the
       original - and spots when the extension has written new text into it. */
    var originals = new WeakMap();
    /* Element -> {attribute: {en, tr}}, the same for translated attributes */
    var attrOriginals = new WeakMap();
    var touched = false;

    /* table is a dictionary of exact strings, or a list of [pattern,
       replacement] pairs that are all applied in turn. */
    function lookup(text, table) {
        if (Array.isArray(table)) {
            for (var i = 0; i < table.length; i++) text = text.replace(table[i][0], table[i][1]);
            return text;
        }
        if (Object.prototype.hasOwnProperty.call(table, text)) return table[text];
        /* Match ignoring surrounding whitespace, but keep that whitespace. */
        var m = /^(\s*)([\s\S]*?)(\s*)$/.exec(text);
        if (m[2] && Object.prototype.hasOwnProperty.call(table, m[2])) {
            return m[1] + table[m[2]] + m[3];
        }
        return text;
    }

    /* The English a text node holds, even if we have translated it. */
    function sourceOf(node) {
        var seen = originals.get(node);
        return seen && node.nodeValue === seen.tr ? seen.en : node.nodeValue;
    }

    function sourceText(el) {
        var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
        var text = '', node;
        while ((node = walker.nextNode())) text += sourceOf(node);
        return text;
    }

    /* What source becomes: the first table that knows it wins. English when
       tables is null; null when no table knows it, so a text another scope
       translated is left alone rather than turned back. */
    function translate(source, tables) {
        if (!tables) return source;
        for (var i = 0; i < tables.length; i++) {
            var text = lookup(source, tables[i]);
            if (text !== source) return text;
        }
        return null;
    }

    /* Translate el's text with tables, or restore English when tables is null.
       Only nodeValue is changed, so the extension keeps the same text nodes it
       rendered and can still update them. */
    function localizeTree(el, tables) {
        var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
        var node;
        while ((node = walker.nextNode())) {
            var source = sourceOf(node);
            var text = translate(source, tables);
            if (text === null || text === node.nodeValue) continue;
            originals.set(node, { en: source, tr: text });
            node.nodeValue = text;
            touched = true;
        }
    }

    function localizeAttr(el, attr, tables) {
        var current = el.getAttribute(attr);
        if (current === null) return;
        var seen = attrOriginals.get(el) || {};
        var source = seen[attr] && current === seen[attr].tr ? seen[attr].en : current;
        var text = translate(source, tables);
        if (text === null || text === current) return;
        seen[attr] = { en: source, tr: text };
        attrOriginals.set(el, seen);
        el.setAttribute(attr, text);
        touched = true;
    }

    function tablesFor(lang, names) {
        return lang ? [].concat(names).map(function (name) { return STRINGS[lang][name]; }) : null;
    }

    /* Translate every scope el is inside of or contains. A full pass passes
       the whole document. */
    function localizeAround(el, lang) {
        var i, j, found;
        for (i = 0; i < SCOPES.length; i++) {
            var tables = tablesFor(lang, SCOPES[i][1]);
            var hit = el.closest(SCOPES[i][0]);
            if (hit) localizeTree(hit, tables);
            found = el.querySelectorAll(SCOPES[i][0]);
            for (j = 0; j < found.length; j++) localizeTree(found[j], tables);
        }
        for (i = 0; i < ATTR_SCOPES.length; i++) {
            var sel = ATTR_SCOPES[i][0], attr = ATTR_SCOPES[i][1];
            var attrTables = tablesFor(lang, ATTR_SCOPES[i][2]);
            if (el.matches(sel)) localizeAttr(el, attr, attrTables);
            found = el.querySelectorAll(sel);
            for (j = 0; j < found.length; j++) localizeAttr(found[j], attr, attrTables);
        }
    }

    /* Direction of the first letter in text: 'rtl', 'ltr', or null. */
    function textDir(text) {
        var m = /[A-Za-zÀ-ɏ֐-ࣿ]/.exec(text);
        if (!m) return null;
        return /[֐-ࣿ]/.test(m[0]) ? 'rtl' : 'ltr';
    }

    /* Set dir on an element, marking it so it can be cleaned up; null removes
       a dir this script set and leaves any other alone. */
    function setDir(el, dir) {
        if (!dir) {
            if (el.hasAttribute('data-ccrk-dir')) {
                el.removeAttribute('dir');
                el.removeAttribute('data-ccrk-dir');
            }
            return;
        }
        if (el.getAttribute('dir') !== dir) el.setAttribute('dir', dir);
        if (!el.hasAttribute('data-ccrk-dir')) el.setAttribute('data-ccrk-dir', '');
        touched = true;
    }

    function orient(on, lang) {
        var i;
        if (!on) {
            var marked = document.querySelectorAll('[data-ccrk-dir]');
            for (i = 0; i < marked.length; i++) setDir(marked[i], null);
            return;
        }
        var options = document.querySelectorAll('[class*="popupOption_"]');
        for (i = 0; i < options.length; i++) setDir(options[i], lang ? 'rtl' : null);

        var dialogs = document.querySelectorAll('[role="dialog"]');
        for (i = 0; i < dialogs.length; i++) {
            var title = dialogs[i].querySelector('h3');
            if (!title || !DIALOG_TITLES[sourceText(title).trim()]) continue;
            setDir(dialogs[i], lang ? 'rtl' : 'ltr');
            /* Agent rows hold free text (task names) - lay each one out in
               the direction of its own text. */
            var rows = dialogs[i].querySelectorAll('[class*="rowTitle_"]');
            for (var j = 0; j < rows.length; j++) {
                setDir(rows[j].parentNode, textDir(rows[j].textContent));
            }
        }

        /* Permission prompt: some button labels name a file or a rule and
           stay in English, so each part follows its own text. */
        var parts = document.querySelectorAll(PERMISSION + ' :is([class*="buttonContainer_"] > button, ' +
            '[class*="keyboardHints_"], [class*="permissionRequestHeader_"])');
        for (i = 0; i < parts.length; i++) {
            setDir(parts[i], lang ? textDir(parts[i].textContent) : null);
        }
    }

    /* Arabic, Persian, Urdu or Hebrew, by which script the user's messages
       use most; falls back to the editor's display language. Persian and Urdu
       share the Arabic script, so they are told apart by letters only one of
       them uses: Urdu tteh, ddal, rreh, noon ghunna, do-chashmi heh, heh goal
       and yeh barree; Persian pe, che, zhe, gaf, keheh and yeh; Arabic teh
       marbuta, kaf, yeh and alef maksura. Re-checked at most once a second. */
    var langCache = null, langCheckedAt = 0;
    function conversationLang() {
        if (FIXED_LANG) return STRINGS[FIXED_LANG] ? FIXED_LANG : null;
        var now = Date.now();
        if (now - langCheckedAt < 1000) return langCache;
        langCheckedAt = now;
        var text = '';
        var msgs = document.querySelectorAll('[class*="userMessage_"]');
        for (var i = 0; i < msgs.length; i++) text += msgs[i].textContent;
        var ar = (text.match(/[؀-ۿ]/g) || []).length;
        var he = (text.match(/[֐-׿]/g) || []).length;
        if (ar || he) {
            if (ar >= he) {
                var ur = (text.match(/[ٹڈڑںھہے]/g) || []).length;
                var fa = (text.match(/[پچژگکی]/g) || []).length;
                var arOnly = (text.match(/[ةكيى]/g) || []).length;
                langCache = ur && ur >= arOnly ? 'ur' : fa > arOnly ? 'fa' : 'ar';
            } else {
                langCache = 'he';
            }
        } else {
            var ui = (navigator.language || '').slice(0, 2).toLowerCase();
            langCache = STRINGS[ui] ? ui : null;
        }
        return langCache;
    }

    /* ------------------------------------------------------------------
       RTL state and toggle button
       ------------------------------------------------------------------ */

    function loadState() {
        try {
            var saved = localStorage.getItem(STORAGE_KEY);
            for (var i = 0; saved === null && i < LEGACY_STORAGE_KEYS.length; i++) {
                saved = localStorage.getItem(LEGACY_STORAGE_KEYS[i]);
            }
            return saved === '1';
        } catch (e) {
            return false;
        }
    }

    function saveState(on) {
        try { localStorage.setItem(STORAGE_KEY, on ? '1' : '0'); } catch (e) { /* not available */ }
    }

    /* Skip headers that belong to a message or to a dialog. */
    function isMainHeader(header) {
        return !header.closest('[class*="messagesContainer_"], [role="dialog"]');
    }

    /* The history and new-chat buttons in the header are rendered by the
       extension's shared icon-button component. Anchoring to the last of them
       puts our button in the same flex row, so nothing is pushed out of view. */
    function findAnchor() {
        var headers = document.querySelectorAll('[class*="header_"]');
        for (var i = 0; i < headers.length; i++) {
            if (!isMainHeader(headers[i])) continue;
            var buttons = headers[i].querySelectorAll('[class*="iconButton_"]');
            if (buttons.length) return buttons[buttons.length - 1];
        }
        return null;
    }

    function findHeader() {
        var headers = document.querySelectorAll('[class*="header_"]');
        for (var i = 0; i < headers.length; i++) {
            if (isMainHeader(headers[i])) return headers[i];
        }
        return null;
    }

    function rootEl() {
        return document.getElementById('root');
    }

    function isRtlOn() {
        var root = rootEl();
        return !!root && root.classList.contains(ROOT_CLASS);
    }

    function paint(btn) {
        var active = isRtlOn();
        btn.classList.toggle('ccrk-active', active);
        btn.setAttribute('aria-pressed', active ? 'true' : 'false');
    }

    /* Tooltip in the conversation's language. Set when the pointer arrives
       rather than on every update, so idle checks stay cheap. */
    function label(btn) {
        var text = BUTTON_TITLES[conversationLang()] || BUTTON_TITLES.en;
        btn.title = text;
        btn.setAttribute('aria-label', text);
    }

    function toggleRtl() {
        var root = rootEl();
        if (!root) return;
        saveState(root.classList.toggle(ROOT_CLASS));
        fullPass = true;
        var btn = document.getElementById(BTN_ID);
        if (btn) paint(btn);
        schedule();
    }

    function makeButton() {
        var btn = Object.assign(document.createElement('button'), {
            id: BTN_ID,
            type: 'button',
            textContent: '⇄'
        });
        label(btn);
        btn.addEventListener('mouseenter', function() { label(btn); });
        btn.addEventListener('click', toggleRtl);
        return btn;
    }

    /* Ctrl+Alt+R (Ctrl+Option+R on macOS) toggles RTL. Matched on the
       physical key, so it also works with an Arabic or Hebrew layout, and
       stopped here so the editor does not act on it too. */
    window.addEventListener('keydown', function(e) {
        if (!e.ctrlKey || !e.altKey || e.shiftKey || e.metaKey || e.code !== 'KeyR') return;
        e.preventDefault();
        e.stopPropagation();
        toggleRtl();
    }, true);

    function placeButton() {
        var existing = document.getElementById(BTN_ID);
        var anchor;
        if (existing) {
            /* A fallback button moves next to the native ones once they
               render; otherwise it would stay in the fallback spot for good. */
            if (!existing.classList.contains('ccrk-standalone')) return;
            anchor = findAnchor();
            if (!anchor) return;
            existing.parentNode.removeChild(existing);
        } else {
            anchor = findAnchor();
        }

        var btn = makeButton();
        if (anchor) {
            /* Copy the neighbour's classes so size, padding, hover and colours
               match the native buttons exactly. */
            btn.className = anchor.className;
            anchor.parentNode.insertBefore(btn, anchor.nextSibling);
        } else {
            var header = findHeader();
            if (!header) return;
            btn.classList.add('ccrk-standalone');
            header.appendChild(btn);
        }

        /* A re-render may have dropped an earlier button while RTL was on, so
           restore the pressed state from the root element rather than assuming
           the button starts off. */
        paint(btn);
    }

    /* Turn RTL back on if it was on last time. Returns false until #root exists. */
    function restoreState() {
        var root = rootEl();
        if (!root) return false;
        if (loadState()) root.classList.add(ROOT_CLASS);
        return true;
    }

    var restored = restoreState();

    /* Elements the extension changed since the last pass. Only these are
       checked, so a long conversation costs nothing extra while a reply
       streams. The whole page is checked at start, on toggle and when the
       language changes. */
    var dirty = [];
    var fullPass = true;
    var lastLang;

    function touches(el) {
        return !!(el.closest(WATCHED) || el.querySelector(WATCHED));
    }

    function update() {
        if (!restored) restored = restoreState();
        placeButton();
        var batch = dirty;
        dirty = [];
        var on = isRtlOn();
        if (!on && !touched) return;
        var lang = on ? conversationLang() : null;
        if (lang !== lastLang) {
            lastLang = lang;
            fullPass = true;
        }
        var full = fullPass;
        fullPass = false;
        var roots = full ? [document.documentElement] : Array.from(new Set(batch)).filter(function (el) {
            return el.isConnected;
        });
        for (var i = 0; i < roots.length; i++) localizeAround(roots[i], lang);
        if (full || roots.some(touches)) orient(on, lang);
        /* Everything is English again - nothing to watch until RTL is back */
        if (!on && full) touched = false;
    }

    function noteChanges(records) {
        for (var i = 0; i < records.length; i++) {
            var r = records[i];
            if (r.type === 'childList') {
                for (var j = 0; j < r.addedNodes.length; j++) {
                    var added = r.addedNodes[j];
                    dirty.push(added.nodeType === 1 ? added : r.target);
                }
            } else {
                var el = r.target.nodeType === 1 ? r.target : r.target.parentElement;
                if (el) dirty.push(el);
            }
        }
        schedule();
    }

    /* React re-renders drop the button and bring back English text, so check
       again on mutation - but coalesce the many mutations a streaming reply
       fires into one check per frame. */
    var scheduled = false;
    function schedule() {
        if (scheduled) return;
        scheduled = true;
        requestAnimationFrame(function() {
            scheduled = false;
            update();
        });
    }

    new MutationObserver(noteChanges).observe(document.body, {
        childList: true,
        characterData: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['placeholder', 'data-placeholder']
    });

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', update);
    else update();
})();
/* End Claude Code RTL Kit: toggle and translation */
"""

# The CSS block starts and ends with these lines
RTL_START_MARKER = "/* Claude Code RTL Kit: styles - added by claude_code_rtl_kit.py */"
RTL_END_MARKER = "/* End Claude Code RTL Kit: styles */"

# ...and the JS block with these
JS_START_MARKER = "/* Claude Code RTL Kit: toggle and translation - added by claude_code_rtl_kit.py */"
JS_END_MARKER = "/* End Claude Code RTL Kit: toggle and translation */"

# Every (start, end) pair a block may carry, current one first. Markers that
# earlier versions (named Claude Code Arabic RTL) and earlier RTL patches wrote
# stay listed, so such an install is detected, upgraded and removed rather than
# patched twice.
CSS_MARKERS = [
    (RTL_START_MARKER, RTL_END_MARKER),
    ("/* Claude Code Arabic RTL: styles - added by claude_code_arabic_rtl.py */",
     "/* End Claude Code Arabic RTL: styles */"),
    ("/* RTL Text Support for Claude Code VS Code / Cursor Extension - Added by script */",
     "/* End RTL Text Support for Claude Code VS Code / Cursor Extension */"),
    ("/* RTL Text Support for Claude Code VS Code Extension - Added by script */",
     "/* End RTL Text Support for Claude Code VS Code Extension */"),
]
JS_MARKERS = [
    (JS_START_MARKER, JS_END_MARKER),
    ("/* Claude Code Arabic RTL: toggle and translation - added by claude_code_arabic_rtl.py */",
     "/* End Claude Code Arabic RTL: toggle and translation */"),
    ("/* RTL Toggle Button - Added by script */", "/* End RTL Toggle Button */"),
]


# ----------------------------------------------------------------------
# Finding Claude Code
# ----------------------------------------------------------------------

# Folder each editor keeps under a user's home, and the name shown for it.
# The -server folders belong to remote sessions (SSH, WSL, containers).
EDITOR_LABELS = {
    ".vscode": "VS Code",
    ".vscode-server": "VS Code (Remote)",
    ".cursor": "Cursor",
    ".cursor-server": "Cursor (Remote)",
    ".kiro": "Kiro",
    ".kiro-server": "Kiro (Remote)",
    ".trae": "Trae",
    ".trae-server": "Trae (Remote)",
    ".trae-cn": "Trae CN",
    ".trae-cn-server": "Trae CN (Remote)",
}
EDITOR_DIRS = tuple(EDITOR_LABELS)

# Windows profile folders that do not belong to a person
NON_USER_PROFILES = {"public", "default", "default user", "all users"}

# One Claude Code install: a label for messages, its folder, and the two
# webview files. js is None when index.js is missing.
Install = namedtuple("Install", "name folder css js")


def running_in_wsl():
    """True inside Windows Subsystem for Linux"""
    if os.environ.get("WSL_DISTRO_NAME"):
        return True
    return platform.system() == "Linux" and "microsoft" in platform.release().lower()


def _child_dirs(path):
    """Sorted sub-folders of path - none when it cannot be read"""
    try:
        with os.scandir(path) as entries:
            return sorted(entry.path for entry in entries if entry.is_dir())
    except OSError:
        return []


def _wsl_homes_from_windows():
    r"""Linux homes inside WSL, seen from Windows: \\wsl.localhost\<distro>\home\<user>"""
    # Both share names lead to the same distributions; use the first that answers.
    for share in ("\\\\wsl.localhost", "\\\\wsl$"):
        homes = [user for distro in _child_dirs(share)
                 for user in _child_dirs(os.path.join(distro, "home"))]
        if homes:
            return homes
    return []


def _windows_homes_from_wsl():
    """Windows profiles seen from WSL, on every mounted drive: /mnt/<drive>/Users/<user>"""
    return [profile for drive in _child_dirs("/mnt")
            for profile in _child_dirs(os.path.join(drive, "Users"))
            if os.path.basename(profile).lower() not in NON_USER_PROFILES]


def _homes_to_search():
    """Home folders that may hold an editor's extensions, without repeats"""
    if platform.system() == "Windows":
        homes = [os.environ.get("USERPROFILE") or str(Path.home())]
        homes += _wsl_homes_from_windows()
    else:
        homes = [str(Path.home())]
        if platform.system() == "Linux":
            homes += _child_dirs("/home")     # other accounts, e.g. when run with sudo
            if running_in_wsl():
                homes += _windows_homes_from_wsl()
    return list(dict.fromkeys(homes))


def find_installs():
    """Every Claude Code install in a supported editor, as Install tuples"""
    installs = []
    for home in _homes_to_search():
        for editor, label in EDITOR_LABELS.items():
            pattern = os.path.join(glob.escape(os.path.join(home, editor, "extensions")),
                                   "anthropic.claude-code-*")
            for folder in sorted(glob.glob(pattern)):
                css = os.path.join(folder, "webview", "index.css")
                js = os.path.join(folder, "webview", "index.js")
                if os.path.isfile(css):
                    installs.append(Install(label + " - " + os.path.basename(folder), folder,
                                            css, js if os.path.isfile(js) else None))
    return installs


# ----------------------------------------------------------------------
# Editing the webview files
#
# A block is appended as "\n" + block, and every block starts and ends with
# a newline, so cutting it out again gives back the file byte for byte.
# ----------------------------------------------------------------------

def _read(path):
    # newline='' keeps the file's own line endings; text mode would otherwise
    # rewrite every LF in the bundle as CRLF on Windows.
    with open(path, 'r', encoding='utf-8', newline='') as f:
        return f.read()


def _write(path, content):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(content)


def _holds_block(text, markers):
    return any(start in text for start, _ in markers)


def _file_holds_block(path, markers):
    """True when the file at path (which may be None) carries one of the blocks"""
    try:
        return bool(path) and _holds_block(_read(path), markers)
    except Exception:
        return False


def _cut_block(text, start, end):
    """text without its first start..end block; unchanged when there is none
    or its end marker is missing"""
    head, found, rest = text.partition(start)
    if not found or end not in rest:
        return text
    tail = rest.split(end, 1)[1]
    # Take back the "\n" written before the block and the block's own
    # opening and closing newlines.
    for _ in range(2):
        if head.endswith("\n"):
            head = head[:-1]
    if tail.startswith("\n"):
        tail = tail[1:]
    return head + tail


def _without_blocks(text, markers):
    """Remove every block, current or from an older version, duplicates too.

    Returns (text, True), or (text, False) untouched when a block has lost its
    end marker - its length is then unknown and nothing can be cut safely.
    """
    for start, end in markers:
        while start in text:
            shorter = _cut_block(text, start, end)
            if shorter == text:
                return text, False
            text = shorter
    return text, True


def _install_state(path, block, markers):
    """'installed', 'outdated' or 'missing' for one patched file"""
    try:
        text = _read(path) if path else ""
    except Exception:
        return "missing"
    if not _holds_block(text, markers):
        return "missing"
    clean, intact = _without_blocks(text, markers)
    return "installed" if intact and clean + "\n" + block == text else "outdated"


def _report_damaged(path, label, name):
    print(f"  {label} {name}: the added block has lost its end marker, so it is left as it is.")
    print(f"       Reinstalling the Claude Code extension gives a clean {os.path.basename(path)}.")


def _inject(path, block, markers, label, name):
    """Append block to the file, replacing any copy an earlier run left. Returns success."""
    try:
        current = _read(path)
        clean, intact = _without_blocks(current, markers)
        if not intact:
            _report_damaged(path, label, name)
            return False
        wanted = clean + "\n" + block
        if wanted == current:
            print(f"  {label} {name}: already current")
            return True

        # The backup has to be the untouched file. One that carries a block -
        # older versions could save it that way - is rewritten as well.
        backup = path + ".bak"
        if not os.path.exists(backup) or _file_holds_block(backup, markers):
            _write(backup, clean)
            print(f"  {label} {name}: original saved as {os.path.basename(backup)}")

        _write(path, wanted)
        print(f"  {label} {name}: {'added' if clean == current else 'updated to this version'}")
        return True
    except PermissionError:
        print(f"  {label} {name}: no permission to change {path}")
        print("       Run it again from an administrator terminal (Windows) or with sudo.")
    except Exception as e:
        print(f"  {label} {name}: failed - {e}")
    return False


def _remove(path, markers, label, name):
    """Take the block out: from a clean .bak if there is one, else by cutting it. Returns success."""
    if not _file_holds_block(path, markers):
        print(f"  {label} {name}: nothing to remove")
        return True

    backup = path + ".bak"
    usable_backup = os.path.exists(backup) and not _file_holds_block(backup, markers)
    if usable_backup:
        try:
            os.replace(backup, path)
            print(f"  {label} {name}: original restored")
            return True
        except OSError as e:
            print(f"  {label} {name}: could not restore the backup ({e}); cutting the block out instead")

    try:
        clean, intact = _without_blocks(_read(path), markers)
        if not intact:
            _report_damaged(path, label, name)
            return False
        _write(path, clean)
        # A backup that carries the block would only bring it back later.
        if os.path.exists(backup) and not usable_backup:
            os.remove(backup)
        print(f"  {label} {name}: removed")
        return True
    except Exception as e:
        print(f"  {label} {name}: failed - {e}")
    return False


# ----------------------------------------------------------------------
# Translation language
#
# Picked when installing and saved, so later runs - including the hourly
# auto re-apply after an update - install the same language.
# ----------------------------------------------------------------------

LANGUAGES = (
    ("auto", "Automatic - follow the language of your messages"),
    ("ar", "Arabic"),
    ("fa", "Persian (Farsi)"),
    ("ur", "Urdu"),
    ("he", "Hebrew"),
    ("en", "English - no translation"),
)
LANGUAGE_NAMES = dict(LANGUAGES)
SETTINGS_PATH = os.path.join(os.path.expanduser("~"), ".claude-code-rtl-kit.json")
# Where versions named Claude Code Arabic RTL saved it
LEGACY_SETTINGS_PATH = os.path.join(os.path.expanduser("~"), ".claude-code-arabic-rtl.json")
FIXED_LANG_LINE = "var FIXED_LANG = null;"


def load_language():
    """The saved translation language, or 'auto'"""
    path = SETTINGS_PATH
    if not os.path.exists(path) and os.path.exists(LEGACY_SETTINGS_PATH):
        path = LEGACY_SETTINGS_PATH
    try:
        with open(path, encoding="utf-8") as f:
            lang = json.load(f).get("language")
    except (OSError, ValueError, AttributeError):
        return "auto"
    return lang if lang in LANGUAGE_NAMES else "auto"


def save_language(lang):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump({"language": lang}, f)
        return True
    except OSError as e:
        print(f"  Could not save the language choice: {e}")
        return False


def js_block(lang):
    """The JS block, with the translation language fixed unless 'auto'"""
    if lang == "auto":
        return RTL_JS_CODE
    return RTL_JS_CODE.replace(FIXED_LANG_LINE, f"var FIXED_LANG = '{lang}';", 1)


def ask_language(current):
    """Ask for a translation language in the menu; Enter keeps current."""
    print("\n  Language of the translated menus and dialogs:")
    for i, (code, label) in enumerate(LANGUAGES, 1):
        print(f"    {i}. {label}{'  (current)' if code == current else ''}")
    try:
        answer = input(f"\n  Choose (1-{len(LANGUAGES)}, Enter keeps current): ").strip()
    except EOFError:
        return current
    if answer.isdigit() and 1 <= int(answer) <= len(LANGUAGES):
        return LANGUAGES[int(answer) - 1][0]
    if answer:
        print("  Not a listed choice - keeping the current language.")
    return current


def add_rtl_support(ext, lang="auto"):
    """Install (or update) both blocks in one Claude Code install. Returns success."""
    ok = _inject(ext.css, RTL_CSS_RULES, CSS_MARKERS, "CSS:", ext.name)
    if ext.js is None:
        print(f"  JS:  {ext.name}: index.js is missing, so there is no button or translation")
        return ok
    return _inject(ext.js, js_block(lang), JS_MARKERS, "JS: ", ext.name) and ok


def remove_rtl_support(ext):
    """Take both blocks out of one Claude Code install. Returns success."""
    results = [_remove(ext.css, CSS_MARKERS, "CSS:", ext.name)]
    if ext.js:
        results.append(_remove(ext.js, JS_MARKERS, "JS: ", ext.name))
    return all(results)


STATE_TEXT = {
    "installed": "INSTALLED",
    "outdated": "OUTDATED - run --apply to update it",
    "missing": "Not installed",
}


def check_status(installs):
    """Print what is installed where, the language and the schedule"""
    lang = load_language()
    print(f"\nClaude Code installs: {len(installs)}")
    for ext in installs:
        print(f"\n  {ext.name}")
        for label, path, block, markers in (("CSS", ext.css, RTL_CSS_RULES, CSS_MARKERS),
                                            ("JS ", ext.js, js_block(lang), JS_MARKERS)):
            backup = "backup kept" if path and os.path.exists(path + ".bak") else "no backup"
            print(f"    {label}  {STATE_TEXT[_install_state(path, block, markers)]} ({backup})")
        print(f"    Folder: {ext.folder}")
    print(f"\n  Translation language: {LANGUAGE_NAMES[lang]}")
    print(f"  Automatic re-apply: {'ON (hourly)' if is_auto_apply_enabled() else 'OFF'}")


# ----------------------------------------------------------------------
# Automatic re-apply
#
# Every Claude Code update installs into a fresh folder without RTL. A
# scheduled job runs --apply every hour; when nothing changed it does nothing.
# ----------------------------------------------------------------------

AUTO_TASK_NAME = "Claude Code RTL Kit"           # Windows Task Scheduler
CRON_TAG = "# claude-code-rtl-kit auto-apply"   # marks our crontab line
# Names versions called Claude Code Arabic RTL scheduled under. Their command
# points to claude_code_arabic_rtl.py, which no longer exists after the rename.
LEGACY_TASK_NAME = "Claude Code Arabic RTL"
LEGACY_CRON_TAG = "# claude-code-arabic-rtl auto-apply"


def _auto_apply_command():
    """The command the scheduler runs: this script with --apply.

    On Windows pythonw.exe is used when present, so no console window
    flashes up every hour.
    """
    python = sys.executable
    if platform.system() == "Windows":
        pythonw = os.path.join(os.path.dirname(python), "pythonw.exe")
        if os.path.exists(pythonw):
            python = pythonw
    return [python, os.path.abspath(__file__), "--apply"]


def _cron_line(command):
    quoted = " ".join(shlex.quote(part) for part in command)
    return f"@hourly {quoted} >/dev/null 2>&1 {CRON_TAG}"


def _cron_without(crontab):
    """crontab text with our line, and any older version's, removed"""
    lines = [line for line in crontab.splitlines()
             if CRON_TAG not in line and LEGACY_CRON_TAG not in line]
    return "".join(line + "\n" for line in lines)


def _cron_with(crontab, line):
    """crontab text with our line present exactly once"""
    return _cron_without(crontab) + line + "\n"


def _run(args, stdin_text=None):
    """Run a command; returns (exit code, combined output). Never raises."""
    try:
        # stdout/stderr pipes rather than capture_output, which needs 3.7
        result = subprocess.run(args, input=stdin_text, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, universal_newlines=True)
    except OSError as e:
        return 127, str(e)
    return result.returncode, (result.stdout or "") + (result.stderr or "")


def _read_crontab():
    """Current crontab, "" when the user has none, or None if cron is missing."""
    code, out = _run(["crontab", "-l"])
    if code == 127:
        return None
    return out if code == 0 else ""


def is_auto_apply_enabled():
    if platform.system() == "Windows":
        return _run(["schtasks", "/Query", "/TN", AUTO_TASK_NAME])[0] == 0
    crontab = _read_crontab()
    return bool(crontab) and CRON_TAG in crontab


def has_legacy_auto_apply():
    """True when a version named Claude Code Arabic RTL left a schedule"""
    if platform.system() == "Windows":
        return _run(["schtasks", "/Query", "/TN", LEGACY_TASK_NAME])[0] == 0
    crontab = _read_crontab()
    return bool(crontab) and LEGACY_CRON_TAG in crontab


def _drop_legacy_auto_apply():
    """Delete that schedule. Returns success."""
    if platform.system() == "Windows":
        return _run(["schtasks", "/Delete", "/F", "/TN", LEGACY_TASK_NAME])[0] == 0
    return _run(["crontab", "-"], _cron_without(_read_crontab() or ""))[0] == 0


def enable_auto_apply():
    """Schedule --apply every hour. Returns success."""
    command = _auto_apply_command()
    if platform.system() == "Windows":
        code, out = _run(["schtasks", "/Create", "/F", "/SC", "HOURLY",
                          "/TN", AUTO_TASK_NAME,
                          "/TR", subprocess.list2cmdline(command)])
    else:
        crontab = _read_crontab()
        if crontab is None:
            print("  'crontab' was not found, so nothing can be scheduled on this system.")
            return False
        code, out = _run(["crontab", "-"], _cron_with(crontab, _cron_line(command)))
    if code != 0:
        print(f"  Could not schedule automatic re-apply: {out.strip()}")
        return False
    # cron's old line went with _cron_without; the old Windows task is separate
    if platform.system() == "Windows" and has_legacy_auto_apply():
        _drop_legacy_auto_apply()
    print("  Automatic re-apply is ON: RTL is re-added every hour after Claude Code updates.")
    print(f"  It runs: {subprocess.list2cmdline(command)}")
    print("  Keep this folder where it is - the schedule points to this copy of the script.")
    return True


def disable_auto_apply(quiet_if_off=False):
    """Remove the schedule. Returns success."""
    if has_legacy_auto_apply() and not _drop_legacy_auto_apply():
        print("  Could not remove the schedule an older version (Claude Code Arabic RTL) made.")
        return False
    if not is_auto_apply_enabled():
        if not quiet_if_off:
            print("  Automatic re-apply is already OFF.")
        return True
    if platform.system() == "Windows":
        code, out = _run(["schtasks", "/Delete", "/F", "/TN", AUTO_TASK_NAME])
    else:
        code, out = _run(["crontab", "-"], _cron_without(_read_crontab() or ""))
    if code != 0:
        print(f"  Could not turn off automatic re-apply: {out.strip()}")
        return False
    print("  Automatic re-apply is OFF.")
    return True


MENU_TITLE = "Claude Code RTL Kit - for VS Code, Cursor, Kiro and Trae"


def show_menu(auto_on):
    items = (
        "Install or update RTL support",
        "Uninstall RTL support",
        "Show status",
        f"Turn automatic re-apply {'OFF' if auto_on else 'ON'}",
        "Quit",
    )
    print("\n" + MENU_TITLE)
    print("-" * len(MENU_TITLE))
    for number, text in enumerate(items, 1):
        print(f"  [{number}] {text}")


FLAGS = ("--apply", "--remove", "--status", "--auto-apply", "--no-auto-apply")
USAGE = ("Usage: python claude_code_rtl_kit.py "
         "[--apply [--lang auto|ar|fa|ur|he|en] | --remove | --status | --auto-apply | --no-auto-apply]")


def _parse_args(args):
    """(flag, lang) from the command line, or None when it is not valid.

    lang is None unless --lang was given; it is accepted only with --apply.
    """
    lang = None
    rest = []
    i = 0
    while i < len(args):
        if args[i] == "--lang" and i + 1 < len(args):
            lang = args[i + 1]
            i += 2
            continue
        if args[i].startswith("--lang="):
            lang = args[i][len("--lang="):]
        else:
            rest.append(args[i])
        i += 1
    flag = rest[0] if rest else None
    if len(rest) > 1 or (flag is not None and flag not in FLAGS):
        return None
    if lang is not None and (lang not in LANGUAGE_NAMES or flag != "--apply"):
        return None
    return flag, lang


def _pause(prompt):
    """Wait for Enter in an interactive console; never block or fail a script."""
    if not sys.stdin or not sys.stdin.isatty():
        return
    try:
        input(prompt)
    except EOFError:
        pass


def _run_all(action, what, installs):
    """Run action on every install - all of them, even after a failure. True if all worked."""
    print(f"\n{what}...\n")
    results = [action(ext) for ext in installs]
    print("\nReload the editor window to see the change: Ctrl+Shift+P > Developer: Reload Window")
    return all(results)


def _apply_all(installs, lang):
    print(f"\nTranslation language: {LANGUAGE_NAMES[lang]}")
    return _run_all(lambda ext: add_rtl_support(ext, lang), "Installing RTL support", installs)


def _remove_all(installs):
    """Remove RTL everywhere - and the schedule, which would add it back."""
    ok = _run_all(remove_rtl_support, "Removing RTL support", installs)
    return disable_auto_apply(quiet_if_off=True) and ok


def _install_from_menu(installs):
    lang = ask_language(load_language())
    if save_language(lang):
        _apply_all(installs, lang)


def _menu_loop(installs):
    """The interactive menu. Returns the exit code."""
    while True:
        auto_on = is_auto_apply_enabled()
        show_menu(auto_on)
        try:
            choice = input("\n  Choose 1-5: ").strip()
        except EOFError:
            return 0    # input ran out, e.g. it was piped in
        if choice == "5":
            return 0
        actions = {
            "1": lambda: _install_from_menu(installs),
            "2": lambda: _remove_all(installs),
            "3": lambda: check_status(installs),
            "4": disable_auto_apply if auto_on else enable_auto_apply,
        }
        if choice not in actions:
            print("\n  Type a number from 1 to 5.")
            continue
        print()
        actions[choice]()
        _pause("\nPress Enter to go back to the menu...")


def main():
    """Returns the process exit code."""
    args = sys.argv[1:]
    parsed = _parse_args(args)
    if parsed is None:
        print(USAGE)
        return 0 if args in (["-h"], ["--help"]) else 2
    flag, lang = parsed

    # A language given on the command line is kept for later runs.
    if lang is not None and not save_language(lang):
        return 1

    # A schedule made under the old name runs a script that no longer exists;
    # move it over to this one.
    if flag in (None, "--apply") and has_legacy_auto_apply():
        print("Moving automatic re-apply over from Claude Code Arabic RTL...")
        enable_auto_apply()

    # The schedule does not depend on an extension being installed yet.
    if flag == "--auto-apply":
        return 0 if enable_auto_apply() else 1
    if flag == "--no-auto-apply":
        return 0 if disable_auto_apply() else 1

    print(f"Running on {platform.system()} {platform.release()}{' under WSL' if running_in_wsl() else ''}")
    installs = find_installs()
    if not installs:
        print("\nClaude Code was not found in VS Code, Cursor, Kiro or Trae.")
        print("Install the Claude Code extension in one of them, then run this again.")
        if flag == "--remove":
            # Still drop the schedule, so nothing gets re-added later.
            return 0 if disable_auto_apply(quiet_if_off=True) else 1
        if flag is None:
            _pause("\nPress Enter to close...")
        return 1
    print(f"Claude Code installs found: {len(installs)}")

    commands = {
        "--apply": lambda: _apply_all(installs, lang or load_language()),
        "--remove": lambda: _remove_all(installs),
        "--status": lambda: check_status(installs) or True,
    }
    if flag in commands:
        return 0 if commands[flag]() else 1
    return _menu_loop(installs)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nStopped.")
        sys.exit(130)
    except Exception as e:
        print(f"\nSomething went wrong: {e}")
        # Keep a double-clicked console window open, but never block a script.
        if len(sys.argv) == 1:
            _pause("Press Enter to close...")
        sys.exit(1)
