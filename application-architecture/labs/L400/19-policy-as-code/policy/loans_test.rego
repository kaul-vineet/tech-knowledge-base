package loans.authz_test

# OPA policy tests (CI: opa test policy/ -v). policy/cases.json is loaded as data.cases.
# The lab's test_policy.py runs the same cases through rego_lite.py.

import data.loans.authz

test_all_requirements if {
	every c in data.cases {
		got := authz.allowed with input as c.input
		got == c.allowed
	}
}

test_librarian_of_another_library_denied if {
	not authz.allowed with input as {
		"action": "view",
		"subject": {"id": "s9", "tenant": "lib01", "roles": ["librarian"]},
		"resource": {"tenant": "lib00", "member_id": "m2", "active_loans": 1},
	}
}

test_suspended_librarian_denied if {
	not authz.allowed with input as {
		"action": "borrow",
		"subject": {"id": "s1", "tenant": "lib00", "roles": ["librarian"], "suspended": true},
		"resource": {"tenant": "lib00", "member_id": "m2", "active_loans": 0},
	}
}
