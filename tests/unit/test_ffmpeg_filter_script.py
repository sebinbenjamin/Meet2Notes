from __future__ import annotations

import asyncio
import shutil
import subprocess
from pathlib import Path

import pytest

from local_meeting_ai.infrastructure.ffmpeg import FFmpegClient, filter_script_arguments

SCRIPT = Path("graph.txt")


@pytest.mark.parametrize(
    "version_line",
    [
        "ffmpeg version 4.4.2-0ubuntu0.22.04.1 Copyright (c) 2000-2021",
        "ffmpeg version 6.1.1-3ubuntu5 Copyright (c) 2000-2023",
        "ffmpeg version n6.0 Copyright (c) 2000-2023",
    ],
)
def test_releases_before_7_use_the_script_option(version_line: str) -> None:
    assert filter_script_arguments(version_line, SCRIPT) == [
        "-filter_complex_script",
        str(SCRIPT),
    ]


@pytest.mark.parametrize(
    "version_line",
    [
        "ffmpeg version 7.0 Copyright (c) 2000-2024",
        "ffmpeg version n8.1 Copyright (c) 2000-2026",
        "ffmpeg version 9.0.2-full_build-www.gyan.dev Copyright (c) 2000-2026",
        "ffmpeg version N-118000-g1234abcd Copyright (c) 2000-2026",
        "ffmpeg version 2026-10-01-git-abc-full_build-www.gyan.dev",
        None,
        "",
    ],
)
def test_current_and_unknown_builds_use_the_file_option(version_line: str | None) -> None:
    assert filter_script_arguments(version_line, SCRIPT) == ["-/filter_complex", str(SCRIPT)]


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="FFmpeg is not installed")
def test_export_audio_ranges_runs_with_installed_ffmpeg(tmp_path: Path) -> None:
    source = tmp_path / "source.wav"
    subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=4",
            str(source),
        ],
        check=True,
    )
    destination = tmp_path / "speaker.wav"

    asyncio.run(
        FFmpegClient().export_audio_ranges(
            source, destination, [(0, 1000), (2000, 3500)], output_format="wav"
        )
    )

    assert destination.stat().st_size > 0
    assert not list(tmp_path.glob("*.filter.txt"))
