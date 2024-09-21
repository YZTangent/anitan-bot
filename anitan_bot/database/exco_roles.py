from enum import Enum


class Exco(Enum):
    PRESIDENT = ("President", 4)
    VICE_PRESIDENT = ("Vice President", 3)

    # Prescell roles
    SECRETARY = ("Secretary", 2)
    TREASURER = ("Treasurer", 2)
    TECH_LEAD = ("Tech Lead", 2)
    CASUALS_HEAD = ("Casuals Head", 2)
    CASUALS_VICE_HEAD = ("Casuals Vice Head", 2)
    TOPICS_HEAD = ("Topics Head", 2)
    TOPICS_VICE_HEAD = ("Topics Vice Head", 2)
    PALETTE_HEAD = ("Palette Head", 2)
    PALETTE_VICE_HEAD = ("Palette Vice Head", 2)
    SAFETY_OFFICER = ("Safety Officer", 2)
    PRESCELL = ("Prescell", 2)

    # Normal Exco
    CASUALS_EXCO = ("Casuals Exco", 1)
    TOPICS_EXCO = ("Topics Exco", 1)
    PALETTE_EXCO = ("Palette Exco", 1)
    EXCO = ("Exco", 1)

    def __init__(self, role, authority):
        self.role = role
        self.authority = authority
