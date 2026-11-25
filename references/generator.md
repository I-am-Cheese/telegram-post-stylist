# Post generator contract

Python 3.9+ and Pillow, using fonts already installed. On Windows the original tests used Segoe UI regular/semibold/italic and Segoe UI Emoji. The renderer discovers those without copying proprietary fonts into the repository. Linux/macOS fallbacks or explicit font paths are supported; font differences can change wrapping. Do not promise pixel identity across font systems.

```text
python scripts/render_post.py --spec job.json --out outputs/post-001 --scheme-out work/post-001-formatting.txt
```

The output folder must be new or empty. It contains exactly `Пост без форматирования.txt` and `Предпросмотр.png`. The optional scheme-out file is working material for the agent; do not attach it as an extra deliverable unless requested. The CLI also reports the final scheme so the agent can place it in a `text` code block in chat.

Specification:
```json
{
  "scheme": "<жирный>Заголовок</жирный>\n\n<курсив>Вводная.</курсив>\n\n<цитата>Важная информация.</цитата>",
  "include_footer": true,
  "profile": "optional path to another channel-profile.json",
  "width": 840
}
```

Supply the edited body with **Russian tags only**. The renderer appends the profile footer by default; `include_footer: false` is valid only after a user opt-out. Do not encode editorial discretion in that flag. The renderer recognizes an already correct footer to avoid duplication. If the draft has a plain unlinked footer, remove it from the body specification and let the renderer add the linked version.

The link grammar is exactly `<ссылка "URL"> caption </ссылка "URL">`; other tags have no attributes. URLs are HTTP(S) or tg links. Malformed/unknown tags, mismatched nesting and nonmatching closing-link URLs fail validation rather than produce a misleading preview. The parser removes line-only wrapper tags from plain text, normalizes excessive empty lines, and preserves intended paragraph/hard-line breaks. Literal less-than signs that aren't tag-shaped text are ordinary characters.

Optional profile font entries `fonts.regular`, `fonts.bold`, `fonts.italic`, `fonts.bold_italic`, `fonts.mono`, `fonts.emoji` may point to local TTF/OTF files; relative paths resolve against that profile. Profile settings are channel name/avatar letter, default footer and preview width/minimum height/clock/label. Missing mandatory regular font/Pillow is a real dependency blocker; never silently replace Cyrillic with missing-glyph boxes. The generator doesn't fetch fonts, install packages or access Telegram.

PNG layout: dark phone UI, clearly labeled test preview, channel header, rounded message bubble, word wrapping, text emphasis, mono backing and quote backgrounds, cyan links, no fabricated subscriber/view statistics. Long words wrap by character cluster to avoid horizontal clipping. Very long posts may create a taller image; review the real output before delivering. It is a synthetic mockup, not an actual client screenshot.

Run `scripts/smoke_test.py` after modifying generator behavior. It checks the parser/outputs against real example contracts, footer defaults/opt-out, nested formatting, wrong URL closures, malformed tags, long-line bounds and Unicode paths. It does not judge prose quality or verify external facts.
