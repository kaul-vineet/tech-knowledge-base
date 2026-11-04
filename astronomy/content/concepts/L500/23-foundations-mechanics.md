**Concept: the mechanics and geometry under every orbit and every sky position**

## Why it matters
Lessons 2, 5, 11 and 20 used formulas without proving them: the altitude of a star from its declination and hour angle, Kepler's third law, a leapfrog orbit that "conserves energy", and V² = GM/R for a rotation curve. Each of those formulas has assumptions. If you do not know them, you cannot tell when a result is wrong. This lesson derives the formulas from two starting points, Newton's law of gravitation and the dot product on a unit sphere. It then checks each one by an independent numerical route.

## Definitions
- **Two-body problem.** Two point masses M and m attract each other with F = GMm/r². The separation vector **r** obeys r̈ = −G(M+m) **r**/r³: one body moving around a fixed centre with mass parameter G(M+m).
- **Conserved quantities.** For any central force, the specific angular momentum h = |**r** × **v**| is conserved. For gravity, which is conservative, the specific energy E = v²/2 − GM/r is conserved too.
- **Semi-major axis a and eccentricity e.** The closest and farthest distances are r_p = a(1−e) and r_a = a(1+e).
- **Virial.** G_v = Σ **p**ᵢ·**r**ᵢ. Its time derivative links kinetic energy K and potential energy U.
- **Spherical triangle.** Three points on the unit sphere joined by great-circle arcs. The sides are angles at the centre; the angles sit at the vertices.

## Key results (proved in the lesson's `theorems`)
1. **Kepler III:** T² = 4π²a³/(G(M+m)). In au, years and solar masses GM☉ = 4π², the constant lesson 11 uses. The planet's own mass shortens its period by (1 + m/M)^(−1/2). For Jupiter this is 0.05 %.
2. **Vis-viva:** v² = GM(2/r − 1/a), and E = −GM/(2a). The energy depends only on a, not on e. Escape means E ≥ 0, so v_esc = √(2GM/r) = √2 · v_circ.
3. **Virial theorem:** 2⟨K⟩ + ⟨U⟩ = 0 for a bound gravitating system. It holds only as a **time average**.
4. **Spherical cosine rule:** cos a = cos b cos c + sin b sin c cos A. In the pole–zenith–star triangle it becomes sin h = sin δ sin φ + cos δ cos φ cos H, the exact line in `sky.py`.

## Intuition
- Conservation laws do most of the work. At the two apsides the velocity is perpendicular to **r**, so angular momentum becomes simply r·v there. Energy then fixes v at every r. That is the whole vis-viva proof.
- The virial theorem is about a quantity that cannot grow forever. G_v is bounded for a bound system, so its average rate of change must be zero. The algebra shows that this rate of change is 2K + U.
- Spherical trigonometry is linear algebra in disguise. Put one vertex at the pole and the cosine rule is a dot product. Alt-az is a rotation of the star's unit vector from a frame tied to the celestial pole into a frame tied to your horizon. The check implements that rotation and compares it with `sky.py`.

## Worked example (real run of `python mechanics.py`)
- Kepler III with IAU 2015 B3's GM☉ and 1 au gives T = **365.2569 d**, the sidereal year. A leapfrog integration of a circular orbit with m/M = 9.546 × 10⁻⁴ measures T = 0.99952317 yr. The formula gives 0.99952304 yr, a relative difference of 1.3 × 10⁻⁷.
- Vis-viva on an e = 0.6 orbit: the semi-major axis is *measured* from the integrated orbit, not assumed. Along 100,001 samples the largest relative difference between v² and GM(2/r − 1/a) is **3.0 × 10⁻⁸**. Escape speed from Earth's surface is **11.18 km/s**. A body launched at 0.99 v_esc stays bound (energy −0.785); at 1.01 v_esc it does not.
- Virial: on the e = 0.6 orbit, the instantaneous 2K/|U| swings from **0.400 to 1.600**. Over three whole orbits the average is **1.000000**. Over the first quarter orbit it is 1.249.
- Alt-az: the cosine rule holds on 10,000 random triangles to 1.9 × 10⁻¹⁴. Lesson 2's `altaz` agrees with the rotation-matrix route to 7 × 10⁻¹⁵ deg for all ten stars, and Deneb is again at **56.27°**.

## A numerical lesson inside the geometry
The cosine rule is exact mathematics but poor numerics for tiny angles. For two stars 0.01″ apart, cos θ = 1 − θ²/2 with θ² ≈ 10⁻¹⁵, close to double precision's resolution of about 2 × 10⁻¹⁶. Most digits vanish before arccos, whose slope is infinite at 1. The float64 result is 0.00972″, about 3 % wrong. The atan2 (Vincenty) form keeps full precision, which is why lesson 7 uses it (problem 23.9). Proving a formula and computing it well are separate jobs.

## Common misconceptions
- "Kepler's third law has the same constant for all planets." Only approximately: the constant is G(M+m), so heavier planets have slightly shorter periods.
- "A faster body is always on a bigger orbit." At a given r, a larger v means a larger a, yes. But on one orbit, speed is highest at perihelion, the *smallest* r.
- "Escape velocity depends on direction." Not for a pure two-body problem. E ≥ 0 is the condition, whatever the direction (ignoring collisions with the central body).
- "The virial theorem holds at every moment." Only on average, and only for systems that are bound and in a steady state. Applying it to a galaxy cluster assumes the cluster is relaxed. That is an assumption, not a theorem.
- "Azimuth is just atan(east/north)." Plain atan loses the quadrant. Use atan2, and treat the zenith, where both components vanish, as a special case.
- "The check proves the formula." A numerical check can falsify a formula, or confirm it to the accuracy of the method (leapfrog error, floating point). The proof is what makes it general. The check guards the implementation.

## Where this is used
- Lesson 2: the alt-az formula.
- Lesson 5: Kepler's laws, Kepler's equation.
- Lesson 7: the separation formula.
- Lesson 11: leapfrog and energy.
- Lesson 20: V² = GM(<R)/R is theorem 1 applied to a galaxy.
- Lesson 22's capstone: the transit-duration bound uses Kepler III.
