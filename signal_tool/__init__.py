"""Signal Tool — leading-indicator discernment for transformer prices.

A small, modular package that tests whether raw metal-input prices (and related
industrial series) lead the Producer Price Index for electrical transformers.

See README.md for the protocol and design choices.
"""

__all__ = [
    "config",
    "fred",
    "process",
    "correlate",
    "screen",
    "significance",
    "leaderboard",
    "matrix",
]
