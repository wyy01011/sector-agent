from agent.graph import graph 
from agent.state import SectorAgentState

user_query = input("What's on your mind? ")

initial_state = SectorAgentState(
    user_query=user_query,
    route_taken=[],
    errors=[],
)

result = graph.invoke(initial_state)

print("Report: ", result["final_report"])
print("Route taken: ", result["route_taken"])
print("Errors: ", result["errors"])