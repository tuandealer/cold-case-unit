# Cold Case Unit

A Devin Bot that leads a squad of agents on one kind of work: open source bugs
that have been open for ten years or more.

## Why

Every large project has bug reports from the 2000s that are still open. Most of
them are not hard. They are abandoned: the reporter moved on, the fix PR went
stale, nobody stayed in the room. An always-on bot can stay in the room.

## How a case runs

1. **Intake.** Pick an open bug filed 10+ years ago that still reproduces on the
   current release.
2. **Reproduce.** One agent writes a minimal failing test.
3. **Trace.** One agent reads the history: where the behaviour came from and why
   earlier fixes stalled.
4. **Fix.** One agent writes the smallest patch that makes the test pass without
   changing anything else, then runs the project's own test suite.
5. **Stay.** The bot opens or joins the upstream PR and answers review until a
   maintainer merges or rejects it.
6. **File.** Every closed case gets a public case file: victim, suspect, how it
   got away, what it cost to solve.

Rules of engagement:

- A human maintainer makes every merge decision.
- No duplicate PRs. If a fix PR is already open upstream, the bot helps that one.
- A case is closed when upstream closes it, not before.

## Docket

| #   | Case                | Report                 | Filed      | Status                                               |
| --- | ------------------- | ---------------------- | ---------- | ---------------------------------------------------- |
| 001 | [God's missing inbox](cases/001-gods-missing-inbox/CASE.md) | python/cpython #40889 | 2004-09-09 | Fix written and tested locally. Not closed upstream. |

Plan for the first month: triage the oldest open CPython bugs, pick the 25 that
are actually fixable, and work them one at a time.

## Status

Day zero. Case 001 was worked by a single coding agent in one sitting as a proof
of concept. The squad itself is not running yet.
