from __future__ import annotations

import contextlib
import io
from unittest.mock import patch

from netra_recon.cli.main import NetraReconCLI


def test_profile_and_search_commands_accept_cmd2_parsers() -> None:
    output = io.StringIO()
    with patch("os.system"), contextlib.redirect_stdout(output):
        app = NetraReconCLI()
        app.onecmd_plus_hooks("profile safe")
        app.onecmd_plus_hooks('searchre "^Domain Info$"')
        app.onecmd_plus_hooks('search --exact "Domain Info"')
        app.onecmd_plus_hooks("quit")

    assert app.global_option_overrides["max_pages"] == "10"
    assert app.last_search_results == []
    transcript = output.getvalue()
    assert "Profile 'safe' applied." in transcript
    assert "Domain Info" in transcript
    assert "No modules matched" not in transcript
    assert "Invalid regular expression" not in transcript
    assert "Traceback" not in transcript
    assert "AttributeError" not in transcript
