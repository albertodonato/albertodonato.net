import subprocess

from pagefind.service import _must_get_executable
from pelican import signals


def run_pagefind(pelican) -> None:
    subprocess.run(
        [_must_get_executable(), "--site", pelican.output_path], check=True
    )


def register() -> None:
    signals.finalized.connect(run_pagefind)
