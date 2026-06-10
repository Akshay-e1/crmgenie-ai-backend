from langgraph.graph import StateGraph
from agent.tools import (
    extract_interaction,
    sentiment_tool,
    followup_tool,
    datetime_tool,
    outcome_tool
)


# 1️⃣ Extract Node
def extract_node(state):
    print("➡️ Extract Node")

    text = state.get("input")
    data = extract_interaction(text)

    return {
        "input": text,
        "data": data,
        "tools_used": ["extract_interaction"]
    }


# 2️⃣ Sentiment Node
def sentiment_node(state):
    print("➡️ Sentiment Node")

    text = state.get("input")
    data = state.get("data", {})
    tools_used = state.get("tools_used", [])

    sentiment = sentiment_tool(text)
    data["sentiment"] = sentiment

    tools_used.append("sentiment_tool")

    return {
        "input": text,
        "data": data,
        "tools_used": tools_used
    }


# 3️⃣ Follow-up + Extra Tools Node
def followup_node(state):
    print("➡️ Follow-up Node")

    text = state.get("input")
    data = state.get("data", {})
    tools_used = state.get("tools_used", [])

    # 3️⃣ follow-up
    data["follow_up"] = followup_tool(text)
    tools_used.append("followup_tool")

    # 4️⃣ datetime tool
    dt = datetime_tool(text)
    data["date"] = dt.get("date")
    data["time"] = dt.get("time")
    tools_used.append("datetime_tool")

    # 5️⃣ outcome tool
    data["outcomes"] = outcome_tool(text)
    tools_used.append("outcome_tool")

    return {
        "input": text,
        "data": data,
        "tools_used": tools_used
    }


# 🔥 Build Graph
def build_graph():
    graph = StateGraph(dict)

    graph.add_node("extract", extract_node)
    graph.add_node("sentiment", sentiment_node)
    graph.add_node("followup", followup_node)

    graph.set_entry_point("extract")

    graph.add_edge("extract", "sentiment")
    graph.add_edge("sentiment", "followup")

    graph.set_finish_point("followup")

    return graph.compile()


agent = build_graph()