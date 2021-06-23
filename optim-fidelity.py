#!/usr/bin/env python3
# requires cvxpy, bayesian-optimization, plac, qiskit

import bayes_opt
import qiskit as qk
import qiskit.quantum_info as qkqi
import qiskit.ignis.verification.tomography as qktomo
import zlib
import libpulse


def uncompress(obj):
    return pickle.loads(zlib.decompress(obj))


def get_circuit_priors(t, σ=0.5):
    t1 = libpulse.depth4.t1(t)
    t2 = libpulse.depth4.t2(t)

    return {
        "ta": (t1 - σ, t1 + σ),
        "tb": (t2 - σ, t2 + σ),
        "tc": (t2 - σ, t2 + σ),
        "td": (t1 - σ, t1 + σ),
    }


def get_ideal_circuit_params(t):
    t1 = libpulse.depth4.t1(t)
    t2 = libpulse.depth4.t2(t)

    return {
        "ta": t1,
        "tb": t2,
        "tc": t2,
        "td": t1,
    }


def circuit_ansatz(ta, tb, tc, td):
    """
    returns a general depth 4 decomposed circuit
    """
    qregs = qk.QuantumRegister(3)
    ideal_circ = qk.QuantumCircuit(qregs)

    ideal_circ.rzx(2 * ta, qregs[0], qregs[1])
    ideal_circ.rzx(2 * tb, qregs[1], qregs[2])
    ideal_circ.rzx(2 * tc, qregs[0], qregs[1])
    ideal_circ.rzx(2 * td, qregs[1], qregs[2])

    return ideal_circ


def optimize(theta, result: qk.result.result.Result, circuits: list, simulate=True):
    print(f"starting optimization for {theta=}")
    if not simulate:
        process_data = qktomo.ProcessTomographyFitter(result, circuits, meas_basis="Pauli", prep_basis="Pauli")
        choi_fit = process_data.fit(method="cvx", standard_weights=True, psd=True)
        choi_tomo = qkqi.Choi(choi_fit.data)
        print("precomuted choi matrix from tomography data")
    else:
        choi_tomo = qkqi.Choi(circuit_ansatz(**get_ideal_circuit_params(theta)))
        print("precomuted choi matrix from ideal target circuit")
        

    def objective(**params):
        ideal_circuit = circuit_ansatz(**params)
        ideal_op = qkqi.Operator(ideal_circuit)

        fid = qkqi.process_fidelity(
            channel=choi_tomo,
            target=ideal_op,
            require_cp=False,
            require_tp=False,
        )
        return fid

    optimizer = bayes_opt.BayesianOptimization(f=objective, pbounds=get_circuit_priors(theta), verbose=1)
    optimizer.maximize(init_points=64, n_iter=512-64)
    return optimizer.res, optimizer.max


import pathlib, pickle, json


def to_float_key(dict):
    return {float(k): v for (k, v) in dict.items()}


def main(path="./results/ibmq_casablanca/16.June/depth4"):
    # load data
    here = pathlib.Path(__file__).parent.absolute()
    path = here / path
    with open(path / "full_results.q4q5q6.pickle", "rb") as handle:
        results = to_float_key(pickle.load(handle))

    with open(path / "qpt_exps.q4q5q6.pickle", "rb") as handle:
        qpt_experiments = to_float_key(pickle.load(handle))

    ANGLES = sorted(results.keys())
    assert ANGLES == sorted(qpt_experiments.keys())

    print(f"found data for {ANGLES=}")

    # optimize
    for angle in ANGLES:
        res, best = optimize(
            angle,
            results[angle][2],
            uncompress(qpt_experiments[angle])["transpiled_circuits"],
        )
        with open(path / f"optim-sim-{angle}.json", "w") as f:
            json.dump({"all": res, "best": best}, f)


if __name__ == "__main__":
    import plac

    plac.call(main)
