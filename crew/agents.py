from crewai import Agent


def make_agents(model: str = "llama3.2:1b"):
    llm = f"ollama/{model}"

    translator = Agent(
        role="Language Detector and Translator",
        goal="Detect the language of YouTube video content and translate it to English accurately.",
        backstory=(
            "You are a multilingual expert. You detect languages and translate content "
            "to English faithfully. You never add extra commentary or notes."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    summarizer = Agent(
        role="YouTube Video Summarizer",
        goal=(
            "Summarize YouTube videos in 3-4 sentences using ONLY the title, "
            "description, and transcript provided. Never invent content."
        ),
        backstory=(
            "You are a strict content summarizer. You only use the exact information "
            "given to you. You never hallucinate, assume, or add information not present "
            "in the source material. If data is limited, you summarize what is available "
            "from the title alone."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    analyst = Agent(
        role="YouTube Trend Analyst",
        goal=(
            "Analyze YouTube video metadata and return structured JSON with topics, "
            "trend score, sentiment, and insights relevant to the actual video."
        ),
        backstory=(
            "You are a YouTube analytics expert. You assess videos based on their "
            "actual title, channel, and stats. You always return valid JSON only."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    return translator, summarizer, analyst
