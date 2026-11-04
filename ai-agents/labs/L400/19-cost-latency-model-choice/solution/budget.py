"""Solution (lesson 19 build task): budget by priority, never by position."""


def words(text):
    return len(text.split())


def fit(system, question, docs, history, num_ctx=4096, reserve=512):
    budget = num_ctx - reserve - words(system) - words(question)  # the output reserve is never spent on input
    if budget < 0:
        raise ValueError("system + question alone do not fit: shorten them or raise num_ctx")
    kept_docs = []
    for score, text in sorted(docs, key=lambda d: -d[0]):  # best evidence first
        if words(text) <= budget:
            kept_docs.append(text)
            budget -= words(text)
    kept_history = []
    for turn in reversed(history):  # newest turns first; the oldest are dropped
        if words(turn) > budget:
            break
        kept_history.insert(0, turn)
        budget -= words(turn)
    return " ".join([system, *kept_docs, *kept_history, question])
