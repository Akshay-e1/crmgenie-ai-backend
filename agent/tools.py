import json
import re
from datetime import datetime

from llm import llm
from database import interactions_collection


# ---------------------------------------------------------
# Helper: Extract JSON safely from LLM response
# ---------------------------------------------------------
def extract_json(content):
    try:
        content = content.strip()

        # Remove markdown code fences if present
        content = content.replace("```json", "").replace("```", "").strip()

        start = content.find("{")
        end = content.rfind("}") + 1

        if start == -1 or end == 0:
            raise ValueError("No JSON object found")

        return json.loads(content[start:end])

    except Exception as e:
        print("JSON Parse Error:", e)
        return None


# ---------------------------------------------------------
# 1. Extract Interaction Tool
# ---------------------------------------------------------
def extract_interaction(text):
    print("✅ Tool Used: extract_interaction")

    prompt = f"""
You are an expert CRM data extraction assistant.

Extract ONLY these two fields from the user's interaction:

1. hcp_name
2. topics

IMPORTANT RULES:

- hcp_name means the healthcare professional/person mentioned.
- If the text says "Dr Reddy", return "Dr Reddy".
- If the text says "Doctor Reddy", return "Doctor Reddy".
- Do NOT return "Unknown" when a person's name is clearly present.
- topics must contain ONLY the main subject discussed.
- Do NOT copy the complete sentence into topics.
- Remove phrases like:
  "Today I met"
  "I met"
  "we discussed"
  "we talked about"
- Keep topics short and meaningful.

Examples:

Input:
Today I met Dr Reddy and discussed diabetes medicine.

Output:
{{
  "hcp_name": "Dr Reddy",
  "topics": "diabetes medicine"
}}

Input:
I met Doctor Suresh and discussed cough tablets.

Output:
{{
  "hcp_name": "Doctor Suresh",
  "topics": "cough tablets"
}}

Input:
Had a meeting with Dr Kumar regarding hypertension treatment.

Output:
{{
  "hcp_name": "Dr Kumar",
  "topics": "hypertension treatment"
}}

Return ONLY valid JSON.

Text:
{text}
"""

    try:
        response = llm.invoke(prompt)
        result = extract_json(response.content)

        if result:
            hcp_name = str(result.get("hcp_name", "")).strip()
            topics = str(result.get("topics", "")).strip()

            # Basic cleanup
            if not hcp_name:
                hcp_name = "Unknown"

            if not topics:
                topics = text

            return {
                "hcp_name": hcp_name,
                "topics": topics
            }

    except Exception as e:
        print("Extract Error:", e)

    # -----------------------------------------------------
    # Fallback extraction
    # -----------------------------------------------------

    hcp_name = "Unknown"
    topics = text

    # Detect Dr Name / Doctor Name
    match = re.search(
        r"\b(Dr\.?|Doctor)\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)",
        text,
        re.IGNORECASE
    )

    if match:
        prefix = match.group(1)
        name = match.group(2).strip()

        hcp_name = f"{prefix} {name}"

    # Try to extract topic after "discussed"
    topic_match = re.search(
        r"discussed\s+(.+?)(?:\.|$)",
        text,
        re.IGNORECASE
    )

    if topic_match:
        topics = topic_match.group(1).strip()

    return {
        "hcp_name": hcp_name,
        "topics": topics
    }


# ---------------------------------------------------------
# 2. Sentiment Tool
# ---------------------------------------------------------
def sentiment_tool(text):
    print("✅ Tool Used: sentiment_tool")

    text_lower = text.lower()

    # Strong explicit indicators
    negative_phrases = [
        "not interested",
        "wasn't interested",
        "was not interested",
        "no interest",
        "rejected",
        "reject",
        "disliked",
        "not happy",
        "unhappy",
        "dissatisfied",
        "negative response",
        "refused"
    ]

    positive_phrases = [
        "very happy",
        "happy with",
        "interested",
        "very interested",
        "showed interest",
        "positive response",
        "satisfied",
        "liked",
        "approved",
        "agreed",
        "good response",
        "enthusiastic"
    ]

    for phrase in negative_phrases:
        if phrase in text_lower:
            return "Negative"

    for phrase in positive_phrases:
        if phrase in text_lower:
            return "Positive"

    # LLM fallback
    prompt = f"""
Classify the sentiment of this CRM interaction.

Return ONLY ONE word:

Positive
Neutral
Negative

Rules:
- Interest, happiness, satisfaction or approval = Positive
- Rejection, dissatisfaction or lack of interest = Negative
- No clear emotion = Neutral

Text:
{text}
"""

    try:
        response = llm.invoke(prompt)
        result = response.content.strip().lower()

        if "negative" in result:
            return "Negative"

        if "positive" in result:
            return "Positive"

        return "Neutral"

    except Exception as e:
        print("Sentiment Error:", e)
        return "Neutral"


# ---------------------------------------------------------
# 3. Follow Up Tool
# ---------------------------------------------------------
def followup_tool(text):
    print("✅ Tool Used: followup_tool")

    sentiment = sentiment_tool(text)

    # Reliable rule-based follow-up
    if sentiment == "Positive":
        return (
            "Follow up with the HCP to discuss the product further "
            "and proceed with the next steps."
        )

    if sentiment == "Negative":
        return (
            "Follow up with the HCP to understand their concerns "
            "and address the reasons for the lack of interest."
        )

    return (
        "Follow up with the HCP to continue the discussion "
        "and clarify the next steps."
    )


# ---------------------------------------------------------
# 4. Date Time Tool
# ---------------------------------------------------------
def datetime_tool(text=None):
    print("✅ Tool Used: datetime_tool")

    now = datetime.now()

    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M")
    }


# ---------------------------------------------------------
# 5. Outcome Tool
# ---------------------------------------------------------
def outcome_tool(text):
    print("✅ Tool Used: outcome_tool")

    text_lower = text.lower()

    if any(
        phrase in text_lower
        for phrase in [
            "very happy",
            "happy with",
            "interested",
            "very interested",
            "showed interest",
            "satisfied",
            "approved",
            "agreed"
        ]
    ):
        return "HCP showed positive interest in the product."

    if any(
        phrase in text_lower
        for phrase in [
            "not interested",
            "wasn't interested",
            "was not interested",
            "rejected",
            "dissatisfied",
            "unhappy",
            "refused"
        ]
    ):
        return "HCP was not interested in the product."

    # LLM fallback
    prompt = f"""
Generate a short CRM interaction outcome.

Rules:
- Mention the HCP's response or result of the discussion.
- Do not invent information.
- Keep it to one sentence.
- Return only the outcome.

Text:
{text}
"""

    try:
        response = llm.invoke(prompt)
        result = response.content.strip()

        if result:
            return result

    except Exception as e:
        print("Outcome Error:", e)

    return "Interaction completed."


# ---------------------------------------------------------
# 6. MongoDB Save Tool
# ---------------------------------------------------------
def log_interaction_tool(data):
    print("✅ Tool Used: log_interaction_tool")

    document = {
        "hcp_name": data.get("hcp_name"),
        "topics": data.get("topics"),
        "sentiment": data.get("sentiment"),
        "follow_up": data.get("follow_up"),
        "date": data.get("date"),
        "time": data.get("time"),
        "outcomes": data.get("outcomes")
    }

    result = interactions_collection.insert_one(document)

    return {
        "_id": str(result.inserted_id),
        **data
    }


# ---------------------------------------------------------
# 7. Edit / Verification Tool
# ---------------------------------------------------------
def edit_interaction_tool(obj):
    print("✅ Tool Used: edit_interaction_tool")

    # Do not modify the actual user data.
    # Only clean whitespace.
    obj["hcp_name"] = str(obj.get("hcp_name", "")).strip()
    obj["topics"] = str(obj.get("topics", "")).strip()
    obj["sentiment"] = str(obj.get("sentiment", "")).strip()
    obj["follow_up"] = str(obj.get("follow_up", "")).strip()

    return obj