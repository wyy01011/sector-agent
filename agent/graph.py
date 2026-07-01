from langgraph.graph import StateGraph, START, END

from agent.state import SectorAgentState
from agent import nodes

builder = StateGraph(SectorAgentState)

builder.add_node("parse_query", nodes.parse_query)
#builder.add_node("map_company_to_sector", nodes.map_company_to_sector)
builder.add_node("retrieve_sector_data", nodes.retrieve_sector_data)
builder.add_node("retrieve_multiple_sector_data", nodes.retrieve_multiple_sector_data)
builder.add_node("retrieve_company_data", nodes.retrieve_company_data)
builder.add_node("retrieve_market_data", nodes.retrieve_market_data)
builder.add_node("analyze_sector", nodes.analyze_sector)
builder.add_node("company_analysis", nodes.company_analysis)
builder.add_node("sectors_comparison", nodes.sectors_comparison)
builder.add_node("final_report", nodes.final_report)
builder.add_node("retrieve_watchlist_data", nodes.retrieve_watchlist_data)
builder.add_node("actionables_analysis", nodes.actionables_analysis)


builder.add_edge(START, "parse_query")


def choose_route(state):
    intent = state.get("intent")

    if intent == "comparison":
        return "comparison_route"
    elif intent == "sector_analysis":    
        return "sector_analysis_route"  
    elif intent == "company_analysis":
        return "company_analysis_route"
    elif intent == "actionables":
        return "actionables_route"
    else:
        return "default_route"
    

builder.add_conditional_edges("parse_query", choose_route,
                              {
                                "comparison_route": "retrieve_multiple_sector_data", 
                                "sector_analysis_route": "retrieve_sector_data", 
                                "company_analysis_route": "retrieve_company_data", 
                                "actionables_route": "retrieve_watchlist_data",
                                "default_route": "final_report"
                              })

builder.add_edge("retrieve_multiple_sector_data", "sectors_comparison")
builder.add_edge("retrieve_sector_data", "analyze_sector")
builder.add_edge("retrieve_company_data", "retrieve_market_data")
builder.add_edge("retrieve_market_data", "company_analysis")
builder.add_edge("retrieve_watchlist_data", "actionables_analysis")

builder.add_edge("sectors_comparison", "final_report")
builder.add_edge("analyze_sector", "final_report")
builder.add_edge("company_analysis", "final_report")
builder.add_edge("actionables_analysis", "final_report")

builder.add_edge("final_report", END)

graph = builder.compile()
