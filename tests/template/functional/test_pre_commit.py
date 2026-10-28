from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from tests.utils import DisallowCallable


@dataclass
class CommitMessageCase:
    name: str
    commit_message: str
    valid: bool = field(kw_only=True)


@pytest.mark.parametrize(
    "case",
    [
        pytest.param(case, id=case.name)
        for case in (
            CommitMessageCase(
                "subject_and_body",
                "Fix Sky Runner\n\nPut all the pieces back together.\n",
                valid=True,
            ),
            CommitMessageCase("short_subject", "?\n", valid=True),
            CommitMessageCase(
                "long_subject",
                (
                    "Confront Starman Jr., Starman,"
                    " Starman Super, Starman Deluxe, & Ghost of Starman\n"
                ),
                valid=False,
            ),
            CommitMessageCase(
                "human_co_author",
                (
                    "Fix baseball bat\n\n"
                    "Co-authored-by: Ness <Ness@onett.example.com>\n"
                ),
                valid=True,
            ),
            CommitMessageCase(
                "assisted_by_tool",
                "Add Mr. Saturn\n\nAssisted-by: Copilot\n",
                valid=True,
            ),
            CommitMessageCase(
                "assisted_by_tool_model",
                (
                    "Add boing! Mr. Saturn\n\n"
                    "Assisted-by: claude-code:claude-opus-5-5\n"
                ),
                valid=True,
            ),
            CommitMessageCase(
                "assisted_by_slash",
                "Buy a hamburger\n\nAssisted-by: ness/mother-2\n",
                valid=True,
            ),
            CommitMessageCase(
                "assisted_by_url",
                "Locate Giant Step\n\nAssisted-by: https://onett.example.com\n",
                valid=False,
            ),
            CommitMessageCase(
                "assisted_by_email",
                "Defeat the Sharks\n\nAssisted-by: ness@onett.example.com\n",
                valid=False,
            ),
            CommitMessageCase(
                "generated_by",
                (
                    "Land a SMAAAASH!! against Spiteful Crow\n\n"
                    "Generated-by: ChatGPT\n"
                ),
                valid=False,
            ),
            CommitMessageCase(
                "llm_co_author",
                (
                    "Eat a cookie\n\n"
                    "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>\n"
                ),
                valid=False,
            ),
            CommitMessageCase(
                "claude_session_url",
                (
                    "Lose a cookie due to Spiteful Crow theft\n\n"
                    "Claude-Session: https://claude.ai/code/session_deadbeef\n"
                ),
                valid=False,
            ),
            CommitMessageCase(
                "llm_session_url",
                (
                    "Visit arcade\n\n"
                    "Ness-Session: https://onett.example.com/s/deadbeef\n"
                ),
                valid=False,
            ),
            CommitMessageCase(
                "promo",
                (
                    "Open the road to Twoson\n\n"
                    "🤖 Generated with"
                    " [Claude Code](https://claude.com/claude-code)\n"
                ),
                valid=False,
            ),
        )
    ],
)
def test_pre_commit_commit_msg_hooks(
    disallow_subprocess: DisallowCallable,
    rendered_template: Path,
    case: CommitMessageCase,
) -> None:
    with tempfile.TemporaryDirectory() as td:
        message_file = Path(td) / "message.txt"
        message_file.write_text(case.commit_message)
        with disallow_subprocess.pause():
            result = subprocess.run(  # noqa: S603
                [
                    "prek",
                    "run",
                    "--hook-stage",
                    "commit-msg",
                    "--commit-msg-filename",
                    str(message_file),
                ],
                cwd=rendered_template,
                check=False,
            )
        assert result.returncode == (0 if case.valid else 1)
