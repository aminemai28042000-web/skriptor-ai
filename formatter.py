def format_transcript(text: str) -> str:
    lines = text.split("\n")
    clean = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        clean.append(line)

    return "\n".join(clean)
