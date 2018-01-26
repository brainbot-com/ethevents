import click
from _pytest.monkeypatch import MonkeyPatch
from typing import Iterator, Union


def mock_prompt(monkeypatch: MonkeyPatch, input_sequence: Iterator[Union[str, int, bool]]):
    def patched_prompt(*args, **kwargs):
        value = next(input_sequence)
        print('{}: {}'.format(args[0], value))
        return value

    monkeypatch.setattr(click, 'prompt', patched_prompt)
    monkeypatch.setattr(click, 'confirm', patched_prompt)
