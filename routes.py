from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from agent.langgraph_agent import agent
from agent.tools import log_interaction_tool, edit_interaction_tool

router = APIRouter()


@router.post("/ai-log")
def ai_log(data: dict, db: Session = Depends(get_db)):

    # Run LangGraph
    result = agent.invoke({
        "input": data.get("text")
    })

    print("AGENT RESULT:", result)

    if result is None:
        return {
            "error": "Agent failed"
        }

    structured = result.get("data")
    tools_used = result.get("tools_used", [])

    print("STRUCTURED:", structured)

    if structured is None:
        return {
            "error": "No structured output"
        }

    # Tool 4
    obj = log_interaction_tool(db, structured)
    tools_used.append("log_interaction")

    # Tool 5
    obj = edit_interaction_tool(db, obj)
    tools_used.append("edit_interaction")

    print("TOOLS USED:", tools_used)

    return {
        "hcp_name": obj.hcp_name,
        "topics": obj.topics,
        "sentiment": obj.sentiment,
        "follow_up": obj.follow_up,

        # From LangGraph
        "date": structured.get("date"),
        "time": structured.get("time"),
        "outcomes": structured.get("outcomes"),

        "tools_used": tools_used
    }