"""The wake-word matcher is a pure function — so it gets deterministic evals.
Whisper mangles phrases in predictable ways; these cases pin the fuzziness."""

import pytest

from waku.gateway.voice import matches_wake

SHOULD_WAKE = [
    ("waku waku", "waku waku"),
    ("Waku, waku!", "waku waku"),            # punctuation
    ("wakuwaku", "waku waku"),               # whisper drops the space
    ("so anyway waku waku schedule it", "waku waku"),  # embedded in speech
    ("walku waku", "waku waku"),             # one-letter mangle → fuzzy match
    ("Hey Waku", "hey waku"),
    ("hey computer, what's up", "hey computer"),
    # regression from the first live session: whisper wrote the wake word in
    # kana — variants after a comma cover other scripts
    ("わくわく", "waku waku,わくわく"),
    ("わくわくわく", "waku waku,わくわく"),
    ("小助手你好", "waku waku,小助手"),
]

SHOULD_NOT_WAKE = [
    ("what a nice day", "waku waku"),
    ("wake up call at nine", "waku waku"),
    ("", "waku waku"),
    ("waku waku", ""),                        # no wake word configured
    ("walk to work", "waku waku"),
]


@pytest.mark.parametrize("heard,wake", SHOULD_WAKE, ids=[h for h, _ in SHOULD_WAKE])
def test_wakes(heard, wake):
    assert matches_wake(heard, wake)


@pytest.mark.parametrize("heard,wake", SHOULD_NOT_WAKE, ids=[h or "empty" for h, _ in SHOULD_NOT_WAKE])
def test_stays_asleep(heard, wake):
    assert not matches_wake(heard, wake)
