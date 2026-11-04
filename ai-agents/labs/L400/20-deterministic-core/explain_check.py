"""Build task (lesson 20): the model may EXPLAIN a decision, but the explanation must not contradict it.

Shipped UNFIXED: any text the model returns is shown to the customer (a model told 'approved' when code denied).
Make checked(text, decision) return text only if it names the decided action, names no other action, and every
number in it is the decided amount; otherwise return template(decision).
"""


def template(decision):
    return f"Decision: {decision['action']} for {decision['amount']}. Reason: {decision['rule']}."


def checked(text, decision):
    return text if text else template(decision)
