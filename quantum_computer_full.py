import time
import random
import json
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor

# --------------------------
# Hardware Interface
# --------------------------
class HardwareInterface:
    @staticmethod
    def calibrate(qubit: int):
        print(f"[Hardware] Calibrating qubit {qubit}")
        time.sleep(0.02)

    @staticmethod
    def send_pulse(qubit: int, gate: str):
        print(f"[Hardware] Applying {gate} to qubit {qubit}")
        time.sleep(0.01)

    @staticmethod
    def send_two_qubit_pulse(q1: int, q2: int, gate: str):
        print(f"[Hardware] Applying {gate} to qubits {q1},{q2}")
        time.sleep(0.02)

    @staticmethod
    def read_state(qubit: int) -> int:
        # Replace with real hardware readout
        return random.choice([0, 1])

# --------------------------
# Quantum Computer Class
# --------------------------
class QuantumComputer:
    def __init__(self, num_qubits: int = 100):
        self.num_qubits = num_qubits
        self.calibrated: List[bool] = [False]*num_qubits
        self.log_file = "qc_lab_surface_log.json"

    def _log(self, entry: Dict):
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry)+"\n")

    def calibrate_qubit(self, qubit: int):
        HardwareInterface.calibrate(qubit)
        self.calibrated[qubit] = True
        self._log({"action":"calibrate","qubit":qubit,"time":time.time()})

    # Parallel single-qubit gates
    def apply_gate_parallel(self, gate: str, qubits: List[int]):
        def task(q): 
            if self.calibrated[q]:
                HardwareInterface.send_pulse(q, gate)
                self._log({"action":"gate","gate":gate,"qubits":[q],"time":time.time()})
        with ThreadPoolExecutor() as executor:
            executor.map(task, qubits)

    def apply_two_qubit_gate(self, gate: str, q1: int, q2: int):
        if self.calibrated[q1] and self.calibrated[q2]:
            HardwareInterface.send_two_qubit_pulse(q1,q2,gate)
            self._log({"action":"two_qubit_gate","gate":gate,"qubits":[q1,q2],"time":time.time()})

    # Physical measurement
    def measure_physical(self, qubits: List[int], shots: int = 1) -> Dict[int, Dict[str,int]]:
        results = {q: {"0":0,"1":0} for q in qubits}
        for _ in range(shots):
            for q in qubits:
                val = HardwareInterface.read_state(q)
                results[q][str(val)] += 1
        self._log({"action":"measure_physical","qubits":qubits,"shots":shots,"results":results,"time":time.time()})
        return results

    # Logical qubit measurement using distance-3 repetition code (example)
    def measure_logical(self, qubit_group: List[int], shots: int = 1) -> Dict[str,int]:
        results = {"0":0,"1":0}
        for _ in range(shots):
            votes = []
            for q in qubit_group:
                votes.append(HardwareInterface.read_state(q))
            corrected = max(set(votes), key=votes.count)
            results[str(corrected)] += 1
        self._log({"action":"measure_logical","qubits":qubit_group,"shots":shots,"results":results,"time":time.time()})
        return results

# --------------------------
# Circuit Builder
# --------------------------
class QuantumCircuit:
    def __init__(self, qc: QuantumComputer):
        self.qc = qc

    def h(self, q): self.qc.apply_gate_parallel("H",[q])
    def x(self, q): self.qc.apply_gate_parallel("X",[q])
    def y(self, q): self.qc.apply_gate_parallel("Y",[q])
    def z(self, q): self.qc.apply_gate_parallel("Z",[q])
    def s(self, q): self.qc.apply_gate_parallel("S",[q])
    def t(self, q): self.qc.apply_gate_parallel("T",[q])
    def swap(self,q1,q2): self.qc.apply_two_qubit_gate("SWAP",q1,q2)
    def cnot(self,q1,q2): self.qc.apply_two_qubit_gate("CNOT",q1,q2)
    def cz(self,q1,q2): self.qc.apply_two_qubit_gate("CZ",q1,q2)

# --------------------------
# Example Usage
# --------------------------
if __name__ == "__main__":
    qc = QuantumComputer()
    circuit = QuantumCircuit(qc)

    # Calibrate qubits
    for i in range(9):
        qc.calibrate_qubit(i)

    # Define logical qubits using groups of 3 physical qubits
    logical0 = [0,1,2]
    logical1 = [3,4,5]

    # Bell state on logical qubits
    circuit.h(logical0[0])
    circuit.cnot(logical0[0],logical1[0])

    # Logical qubit measurement
    results0 = qc.measure_logical(logical0, shots=10)
    results1 = qc.measure_logical(logical1, shots=10)
    print("Logical Qubit 0 Results:", results0)
    print("Logical Qubit 1 Results:", results1)
