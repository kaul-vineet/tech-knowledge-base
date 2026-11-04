"""Option A: plain role-based access control (role -> permitted actions). Not lesson code; the comparison.

RBAC answers "may this ROLE do this ACTION?". It cannot see attributes: whose loan, which library, how many
loans, how large the fine. Each such rule needs a new role or code outside the model.
"""
PERMISSIONS = {
    "member": {"borrow", "return", "view"},
    "librarian": {"borrow", "return", "view", "waive_fine"},
    "manager": {"borrow", "return", "view", "waive_fine"},
}


def allowed(inp):
    return any(inp["action"] in PERMISSIONS.get(role, set()) for role in inp["subject"].get("roles", []))
