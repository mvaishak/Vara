# LLM logic for outfit recommendations
import os
import json
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_outfit_recommendation(user_query: str, closet_data_json: str, num_variations: int = 1, temperature: float | None = None, seed: int | None = None) -> str:
    if not OPENAI_API_KEY:
        return "Error: Missing API key"
    llm = ChatOpenAI(model="gpt-4", temperature=(0.7 if temperature is None else temperature), api_key=OPENAI_API_KEY)
    if num_variations and num_variations > 1:
        multi_instructions = f"\n\nProvide EXACTLY {num_variations} distinct outfit recommendations. For each recommendation, start with a line like '=== Recommendation [i] ===' (where [i] is 1..{num_variations}) and then include the recommendation content using the exact format below. Separate recommendations clearly."
    else:
        multi_instructions = ""

    prompt_text = f"""Here is the user's available wardrobe inventory in JSON format:

{{closet_data}}

The user asks: {{user_query}}

{{variation}}

Based strictly on the inventory above, suggest a complete outfit.

IMPORTANT: Format your response EXACTLY as follows:

**Selected Items:**
- Item [ID]: [color] [item_type]
- Item [ID]: [color] [item_type]
(continue for all selected items)

**Styling Notes:**
[Explain why the colors and styles work together, why this outfit is appropriate for the occasion, and any styling tips. Keep it concise but informative.]

Use this exact format with "Item [ID]:" for each clothing piece.
{multi_instructions}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a professional fashion stylist."),
        ("human", prompt_text),
    ])

    chain = prompt | llm | StrOutputParser()

    variation = ""
    if seed is not None:
        variation = f"Variation hint: Please produce an alternate valid outfit from the same inventory. Variation seed: {seed}."

    return chain.invoke({"closet_data": closet_data_json, "user_query": user_query, "variation": variation})
