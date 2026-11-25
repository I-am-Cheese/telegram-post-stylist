# Telegram syntax and explanatory notation

Official references consulted during learning:
- https://t.me/s/TelegramTips/100 — shortcut examples **bold**, __italic__, ||spoiler||, ~~strikethrough~~; desktop monospace/code.
- https://telegram.org/faq — select text in composer to apply bold/italic/monospace/link/quote and other formats.
- https://telegramdesktop.github.io/tdesktop/changelog/ — desktop Markdown shortcuts are applied on sending.

The final output deliberately does **not** depend on these shortcuts parsing in every client. The owner requested a plain TXT plus an explanatory Russian scheme for applying formatting manually. Do not switch back to MarkdownV2/HTML, or treat the Russian tags as Telegram API markup.

Examples:
```text
<цитата>
<жирный>Важная строка.</жирный>
Обычный текст той же цитаты.
</цитата>

<ссылка "https://t.me/ExitDLC"> Подписаться на ExitDLC </ссылка "https://t.me/ExitDLC">
```

Quotes must form their own block, not half a line. A normal hyperlink's visible caption is in TXT; its target is in the scheme. A raw URL is plain visible text only when the post should actually display that URL. Don't invent links from a guessed username. The renderer colors link captions cyan and draws native-looking quote blocks; it doesn't send message entities to Telegram.
