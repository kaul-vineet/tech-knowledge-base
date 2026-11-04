**Concept: how wrong is a time-stepped model, and why?**

## Why it matters
L100 #4 dropped a parcel with Euler's method and watched the error fall from 1.47 m to 0.0147 m as dt shrank. L200 #9 saw an explicit solver take 3,027 steps on a stiff circuit that an implicit one finished in 1,000. Those were observations. This lesson explains them: where the error comes from, why it scales as a power of h, why some step sizes explode however accurate they look, and why making h ever smaller eventually makes things worse.

## Definitions
- **One-step method.** It advances y′ = f(t, y) by yₙ₊₁ = yₙ + hΦ(tₙ, yₙ, h). For explicit Euler, Φ = f(tₙ, yₙ).
- **Local truncation error τ.** The error of *one* step that starts from the exact solution.
- **Global error eₙ = y(tₙ) − yₙ.** The error after n steps, with every earlier error carried along.
- **Order p.** The global error is O(hᵖ). For a one-step method this follows from a local error of O(hᵖ⁺¹).
- **Lipschitz constant L.** |f(t, y) − f(t, z)| ≤ L|y − z|. It measures how fast nearby solutions pull apart.
- **Stability function R(z), with z = hλ.** One step on y′ = λy multiplies y by R(z). The **region of absolute stability** is the set where |R(z)| ≤ 1.
- **Stiffness.** The step is limited by stability, not accuracy. The usual cause is fast-decaying modes (large negative λ) alongside the slow behaviour you care about.
- **Unit roundoff u.** For IEEE 754 binary64 with round-to-nearest, fl(x) = x(1 + δ) with |δ| ≤ u = 2⁻⁵³ ≈ 1.1e-16. Machine epsilon is 2u.

## Key results
1. **Euler (Theorem 24.1).** Taylor's theorem gives τ = (h²/2)y″(ξ). The Lipschitz condition gives |eₙ₊₁| ≤ (1 + hL)|eₙ| + Mh²/2, which unrolls to |eₙ| ≤ (hM/2L)(e^(L(tₙ − t₀)) − 1). That is first order: n = T/h steps, each adding O(h²).
2. **RK4 (Theorem 24.2).** On y′ = λy one step gives exactly R(z) = 1 + z + z²/2 + z³/6 + z⁴/24, which is e^z truncated after z⁴. For general f there are eight order conditions on the coefficients, and the check verifies all eight in exact fractions. The local error is O(h⁵) and the global error O(h⁴).
3. **Stability (Theorem 24.3).** Explicit Euler gives yₙ = (1 + z)ⁿy₀, which decays only inside the disc |1 + z| < 1. For real λ < 0 that means h < 2/|λ|. Implicit Euler gives 1/(1 − z), which decays for every z with Re z < 0 (A-stability). RK4's real-axis limit is −2.785.
4. **Floating point (Theorem 24.4).** Every operation is correctly rounded with relative error at most u. Subtracting nearly equal numbers magnifies relative error by (|a| + |b|)/|a − b|. A forward difference has error ≈ (h/2)|f″| + 2u|f|/h, which is smallest near h* = 2√(u|f|/|f″|).

## Intuition
Picture global error as a ledger. Each step deposits a local error, and the ODE's own dynamics multiply the existing balance by about (1 + hL) per step. Order drops by one from local to global simply because there are T/h deposits.

Stability is a different question from accuracy. On y′ = −50y the exact solution vanishes almost at once. Explicit Euler with h = 0.041 multiplies the solution by −1.05 each step and explodes. You will not notice by looking at the first few steps.

Round-off is the floor under everything. Each step adds an error of order u, so very many tiny steps eventually lose to rounding.

## Worked example (numbers from the check scripts)
- **Euler on y′ = y − t² + 1, y(0) = 0.5, to t = 2.** Halving h divides the local error by 3.95-4.00 (order 2) and the global error by 1.82-1.99. The observed order reaches 0.990. At h = 0.1 the global error is 0.242, against a Theorem 24.1 bound of 0.541 (L = 1, M = 0.5e² − 2 = 1.695). The bound is valid, but about twice the true value.
- **RK4 on the same problem.** Error ratios per halving are 15.59, 15.81, 15.91 and 15.96, and the observed order is 3.996. At z = −0.13, e^z − R(z) = −3.03e-7, close to z⁵/120 = −3.09e-7.
- **Stiff problem y′ = −1000(y − cos t) − sin t.** The exact solution is cos t, which is smooth. Explicit Euler with 952 steps blows up to 2.7e33, while with 1,053 steps the error is 6.4e-4. Implicit Euler with 20 steps gives an error of 1.9e-5.
- **Floating point.** (1 − cos x)/x² at x = 1e-8 returns 0.0, while the rewritten 2sin²(x/2)/x² returns 0.5. Adding 0.1 ten times gives 0.9999999999999999, while `math.fsum` gives 1.0. The forward-difference error is smallest at h = 1e-7, near √ε (the grid is in decades). In float32, Euler stops improving after about 10⁴ steps.

## Where the course uses it
- **L100 #4.** The 1.47 → 0.0147 m sequence is Theorem 24.1's O(h). The exactness of RK4 there comes from y″ being constant, so its higher derivatives vanish.
- **L200 #9.** The adaptive RK45 error estimate compares a 4th- and a 5th-order solution. The stiff RC circuit is Theorem 24.3.
- **L300 #15.** A co-simulation communication step that is too large causes chatter for the same reason: an explicit coupling outside its stability limit.
- **L300 #16.** NumPy and the Python loop agree only to 9.1e-14, because floating-point addition is not associative and vectorised code sums in a different order.

## Common misconceptions
- **"Smaller steps are always more accurate."** Round-off grows as the number of steps grows. The difference-quotient example has an optimum near 1e-7, and float32 Euler bottoms out near 10⁴ steps.
- **"A method of order 4 is 4 times better."** Order describes how the error *scales*. Halving h cuts RK4's error 16×, but at a fixed h a low-order method can still win on a rough (non-smooth) problem.
- **"If it is accurate, it is stable."** Stability is a property of hλ, not of how smooth the answer is. Stiff problems have smooth solutions.
- **"Implicit methods are more accurate."** Implicit Euler is still first order. Its advantage is stability: it lets the step size follow accuracy.
- **"0.1 + 0.2 ≠ 0.3 is a Python bug."** It is IEEE 754 working as specified: 0.1 has no finite binary expansion. Compare with tolerances, and use `math.fsum` or `math.isclose` where it matters.

## Check yourself
1. Why is the global order one less than the local order? (There are T/h steps, each adding O(hᵖ⁺¹).)
2. What is the largest stable explicit Euler step for λ = −50? (0.04)
3. Why does the best forward-difference step scale like √u rather than u? (It balances truncation, which grows with h, against round-off, which grows like 1/h.)

Sources: Verschelde, UIC MCS 471 notes on Runge-Kutta; Princeton COS 323 notes on stability and stiffness; Goldberg (1991); Python docs on floating point. Next: Foundations III, random numbers and Monte Carlo theory.
