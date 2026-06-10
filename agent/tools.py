import json
from datetime import datetime

from llm import llm
from database import interactions_collection


# 1️⃣ Extract Interaction Tool
def extract_interaction(text):
    print("✅ Tool Used: extract_interaction")

    prompt = f"""
You are a CRM assistant.

Extract the following information from the text.

Return ONLY valid JSON.

Format:
{{
  "hcp_name": "",
  "topics": ""
}}

Text:
{text}
"""

    try:
        response = llm.invoke(prompt)

        content = response.content.strip()

        start = content.find("{")
        end = content.rfind("}") + 1

        json_text = content[start:end]

        return json.loads(json_text)

    except Exception as e:
        print("Extract Error:", e)

        return {
            "hcp_name": "Unknown",
            "topics": text
        }


# 2️⃣ Sentiment Tool
def sentiment_tool(text):
    print("✅ Tool Used: sentiment_tool")

    prompt = f"""
Classify sentiment.

Return ONLY one word:

Positive
Neutral
Negative

Text:
{text}
"""

    try:
        response = llm.invoke(prompt)

        result = response.content.strip()

        if "Positive" in result:
            return "Positive"

        if "Negative" in result:
            return "Negative"

        return "Neutral"

    except Exception:
        return "Neutral"


# 3️⃣ Follow Up Tool
def followup_tool(text):
    print("✅ Tool Used: followup_tool")

    prompt = f"""
Generate one short professional follow-up action.

Text:
{text}
"""

    try:
        return llm.invoke(prompt).content.strip()

    except Exception:
        return "Schedule follow-up meeting."


# 4️⃣ Date Time Tool
def datetime_tool(text=None):
    print("✅ Tool Used: datetime_tool")

    now = datetime.now()

    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M")
    }


# 5️⃣ Outcome Tool
def outcome_tool(text):
    print("✅ Tool Used: outcome_tool")

    prompt = f"""
Generate a short outcome summary.

Examples:
- Doctor showed interest.
- Follow-up planned.
- Product discussion completed.

Text:
{text}
"""

    try:
        return llm.invoke(prompt).content.strip()

    except Exception:
        return "Interaction completed."


# 6️⃣ MongoDB Save Tool
def log_interaction_tool(data):
    print("✅ Tool Used: log_interaction_tool")

    result = interactions_collection.insert_one({
        "hcp_name": data.get("hcp_name"),
        "topics": data.get("topics"),
        "sentiment": data.get("sentiment"),
        "follow_up": data.get("follow_up"),
        "date": data.get("date"),
        "time": data.get("time"),
        "outcomes": data.get("outcomes")
    })

    return {
        "_id": str(result.inserted_id),
        **data
    }


# 7️⃣ Edit Tool
def edit_interaction_tool(obj):
    print("✅ Tool Used: edit_interaction_tool")

    obj["topics"] = obj.get("topics", "") + " (verified)"

    return obj