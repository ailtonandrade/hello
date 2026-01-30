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
        "universe_sleep_shorts": {
                "ollama": """
                        Write up to 50 words a short scientific real curiousity discovery about one of these themes: space, nasa, satelite, planets, or comets.
                        Text in Brazilian Portuguese.
                        Do use facts, numbers, names, or discoveries.
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
        "universe_sleep_long": {
                "ollama": """
                        Write a lomg documentary scientific real curiousity discovery about one of these themes: space, nasa, satelite, planets, or comets.
                        Text in Brazilian Portuguese.
                        Do use facts, numbers, names, or discoveries.
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
        "universe_scriptures": {
                "ollama": """
                        Write up to 700 words in Brazilian Portuguese.
                        The text must sound like ancient astronomical knowledge,
                        spoken by someone trying to understand the sky without science.
                        Mix real celestial ideas with doubt, fear and obsession.
                        Do not explain anything clearly.
                        Avoid conclusions, lists or certainty.
                        End mid-thought, as if the writing suddenly stopped.
                        Respond only with the final text.
                        """,

                "comfy_positive": """
                        ancient parchment manuscript,
                        fictional pre-columbian inspired glyph writing,
                        unknown symbols repeating with internal logic,
                        looks like a real ancient language but not identifiable,
                        astronomical drawings mixed with strange glyph text,
                        hand drawn stars, planets and celestial paths,
                        obsessive annotations covering the page,
                        uneven ink density, handmade imperfections,
                        ritualistic and obsessive tone,
                        drawings feel intentional but misunderstood,
                        as if an ancient mind tried to explain the cosmos,
                        no modern knowledge, no clear diagrams,
                        feels like forbidden astronomical notes
                        """,

                "comfy_negative": """
                        mandala, concentric circles,
                        perfect symmetry,
                        geometric diagram,
                        astrological chart,
                        single central object,
                        balanced composition,
                        japanese, chinese"""
        },
    
}
