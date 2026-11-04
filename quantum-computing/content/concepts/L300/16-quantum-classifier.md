# Concept: a variational quantum classifier

## Why it matters
"Quantum machine learning" is often presented as the obvious use of quantum computers. As an engineer you need two habits before you believe any claim. Compare against a classical baseline on a held-out test set. Check that the model can be trained at all once it grows. This lesson builds the smallest honest experiment: it shows a tie, not an advantage, and then shows why naive scaling fails.

## Mental model
A variational classifier is a parameterised circuit used as a model f(x; w). Data enters as rotation angles (angle encoding). Trainable layers follow, and one expectation value is the score; its sign is the class. Training is the hybrid loop of lesson 15 with a data-dependent cost.

```
x = (x0, x1) ─▶ RY(x0), RY(x1) ─▶ [RY(w) on every qubit ─ CNOT chain] × L ─▶ <Z0> + b ─▶ sign ─▶ class
                 encoding                 trainable layers                     readout
```

## How it works
1. **Angle encoding.** Each feature becomes one rotation. PennyLane's `AngleEmbedding(features, wires, rotation="Y")` does this. Wide models reuse the two features on more qubits → see lab step 1.
2. **Parameter-shift gradients.** For RY, ∂⟨Z⟩/∂w = (⟨Z⟩(w + π/2) − ⟨Z⟩(w − π/2))/2, exactly. That costs two circuit evaluations per weight per data point → see lab step 2.
3. **Train/test split and baseline.** 60 points from two overlapping blobs: 40 for training, 20 held out. Logistic regression in numpy (3 parameters) is the baseline → see lab steps 1 and 3.
4. **Worked example** (`classifier_lab.py`, dataset seed 3): quantum 2 qubits × 2 layers (5 parameters), train 0.975 / test 0.9. Logistic regression, train 0.975 / test 0.85. Over 5 dataset seeds the two models are equal 3 times, and the quantum model is one test point ahead twice → see lab step 3.
5. **Flat gradients at scale.** With angles uniform in [0, 2π), the median |∂⟨Z0⟩/∂w| is 0.7171 at 2 qubits × 2 layers, 0.1121 at 6 × 12, and 0.0208 at 10 × 20. That is below the shot-noise floor of a 1000-shot gradient (0.0224) → see lab step 4.
6. **Near-identity start.** Initialise angles ~N(0, 0.05²) so each layer starts as roughly the identity (the idea behind Grant et al.'s initialisation in PennyLane's barren-plateau demo). Keep a local readout. The 10 × 20 model then starts at a median 0.863 → see lab step 6.

## Failure modes
- **Barren plateau.** Training loss barely moves and gradient norms in the JSON log sit at the noise floor. With shots, the optimiser performs a random walk. Measure gradients before you train.
- **Global readout.** Reading the parity of all qubits stays flat (0.0303) even with the good initialisation (tryIt 1).
- **Shot noise at prediction time.** Classifying from 100 shots instead of the exact ⟨Z0⟩ dropped test accuracy from 0.9 to 0.85 (tryIt 2).

## Common mistakes
- Reporting training accuracy, or one lucky split. Use a held-out set and several seeds; 1 of 20 test points is 0.05 accuracy.
- Skipping the classical baseline. Here 3 logistic-regression parameters match a circuit that needed 21,600 circuit evaluations to train (60 epochs × 9 evaluations × 40 points).
- Making the circuit wider and deeper "for capacity" without checking that its gradients survive.
