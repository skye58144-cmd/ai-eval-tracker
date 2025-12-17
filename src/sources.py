"""Source definitions for the eval tracker."""

SOURCES = [
    {
        "name": "METR GPT-5 report",
        "url": "https://evaluations.metr.org/gpt-5-report/",
        "parser": "metr",
    },
    {
        "name": "METR GPT-5.1-Codex-Max report",
        "url": "https://evaluations.metr.org/gpt-5-1-codex-max-report/",
        "parser": "metr",
    },
    {
        "name": "GDPval arXiv",
        "url": "https://arxiv.org/abs/2510.04374",
        "parser": "gdpval",
    },
    {
        "name": "ARC Prize results and analysis",
        "url": "https://arcprize.org/blog/arc-prize-2025-results-analysis",
        "parser": "arcagi2",
    },
]
