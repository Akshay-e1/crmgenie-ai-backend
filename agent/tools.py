import json
from llm import llm
from datetime import datetime


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

    except:
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

    except:
        return "Schedule follow-up meeting."


# 4️⃣ Date Time Tool
def datetime_tool(text):
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

    except:
        return "Interaction completed."


# DB Save Tool
def log_interaction_tool(db, data):
    from models import Interaction

    allowed_data = {
        "hcp_name": data.get("hcp_name"),
        "topics": data.get("topics"),
        "sentiment": data.get("sentiment"),
        "follow_up": data.get("follow_up")
    }

    obj = Interaction(**allowed_data)

    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj


# Edit Tool
def edit_interaction_tool(db, obj):
    obj.topics = obj.topics + " (verified)"

    db.commit()

    return obj