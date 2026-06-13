from typing import TypedDict

class SectorAgentState(TypedDict):
    user_query: str
    intent: str | None
    detected_sector: str | None
    detected_sectors: list[str] | None
    detected_company: str | None

    sector_data: dict | None
    sectors_data: list[dict] | None
    company_data: dict | None

    sector_analysis: str | None
    comparison_analysis: str | None
    company_analysis: str | None

    route_taken: list[str]
    errors: list[str]

    final_report: str | None