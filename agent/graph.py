from langgraph.graph import StateGraph, START, END

from agent.state import SectorAgentState
from agent import nodes

builder = StateGraph(SectorAgentState)

builder.add_node("parse_query", nodes.parse_query)
builder.add_node("classify_route", nodes.classify_route)
builder.add_node("map_company_to_sector", nodes.map_company_to_sector)
builder.add_node("retrieve_sector_data", nodes.retrieve_sector_data)
builder.add_node("retrieve_multiple_sector_data", nodes.retrieve_multiple_sector_data)
builder.add_node("retrieve_company_data", nodes.retrieve_company_data)