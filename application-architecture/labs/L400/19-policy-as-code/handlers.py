"""Policy enforcement points (PEP): every public handler asks the decision point before doing anything.

The handlers never contain authorization rules themselves; the fitness function checks they all call authorize().
"""


class Forbidden(Exception):
    pass


def authorize(pdp, action, subject, resource):
    decision = pdp.decide({"action": action, "subject": subject, "resource": resource})
    if not decision["allowed"]:
        raise Forbidden(f"{action} denied: {decision['deny'] or 'no rule allows it'}")
    return decision


def borrow(pdp, subject, resource, book_id):
    authorize(pdp, "borrow", subject, resource)
    return {"member_id": resource["member_id"], "book_id": book_id, "status": "on loan"}


def return_loan(pdp, subject, resource, loan_id):
    authorize(pdp, "return", subject, resource)
    return {"loan_id": loan_id, "status": "returned"}


def view_loans(pdp, subject, resource):
    authorize(pdp, "view", subject, resource)
    return {"member_id": resource["member_id"], "loans": []}


def waive_fine(pdp, subject, resource):
    authorize(pdp, "waive_fine", subject, resource)
    return {"member_id": resource["member_id"], "waived": resource["amount"]}
