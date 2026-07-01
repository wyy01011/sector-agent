import json

from matplotlib import ticker
from agent.llm import llm
from agent import prompt, state
import yfinance as yf

from pathlib import Path

data_path = Path(__file__).parent.parent / "data" / "sector.json"

with data_path.open(encoding="utf-8") as file:
    data = json.load(file)


data_path2 = Path(__file__).parent.parent / "data" / "company.json"

with data_path2.open(encoding="utf-8") as file2:
    data2 = json.load(file2)


watchlist_path = Path(__file__).parent.parent / "data" / "watchlist.json"

with watchlist_path.open(encoding="utf-8") as file3:
    watchlist = json.load(file3)


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

def parse_query(state):
    query = state["user_query"].lower()

    if "actionable" in query or "stocks to monitor" in query or "watchlist" in query:
        intent = "actionables"

    elif "compare" in query:
        intent = "comparison"
        sectors = query.replace("compare ", "").split(" and ")
        sectors = [
            sector.replace("sectors", "").replace("sector", "").strip()
            for sector in sectors
        ]
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


""" def map_company_to_sector(state):
    company = state.get("detected_company")
    sector = None

    if company:
        company = company.lower().strip()
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
 """

def retrieve_sector_data(state):
    sector = state.get("detected_sector")
    state["sector_data"] = None

    if sector:
        sector = sector.lower().strip()
        sector = SECTOR_ALIASES.get(sector, sector)
      
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
        multiple_sectors = [sector.lower().strip() for sector in multiple_sectors]
        multiple_sectors = [SECTOR_ALIASES.get(sector, sector) for sector in multiple_sectors]
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

def retrieve_watchlist_data(state):
    state["watchlist_data"] = watchlist
    state["route_taken"].append("retrieve_watchlist_data")
    return state


def actionables_analysis(state):
    watchlist_data = state.get("watchlist_data")

    if not watchlist_data:
        state["errors"].append("No watchlist data available.")
        state["route_taken"].append("actionables_analysis")
        return state

    chain = prompt.actionables_prompt | llm
    response = chain.invoke({
        "watchlist_data": watchlist_data,
    })

    state["actionables"] = response.content
    state["route_taken"].append("actionables_analysis")
    return state


def analyze_sector(state):
    # Read sector_data. Handle missing data.
    # Send valid data through the prompt and LLM.
    # Store the returned text.

    sector_data = state.get("sector_data")
    state["sector_analysis"] = None

    if not sector_data:
        state["errors"].append("No sector data available for analysis.")
        state["route_taken"].append("analyze_sector")
        return state
    
    chain = prompt.sector_analysis_prompt | llm
    response = chain.invoke({

        "sector_name": sector_data["sector"],
        "sector_data": sector_data,

    })

    state["sector_analysis"] = response.content
    state["route_taken"].append("analyze_sector")
    return state


def company_analysis(state):

    company_data = state.get("company_data")
    state["company_analysis"] = None

    if not company_data:
        state["errors"].append("No company data available for analysis.")
        state["route_taken"].append("company_analysis")
        return state

    chain = prompt.company_analysis_prompt | llm
    response = chain.invoke({

        "company_name": company_data["company"],
        "company_data": company_data,
        "market_data": state.get("market_data"),

    })

    state["company_analysis"] = response.content
    state["route_taken"].append("company_analysis")
    return state


def sectors_comparison(state):

    sectors_data = state.get("sectors_data")
    state["comparison_analysis"] = None

    if not sectors_data:
        state["errors"].append("No sector data available for comparison.")
        state["route_taken"].append("sectors_comparison")
        return state

    chain = prompt.sectors_comparison_prompt | llm
    response = chain.invoke({
        "sectors_name": [s["sector"] for s in sectors_data],
        "sectors_data": sectors_data

    })

    state["comparison_analysis"] = response.content
    state["route_taken"].append("sectors_comparison")
    return state


def retrieve_market_data(state):

    company_data = state.get("company_data")
    state["market_data"] = None

    if not company_data:
        state["errors"].append("No company data available for market data retrieval.")
        state["route_taken"].append("retrieve_market_data")
        return state
    
    ticker = company_data.get("ticker")

    if ticker:

        try:
            stock = yf.Ticker(ticker)
            history = stock.history(period="5d")
        except Exception as exc:
            state["errors"].append(f"Failed to retrieve market data: {exc}")
            state["route_taken"].append("retrieve_market_data")
            return state
    
    if "Close" not in history.columns:
        state["errors"].append(f"No closing price data available for ticker: {company_data.get('ticker')}")
        state["route_taken"].append("retrieve_market_data")
        return state

    close_prices = history["Close"].dropna()

    if len(close_prices) < 2:
        state["errors"].append(f"Not enough market data available for ticker: {company_data.get('ticker')}")
        state["route_taken"].append("retrieve_market_data")
        return state

    if history.empty:
        state["errors"].append(f"No market data found for ticker: {company_data.get('ticker')}")
        state["route_taken"].append("retrieve_market_data")
        return state

    latest_close = close_prices.iloc[-1]
    previous_close = close_prices.iloc[-2]

    state["market_data"] = {"latest_close": latest_close, 
                            "previous_close": previous_close}

    state["route_taken"].append("retrieve_market_data")
    return state


def final_report(state):

    user_query = state.get("user_query")
    sector_analysis = state.get("sector_analysis")
    comparison_analysis = state.get("comparison_analysis")
    company_analysis = state.get("company_analysis")
    actionables = state.get("actionables")

    state["final_report"] = None

    if state.get("errors"):
        state["final_report"] = "Could not generate report because errors occurred: " + "; ".join(state["errors"])
        state["route_taken"].append("final_report")
        return state

    if not user_query:
        state["errors"].append("No user query available for final report.")
        state["route_taken"].append("final_report")
        return state

    chain = prompt.final_report_prompt | llm
    response = chain.invoke({
        "user_query": user_query,
        "sector_analysis": sector_analysis,
        "comparison_analysis": comparison_analysis,
        "company_analysis": company_analysis,
        "actionables": actionables

    })

    state["final_report"] = response.content
    state["route_taken"].append("final_report")
    return state

