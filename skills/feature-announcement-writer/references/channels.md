# Channel formatting

Pick the target channel before writing. Default: Slack. Lint with the flag below.

| Element | Slack (`--channel slack`) | WhatsApp (`--channel whatsapp`) | Google Chat (`--channel gchat`) | Teams (`--channel teams`) |
|---|---|---|---|---|
| Bold | **none**: plain text, emphasis via emoji + line breaks | `*text*` | `*text*` | `*text*` |
| Bullet list | `• item` | `- item` (renders as bullet) | `- item` | `- item` |
| Heading | none | none | none | `# title` |
| Link | bare URL | bare URL | bare URL | `[label](url)` |

Rules:

- **Slack gets no markers at all.** Users paste the message into the composer, and Slack keeps pasted text plain: `*text*` shows literal asterisks (confirmed by pasting into Slack and by Slack help below). Slack mrkdwn only renders for typed text or API/webhook posts.
- **Never use `**double asterisk**`** on any channel; none documents it.
- Title = 🚀 line, never a `#` heading (only Teams renders headings).
- Teams renders Markdown only when sent from desktop/web, not mobile.
- Keep it under ~3000 characters (`lint_announcement.py` default): long chat messages get collapsed and skimmed.

Sources (checked 2026-10-29):
- Slack, pasted text stays plain: https://slack.com/help/articles/360039953113
- Slack mrkdwn (API/webhook only): https://docs.slack.dev/messaging/formatting-message-text/
- WhatsApp: `*bold*` and `- ` bullets render on paste (`assets/whats_evidence.png`)
- Google Chat: https://support.google.com/chat/answer/7649118
- Teams: https://support.microsoft.com/en-US/teams/chat/use-markdown-formatting-in-microsoft-teams
