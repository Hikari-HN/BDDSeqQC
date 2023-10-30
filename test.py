from kernel import *

Sim = BDDSeqSim(2, 1, 32)
result_list = [[0], [1], [0], [1], [0], [1]]
input_basis_list = [0] * len(result_list)
Sim.init_stored_state_by_basis(0)
for result, input_basis in zip(result_list, input_basis_list):
    Sim.init_input_state_by_basis(input_basis)
    Sim.init_comb_bdd()
    Sim.H(0)
    Sim.T(0)
    Sim.H(0)
    Sim.CZ(0, 1)
    Sim.Z(0)
    Sim.S(0)
    Sim.T(0)
    Sim.H(0)
    Sim.T(0)
    Sim.CZ(0, 1)
    Sim.H(0)
    Sim.T(0)
    Sim.H(0)
    Sim.Z(1)
    Sim.measure(result)
    print("Prob: ", Sim.get_step_prob())
    Sim.print_stored_state_vec()