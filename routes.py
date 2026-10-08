from fastapi import APIRouter

from agent.langgraph_agent import agent
from agent.tools import (
    log_interaction_tool,
    edit_interaction_tool
)

router = APIRouter()


@router.post("/ai-log")
def ai_log(data: dict):

    text = data.get("text", "").strip()

    if not text:
        return {
            "error": "Text is required"
        }

    print("📝 INPUT:", text)

    # -----------------------------------------------------
    # Run LangGraph
    # -----------------------------------------------------
    result = agent.invoke({
        "input": text
    })

    print("🤖 AGENT RESULT:", result)

    if result is None:
        return {
            "error": "Agent failed"
        }

    # -----------------------------------------------------
    # Get structured data
    # -----------------------------------------------------
    structured = result.get("data")

    tools_used = list(
        result.get("tools_used", [])
    )

    print("📦 STRUCTURED:", structured)

    if structured is None:
        return {
            "error": "No structured output"
        }

    # -----------------------------------------------------
    # Edit / Verify
    # -----------------------------------------------------
    structured = edit_interaction_tool(structured)

    tools_used.append("edit_interaction")

    # -----------------------------------------------------
    # Save to MongoDB
    # -----------------------------------------------------
    saved = log_interaction_tool(structured)

    tools_used.append("log_interaction")

    print("🛠️ TOOLS USED:", tools_used)

    # -----------------------------------------------------
    # Return response
    # -----------------------------------------------------
    return {
        "hcp_name": saved.get("hcp_name"),
        "topics": saved.get("topics"),
        "sentiment": saved.get("sentiment"),
        "follow_up": saved.get("follow_up"),
        "date": saved.get("date"),
        "time": saved.get("time"),
        "outcomes": saved.get("outcomes"),
        "tools_used": tools_used
    }