# Foundations II: quantum information basics

Lesson 23 gave the rules: unit vectors, unitaries, tensor products, the Born rule. This note uses them to derive what quantum information can and cannot do. Every claim is checked by `labs/L500/24-quantum-information-basics/theorems.py`.

## Definitions

- **e-bit:** one shared Bell pair |Φ+> = (|00> + |11>)/√2, treated as a resource that a protocol consumes.
- **Oracle:** a black box for a Boolean function f. The standard form is |x>|y> -> |x>|y ⊕ f(x)>. If the target qubit starts in |->, this acts as |x> -> (-1)^{f(x)}|x> (phase kickback).
- **Density matrix:** ρ = Σ_i p_i |ψ_i><ψ_i| for a source that prepares |ψ_i> with probability p_i. It is Hermitian, positive semidefinite and has trace 1. Pure states have Tr ρ^2 = 1; mixtures have less.
- **Partial trace:** the operation that gives the state of one subsystem alone. For two qubits, (Tr_A ρ)_{jk} = Σ_i ρ_{(i,j),(i,k)}: keep only the terms where A's labels agree.

## Key results

**No-cloning (T24.1).** No unitary U and blank state |e> satisfy U|ψ>|e> = |ψ>|ψ> for every |ψ>. Proof in one line: unitaries preserve inner products, so <ψ|φ> = <ψ|φ>^2 for any two clonable states, which forces overlaps of 0 or 1. Orthogonal states (|0>, |1>) can be copied with a CNOT; non-orthogonal ones (|0>, |+>, overlap 0.7071) cannot. The check shows the CNOT "copier" turning |+> into a Bell state: its joint fidelity with |+>|+> is 0.5000, and at θ = π/3 it is 0.5999 jointly and 0.6250 for the copy alone.

**Teleportation (T24.2a).** With |ψ> = α|0> + β|1> and a shared |Φ+>, rewriting Alice's two qubits in the Bell basis gives

|ψ>|Φ+> = ½[ |Φ+>|ψ> + |Φ->Z|ψ> + |Ψ+>X|ψ> + |Ψ->XZ|ψ> ].

Alice's Bell measurement returns each outcome with probability 1/4, independent of α and β, and tells Bob which Pauli correction to apply. Over 200 random states and all four outcomes the check finds probability 0.25 and fidelity 1 to within 10^-12.

**Superdense coding (T24.2b).** If Alice applies Z^a X^b to her half of |Φ+> and sends it, Bob's Bell measurement (CX then H) returns (a, b) with probability 1. Teleportation spends 1 e-bit + 2 bits to send 1 qubit; superdense coding spends 1 e-bit + 1 qubit to send 2 bits.

**Deutsch-Jozsa (T24.3).** The amplitude of |0^n> after H^n, oracle, H^n is (1/2^n) Σ_x (-1)^{f(x)}. It is ±1 for a constant f and 0 for a balanced f. The check enumerates all 70 balanced functions on 3 bits: every one gives P(000) = 0.0000.

**Density matrices and no-signalling (T24.4).** The reduced state of either half of |Φ+> is I/2, with purity 0.5, although the pair is pure. Anything Alice does locally, whether a unitary or a measurement whose result she keeps, leaves Bob's reduced state unchanged. The check tries 200 random states with random operations on Alice's side and finds changes below 10^-12.

## Intuition

Linearity is the hero and the villain. It lets a superposition flow through an oracle so that one query "sees" a global property of f (Deutsch-Jozsa). It also forbids copying, because copying is quadratic in the amplitudes.

Entanglement is not a communication channel. It is a correlation resource. On its own it carries nothing (Bob sees I/2); combined with classical bits it can replace a quantum channel (teleportation), and combined with a quantum channel it doubles its classical capacity (superdense coding).

## Worked example: following one teleportation branch

Let |ψ> = cos(π/8)|0> + sin(π/8)|1>. Alice gets the outcome Ψ- (both bits 1). Bob holds XZ|ψ> ∝ -sin(π/8)|0> + cos(π/8)|1>.

- If Bob forgets the corrections and measures, P(1) = cos^2(π/8) = 0.8536.
- If he applies X then Z first, he holds |ψ>, and P(1) = sin^2(π/8) = 0.1464.
- Before the bits arrive, averaged over Alice's four equally likely outcomes, his state is I/2 and P(1) = 0.5.

The arithmetic shows why the two classical bits are essential, and why teleportation cannot outrun light.

## Where density matrices meet practice

Any statement about "the state of qubit 3" in a register is a partial trace. Noise is modelled as a map on ρ: the depolarizing and amplitude-damping channels of L300 #12 are such maps. Different preparations can give the same ρ. Equal mixtures of {|0>, |+>} and of the two eigenvectors of that ρ (weights 0.8536 and 0.1464) cannot be told apart by any experiment, so ρ, not the recipe, is the physical description.

## How this connects to the labs

- L100 #4 prepares the e-bit; lesson 23's Bell measurement is the decoder used in both protocols here.
- L200 #7 (Bernstein-Vazirani) and L200 #8 (Grover's phase oracle) use exactly the phase-kickback step of T24.3.
- L300 #12-#13 work entirely with density matrices. Mitigation estimates expectation values from many shots; it never "copies" or "cleans" the quantum state itself, as no-cloning forbids.

## Common misconceptions

- **"Teleportation copies the qubit."** Alice's original is destroyed by her measurement; one copy exists at all times.
- **"Entanglement sends information instantly."** Bob's local state is I/2 until classical bits arrive (no-signalling).
- **"Deutsch-Jozsa shows an exponential speed-up for a practical problem."** Only against deterministic algorithms; a randomised classical algorithm with k queries errs with probability at most 2^(1-k).
- **"A density matrix is just a probability list."** Off-diagonal entries (coherences) matter: |+><+| and I/2 have the same diagonal but different physics.
- **"No-cloning means you cannot copy any quantum data."** Known or orthogonal states (like computational-basis outputs) are easy to copy; the theorem is about unknown states.
- **"Superdense coding beats information theory."** One qubit alone carries at most one classical bit; the second bit was paid for by the e-bit shared earlier.

## Check yourself

Predict, then verify with code: (1) Bob's reduced state if Alice and Bob share √0.8|00> + √0.2|11>; (2) P(00) in Deutsch-Jozsa for f(x1, x2) = x1 AND x2 (careful: this f is neither constant nor balanced); (3) which Bell state Alice must send to transmit the message 10.
