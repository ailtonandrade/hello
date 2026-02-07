# prompts.py

PROMPTS = {
        "pregacao": {
                "ollama": """
                        Write an inspiring biblical exegesis as a single flowing text in natural spoken Brazilian Portuguese.
                        The tone should be reflective and accessible, not academic.

                        Include one biblical passage naturally within the text, mentioning the book and chapter in a subtle and reverent way.
                        Do not quote the verse number explicitly unless it fits naturally into the narration in Brazilian Portuguese.

                        Guidelines:
                        - Write up to 70 words.
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
        "bkp_1_universe_sleep_shorts": {
                "ollama": """
                        Write up to 120 words a short scientific real curiousity discovery about one of these themes choiced randomly: space, nasa, satelite, planets, or comets.
                        Text in Brazilian Portuguese.
                        Do use facts, numbers, names, or discoveries.
                        Do not use lists, emojis, or titles.
                        The text should feel gentle, spacious, and comforting.
                        End with an open and serene thought, without a conclusion.
                        Respond only with the final text.Don’t interrupt the text abruptly.
                        """,

                "comfy_positive": """
                        cinematic film still, low light atmosphere,
                        vast universe inspired scene,
                        deep space or quiet night sky,
                        soft celestial light, dark purple and black tones,
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
        "universe_sleep_shorts": {
                "ollama": """
                        Write up to 120 words a short scientific curiosity with an exaggerated conspiracy-theory tone, designed to feel intriguing and slightly unsettling without being aggressive.
                        Randomly choose one of these themes: space, NASA, satellites, planets, or comets.
                        The text must be written in Brazilian Portuguese.
                        Do NOT mention NASA, or institutions by name.
                        Use facts, numbers, names, or real discoveries, but reinterpret them through speculative or conspiratorial ideas.
                        Do not use lists, emojis, or titles.
                        The tone should be calm, mysterious, and gently dramatic, as if revealing a hidden truth.
                        End with an open, serene, and suggestive thought, without conclusions.
                        Respond only with the final text and do not interrupt it abruptly.
                        """,

                "comfy_positive": """
                        realistic night orbit atmosphere, bloom, International Space Station, dark blue and emerald tones, cosmic cloud
                        """,

                "comfy_negative": """
                        text, watermark, woman, girl, abstract
                        """
        },
        "universe_sleep_long": {
                "ollama": """
                        Write a lomg documentary scientific real curiousity discovery about one of these themes: space, nasa, satelite, planets, or comets.
                        Text in Brazilian Portuguese.
                        Do use facts, numbers, names, or discoveries.
                        Do not use lists, emojis, or titles.
                        The text should feel gentle, spacious, and comforting.
                        End with an open and serene thought, without a conclusion.
                        Respond only with the final text. Don’t interrupt the text abruptly.
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
}
