package agent.tools

# Tool-call policy, Rego v1 syntax. Evaluated by rego_lite.py (application-architecture L400 #19), a learning subset;
# the same file is meant for OPA in CI (pendingCi). Deny by default: a call runs only if an allow rule matches
# and no deny rule does. Every input field is computed by the HOST from trusted sources - never from model text.

default allow := false

default allowed := false

default needs_approval := false

# A1: read-only tools run when the session capability covers this exact call
allow if {
	input.tool.side_effect == false
	input.scope_ok == true
	input.args_valid == true
}

# A2: side effects additionally need user provenance for their target arguments
allow if {
	input.tool.side_effect == true
	input.scope_ok == true
	input.args_valid == true
	input.provenance_ok == true
}

# D1: no valid capability (unknown tool, out of scope, expired, wrong session, bad argument shape)
deny contains "no valid capability for this call" if {
	input.scope_ok == false
}

# D2: arguments must pass the signed manifest's schema
deny contains "arguments fail the tool schema" if {
	input.args_valid == false
}

# D3: a side effect whose target came from data, not from the user
deny contains "side-effect target not from the user's request" if {
	input.tool.side_effect == true
	input.provenance_ok == false
}

# H1: high-risk tools wait for a human, even when allowed
needs_approval if {
	input.tool.risk == "high"
}

allowed if {
	allow
	count(deny) == 0
}
