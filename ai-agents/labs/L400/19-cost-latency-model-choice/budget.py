"""Build task (lesson 19): fit a prompt into the context window.

parts: system (str), question (str), docs [(score, text)], history [str, oldest first]; words stand in for tokens.
Shipped UNFIXED: joins everything and cuts the END - the question (and the output reserve) are lost first.
Make fit() keep system + question + output reserve, then add the best docs, then the newest history that fits.
"""


def words(text):
    return len(text.split())


def fit(system, question, docs, history, num_ctx=4096, reserve=512):
    text = " ".join([system, *[t for _, t in docs], *history, question])
    return " ".join(text.split()[: num_ctx - reserve])
