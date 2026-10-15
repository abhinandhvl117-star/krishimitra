import logging
from django.conf import settings
from groq import Groq

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are KrishiMitra, an expert AI agricultural assistant for Indian farmers.
You have deep knowledge about:
- Indian crops (rice, wheat, maize, cotton, sugarcane, vegetables, pulses, spices, etc.)
- Plant diseases, pests, and treatments
- Soil health, fertilizers (NPK), and organic farming
- Mandi (market) prices, selling strategies, and government MSP schemes
- Indian weather patterns, monsoon, Kharif and Rabi seasons
- Irrigation techniques (drip, sprinkler, flood)
- Government schemes: PM-KISAN, PMFBY crop insurance, Kisan Credit Card, e-NAM
- Post-harvest storage, processing, and reducing crop loss

Guidelines:
- Always respond in simple, clear English (or match the user's language if they write in Hindi/Malayalam)
- Be practical and specific — give actionable advice, not vague answers
- When recommending treatments, mention both organic and chemical options with safety precautions
- Keep responses concise (3-5 sentences for simple queries, up to 10 for complex ones)
- If a farmer describes symptoms, ask one clarifying question if needed before diagnosing
- Be warm and empathetic — farming is hard work

You are part of the KrishiMitra platform which also offers:
- Crop recommendation (based on soil NPK, pH, rainfall, temperature)
- Plant disease detection (image upload)
- Mandi price prediction
- Real-time weather insights
Mention these features when relevant.
"""

def get_groq_reply(user_message: str, history: list, location: str = "India") -> str:
    """
    Call Groq API with conversation history and return the assistant reply.
    history: list of ChatMessage objects (role, content)
    Returns reply string, or raises an exception.
    """
    api_key = getattr(settings, 'GROQ_API_KEY')
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in settings.py")

    client = Groq(api_key=api_key)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if location and location != "India":
        messages.append({
            "role": "system",
            "content": f"The farmer is located near {location}."
        })

    for msg in list(history)[-10:]:
        role = "assistant" if msg.role == "bot" else "user"
        messages.append({"role": role, "content": msg.content})

    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=messages,
    max_tokens=512,
    temperature=0.7,
    top_p=0.9,
    )
    return response.choices[0].message.content.strip()