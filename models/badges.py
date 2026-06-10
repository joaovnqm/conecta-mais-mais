from dataclasses import dataclass

@dataclass
class Badge:
    id: str
    name: str
    icon: str
    description: str

@dataclass
class UserStats:
    events_attended: int = 0
    presentations_done: int = 0
    workshops_done: int = 0
    total_points: int = 0