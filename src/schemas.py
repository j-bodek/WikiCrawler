from dataclasses import dataclass


@dataclass
class SaveMessage:
    """Message used to send data to the TaskQueue."""

    url: str
    text: str
