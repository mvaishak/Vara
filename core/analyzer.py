# Image analysis logic
import base64
import io
import os
import json
from openai import OpenAI
from PIL import Image

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_clothing(pil_image: Image.Image) -> str:
    prompt = (
        "Analyze this image of a clothing item in detail. Return ONLY a valid JSON object with these keys:\n"
        "- item_type: specific type (e.g., 'button-down shirt', 'skinny jeans', 'blazer')\n"
        "- color: primary and secondary colors (e.g., 'navy blue', 'black with white stripes')\n"
        "- pattern: detailed pattern description (e.g., 'vertical pinstripes', 'floral print', 'solid')\n"
        "- style: style category (e.g., 'business casual', 'streetwear', 'formal', 'bohemian')\n"
        "- season: suitable seasons (e.g., 'spring/summer', 'all-season', 'winter')\n"
        "- material: fabric type if visible (e.g., 'cotton', 'denim', 'wool blend', 'silk')\n"
        "- fit: fit description (e.g., 'slim fit', 'oversized', 'tailored', 'relaxed')\n"
        "- details: notable features (e.g., 'gold buttons', 'ripped knees', 'collar', 'pockets')\n"
        "- description: a comprehensive 2-3 sentence description of the item\n"
        "Do not add markdown formatting or code blocks."
    )

    img_byte_arr = io.BytesIO()
    pil_image.save(img_byte_arr, format=pil_image.format or "PNG")
    img_bytes = img_byte_arr.getvalue()

    base64_image = base64.b64encode(img_bytes).decode("utf-8")
    mime_type = "image/jpeg" if (pil_image.format or "").lower() in ["jpeg", "jpg"] else "image/png"

    try:
        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": f"data:{mime_type};base64,{base64_image}"},
                    ],
                }
            ],
        )
        return response.output_text
    except Exception as e:
        return json.dumps({"item_type": "unknown", "color": "unknown", "pattern": "unknown", "style": "unknown", "season": "all-season", "material": "unknown", "fit": "unknown", "details": "", "description": "Unable to analyze (API error)."})
