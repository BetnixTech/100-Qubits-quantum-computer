import time
import random
import json
from typing import List, Dict

# --- Hardware Interface ---
class HardwareInterface:
    @staticmethod
    def calibrate(qubit: int):
        print(f"[Hardware] Calibrating qubit {qubit}")
        # Real lab call goes here, e.g., pulse_generator.calibrate(qubit)
        time.sleep(0.05)

    @staticmethod
    def send_pulse(qubit: int, gate: str):
        print(f"[Hardware] Applying {gate} to qubit {qubit}")
        # Real lab pulse command here
        time.sleep(0.02)

    @staticmethod
    def send_two_qubit_pulse(q1: int, q2: int, gate: str):
        print(f"[Hardware] Applying {gate} to qubits {q1},{q2}")
        # Real lab two-qubit pulse here
        time.sleep(0.05)

    @staticmethod
    def read_state(qubit: int) -> int:
        # Real readout from hardware
        # Replace simulated randomness with actual measurement
        return random.choice([0,1])

# --- Quantum Computer Class ---
class QuantumComputer:
    def __init__(self, num_qubits: int = 100):
        self.num_qubits = num_qubits
        self.calibrated: List[bool] = [False]*num_qubits
        self.queue: List[Dict] = []
        self.log_file = "qc_lab_log.json"

    def _log(self, entry: Dict):
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(entry)+"\n")
        except:
            pass

    def calibrate_qubit(self, qubit: int):
        HardwareInterface.calibrate(qubit)
        self.calibrated[qubit] = True
        self._log({"action":"calibrate","qubit":qubit,"time":time.time()})

    def apply_gate(self, gate: str, qubits: List[int], delay: float=0.0):
        self.queue.append({"type":"single","gate":gate,"qubits":qubits,"delay":delay})
        for q in qubits:
            if self.calibrated[q]:
                if delay>0: time.sleep(delay)
                HardwareInterface.send_pulse(q, gate)
                self._log({"action":"gate","gate":gate,"qubits":[q],"time":time.time()})

    def apply_two_qubit_gate(self, gate: str, q1: int, q2: int, delay: float=0.0):
        self.queue.append({"type":"two","gate":gate,"qubits":[q1,q2],"delay":delay})
        if self.calibrated[q1] and self.calibrated[q2]:
            if delay>0: time.sleep(delay)
            HardwareInterface.send_two_qubit_pulse(q1,q2,gate)
            self._log({"action":"two_qubit_gate","gate":gate,"qubits":[q1,q2],"time":time.time()})

    def measure(self, qubits: List[int], shots: int = 1) -> Dict[int, Dict[str,int]]:
        results = {q: {"0":0,"1":0} for q in qubits}
        for _ in range(shots):
            for q in qubits:
                if self.calibrated[q]:
                    val = HardwareInterface.read_state(q)
                    results[q][str(val)] += 1
        self._log({"action":"measure","qubits":qubits,"shots":shots,"results":results,"time":time.time()})
        return results

# --- Circuit Builder ---
class QuantumCircuit:
    def __init__(self, qc: QuantumComputer):
        self.qc = qc

    def h(self, q): self.qc.apply_gate("H",[q])
    def x(self, q): self.qc.apply_gate("X",[q])
    def y(self, q): self.qc.apply_gate("Y",[q])
    def z(self, q): self.qc.apply_gate("Z",[q])
    def s(self, q): self.qc.apply_gate("S",[q])
    def t(self, q): self.qc.apply_gate("T",[q])
    def swap(self,q1,q2): self.qc.apply_two_qubit_gate("SWAP",q1,q2)
    def cnot(self,q1,q2): self.qc.apply_two_qubit_gate("CNOT",q1,q2)
    def cz(self,q1,q2): self.qc.apply_two_qubit_gate("CZ",q1,q2)

# --- Example Usage ---
if __name__=="__main__":
    qc = QuantumComputer()
    circuit = QuantumCircuit(qc)

    # Calibrate first 5 qubits
    for i in range(5):
        qc.calibrate_qubit(i)

    # Bell state example
    circuit.h(0)
    circuit.cnot(0,1)

    # Multi-shot measurement
    results = qc.measure([0,1],shots=10)
    print("Measurement Results:")
    for q,r in results.items():
        print(f"Qubit {q}: {r}")
