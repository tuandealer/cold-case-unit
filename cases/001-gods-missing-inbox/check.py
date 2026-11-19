"""Case 001 (python/cpython#40889): fails on stock, passes with fix.patch.

Usage: python3 check.py

Copies this interpreter's email/_parseaddr.py to a temp dir, applies fix.patch
to the copy, and swaps the patched getrouteaddr in for this process only.
Needs the `patch` command and a Python that ships the `test` package.
"""
import importlib.util
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

import email._parseaddr as stock
import email.utils

HERE = pathlib.Path(__file__).resolve().parent

CASES = [
    ('"God" <@hop1.org,@hop2.net:jeff@spec.org>', ('God', 'jeff@spec.org')),
    ('<@a.org,@b.net,@c.com:jeff@spec.org>', ('', 'jeff@spec.org')),
    ('"God" <@hop1.org , @hop2.net : jeff@spec.org>', ('God', 'jeff@spec.org')),
]
# Must not change: ordinary addresses, one-hop routes, and junk commas.
UNCHANGED = [
    '"God" <@hop1.org:jeff@spec.org>',
    'user@example.com',
    '"Full Name" <foo@example.com>',
    'Full Name <foo@example.com>',
    '<,foo@example.com>',
    '<foo@example.com,bar@example.com>',
    'a@b, c@d',
    '<>',
    'a(WRONG)@b',
    'a@malicious.org@important.com',
]


def run(label):
    bad = [(s, email.utils.parseaddr(s), want) for s, want in CASES
           if email.utils.parseaddr(s) != want]
    print(f'{label}: {len(CASES) - len(bad)}/{len(CASES)} multi-hop cases pass')
    for s, got, want in bad:
        print(f'   FAIL {s!r} -> {got!r}, want {want!r}')
    return not bad


def snapshot():
    return {s: (email.utils.parseaddr(s),
                email.utils.getaddresses([s], strict=False))
            for s in UNCHANGED}


def load_patched():
    tmp = pathlib.Path(tempfile.mkdtemp())
    copy = tmp / '_parseaddr_fixed.py'
    shutil.copy(stock.__file__, copy)
    subprocess.run(['patch', '-s', str(copy), str(HERE / 'fix.patch')], check=True)
    spec = importlib.util.spec_from_file_location('_parseaddr_fixed', copy)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


before = snapshot()
assert not run('stock  '), 'expected the stock parser to fail'

stock.AddrlistClass.getrouteaddr = load_patched().AddrlistClass.getrouteaddr

assert run('patched'), 'fix does not work'
after = snapshot()
assert before == after, {s: (before[s], after[s]) for s in before if before[s] != after[s]}
print(f'unchanged: {len(UNCHANGED)}/{len(UNCHANGED)} existing behaviours identical')

# CPython's own email tests, with the patched method in place.
suite = unittest.defaultTestLoader.loadTestsFromNames(
    ['test.test_email.test_email', 'test.test_email.test_utils',
     'test.test_email.test__header_value_parser'])
with open('/dev/null', 'w') as devnull:
    result = unittest.TextTestRunner(verbosity=0, stream=devnull).run(suite)
print(f'test_email: ran {result.testsRun}, failures {len(result.failures)}, '
      f'errors {len(result.errors)}, skipped {len(result.skipped)}')
sys.exit(0 if result.wasSuccessful() else 1)
