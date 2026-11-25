---
name: telegram-post-stylist
description: Write or edit Russian Telegram channel posts in the learned ExitDLC style, delivering plain TXT, a Russian angle-bracket formatting scheme in chat and a phone preview PNG. Use for a post topic, a draft to restyle, or requests like «напиши пост», «оформи сообщение», «следующее сообщение».
---

# Telegram post stylist

## Always load the learned rules

At the first use in each new chat, read this file, [learned-style.md](references/learned-style.md), [decision-history.md](references/decision-history.md), `assets/channel-profile.json`, and the small accepted examples in `examples/`. These preserve the relevant learning history, including superseded output formats. After compaction reread anything lost. Do not load the unrelated video-editing skill/archive. Current explicit user instructions override earlier style decisions. This is a repeatable writing/rendering workflow, not a transfer of hidden model state or a promise of identical new prose.

The raw saved tests/scripts are preserved in [history/README.md](history/README.md) with a checksummed archive; use that evidence to recover a specific detail, never as a replacement for current rules. The original drafts and reference links are indexed in `references/learning-record.json`. Do not automatically repeat outdated outputs or run historical scripts.

Discover optional owner settings at `<project>/local-state/telegram-post-stylist.json`, then `~/.codex/telegram-post-stylist/profile.json`. Bundled ExitDLC links are the original creator's explicit default; other channel owners should configure their own profile once. Never silently use another person's channel branding for a different channel.

## Intake and writing

- If no topic/draft is provided, ask briefly: «Пришли тему или свой черновик поста». Stay ready for the next message. If the topic/draft is present and sufficient, do the work without a questionnaire.
- Accept rough text or voice transcription. Correct grammar, punctuation, address and structure; write naturally and consistently to **«вы»** by default. A topic alone needs an original post. A draft may be rewritten, but **preserve its intended meaning, supplied facts, stance and promises**. Do not replace them with a different narrative, add deadlines/conditions/guarantees or insert an unasked lecture. The final correction in training preferred restrained edits over creative changes of meaning.
- Distinguish editing user-supplied information from verifying it. Never claim an APK, security statement or other external fact was independently checked when it wasn't. Do not treat a routine copyedit as an unsolicited technical audit. If a genuinely necessary fact/link is missing, ask only for that missing item; do not invent it.
- Use Telegram only: short meaningful paragraphs, deliberate blank lines, a clear heading when useful, restrained emojis, and formatting that has a purpose. Monospace is for commands/identifiers rather than random decoration. Not every post needs the same number/order of blocks.
- **Always include the two configured footer links, unless the user explicitly asks to omit them.** Do not decide yourself that the topic is an exception. Preserve the exact footer captions and URLs in the profile. This supersedes the earlier suggestion of discretionary exceptions.

## Exact delivery contract

Every completed post has three components:
1. One UTF-8 **`.txt` file containing only the publishable plain text**, emojis and line breaks. No formatting markers, Russian tags, HTML, explanatory headings, preview labels or instructions in that file. Footer captions are ordinary text in it; their hidden URLs are provided in the chat scheme.
2. In chat, a `text` code block with the same post and these **Russian explanatory tags**:
   - `<жирный>текст</жирный>`
   - `<курсив>текст</курсив>`
   - `<моно>текст</моно>`
   - `<цитата>текст</цитата>`; nesting bold/italic inside a quote is allowed.
   - **`<ссылка "https://link.com/test"> текст ссылки </ссылка "https://link.com/test">`** — repeat the identical quoted URL in the closing tag, with the same custom spacing. Do not replace it with `</ссылка>`, HTML `<a>`, or Markdown links inside the scheme.
3. One **PNG mobile Telegram mockup** matching the exact text and intended emphasis, quotes and link colors. Embed it using its absolute local path. It is a labeled synthetic preview, not proof of a publication or a guarantee of identical automatic wrapping across phones.

Deliver the TXT link, scheme and PNG directly. No duplicate formatted post above the scheme, no HTML/Markdown file attachment, no tutorials or extra versions unless requested. A brief essential clarification may precede the deliverables, but routine output should be compact.

## Deterministic generator

Use `scripts/render_post.py` with a JSON specification; see [generator.md](references/generator.md). It derives TXT, scheme and PNG from one source, checks nesting/link closures, appends the exact footer once, and wraps the text at the chosen phone width. Use the learned dark theme by default. Read/reuse the script instead of rewriting the renderer for every post.

Before delivery open the actual generated PNG, check clipping, quote boundaries, visible emojis, blank lines, complete footer and equality of plain text to the scheme. Fix the specification and rerender when needed. Do not claim every device uses those exact line breaks. Preserve previous tests/revisions; don't overwrite the user's originals.

## Telegram, publishing and economy

These tags are a **human editing map**, not Telegram input syntax. Native quote/link styling is applied through Telegram's formatting UI or actual message entities. Do not promise that pasting these Russian tags, HTML or MarkdownV2 into a regular composer creates the intended post. Official sources and the distinction are in [telegram-formatting.md](references/telegram-formatting.md).

The owner initially allowed delivery to their own Saved Messages; the final normal delivery is TXT + scheme + PNG. Don't send/publish posts to a channel or other people without an explicit request for that destination. If sending to Saved Messages is requested and supported, verify the destination and formatting and report only observed success. The original UI attempt failed; it is not evidence that a message was sent. Never extract Telegram auth sessions/tokens to bypass a UI failure.

Routine posts use one agent and the reusable local renderer, with no subagents or repeated web research. For an unusually large batch, at most one bounded reviewer when authorized and useful; don't fork the entire chat or delegate each paragraph. Reuse Pillow/fonts already present; install only missing dependencies when needed. Don't repeatedly poll a download. Preview assets and completed TXT/PNG are outputs; temporary render files can be removed only within explicitly owned scratch folders, preserving outputs, profiles and accepted preferences. Do not publish skill updates/GitHub changes as part of normal post writing.
