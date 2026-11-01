import re
from dataclasses import dataclass

@dataclass
class PreprocessedText:
    cleaned: str
    original: str

def _repair_spaced_out_words(text: str) -> str:
    """Repairs spaced-out headings or names like 'J O H N   S M I T H' -> 'JOHN SMITH'
    without mangling normal text or initials.
    """
    lines = text.split("\n")
    processed_lines = []

    for line in lines:
        # Check if line contains words separated by 2+ spaces where parts are single characters
        # e.g., 'J O H N   S M I T H'
        tokens = re.split(r'(\s{2,})', line)
        repaired_tokens = []
        for token in tokens:
            # If token is spaced-out letters like "J O H N" (3 or more single letters separated by 1 space)
            if re.fullmatch(r'[A-Za-z](?:\s[A-Za-z]){2,}', token.strip()):
                repaired_tokens.append(re.sub(r'\s+', '', token.strip()))
            else:
                repaired_tokens.append(token)
        processed_lines.append("".join(repaired_tokens))

    return "\n".join(processed_lines)

def preprocess(text: str) -> PreprocessedText:
    """Cleans and standardizes extracted resume text while strictly preserving:
    - Original raw text
    - Non-ASCII/Unicode letters, accents, and symbols
    - Paragraph and section structure
    """
    if not text:
        return PreprocessedText(cleaned="", original="")

    original = text

    # 1. Normalize line breaks (\r\n and \r -> \n)
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")

    # 2. Normalize non-breaking and zero-width spaces to regular space
    cleaned = re.sub(r'[\u00A0\u1680\u2000-\u200B\u202F\u205F\u3000\uFEFF]', ' ', cleaned)

    # 3. Repair spaced out characters (e.g. 'J O H N   S M I T H')
    cleaned = _repair_spaced_out_words(cleaned)

    # 4. Normalize horizontal whitespace per line (tabs, multiple spaces -> single space)
    lines = cleaned.split("\n")
    cleaned_lines = []
    for line in lines:
        collapsed_line = re.sub(r'[^\S\n]+', ' ', line).strip()
        cleaned_lines.append(collapsed_line)

    cleaned = "\n".join(cleaned_lines)

    # 5. Collapse excessive vertical blank lines (3+ newlines -> 2 newlines)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    return PreprocessedText(
        cleaned=cleaned.strip(),
        original=original,
    )

