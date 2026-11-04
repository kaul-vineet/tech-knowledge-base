"""The four seams where the three topics meet. Each check returns ok + what it measured."""
import adapters
import crypto_registry as registry
import estimates
import migration_plan


def s1_quantum_to_risk(sim_results):
    """Simulator results are evidence of the mechanism only; z comes from a labelled assumption, never from them."""
    bad = estimates.check_claims(estimates.claims(sim_results))
    try:
        migration_plan.exposed(10, 3, sim_results[0])
        refused = False
    except TypeError:
        refused = True
    scoped = all("toy" in r["scope"] for r in sim_results)
    return {"ok": not bad and refused and scoped, "bad_claims": len(bad), "sim_result_as_z_refused": refused,
            "z_source": migration_plan.HORIZON.source}


def s2_inventory_to_plan(findings):
    """Every finding becomes exactly one plan row; a file nobody owns is escalated, never dropped."""
    rows = migration_plan.plan(findings)
    stray = {"file": "vendor/legacy/kx.py", "line": 1, "algorithm": "ECDH P-256", "usage": "key-establishment",
             "service": "unowned", "pq": False}
    stray_row = migration_plan.plan([stray])[0]
    unowned = sum(1 for f in findings if f["service"] == "unowned")
    return {"ok": len(rows) == len(findings) and stray_row["priority"] == "P1-review" and unowned == 0,
            "findings": len(findings), "plan_rows": len(rows), "unowned": unowned, "stray_file_priority": stray_row["priority"]}


def measured_sizes():
    """Run each adapter once and measure what it really puts on the wire."""
    out = {}
    for k in registry.KEX.values():
        st, share = k.client_hello()
        server_share, _ = k.server_respond(share)
        out[k.id] = {"client_share": len(share), "server_share": len(server_share)}
    for s in registry.SIG.values():
        sk, pk = s.keygen()
        out[s.id] = {"public_key": len(pk.public_bytes_raw()), "signature": len(s.sign(sk, b"x"))}
    return out


def s3_agility_to_wire(tap, service="messaging"):
    """On the wire, messaging offers exactly the registry's groups with the sizes its adapters advertise."""
    expected = registry.expected_offers(service)
    problems = []
    for f in tap.flights:
        if f["service"] != service:
            continue
        if f["t"] == "client_hello":
            if f["groups"] != expected:
                problems.append(f"offered {f['groups']}, registry says {expected}")
            problems += [f"{g} share {n} B" for g, n in zip(f["groups"], f["blob_bytes"])
                         if g in registry.KEX and n != registry.KEX[g].client_share_bytes]
        elif f["t"] == "server_hello":
            share, sig = f["blob_bytes"]
            if share != registry.KEX[f["group"]].server_share_bytes or sig != registry.SIG[f["sig"]].signature_bytes:
                problems.append(f"server_hello sizes {f['blob_bytes']} for {f['group']}/{f['sig']}")
    sizes = measured_sizes()
    advertised = all(sizes[k.id] == {"client_share": k.client_share_bytes, "server_share": k.server_share_bytes}
                     for k in registry.KEX.values()) and all(
        sizes[s.id] == {"public_key": s.public_key_bytes, "signature": s.signature_bytes} for s in registry.SIG.values())
    return {"ok": not problems and advertised, "problems": sorted(set(problems))[:3], "adapters_match_advertised": advertised,
            "hybrid_shares": [adapters.X25519MLKEM768Kex.client_share_bytes, adapters.X25519MLKEM768Kex.server_share_bytes]}


def can_require_pq(servers):
    return all(s.version >= 2 for s in servers)


def s4_rollout_to_policy(stats_required_mixed, servers):
    """With pq_required on, a v1 server left in the fleet must cause refusals, never classical sessions."""
    classical = sum(n for g, n in stats_required_mixed["sessions"].items() if not registry.KEX[g].pq)
    v1_handshakes = sum(1 for r in stats_required_mixed["results"] if r["server"] in {s.name for s in servers if s.version == 1})
    return {"ok": classical == 0 and stats_required_mixed["refused"] == v1_handshakes and not can_require_pq(servers),
            "classical_sessions": classical, "refused": stats_required_mixed["refused"],
            "flip_gate_allows_pq_required": can_require_pq(servers)}
