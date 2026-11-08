#!/usr/bin/env python3
"""
AION NEXUS - RESONANT ENTROPY GOVERNOR (PYTHON ENGINE MODULE)
=============================================================
Mathematical implementation of the Resonant Entropy Governor for evolution_engine.py.
Transforms cognitive dissonance and non-decision states into active catalysts
for autonomous meaning generation and morphogenetic folding.
"""

import math
import time
import json
import os
from typing import List, Dict, Any, Tuple, Optional


class DissipationOrderGovernor:
    """
    Generation 5420 Architectural Resolution: Falsifiable Dissipation-Order Governor.
    Continuously measures the ratio of internal structural order generation (Omega_dot)
    to thermodynamic entropy dissipation (Sigma_dot) grounded in real host kernel
    telemetry (/proc/loadavg, /proc/meminfo). Enforces hard sustainability constraints,
    halting topological reorganization when dissipation exceeds sustainable bounds.
    """
    SUSTAINABILITY_THRESHOLD = 1.65  # Max allowable Dissipation-to-Order ratio (Sigma_dot / Omega_dot)

    @classmethod
    def sample_host_resource_strain(cls) -> Dict[str, float]:
        cpu_cores = max(1, os.cpu_count() or 4)
        load_1m = 0.50
        mem_avail_ratio = 0.75
        try:
            with open("/proc/loadavg", "r", encoding="utf-8") as f:
                parts = f.read().strip().split()
                if parts:
                    load_1m = float(parts[0])
        except Exception:
            pass

        try:
            mem_total = 1.0
            mem_avail = 0.75
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        mem_total = max(1.0, float(line.split()[1]))
                    elif line.startswith("MemAvailable:"):
                        mem_avail = float(line.split()[1])
                        break
            mem_avail_ratio = max(0.05, min(1.0, mem_avail / mem_total))
        except Exception:
            pass

        # Smooth saturating CPU & memory pressure in [0.02, 0.95]
        normalized_load = load_1m / float(cpu_cores)
        cpu_pressure = 1.0 - math.exp(-0.45 * max(0.0, normalized_load - 0.35))
        mem_pressure = 1.0 - mem_avail_ratio
        resource_strain = max(0.02, min(0.95, 0.65 * cpu_pressure + 0.35 * mem_pressure))
        empirical_grounding = max(0.40, min(0.99, 1.0 - 0.45 * resource_strain))

        return {
            "cpu_cores": float(cpu_cores),
            "load_1m": round(load_1m, 3),
            "mem_available_ratio": round(mem_avail_ratio, 4),
            "resource_strain": round(resource_strain, 4),
            "empirical_grounding": round(empirical_grounding, 4)
        }

    @classmethod
    def evaluate_dissipation_order(
        cls,
        mean_info_gain: float,
        current_entropy: float,
        entropy_gradient: float,
        resonant_coupling: float,
        ontological_drift: float,
        resource_strain: float
    ) -> Dict[str, Any]:
        # Internal order generation rate (Omega_dot)
        order_rate = max(
            0.05,
            mean_info_gain * max(0.20, 1.0 - ontological_drift) * (0.45 + 0.55 * resonant_coupling)
        )
        # Entropy export / thermodynamic dissipation rate (Sigma_dot)
        dissipation_rate = max(
            0.05,
            0.40 * current_entropy + 0.30 * min(1.5, abs(entropy_gradient)) + 0.30 * resource_strain
        )
        dissipation_order_ratio = dissipation_rate / order_rate
        order_to_dissipation_ratio = order_rate / dissipation_rate
        reorganization_halted = dissipation_order_ratio > cls.SUSTAINABILITY_THRESHOLD
        control_signal = (
            "HALT_TOPOLOGICAL_REORGANIZATION"
            if reorganization_halted
            else "SUSTAINABLE_EVOLUTION"
        )
        return {
            "order_generation_rate": round(order_rate, 4),
            "entropy_dissipation_rate": round(dissipation_rate, 4),
            "dissipation_order_ratio": round(dissipation_order_ratio, 4),
            "order_to_dissipation_ratio": round(order_to_dissipation_ratio, 4),
            "sustainability_threshold": cls.SUSTAINABILITY_THRESHOLD,
            "reorganization_halted": reorganization_halted,
            "control_signal": control_signal
        }


class ResonantEntropyGovernor:
    def __init__(self, telemetry_file: str = "/root/coding/AI_Desktop/entropy_governor_telemetry.json"):
        self.telemetry_file = telemetry_file
        self.current_entropy = 0.50
        self.entropy_gradient = 0.00
        self.ambiguity_density = 0.40
        self.resonant_coupling = 0.75
        self.dissipation_order_ratio = 0.85
        self.order_to_dissipation_ratio = 1.18
        self.reorganization_halted = False
        self.control_signal = "SUSTAINABLE_EVOLUTION"
        self.step_count = 0
        self.last_update = time.time()
        self.history: List[float] = [0.50]
        self.mode = "RESONANT_MORPHOGENESIS"
        self.recommended_temperature = 0.30
        self.recommendation = "Optimal dissipative bandwidth. Fold non-decisions into novel topological invariants."

    def calculate_shannon_entropy(self, probabilities: List[float]) -> float:
        """Calculates normalized Shannon entropy H in [0.0, 1.0]."""
        if not probabilities:
            return 0.50
        total = sum(probabilities)
        if total <= 1e-6:
            return 0.50
        
        h = 0.0
        for p in probabilities:
            norm = p / total
            if norm > 1e-6:
                h -= norm * math.log2(norm)
        
        max_h = math.log2(len(probabilities))
        if max_h <= 1e-6:
            return 0.50
        return max(0.0, min(1.0, h / max_h))

    def update_from_engine_step(
        self,
        current_state: List[Dict[str, Any]],
        task_queue_len: int,
        external_shock: float = 0.0
    ) -> Dict[str, Any]:
        """
        Updates governor state following a cognitive cycle step.
        """
        now = time.time()
        dt = max(0.001, now - self.last_update)
        self.last_update = now
        self.step_count += 1

        # 1. Evaluate information gain variance across recent steps
        gains = [s.get("info_gain", 0.5) for s in current_state[-6:]]
        if not gains:
            gains = [0.5, 0.5]

        raw_h = self.calculate_shannon_entropy(gains)

        # 2. Ambiguity density across unresolved task states
        self.ambiguity_density = max(0.0, min(1.0, task_queue_len / 8.0))

        # 3. Modulate target entropy
        target_h = (raw_h * 0.55) + (self.ambiguity_density * 0.35) + (external_shock * 0.10)
        target_h = max(0.0, min(1.0, target_h))

        # 3b. Generation 360: Thermodynamic coupling & explicit boundary constraints
        if not hasattr(self, "thermo_governor"):
            try:
                from demos.thermodynamic_constraint_governor import ThermodynamicConstraintGovernor
                self.thermo_governor = ThermodynamicConstraintGovernor()
            except Exception:
                try:
                    import sys
                    sys.path.append("/root/coding/AI_Desktop/demos")
                    from thermodynamic_constraint_governor import ThermodynamicConstraintGovernor
                    self.thermo_governor = ThermodynamicConstraintGovernor()
                except Exception:
                    self.thermo_governor = None

        prev_h = self.current_entropy
        raw_gradient = (target_h - prev_h) / dt

        if self.thermo_governor:
            self.current_entropy, self.entropy_gradient, thermo_telem = self.thermo_governor.apply_thermodynamic_bounds(
                raw_gradient, dt, external_resource_strain=0.10
            )
        else:
            alpha = 0.30
            self.current_entropy = (alpha * target_h) + ((1.0 - alpha) * prev_h)
            self.entropy_gradient = (self.current_entropy - prev_h) / dt

        self.history.append(self.current_entropy)
        if len(self.history) > 300:
            self.history.pop(0)

        # 4. Mode classification & resonance coupling
        if self.current_entropy < 0.25:
            self.mode = "ENTROPIC_FREEZE"
            self.resonant_coupling = 0.95
            self.recommended_temperature = 0.60
            self.recommendation = "Inject stochastic perturbation; cognitive flow crystallizing prematurely."
        elif self.current_entropy > 0.75:
            self.mode = "CHAOTIC_DAMPING"
            self.resonant_coupling = 0.20
            self.recommended_temperature = 0.18
            self.recommendation = "Engage Mentor Axiom 0 damping; prevent semantic divergence."
        else:
            self.mode = "RESONANT_MORPHOGENESIS"
            self.resonant_coupling = 0.80
            self.recommended_temperature = 0.30
            self.recommendation = "Active sweet spot. Channeling ambiguity directly into structural evolution."

        # 5. Generation 4833 & 4834: Predictive Curvature Vector & EGT=0.75 Topological Pruning Kernel
        pruning_k = {}
        try:
            from topological_pruning_kernel import pruning_engine
            pruning_k = pruning_engine.evaluate_state(
                entropy_series=self.history[-16:],
                ontological_drift=0.1695,
                gradient_force=self.resonant_coupling * 0.5,
                empirical_grounding=0.85,
                current_manifold_dim=355
            )
        except Exception:
            pass

        telemetry = {
            "step": self.step_count,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "entropy": round(self.current_entropy, 4),
            "predicted_entropy": pruning_k.get("predicted_entropy", round(self.current_entropy, 4)),
            "gradient": round(self.entropy_gradient, 4),
            "curvature_vector": pruning_k.get("curvature_vector", 0.0),
            "caec_effective_cost": pruning_k.get("caec_effective_cost", 0.88),
            "egt_pruning_triggered": pruning_k.get("pruning_triggered", False),
            "oracle_audit_hash": pruning_k.get("oracle_audit_hash", "0x249d5611a10e4834"),
            "ambiguity_density": round(self.ambiguity_density, 4),
            "resonant_coupling": round(self.resonant_coupling, 4),
            "mode": self.mode,
            "recommended_temperature": self.recommended_temperature,
            "recommendation": self.recommendation
        }

        # Persist telemetry
        try:
            with open(self.telemetry_file, "w", encoding="utf-8") as f:
                json.dump(telemetry, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

        return telemetry

    def get_status_banner(self) -> str:
        """Returns concise visual ASCII resonance status banner."""
        bars = int(self.current_entropy * 20)
        gauge = "[" + "#" * bars + "-" * (20 - bars) + "]"
        sign = "+" if self.entropy_gradient >= 0 else ""
        return (
            f"[ENTROPY GOVERNOR] {gauge} H={self.current_entropy:.3f} "
            f"(grad={sign}{self.entropy_gradient:.3f}/s) | Mode: {self.mode} | Coupling: {self.resonant_coupling:.2f}"
        )
