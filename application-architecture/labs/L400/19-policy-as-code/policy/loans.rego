package loans.authz

# Library Loans authorization policy, Rego v1 syntax.
# Evaluated by rego_lite.py in the lab (a learning subset) and by OPA in CI (opa test policy/).
# Decision: allowed = some allow rule matched AND no deny rule matched (deny overrides).

default allow := false

default allowed := false

# R1: members borrow for themselves, in their own library, under the loan limit
allow if {
	input.action == "borrow"
	input.subject.tenant == input.resource.tenant
	input.subject.id == input.resource.member_id
	input.resource.active_loans < 5
}

# R2: members return and view their own loans
allow if {
	input.action in ["return", "view"]
	input.subject.tenant == input.resource.tenant
	input.subject.id == input.resource.member_id
}

# R3: librarians act for any member of the library (new rule, 2026-10)
allow if {
	"librarian" in input.subject.roles
	input.action in ["borrow", "return", "view", "waive_fine"]
}

# D1: suspended accounts can do nothing
deny contains "account suspended" if {
	input.subject.suspended == true
}

# D2: large fine waivers need a manager
deny contains "waivers above 20.00 need a manager" if {
	input.action == "waive_fine"
	input.resource.amount > 20
	not "manager" in input.subject.roles
}

allowed if {
	allow
	count(deny) == 0
}
