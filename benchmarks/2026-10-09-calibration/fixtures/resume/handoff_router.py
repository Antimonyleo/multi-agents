"""Route documentation updates to their intended document."""


def destination(kind):
    """Accept session, lesson, or result; reject all other inputs."""
    paths = {
        "session": "HANDOFF.md",
        "lesson": "docs/lessons.md",
        "result": "docs/results.md",
    }
    return paths.get(kind, "HANDOFF.md")
