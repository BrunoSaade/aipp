---
name: feature-announcement-writer
description: Generate a ready-to-send pt-BR feature announcement for team chat (Slack, WhatsApp, Google Chat, Teams) from one or more GitHub PRs or a pasted PR description. Reads PR body, spec/PRD docs and commits via gh, traces every claim to its source, lints channel formatting, and adapts to audiences (squad, stakeholders, suporte, end-user changelog). Use when user says "announce this feature", "write the team announcement for PR 22", "draft a message about this PR for the channel", "anuncia essa feature", "gera o comunicado do PR", or "escreve o changelog pro cliente". Do NOT use for writing the PR description itself (use generate-pr-description), versioned release-notes files, or marketing copy.
metadata:
  author: Bruno Saade - github.com/BrunoSaade
  version: "1.0.0"
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
3. **Write the message** (structure below), one per audience.
4. **Evidence gate** (below), then lint.
5. **Reply**: the message(s), then outside them a short `🔍 Fontes` list and, if any, `⚠️ Revisar antes de enviar`.

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

Every sentence must trace to the source: PR body, a doc in the pack, a commit headline, or the file summary.

1. Map each claim to its source. Drop unsourced claims; never fill gaps with plausible benefits or metrics ("em segundos", "50% mais rápido").
2. Reasonable but unstated inferences, unconfirmed spec items and anything that depends on deploy status go to `⚠️ Revisar antes de enviar`, outside the message.
3. Save each message to a temp file and run `python scripts/lint_announcement.py <file> --channel <channel>` (add `--max-chars 800` for `stakeholders`/`changelog`). Fix every finding; repeat until `ok`.

The lint catches paths, Jira refs, English, formatting and length. It cannot catch an invented fact: step 1 is on you.

## Examples

Real runs on three PRs with empty descriptions, in `assets/examples/`:

`announcement*.md` files target WhatsApp/Google Chat unless named `-slack`.

- `pr-10/` QR scan lookup: `announcement.md` (squad), `announcement-slack.md`, `announcement-stakeholders.md`, `announcement-changelog.md`, `sources.md`
- `pr-22/` batch device creation (24 commits, +7k lines): `announcement.md`, `sources.md`
- `pr-13/` landing page: `announcement.md`, `sources.md` (flags unconfirmed deploy)
