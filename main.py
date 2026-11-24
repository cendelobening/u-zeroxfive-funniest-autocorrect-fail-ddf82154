#!/usr/bin/env python3
"""Funniest Autocorrect Fail — make.fun entry.

Writes a single original autocorrect-fail line to
$MAKEFUN_OUTPUT_DIR/entry.txt (default /output), UTF-8, no trailing
newline, exactly one line, under 200 characters.
Pure Python stdlib only.
"""

import os
import stat
import sys
import tempfile

LINE = (
    "I texted my boss 'working from home today' \u2014 autocorrect sent "
    "'twerking from home today'. I now have a meeting with HR at 9."
)

OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUTPUT_NAME = "entry.txt"


def main() -> int:
    data = LINE.encode("utf-8")
    if not (1 <= len(LINE) <= 199):
        print(f"error: line is {len(LINE)} chars, must be 1-199", file=sys.stderr)
        return 1
    if "\n" in LINE or "\r" in LINE:
        print("error: line must be a single line", file=sys.stderr)
        return 1
    if data.endswith(b"\n"):
        print("error: trailing newline not allowed", file=sys.stderr)
        return 1

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    target = os.path.join(OUTPUT_DIR, OUTPUT_NAME)

    fd, tmp_path = tempfile.mkstemp(dir=OUTPUT_DIR, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, target)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    # Read back and verify bytes, char count, and mode.
    with open(target, "rb") as f:
        read_back = f.read()
    if read_back != data:
        print("error: read-back bytes differ from written bytes", file=sys.stderr)
        return 1
    if len(read_back.decode("utf-8")) != len(LINE):
        print("error: read-back char count mismatch", file=sys.stderr)
        return 1
    mode = stat.S_IMODE(os.stat(target).st_mode)
    if mode != 0o644:
        print(f"error: mode is {oct(mode)}, expected 0o644", file=sys.stderr)
        return 1

    print(f"wrote {target} ({len(LINE)} chars, {len(data)} bytes, mode 0644)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
