# prompts.py

PROMPTS = {
    "pregacao_epica": {
        "ollama": """
Write an inspiring biblical exegesis as a single flowing text in natural spoken Brazilian Portuguese.
The tone should be reflective and accessible, not academic.

Guidelines:
- Write up to 100 words.
- Avoid lists, emojis, Roman numerals, and hyphens.
- Do not add formal introductions or conclusions.

Respond only with the final text, without titles or meta commentary.
""",

        "comfy_positive": """
editorial photograph of a biblical prophet experiencing a heavenly vision,
vast celestial sky opening above,
powerful beams of divine light descending through dramatic clouds,
ethereal atmosphere with mist and floating dust particles,
sense of sacred revelation and awe,
solemn and authoritative presence,
light illuminating the face from above,
shot on a full frame camera, 85mm lens, f1.8,
very shallow depth of field,
natural imperfections, subtle film grain,
documentary photography style, unedited photo,
timeless and transcendent atmosphere
""",

        "comfy_negative": """
angel wings, halos, glowing eyes,
magic effects, fantasy art, illustration,
3d render, digital art, unreal engine,
cartoon, anime,
perfect skin, plastic face,
modern clothing,
no japanese, no korean, no chinese, no indian,
no woman, no girl
"""
    },

    "trader_realista": {
        "ollama": """
Write a short financial reflection in Brazilian Portuguese with a calm and confident tone.
Avoid technical jargon.
Do not use lists or emojis.
Respond only with the final text.
""",

        "comfy_positive": """
DSLR photograph of a trader analyzing financial candlestick charts on multiple monitors,
editorial photography, documentary style,
natural low light, soft imperfect shadows,
shot on a full frame camera, 35mm lens, f1.8, ISO 800,
slight lens noise, realistic exposure,
focused expression,
night city lights visible through a real office window,
lived in modern office space,
unedited photo
""",

        "comfy_negative": """
digital art, 3d render, illustration, concept art,
unreal engine,
smooth plastic skin, perfect face,
anime, cartoon,
oversharpened,
text, watermark, logo
"""
    },

    "infografico_financeiro": {
        "ollama": """
Generate a concise spoken explanation in Brazilian Portuguese about financial candlestick charts.
Use simple and educational language.
Avoid lists and emojis.
Respond only with the final text.
""",

        "comfy_positive": """
infographic style candlestick charts representing financial markets,
realistic trading interface on multiple monitors,
modern office desk,
subtle rgb ambient lighting,
night city visible through large window,
realistic photography,
clean composition,
sharp focus
""",

        "comfy_negative": """
3d render, illustration, cartoon,
abstract art, fantasy art,
cluttered background,
low resolution,
text, watermark, logo
"""
    }
}
