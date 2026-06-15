"""Static roadmap metadata (month titles) — mirrors content/syllabus.yaml."""

MONTH_TITLES = {
    1: "Programming, DS, & Algorithms",
    2: "Math Engine",
    3: "Systems & Automata",
    4: "Data & Connections",
    5: "Hardware & Consolidation",
    6: "The Mock Crucible",
}

TOTAL_WEEKS = 24  # 6 months × 4 weeks


def month_title(month: int) -> str:
    return MONTH_TITLES.get(month, f"Month {month}")
