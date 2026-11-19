# Case 001: God's missing inbox

| | |
| --- | --- |
| Victim | `email.utils.parseaddr` |
| Report | [python/cpython#40889](https://github.com/python/cpython/issues/40889), originally bpo-1025395 |
| Filed | 2004-09-09 |
| At large | 22 years |
| Reproduced on | Python 3.14.5. `getrouteaddr` is unchanged on `main` at `441c010fef`. |

## The crime

RFC 2822 still accepts a source route with several hops in front of an address.
One hop parses. Two hops and the address is gone.

```pycon
>>> from email.utils import parseaddr
>>> parseaddr('"God" <@hop1.org:jeff@spec.org>')
('God', 'jeff@spec.org')
>>> parseaddr('"God" <@hop1.org,@hop2.net:jeff@spec.org>')
('', '')
>>> parseaddr('"God" <@hop1.org,@hop2.net:jeff@spec.org>', strict=False)
('God', '')
```

## The suspect

`AddrlistClass.getrouteaddr` in `Lib/email/_parseaddr.py`. Its loop knows `@`,
`:` and `>`, but not the comma that separates hops. At the comma it falls
through to `getaddrspec()`, gets an empty string back and stops.

## How it got away

Nobody failed to write the fix. Four pull requests tried:

| PR | Opened | Outcome |
| --- | --- | --- |
| python/cpython#142 | 2017 | closed, unmerged |
| python/cpython#6917 | 2018 | closed, unmerged |
| python/cpython#123311 | 2024 | open |
| python/cpython#160775 | 2026-10 | open |

The hard part was never the patch. It was staying on the review.

## The fix

Seven added lines in [`fix.patch`](fix.patch): remember that we are inside a
route (between the first `@` and the `:`), and skip commas only there. A comma
anywhere else behaves exactly as before.

## Evidence

```console
$ python3 check.py
stock  : 0/3 multi-hop cases pass
   FAIL '"God" <@hop1.org,@hop2.net:jeff@spec.org>' -> ('', ''), want ('God', 'jeff@spec.org')
   FAIL '<@a.org,@b.net,@c.com:jeff@spec.org>' -> ('', ''), want ('', 'jeff@spec.org')
   FAIL '"God" <@hop1.org , @hop2.net : jeff@spec.org>' -> ('', ''), want ('God', 'jeff@spec.org')
patched: 3/3 multi-hop cases pass
unchanged: 10/10 existing behaviours identical
test_email: ran 940, failures 0, errors 0, skipped 1
```

`check.py` copies your interpreter's own `_parseaddr.py`, applies `fix.patch`
to the copy and runs the cases above, plus CPython's `test_email`, with the
patched method. Nothing in your Python installation is modified.

## Not done

- **Not closed upstream.** Two fix PRs are already open, so the next step is to
  run these cases against them and help the stronger one through review, not to
  open a third.
- **`getaddresses` in strict mode still fails.** It counts commas before parsing,
  so a multi-hop route gives `[('', '')]` even with this patch
  (`strict=False` returns the right answer). That is a separate change.
- **Cost to solve.** One agent, one sitting. No dollar figure was tracked.
