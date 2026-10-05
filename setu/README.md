# Setu — CWI Studio's build of Twenty

Setu (सेतु, "bridge") is [Twenty](https://github.com/twentyhq/twenty) rebranded and run by CWI Studio as a hosted CRM.
Live at **https://setu.cwistudio.in**. Public source (AGPL §13): https://github.com/aniket328/setu, branch `setu`.

| | |
|---|---|
| `upstream` | twentyhq/twenty — never pushed to |
| `origin` | aniket328/setu (GitHub fork; Actions disabled; push over SSH) |
| `setu` | our branch = an upstream release tag + our commits. Base today: **twenty/v2.44.0** |

## Licence — read before changing anything
Twenty's core is AGPL-3.0 (our duty: keep this fork public and in sync with what is deployed; keep their copyright
notices; their name/logo must not appear in the UI). **Files marked `@license Enterprise` are under Twenty's
commercial licence** (Stripe billing, record sharing, advanced permissions, SSO): never edit them, never enable
those features in production without a Twenty Enterprise subscription. `rebrand.py` skips them. The **DPA
template** (`core-modules/dpa`) is a legal document naming Twenty, PBC — it is excluded from the rebrand and must
be replaced by CWI's own legal text before any DPA is offered.

## What we change
| Change | Where | Merge cost |
|---|---|---|
| Name and links (Lingui `msgstr` in all locales + plain strings) | `setu/rebrand.py` — never hand-edit | re-run |
| Icons (every Android/iOS/Windows size), OG image, integration logo | `setu/brand/build_assets.mjs` | re-run |
| Docker build compiles catalogs only (extract would reset English to "Twenty") | `packages/twenty-docker/twenty/Dockerfile` | small |
| Deploy kit | `setu/deploy/` (`build.sh`, `docker-compose.yml`) | none |

Not rebranded on purpose: webhook headers, code identifiers (`TwentyORM`, `twenty-*` packages), tests, seeds,
migrations, Enterprise files, the DPA.

## Taking an upstream release
```bash
git fetch upstream --tags && git merge twenty/vX.Y.Z      # conflicts in .po/branding: take upstream, the scripts redo them
python3 setu/rebrand.py && node setu/brand/build_assets.mjs
python3 setu/rebrand.py --check                           # must print "would change 0 files"
git commit -am "setu: rebrand twenty vX.Y.Z" && git push origin setu
```
Build + deploy: rsync to `/opt/setu-src` on stepapp-ops-runner, `setu/deploy/build.sh <tag>` (~10 min, 8 cores), set
`SETU_RELEASE` in `/opt/setu/setu.env`, `docker compose --env-file setu.env -p setu up -d`.

## Hosting model today
Single-workspace mode (`IS_MULTIWORKSPACE_ENABLED=false`): one workspace, invite-only after the first admin signs
up. Per-client workspaces need multi-workspace mode, which gives each workspace a subdomain
(`client.setu.cwistudio.in`) — Cloudflare's free certificate does not cover that second level; decide (Advanced
Certificate, a dedicated apex domain, or one instance per client) before onboarding a second customer.
