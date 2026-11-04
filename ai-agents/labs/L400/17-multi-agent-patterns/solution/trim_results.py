"""Solution (lesson 17 build task): keep the first line + a word budget; tell the model what was cut."""


def trim(result, max_words=60):
    lines = result.splitlines()
    head, rest = lines[0] if lines else "", " ".join(lines[1:]).split()
    if len(rest) <= max_words:
        return result
    kept = " ".join(rest[:max_words])
    return f"{head}\n{kept}\n[{len(rest) - max_words} more words cut; ask for a narrower query]"
