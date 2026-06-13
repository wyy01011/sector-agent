import json

from pathlib import Path

data_path = Path(__file__).parent.parent / "data" / "sector.json"

with data_path.open(encoding="utf-8") as file:
    data = json.load(file)


data_path2 = Path(__file__).parent.parent / "data" / "company.json"

with data_path2.open(encoding="utf-8") as file2:
    data2 = json.load(file2)


SECTOR_ALIASES = {
    "semiconductor": "Semiconductors",
    "semiconductors": "Semiconductors",
    "bank": "Banking",
    "banks": "Banking",
    "banking": "Banking",
    "energy": "Energy",
    "consumer tech": "Consumer Technology",
    "consumer technology": "Consumer Technology",
    "tech": "Consumer Technology",
    "technology": "Consumer Technology",
    "health": "Healthcare",
    "health care": "Healthcare",
    "healthcare": "Healthcare",
}


def normalize_sector_name(sector):
    normalized = sector.lower().strip()
    return SECTOR_ALIASES.get(normalized, sector.strip())


def parse_query(state):
    query = state["user_query"].lower()

    if "compare" in query:
        intent = "comparison"
        sectors = query.replace("compare ", "").split(" and ")
        state["detected_sectors"] = sectors

    elif "sector" in query:
        intent = "sector_analysis"
        sector = query.replace("analyze ", "")
        sector = sector.replace("sector", "").strip()
        state["detected_sector"] = sector

    elif "analyze" in query:
        intent = "company_analysis"
        company = query.replace("analyze ", "")
        state["detected_company"] = company
    else:
        intent = None

    state["intent"] = intent
    state["route_taken"].append("parse_query")

    return state


def classify_route(state):
    intent = state.get("intent")

    if intent == "comparison":
        route = "comparison_route"
    elif intent == "sector_analysis":
        route = "sector_analysis_route"
    elif intent == "company_analysis":
        route = "company_analysis_route"
    else:
        route = "default_route"

    state["route_taken"].append(route)

    return state

def map_company_to_sector(state):
    company = state.get("detected_company")
    sector = None

    if company:
        company = company.lower()
    else:
        state["detected_sector"] = None
        state["errors"].append("Empty company name!")
        state["route_taken"].append("map_company_to_sector")
        return state

    for item in data:
        if company in [comp.lower() for comp in item["major_companies"]]:
            sector = item["sector"]
            break

    if sector is None:
        state["errors"].append(f"Company not found: {company}")

    state["detected_sector"] = sector
    state["route_taken"].append("map_company_to_sector")
    return state


def retrieve_sector_data(state):
    sector = state.get("detected_sector")
    state["sector_data"] = None

    if sector:
        sector = normalize_sector_name(sector)
        state["detected_sector"] = sector

        for item in data:
            if sector.lower() == item["sector"].lower():
                state["sector_data"] = item
                break
        if state["sector_data"] is None:
            state["errors"].append(f"Sector not found: {sector}")
    else:
        state["errors"].append("Empty sector name!")

    state["route_taken"].append("retrieve_sector_data")
    return state
     

def retrieve_multiple_sector_data(state):
    multiple_sectors = state.get("detected_sectors")
    state["sectors_data"] = []

    if multiple_sectors:
        multiple_sectors = [normalize_sector_name(s) for s in multiple_sectors]
        state["detected_sectors"] = multiple_sectors

        for sector in multiple_sectors:
            match = next(
                (item for item in data if sector.lower() == item["sector"].lower()),
                None,
            )

            if match:
                state["sectors_data"].append(match)
            else:
                state["errors"].append(f"Sector not found: {sector}")
    else:
        state["errors"].append("Empty sector names!")

    state["route_taken"].append("retrieve_multiple_sector_data")
    return state


def retrieve_company_data(state):
    company = state.get("detected_company")
    state["company_data"] = None

    if company:
        company = company.lower().strip()

        for item in data2:
            if company == item["company"].lower():
                state["company_data"] = item
                break

        if state["company_data"] is None:
            state["errors"].append(f"Company not found: {company}")
    else:
        state["errors"].append("Empty company name!")
    

    state["route_taken"].append("retrieve_company_data")
    return state


def analyze_sector(state):
    sector_data = state.get("sector_data")
    state["sector_analysis"] = None

    state["route_taken"].append("analyze_sector")
    return state
