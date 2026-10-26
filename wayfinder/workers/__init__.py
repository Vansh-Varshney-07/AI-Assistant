# wayfinder/workers — Worker definitions, schemas, and fixtures.
# Each subdirectory is one bounded worker configuration.

"""Scoped desktop worker integration. Hermes owns reasoning and model execution."""

ROLES = {
    "W33": "Desktop Context Analyst",
    "W34": "File Discovery Worker",
    "W35": "Local File Analyst",
    "W36": "Desktop Action Planner",
    "W37": "Desktop Action Worker",
}
