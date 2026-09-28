# -*- coding: utf-8 -*-

import os
from unittest.mock import Mock, patch

from deep_scrape.backends import OpenCLIStatus
from deep_scrape.channels.twitter import TwitterChannel


def _which(*present):
    return lambda name: f"/usr/bin/{name}" if name in present else None


def test_twitter_cli_unverified_does_not_mutate_os_environ(monkeypatch):
    monkeypatch.delenv("TWITTER_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("TWITTER_CT0", raising=False)

    with patch("shutil.which", side_effect=_which("twitter")), patch(
        "subprocess.run"
    ) as run:
        channel = TwitterChannel()
        status, message = channel.check()

    assert status == "warn"
    assert channel.active_backend is None
    run.assert_not_called()
    assert "TWITTER_AUTH_TOKEN" not in os.environ
    assert "TWITTER_CT0" not in os.environ


def test_saved_credentials_are_recognised_without_starting_upstream(
    monkeypatch,
):
    config = Mock()
    config.get.side_effect = lambda key: {
        "twitter_auth_token": "saved-auth-token",
        "twitter_ct0": "saved-ct0",
    }.get(key)
    monkeypatch.delenv("TWITTER_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("TWITTER_CT0", raising=False)

    with patch("shutil.which", side_effect=_which("twitter")), patch(
        "subprocess.run"
    ) as run:
        channel = TwitterChannel()
        status, message = channel.check(config)

    assert status == "warn"
    assert "configured" in message.lower()
    assert "does not run" in message.lower()
    assert channel.active_backend is None
    run.assert_not_called()
    assert "TWITTER_AUTH_TOKEN" not in os.environ
    assert "TWITTER_CT0" not in os.environ


def test_child_env_keeps_existing_shell_credentials_authoritative(
    monkeypatch,
):
    config = Mock()
    config.get.side_effect = lambda key: {
        "twitter_auth_token": "config-auth",
        "twitter_ct0": "config-ct0",
    }.get(key)
    monkeypatch.setenv("TWITTER_AUTH_TOKEN", "shell-auth")
    monkeypatch.setenv("TWITTER_CT0", "shell-ct0")

    env = TwitterChannel._child_env(config)

    assert env["TWITTER_AUTH_TOKEN"] == "shell-auth"
    assert env["TWITTER_CT0"] == "shell-ct0"


def test_child_env_falls_back_to_config_when_env_unset(monkeypatch):
    config = Mock()
    config.get.side_effect = lambda key: {
        "twitter_auth_token": "config-auth",
        "twitter_ct0": "config-ct0",
    }.get(key)
    monkeypatch.delenv("TWITTER_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("TWITTER_CT0", raising=False)

    env = TwitterChannel._child_env(config)

    assert env["TWITTER_AUTH_TOKEN"] == "config-auth"
    assert env["TWITTER_CT0"] == "config-ct0"


def test_bird_with_explicit_env_remains_unverified(monkeypatch):
    monkeypatch.setenv("AUTH_TOKEN", "explicit-auth")
    monkeypatch.setenv("CT0", "explicit-ct0")
    with patch("shutil.which", side_effect=_which("bird")), patch(
        "subprocess.run",
        side_effect=AssertionError("bird check must not run"),
    ):
        channel = TwitterChannel()
        status, message = channel.check()

    assert status == "warn"
    assert "explicit environment credentials" in message.lower() or "skips" in message.lower()
    assert channel.active_backend is None


def test_bird_without_explicit_env_is_warn(monkeypatch):
    monkeypatch.delenv("AUTH_TOKEN", raising=False)
    monkeypatch.delenv("CT0", raising=False)
    with patch("shutil.which", side_effect=_which("bird")):
        channel = TwitterChannel()
        status, message = channel.check()

    assert status == "warn"
    assert "without explicit" in message.lower()
    assert channel.active_backend is None


def test_nothing_installed_returns_install_hint():
    channel = TwitterChannel()
    with patch("shutil.which", return_value=None):
        status, message = channel.check()

    assert status == "warn"
    assert "twitter-cli" in message
    assert channel.active_backend is None


def test_opencli_bridge_ready_is_unverified_for_twitter():
    with patch(
        "deep_scrape.backends.opencli_status",
        return_value=OpenCLIStatus(
            installed=True,
            extension_connected=True,
            version="1.8.6",
        ),
    ):
        status, message = TwitterChannel()._check_opencli()

    assert status == "warn"
    assert "bridge connected" in message.lower()
    assert "not verified" in message.lower()


def test_verified_backend_result_wins_over_unverified_twitter_cli():
    channel = TwitterChannel()
    with patch.object(
        TwitterChannel,
        "_check_twitter_cli",
        return_value=("warn", "twitter-cli unverified"),
    ), patch.object(
        TwitterChannel,
        "_check_opencli",
        return_value=("ok", "OpenCLI available"),
    ), patch.object(TwitterChannel, "_check_bird", return_value=None):
        status, message = channel.check()

    assert status == "ok"
    assert message == "OpenCLI available"
    assert channel.active_backend == "OpenCLI"


def test_all_warn_returns_first_warning_without_active_backend():
    channel = TwitterChannel()
    with patch.object(
        TwitterChannel,
        "_check_twitter_cli",
        return_value=("warn", "twitter-cli unverified"),
    ), patch.object(
        TwitterChannel,
        "_check_opencli",
        return_value=("warn", "extension not connected"),
    ), patch.object(TwitterChannel, "_check_bird", return_value=None):
        status, message = channel.check()

    assert status == "warn"
    assert message == "twitter-cli unverified"
    assert channel.active_backend is None
