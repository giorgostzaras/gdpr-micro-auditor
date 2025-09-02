from typing import TypedDict
from langgraph.graph import StateGraph, END
from agents.router import route
from agents.worker import work

class State(TypedDict):
    input: str
    task: str
    answer: str

def route_node(state: State) -> State:
    state["task"] = route(state["input"])
    return state

def work_node(state: State) -> State:
    state["answer"] = work(state["task"], state["input"])
    return state

def build_graph():
    sg = StateGraph(State)
    sg.add_node("route", route_node)
    sg.add_node("work", work_node)
    sg.set_entry_point("route")
    sg.add_edge("route", "work")
    sg.add_edge("work", END)
    return sg.compile()
