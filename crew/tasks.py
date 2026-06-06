from crewai import Task


def make_tasks(translator, summarizer, analyst, metadata: dict, transcript: str):

    title = metadata.get('title', '')
    channel = metadata.get('channel', '')
    description = metadata.get('description', '')
    views = metadata.get('view_count', 0)
    likes = metadata.get('like_count', 0)
    published = metadata.get('published_at', '')

    has_transcript = bool(transcript and len(transcript.strip()) > 100)

    raw_content = f"""
VIDEO TITLE: {title}
CHANNEL NAME: {channel}
PUBLISHED DATE: {published}
VIEW COUNT: {views:,}
LIKE COUNT: {likes:,}
DESCRIPTION: {description if description else 'Not available'}
TRANSCRIPT: {transcript[:4000] if has_transcript else 'NOT AVAILABLE - use title and description only'}
"""

    # ── Task 1: Translate ──────────────────────────────────────────────────
    translate_task = Task(
        description=(
            f"You are given this YouTube video information:\n\n{raw_content}\n\n"
            "INSTRUCTIONS:\n"
            "1. Detect the language of the title and description\n"
            "2. If not English, translate title and description to English\n"
            "3. If already English, keep as-is\n"
            "4. Return EXACTLY this format with no extra text:\n\n"
            "DETECTED_LANGUAGE: <language name>\n"
            "ENGLISH_TITLE: <title in English>\n"
            "ENGLISH_DESCRIPTION: <description in English, or 'Not available'>\n"
            "ENGLISH_TRANSCRIPT: <transcript in English, or 'Not available'>\n"
        ),
        expected_output=(
            "Exactly four labeled lines: DETECTED_LANGUAGE, ENGLISH_TITLE, "
            "ENGLISH_DESCRIPTION, ENGLISH_TRANSCRIPT"
        ),
        agent=translator,
    )

    # ── Task 2: Summarize ──────────────────────────────────────────────────
    summarize_task = Task(
        description=(
            "Using ONLY the translated content from the previous task, write a summary.\n\n"
            "STRICT RULES:\n"
            "- Base your summary ONLY on the actual video title and description provided\n"
            "- Do NOT invent, assume, or hallucinate any content not present in the data\n"
            "- If transcript is 'Not available', use only the title and description\n"
            "- Write 3-4 sentences in plain English\n"
            "- Start with what the video is about based on the TITLE\n"
            "- Do NOT add notes, disclaimers, or meta-commentary\n"
            "- Do NOT say things like 'based on the translation' or 'as provided'\n"
            "- Just write the summary directly\n\n"
            "Example of GOOD output:\n"
            "'This video follows [channel] as they [what title says]. "
            "The content focuses on [topic from title/description]. "
            "It appears to target [audience type] interested in [subject].'\n\n"
            "Example of BAD output:\n"
            "'Based on the translated content provided... Note: I am using...'"
        ),
        expected_output=(
            "3-4 sentences of plain English summary based strictly on the video title "
            "and description. No meta-commentary, no disclaimers."
        ),
        agent=summarizer,
        context=[translate_task],
    )

    # ── Task 3: Analyze ────────────────────────────────────────────────────
    analyze_task = Task(
        description=(
            f"Analyze this YouTube video and return a JSON object.\n\n"
            f"VIDEO TITLE: {title}\n"
            f"CHANNEL: {channel}\n"
            f"VIEWS: {views:,}\n"
            f"LIKES: {likes:,}\n\n"
            "Return ONLY this JSON — no explanation, no markdown fences:\n"
            "{\n"
            '  "topics": ["topic1", "topic2", "topic3", "topic4", "topic5"],\n'
            '  "trend_score": 7.5,\n'
            '  "trend_label": "Trending 🔥",\n'
            '  "sentiment_positive": 70,\n'
            '  "sentiment_neutral": 20,\n'
            '  "sentiment_negative": 10,\n'
            '  "insights": [\n'
            '    "insight about this specific video",\n'
            '    "another specific insight",\n'
            '    "third insight"\n'
            '  ]\n'
            "}\n\n"
            "Base topics and insights on the ACTUAL video title and channel name. "
            "Do NOT use generic placeholders."
        ),
        expected_output="Valid JSON object only. No markdown, no extra text.",
        agent=analyst,
        context=[translate_task, summarize_task],
    )

    return translate_task, summarize_task, analyze_task
