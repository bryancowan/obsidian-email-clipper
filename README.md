# obsidian-email-clipper

Convert email newsletters into [Obsidian Web Clipper](https://obsidian.md/clipper)-compatible markdown notes (`.eml` → vault).

Built for paywalled newsletters that the browser-extension Web Clipper can't reach. Save the email as `.eml`, run it through `email-clipper`, and a properly-formatted note lands in your `Reading List` folder with the same frontmatter shape as a regular web clip.

## Features

- Parses `.eml` files (drag-and-drop friendly from any Mac email client)
- Strips newsletter chrome (top nav, footers, tracking pixels)
- Unwraps table-based email layouts so the markdown reads like an article
- Builds frontmatter that matches the Obsidian Web Clipper default template exactly — `title`, `source`, `author` (as wikilinks), `published`, `created`, `description`, `tags`, `status`
- Per-sender configuration: subject prefix stripping, author override, custom tags, canonical URL construction
- Optional macOS launchd watcher: drop `.eml` into a folder, note appears in your vault automatically
- Bundled config for **Bloomberg *Money Stuff*** (Matt Levine). Adding more newsletters is a small config edit.

## Install

Requires Python 3.11+ and macOS for the optional folder watcher (the CLI itself is cross-platform).

```bash
git clone https://github.com/bryancowan/obsidian-email-clipper.git
cd obsidian-email-clipper
make install
```

`make install` creates a runtime venv at `~/Library/Application Support/email-clipper/`, installs the package, and bootstraps a launchd watcher on `~/Obsidian Inbox/`. Drop any `.eml` into that folder and a note appears in your vault within seconds.

> **Why a separate runtime venv?** macOS TCC blocks launchd-spawned processes from reading `~/Documents/`, where most people clone repos. The runtime lives elsewhere so the watcher always works regardless of where you put the source.

### Configure your vault path

Default vault target is `~/Obsidian/Reading List/`. Override with an environment variable:

```bash
export EMAIL_CLIPPER_VAULT="$HOME/Path/To/Your Vault/Reading List"
make install   # picks up the env var into the script
```

Or pass `--vault` on each CLI invocation.

## Usage

### Folder watcher (recommended)

```
1. Drop foo.eml into ~/Obsidian Inbox/
2. Note appears at ~/Obsidian/Reading List/{title} - {timestamp}.md
3. The .eml is moved to ~/Obsidian Inbox/processed/ on success
   (or ~/Obsidian Inbox/failed/ on error)
```

Logs: `~/Library/Logs/email-clipper.log`

### Manual CLI

```bash
~/Library/Application\ Support/email-clipper/venv/bin/email-clipper path/to/email.eml
~/Library/Application\ Support/email-clipper/venv/bin/email-clipper path/to/email.eml --vault /custom/Reading\ List
```

Output: a single `.md` file named `{title} - {YYYY-MM-DDTHHmmss±ZZZZ}.md`.

## Make targets

| Command | What it does |
|---|---|
| `make install` | First-time setup |
| `make refresh` | Push code changes from this repo into the live runtime |
| `make reload` | Bootout + bootstrap the launchd agent (pick up plist changes) |
| `make uninstall` | Tear down — leaves the inbox folder and vault notes alone |
| `make status` | Show launchd state |
| `make logs` | Tail conversion + error logs |
| `make test` | Run pytest in a local dev venv |
| `make dev` | Create a local `.venv/` with an editable install |

## Adding a newsletter

1. Open `src/email_clipper/senders.py`
2. Add a `SenderConfig` keyed by the sender's `From:` address:

   ```python
   "newsletter@example.com": SenderConfig(
       name="Example Newsletter",
       subject_prefix="Example: ",
       tags=["clippings", "ExampleNewsletter"],
       author_override="Jane Doe",
       url_builder="example_newsletter",  # optional
   ),
   ```

3. If the newsletter publishes its articles to a predictable URL, add a builder in `src/email_clipper/url_builder.py` and reference its name in the config above.
4. If the sender uses a tracking-redirect domain not yet recognized, add it to `is_tracker_redirect()` in `src/email_clipper/extract.py`.
5. `make test` to verify nothing broke; `make refresh` to push.

Unknown senders fall back to a generic config: the `From:` display name as author, `["clippings"]` as tags, and an empty `source` field.

## How it works

```
.eml ─┬─► parser (stdlib email)
      ├─► sender lookup (From: → publication config)
      ├─► HTML extraction
      │   ├─ strip script/style/tracking pixels
      │   ├─ unwrap layout tables (table/tr/td → div)
      │   └─ find "View in browser" link
      ├─► URL fallback
      │   └─ if VIB is a tracker redirect, build canonical URL from title + date
      ├─► HTML → Markdown (markdownify)
      │   ├─ trim leading chrome (everything before first ## heading)
      │   └─ trim trailing footer (Follow Us / Unsubscribe / etc.)
      ├─► frontmatter (manual YAML to match Web Clipper exactly)
      └─► writer ─► {title} - {timestamp}.md in vault
```

## Limitations

- **Inline tracker URLs are kept verbatim.** Decoding sender-side click-tracking redirects (e.g. `links.message.bloomberg.com/s/c/...`) requires HTTP, which v1 deliberately avoids. Links remain functional through the redirect.
- **Images stay remote.** No download to vault attachments.
- **macOS-only watcher.** The folder watcher uses launchd. The CLI itself runs anywhere Python does.

## License

[MIT](LICENSE) © 2026 Bryan Cowan
