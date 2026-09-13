"""
AutoClicker - Click Pattern Recording

A pattern is the sequence of clicks the user performed: where each one landed,
which button it used, and how long they waited before it. Replaying the
pattern reproduces that sequence, so the timing the user recorded is the
timing they get back.
"""

import time
from collections import namedtuple

#: One recorded click. `delay` is the pause before it, in seconds.
PatternStep = namedtuple("PatternStep", "x y button delay")

#: Buttons that can be recorded, mapped to the names the click engine uses.
#: Side buttons are left out because the engine cannot send them back.
BUTTON_NAMES = {"left": "left", "right": "right", "middle": "mid"}

#: A recorded pattern longer than this is unmanageable in the list, and is
#: almost certainly an accident rather than something anyone meant to record.
MAX_STEPS = 200

#: Pauses longer than this were the user thinking, not part of the pattern.
MAX_DELAY = 10.0


class PatternRecorder:
    """Collects clicks into a pattern.

    `add` is called from the mouse hook thread while the UI reads `steps` on
    the main thread, so steps is only ever replaced or appended to - never
    mutated in place.
    """

    def __init__(self):
        self.steps = []
        self._last_time = None

    def start(self):
        """Begin a new recording, discarding anything held before."""
        self.steps = []
        self._last_time = None

    def add(self, x, y, button):
        """Record one click. Returns False once the pattern is full."""
        name = BUTTON_NAMES.get(button)
        if name is None:
            return True                 # not recordable, but not an overflow
        now = time.perf_counter()
        if self._last_time is None:
            delay = 0.0
        else:
            delay = min(now - self._last_time, MAX_DELAY)
        self._last_time = now
        if len(self.steps) >= MAX_STEPS:
            return False
        self.steps.append(PatternStep(int(x), int(y), name, round(delay, 3)))
        return True

    def pop(self):
        """Drop the last recorded click, for when one lands by accident."""
        if not self.steps:
            return False
        self.steps = self.steps[:-1]
        return True

    def clear(self):
        self.steps = []
        self._last_time = None

    def duration(self):
        """How long one pass through the pattern takes, in seconds."""
        return sum(step.delay for step in self.steps)

    def is_full(self):
        return len(self.steps) >= MAX_STEPS

    def __len__(self):
        return len(self.steps)
