"""Static roadmap metadata (month titles) — mirrors content/syllabus.yaml."""

MONTH_TITLES = {
    "CSE": {
        1: "Programming, DS, & Algorithms",
        2: "Math Engine",
        3: "Systems & Automata",
        4: "Data & Connections (Selective Targeting)",
        5: "Hardware & Consolidation",
        6: "The Mock Crucible",
    },
    "ECE": {
        1: "Networks, Signals & Systems",
        2: "Electronic Devices & Analog Circuits",
        3: "Digital Circuits & Control Systems",
        4: "Communications & Electromagnetics",
        5: "Engineering Math & Revision",
        6: "The Mock Crucible",
    }
}

TOTAL_WEEKS = 24  # 6 months × 4 weeks


def month_title(field: str, month: int) -> str:
    return MONTH_TITLES.get(field.upper(), {}).get(month, f"Month {month}")
