# OPERATING.md — how the kit and its bundles fit together day to day

Two kinds of repo, and they are **independent**:

- **The kit** (this repo) — the machinery. Checks, the projection builder, the base ontology
  and the agent instructions. It contains no knowledge.
- **A bundle** (`privacy-act-okf`, and any future one) — the knowledge. Concepts, log, index,
  its own domain ontology. It carries the kit inside itself at `okf-kit/` as a git submodule,
  **pinned to one specific kit commit**.

The kit does not know its bundles exist. There is no list of them anywhere, and nothing
propagates automatically.

---

## The short answers

**Working on the kit — do I need to pull a bundle first?**
No. Never. Kit work touches no bundle. Change it, test it, push it, done.

**Working on a bundle — do I need to be inside the kit, or pull other bundles?**
No. Open that bundle and work in it. The kit is already inside it, at `okf-kit/`. Other
bundles are irrelevant and untouched.

**How does a bundle get a kit change?**
Only when you tell it to. In that bundle, double-click **`update-kit.command`**. It moves the
pin to the newest kit, rebuilds, re-checks, and tells you whether to keep or roll back.

**So a kit change reaches a bundle only if I go and fetch it?**
Yes, and that is deliberate. One kit change cannot break three bundles at once, and each
bundle records which kit version last validated it. If a bundle looks wrong later, the pin
tells you what it was checked with.

---

## Working on the kit

```
cd okf-spec-build
# edit
python3 -m unittest discover -s tests     # must pass
python3 scripts/okf_check.py .            # must exit 0
git add -A && git commit && git push
```

**Push before any bundle pins to it.** A bundle can pin to a commit that exists only on your
machine — git will let you — and it will work locally and fail for everyone else. See
*Consequences* below.

Nothing else is required. You do not need to update any bundle. Bundles are pinned and will
carry on with the version they have.

## Working on a bundle

```
cd privacy-act-okf
# add or edit concepts; put new source material in inbox/
./check.command          # builds projections + runs conformance
git add -A && git commit && git push
```

`check.command` initialises the submodule on first run, so a fresh clone needs nothing extra.

You are not editing the kit. `okf-kit/` is read-only as far as bundle work is concerned — do
not edit files inside it. If something in the machinery is wrong, fix it in the kit repo and
then pull it in.

## Moving a bundle to a newer kit

```
cd privacy-act-okf
./update-kit.command
```

It prints the kit version before and after, rebuilds projections, and re-runs the checks.

- **Checks pass** → `git add okf-kit && git commit -m "Move to newer OKF kit"` and push. The
  new pin is now recorded.
- **Checks fail** → the new kit found something. Either fix it, or roll back with
  `git checkout -- okf-kit` and nothing has changed.

**Bundles do not have to move together.** One can sit on an older kit indefinitely.

## Starting a new bundle

```
mkdir new-bundle && cd new-bundle && git init
git submodule add https://github.com/adamsonwalter/okf-spec-build.git okf-kit
cp okf-kit/templates/log-domain-init.md log.md      # set your domain and date
cp okf-kit/ontology.md ontology.md                  # then cut it down to your domain
cp okf-kit/.github/workflows/bundle-conformance.yml .github/workflows/conformance.yml
```

Copy `check.command` and `update-kit.command` from an existing bundle. Then declare
`# Projection` and `# Authority Posture` in your `ontology.md` — everything else has defaults.

---

## Consequences — what actually breaks, and what merely waits

**The one that genuinely breaks.**

*Pinning a bundle to a kit commit you have not pushed.* Git allows it. It works on your
machine because the commit is in your local clone. It fails everywhere else — CI, another
machine, a colleague — with `fatal: reference is not a tree`. Silent where you are, broken
where you are not.

**Fix:** push the kit first, then pin. `update-kit.command` fetches from the remote, so using
it avoids this entirely. The trap is only there if you pin by hand.

**Everything else is a wait, not a break.**

| Situation | What happens | Recovery |
|---|---|---|
| Kit changed, bundle not updated | Bundle keeps using its pinned kit. New checks simply do not run. | Run `update-kit.command` whenever you like. |
| Bundle work not pushed | Local only, like any repo. | Push. |
| Kit work not pushed | Bundles are unaffected — they are pinned to older commits. | Push. |
| Ran `update-kit` but did not commit `okf-kit` | You are testing against the new kit; the repo still records the old one, and CI checks the old one. Shows as a modified `okf-kit` in `git status`. | Commit it, or `git checkout -- okf-kit`. |
| Concepts committed without rebuilding projections | Projections go stale — the corpus and what consumers read diverge. | **CI fails on this.** Run `./check.command` and commit. |

**Nothing here can damage the knowledge.** The worst case in every row is a check that did not
run, or ran an older version. Concepts, log and history are never at risk, and a bad kit
version is one `git checkout -- okf-kit` away from gone.

**The one to actually watch is the last row**, because it is the one that misleads a reader
rather than a developer: the master `.md`/`.json` are what other projects consume, and a stale
projection is a confident answer from an out-of-date corpus. That is why CI fails the build
rather than warning.

---

## Quick reference

| I want to… | Do this | Where |
|---|---|---|
| Change a check or the builder | edit, test, push | kit |
| Add knowledge, or ingest a new source | edit / `inbox/`, then `./check.command` | bundle |
| Give a bundle the newest machinery | `./update-kit.command`, then commit `okf-kit` | bundle |
| Know which kit checked this corpus | `git -C okf-kit log --oneline -1` | bundle |
| Publish knowledge to a Project or app | `projections/<slug>-master.md` / `.json` | bundle |

**Rule of thumb:** the kit changes when the *method* changes. A bundle changes when the
*knowledge* changes. They only meet when you run `update-kit.command`.
