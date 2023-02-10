def count_lines(text: str, filter_empty: bool = True) -> int:
    lines = [line for line in text.splitlines() if (line if filter_empty else True)]
    return len(lines)
