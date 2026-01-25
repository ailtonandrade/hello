# prompts.py

PROMPTS = {
    "pregacao_epica": {
        "ollama": """
                Write an inspiring biblical exegesis as a single flowing text in natural spoken Brazilian Portuguese.
                The tone should be reflective and accessible, not academic.

                Include one biblical passage naturally within the text, mentioning the book and chapter in a subtle and reverent way.
                Do not quote the verse number explicitly unless it fits naturally into the narration in Brazilian Portuguese.

                Guidelines:
                - Write up to 130 words.
                - Just in Brazilian Portuguese
                - Avoid lists, emojis, Roman numerals, and hyphens.
                - Do not add formal introductions or conclusions.

                Respond only with the final text, without titles or meta commentary.
                """,

        "comfy_positive": """
                cinematic film still captured mid action,
                off center composition, imperfect framing,
                a human medieval warrior caught in motion,
                slightly turned away from camera, not facing the lens,
                fabric and cloak moving in the wind,shot on anamorphic 50mm lens,
                natural imbalance in posture, weight shifting,
                dramatic celestial sky with cold light breaking through clouds,
                angelic atmosphere implied only by scale and light,
                handheld camera feel, subtle motion blur,
                anamorphic lens, shallow depth of field,
                cinema color grading, realistic exposure,
                feels like an unplanned frame from a high budget movie scene
                """,

        "comfy_negative": """
                statue, sculpture, marble, stone texture,
                japan, korean, chimese, woman,
                illustration, concept art,
                digital art, cgi, unreal engine,
                perfect symmetry, godlike pose,
                mythological figure, painting
                """
    },
        "universe_sleep": {
        "ollama": """
        Write a short scientific real curiousity discovery text in Brazilian Portuguese.
        The tone must be calm, soft, and reassuring, like a quiet nighttime narration.
        The text should help the listener slow down and relax.
        Do use facts, numbers, names, or discoveries.
        If a number appears, it must always be written in full, even years, quantities, distances, or measurements.
        - Write up to 180 words.
        Do not use lists, emojis, or titles.
        The text should feel gentle, spacious, and comforting.
        End with an open and serene thought, without a conclusion.
        Respond only with the final text.
        """,

        "comfy_positive": """
        cinematic film still, low light atmosphere,
        vast universe inspired scene,
        deep space or quiet night sky,
        soft celestial light, dark blue and black tones,
        subtle stars, distant galaxies, gentle cosmic clouds,
        slow and calm visual mood,
        shot on anamorphic 50mm lens,
        slight softness, shallow depth of field,
        natural film grain, cinematic color grading,
        minimal composition, no visual tension,
        feels like a quiet contemplative moment from a calm science fiction film,
        timeless, peaceful, soothing
        """,

    "comfy_negative": """
                japanese, chinese, woman, girl, man, indian"""
                },

    "trader_realista": {
        "ollama": """
                Write a short financial reflection in Brazilian Portuguese.
                The tone must be calm, confident, and realistic, as if spoken by an experienced trader.
                Focus on mindset, behavior, and decision making, not on strategies, indicators, or specific assets.
                Do not teach or explain concepts.
                Avoid technical jargon.
                Do not reference charts, candles, timeframes, or the current market.
                Do not use lists, emojis, questions, or titles.
                End with an open insight that feels unfinished.
                Respond only with the final text.
                """,

        "comfy_positive": """
                DSLR photograph of a professional trader in a real office environment,
                observing financial candlestick charts on multiple monitors,
                editorial photography, documentary style,
                natural low light with soft imperfect shadows,
                shot on a full frame camera, 35mm lens, f1.8, ISO 800,
                subtle film grain, realistic exposure,
                calm focused expression, thoughtful posture,
                night city lights visible through a real window,
                lived in modern workspace, cables, desk details,
                unposed, unedited, candid moment
        """,

        "comfy_negative": """
                digital art, 3d render, illustration, concept art,
                cgi, unreal engine, videogame style,
                anime, cartoon, comic,
                perfect skin, plastic skin, beauty retouch,
                overprocessed, oversharpened,
                studio lighting, dramatic spotlight,
                text, subtitles, captions, watermark, logo,
                posing for camera, staged photo
        """
    },
    
}
