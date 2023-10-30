# import numpy as np
# from qiskit.circuit import QuantumCircuit
# from qiskit.transpiler.passes.synthesis import SolovayKitaev
# from qiskit.quantum_info import Operator
#
# circuit = QuantumCircuit(1)
# circuit.rx(0.8, 0)
#
# print("Original circuit:")
# print(circuit.draw())
#
# skd = SolovayKitaev(recursion_degree=2)
#
# discretized = skd(circuit)
#
# print("Discretized circuit:")
# print(discretized.draw())
#
# print("Error:", np.linalg.norm(Operator(circuit).data - Operator(discretized).data))
from qiskit.synthesis import generate_basic_approximations
from qiskit.transpiler.passes import SolovayKitaev
from qiskit import QuantumCircuit

qc = QuantumCircuit.from_qasm_file('qft_3.qasm')
# print(qc.draw())
CliffordPlusT_gates = ["z", "t", "h"]  # ['x', 'y', 'z', 'h', 's', 't', 'cx', 'cz', 'ccx', 'cswap']
approx = generate_basic_approximations(CliffordPlusT_gates, depth=5)
skd = SolovayKitaev(recursion_degree=2, basic_approximations=approx)
discretized = skd(qc)
print(discretized.qasm())
# print(discretized.draw())

