---
name: feature-announcement-writer
description: Generate a ready-to-send pt-BR feature announcement for team chat (Slack, WhatsApp, Google Chat, Teams) from one or more GitHub PRs or a pasted PR description. Reads PR body, spec/PRD docs and commits via gh, backs every line with a verbatim quote checked by script, lints channel formatting, adapts to audiences (squad, stakeholders, suporte, end-user changelog), and can attach a recorded video of the feature via the demo skill. Use when user says "announce this feature", "write the team announcement for PR 22", "draft a message about this PR for the channel", "anuncia essa feature", "gera o comunicado do PR", "escreve o changelog pro cliente", or "anuncia o PR 22 com vídeo". Do NOT use for writing the PR description itself (use generate-pr-description), versioned release-notes files, or marketing copy.
metadata:
  author: Bruno Saade - github.com/BrunoSaade
  version: "1.1.0"
---

# Feature Announcement Writer

Turn a merged (or ready) PR into a chat message the whole team can read: what changed, why it matters, what to watch. Output is always Brazilian Portuguese (`pt-BR`), even though these instructions are in English.

Paths below (`scripts/`, `references/`, `assets/`) are relative to this skill's base directory. Run scripts by absolute path, e.g. `python <skill-base-dir>/scripts/lint_announcement.py`, since the working directory is usually the user's repo.

## Workflow

1. **Collect the source.**
   - PR number(s) or URL(s) → `python scripts/fetch_pr_context.py <PR> [<PR> ...] [--repo OWNER/REPO]`. The pack has the PR body, product docs added in the PR (PRD/spec/requirements), commit headlines and file counts (source/tests/docs/generated). PR bodies are often empty (`(vazia)`): rely on docs and commits then. Never fetch the full diff; open one file with `gh api` only when a commit is ambiguous.
   - Pasted text or a `.md` file → use it as the only source.
   - `gh` fails (auth, no repo access) → show the exact error, suggest `gh auth login` / `gh auth switch` or pasting the PR text. Never invent PR content.
2. **Pick channel and audience.** Defaults: `slack`, `squad`. Use what the user states; ask only when they want several audiences and didn't name them. Rules: `references/channels.md`, `references/audiences.md`.
3. **Write the cited draft** (structure below), one per audience.
4. **Evidence gate** (below): citations check, then lint.
5. **Reply**: the message(s) from `message.md`, then outside them `🔍 Fontes` (the verified `[n] "quote"` list) and, if any, `⚠️ Revisar antes de enviar`. Video requested → see Video (opt-in).

## Message structure (`squad`)

`*bold*` below is for WhatsApp, Google Chat and Teams. For Slack, drop every `*` and use `•` bullets: pasted text stays plain there.

```markdown
🚀 *[Título curto da feature]*

Pessoal, disponibilizamos [melhoria] em [área] para [benefício principal].

✨ *O que mudou?*

[emoji] [mudança 1, em linguagem de produto]

[emoji] [mudança 2]

🧪 [só se o PR tiver testes]

🎯 *Benefícios da melhoria*
- [benefício com fonte]

Caso encontrem qualquer comportamento inesperado durante os testes ou uso da funcionalidade, por favor reportem no canal da squad. 🙌
```

Other audiences change emphasis and length, not facts: see `references/audiences.md`.

## Content rules

- Lead with user/business impact; translate implementation into product language.
- Keep technical detail only when it changes usage, QA or operations (browser support, HTTPS, unchanged flows, compatibility, limits).
- Preserve constraints: when the feature appears or not, what stays unchanged, validation rules, limits.
- Docs explain *why*, commits confirm *what shipped*. A doc item with no backing commit/file is not shipped. Items listed as out of scope or backlog are never announced as delivered.
- Mention automated tests only when the pack shows `tests:` > 0 or the description says so.
- Manual testing appears only as the closing call to report issues.
- Emojis organize sections (🚀 title, ✨ changes, 📝 forms, 🔎 search/filters, 🛡️ safety, 🚫 restrictions, 🔄 compatibility, 💬 messages/copy, 🧪 tests, 🎯 benefits, 🙌 closing); not one per sentence.
- Never include: file paths, test commands, Jira links/keys, English sentences, `**double asterisk**` (any `*` on Slack), verbatim PR text.

## Evidence gate

Every sentence must quote its source: PR body, a doc in the pack, a commit headline, or the file summary. Work in a temp dir inside the user's repo.

1. Save the source to `pack.md`: the `fetch_pr_context.py` output (redirect stdout), or the pasted text as-is.
2. Write `draft.md`: the message with `[n]` at the end of every line that states a fact (several allowed: `[1][3]`), `[—]` on lines with no fact (title, section header, closing), then a `---fontes---` line and one `[n] "verbatim quote from pack.md"` per source. Quote the pack exactly (≥ 15 chars, unaccented docs stay unaccented); never paraphrase inside the quotes. No quote → drop the claim; never fill gaps with plausible benefits or metrics ("em segundos", "50% mais rápido").
3. Run `python scripts/check_citations.py pack.md draft.md --out message.md`. Fix every finding (drop the claim or quote the real text) and repeat until `ok`. Reread each `no claim:` line it lists: a fact hidden behind `[—]` is a cheat.
4. Run `python scripts/lint_announcement.py message.md --channel <channel>` (add `--max-chars 800` for `stakeholders`/`changelog`). Fix in `draft.md`, rerun both until `ok`.
5. Reasonable but unstated inferences, unconfirmed spec items and anything that depends on deploy status go to `⚠️ Revisar antes de enviar`, outside the message.

`check_citations.py` proves each quote exists in the source, not that it supports the sentence; one quote, one claim keeps that easy to eyeball. The lint catches paths, Jira refs, English, formatting and length.

## Video (opt-in)

Only when the user asks for a video/demo and the PR changes a screen. Needs the `demo` skill (Tech Leads Club), Docker and the app running locally.

1. Pick one flow the cited claims already describe (PRD user story, main commit). The video shows shipped behavior; it never adds a claim.
2. Hand it to the `demo` skill: name `pr-<n>-<flow>`, sign in before `record()`, record, then check 3-4 frames. If sign-in needs a secret, start the app with a local-only override (e.g. `wrangler dev --var ADMIN_PASSWORD:demo-local-only`) instead of reading or hardcoding the real one.
3. Add `🎥 Vídeo em anexo: <fluxo> [n]` right after the opening line, cited like any other line, and give the `video.mp4` path in the reply to attach on send.
4. Recording fails (app down, no Docker, `failed.json`) → send the announcement without the line and say why. The text never waits on the video.

## Examples

Real runs on three PRs with empty descriptions, in `assets/examples/` (`pr-13` predates the citation check):

`announcement*.md` files target WhatsApp/Google Chat unless named `-slack`.

- `pr-10/` QR scan lookup: `draft.md` (cited draft that passed `check_citations.py`), `announcement.md` (squad), `announcement-slack.md`, `announcement-stakeholders.md`, `announcement-changelog.md`
- `pr-22/` batch device creation (24 commits, +7k lines): `draft.md`, `announcement.md` (with the `🎥` line), `video.mp4` (the real recording)
- `pr-13/` landing page: `announcement.md`, `sources.md` (flags unconfirmed deploy)
