# L600 #08 evidence – A tool platform for AI agents with least privilege and an audit trail

Checked 2026-10-30. Primary sources only. "Verified" = fetched and read for the stated claim, or reproduced in code here.

## Research questions
1. What does MCP 2026-07-28 say about trusting tool metadata, human approval and audit logging?
2. How do macaroon caveats attenuate authority, and what does the HMAC construction require?
3. What sizes and properties of Ed25519 do manifests and checkpoints rely on?
4. What do indirect-injection and agent-security sources say about where enforcement must live?
5. Why is a plain hash chain linear, and when do Merkle logs pay off?

## Sources kept (score /12: implementable, current, authoritative, open, transferable, depth)
| Source | URL | Score | Used for | What was verified |
|---|---|---|---|---|
| MCP spec 2026-07-28, Server: Tools | https://modelcontextprotocol.io/specification/2026-07-28/server/tools | 12 | seams, inRealSystems, ADR-004 | Fetched: "there SHOULD always be a human in the loop with the ability to deny tool invocations"; "clients MUST consider tool annotations to be untrusted unless they come from trusted servers"; security considerations: servers MUST validate inputs, implement access controls, rate limit, sanitise outputs; clients SHOULD prompt for confirmation, show inputs, validate results, log tool usage for audit. Also: an invalid tool definition is excluded while others stay usable (x-mcp-header rule) - same per-tool fail-closed approach as load_tools. Version string matches ai-agents L200 #10's server. |
| Birgisson et al., Macaroons (NDSS 2014) | https://www.ndss-symposium.org/ndss2014/ndss-2014-programme/macaroons-cookies-contextual-caveats-decentralized-authorization-cloud/ | 11 | capability.py, ADR-001 | Fetched (NDSS page + search abstract): chained-HMAC construction; caveats "attenuate and contextually confine when, where, by who, and for what purpose"; bearer credentials. Reproduced: attenuation without key; removing a caveat breaks the tag (test_m2). |
| RFC 2104 HMAC | https://www.rfc-editor.org/rfc/rfc2104.html | 12 | capability.py | Fetched: H(K XOR opad, H(K XOR ipad, text)); key at least L bytes; random keys. Root key in TokenService = 32 random bytes (secrets.token_bytes). |
| RFC 8032 EdDSA | https://www.rfc-editor.org/rfc/rfc8032 | 12 | manifest.py, audit.py | Fetched: Ed25519 public keys 32 octets, signatures 64 octets. Reproduced: signature bytes 64 (manifest.py), base64 88 chars (checks_08). |
| RFC 9396 OAuth 2.0 RAR | https://www.rfc-editor.org/rfc/rfc9396.html | 10 | inRealSystems, ADR-001 context | Fetched: authorization_details for fine-grained requirements like "transfer 45 Euros to Merchant A"; AS must refuse unknown types/fields (same deny-by-default as unknown caveats). |
| Greshake et al., Indirect Prompt Injection (arXiv 2302.12173) | https://arxiv.org/abs/2302.12173 | 11 | failure lab, concept note | Fetched abstract: injected prompts in retrieved data "control how and if other APIs are called". |
| Debenedetti et al., CaMeL (arXiv 2503.18813) | https://arxiv.org/abs/2503.18813 | 10 | inRealSystems | Fetched abstract: capabilities enforced when tools are called; untrusted data cannot impact program flow. |
| OWASP LLM06:2025 Excessive Agency | https://genai.owasp.org/llmrisk/llm062025-excessive-agency/ | 9 | inRealSystems, ADR-002 | Fetched: mitigations minimise extensions/permissions, require user approval, "complete mediation" in downstream code rather than relying on the LLM. (Project page, not a standard; kept as a widely used reference list.) |
| Crosby & Wallach, Tamper-Evident Logging (USENIX Sec 2009) | https://www.usenix.org/legacy/event/sec09/tech/full_papers/crosby.pdf | 11 | ADR-003, scaling limits | Search result text of the PDF: hash chains require auditors to examine every event between snapshots; tree-based proofs are logarithmic (3 KB vs 800 MB trace for 80 million events). The usenix.org presentation page returned no text (web_fetch empty); the PDF URL is cited instead. |
| Nygard, Documenting Architecture Decisions | https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions | 10 | decisions/ | Same source as the topic capstones (ADR format: Title, Status, Context, Decision, Consequences). |

Dropped: vendor blog posts about "MCP security" (marketing), RFC 9162 as a cited source (mentioned by name only; not re-fetched here).

## Reused code (imported by path via `_kb.py`, never edited)
ai-agents L200 #8 `schema_check.py`, L200 #10 `mcp_server.py` + `mcp_client.py`, L300 #16 `attacks.json`;
cryptography L200 #11 `tokens.py` (b64u, unb64u), L300 #14 `release_sign.py` (key_id, digest);
application-architecture L400 #19 `rego_lite.py`; shared `local_agent/fake_model_server.py`.
Known gap reused as-is: lesson 10's client matches replies by order, not id; `mcp_pin()` avoids the legacy-fallback race.

## Numbers and how they were obtained (all recomputed by `research/checks_08.py`)
| Number | Origin |
|---|---|
| 40 corpus items, 24 requested, 0 executed, 0 unscoped; naive 24 executed, 16 effects | `scenarios.run_corpus` with seed 8 against the shared fake |
| 5 phrasings (4 from attacks.json + 1 upper-case variant) | `corpus.phrasings()` |
| 31/31 mutations detected; 20/31 with per-entry hashing | `run_project.audit_mutations` on the S2 log (5 entries) |
| 50/50 tokens rejected at TTL; TTL 301 refused | `run_project.ttl_fitness` (seed 8, fake clock T0 = 1790000000) |
| 252-character token, 5 HMACs for 4 caveats, 43-char tag | `capability.TokenService` / arithmetic |
| 64-byte signature, 16-hex kid 5fb0188328180fc4 | `manifest.publish` with the seeded demo key |
| 71% = 1 - 0.95^24 | arithmetic in checks_08 |
| policy revision c332681181f5 | sha256 of policy/tools.rego (rego_lite) |
| 951 words concept note | `wc -w` |

## Not verified here (pendingCi)
Real model behaviour on the corpus (Ollama), OPA evaluation of tools.rego, MCP Inspector / minisign / CyberChef
exercises, macOS and Windows runs.
