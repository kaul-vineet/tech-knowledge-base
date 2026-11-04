"""Build task (lesson 17): a tool-result budget so ONE agent fits long results into its context window.

Shipped UNFIXED: results pass through untouched, so three log reads overflow a 1000-token context (task t07).
Make trim(result) keep the first line (the fact) plus at most max_words words, and say what was cut.
"""


def trim(result, max_words=60):
    return result
