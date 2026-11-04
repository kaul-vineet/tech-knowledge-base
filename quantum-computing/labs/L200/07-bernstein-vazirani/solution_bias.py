"""Build-task solution for lab 07: support f(x) = secret . x XOR bias.

Run: python solution_bias.py
A constant bias only adds a global phase (-1), so the measured string must still be `secret`.
The numpy part runs anywhere; bv_oracle_with_bias needs qiskit.
"""
import crosscheck_numpy as cc
from qsim import statevector as sv


def oracle_ops_with_bias(secret, bias):
    ops = cc.oracle_ops(secret)
    if bias:
        ops.append(sv.x(len(secret)))       # f(x) XOR 1: flip the ancilla once, for every input
    return ops


def recovered_numpy(secret, bias):
    n = len(secret)
    return cc.input_probabilities(sv.run(n + 1, cc.bv_ops(oracle_ops_with_bias(secret, bias), n)), n)


def bv_oracle_with_bias(secret, bias):
    import bv_lab
    qc = bv_lab.bv_oracle(secret)
    if bias:
        qc.x(len(secret))                   # same feature in Qiskit: one X on the ancilla
    return qc


if __name__ == "__main__":
    for bias in (0, 1):
        print(f"secret 1011 bias {bias}: numpy {recovered_numpy('1011', bias)}")
