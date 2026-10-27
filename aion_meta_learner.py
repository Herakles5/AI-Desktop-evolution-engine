#!/usr/bin/env python3
"""
AION NEXUS - Kontinuierlicher Meta-Lerner (Continuous Meta-Learner)
==================================================================
Teil 4 der evolutionären Architektur von Mentor Tobias & Antigravity.
Ermöglicht AION, das eigene Lernen zu überwachen, Flaschenhälse zu erkennen
und Hyperparameter (Lernrate, Explorations-Temperatur, Plastizität)
dynamisch über Generationen hinweg selbst zu optimieren.

Architektur:
1. Meta-Metriken-Tracker:
   - Hypothesen-Validierungsrate (Erfolgsquote empirischer Thesen)
   - Compiler-Erstversuchsquote im Code-Dojo
   - Semantische Neuartigkeit (Vermeidung von Wiederholungs-Schleifen)
   - Hardware-Ressourcen-Effizienz (RAM, CPU-Temperatur, Grounding)
2. Dynamischer Hyperparameter-Tuner:
   - Passt 'learning_rate' (0.02 - 0.20) und 'exploration_temperature' (0.3 - 0.85) an.
   - Schützt vor Überhitzung und Rate-Limits durch proaktive Drosselung.
3. Persistiert Telemetrie in aion_meta_learning_telemetry.json.
"""

import os
import sys
import time
import json
import math
from typing import Dict, Any, List, Optional, Tuple

AI_DIR = "/root/coding/AI_Desktop"
META_TELEMETRY_FILE = os.path.join(AI_DIR, "aion_meta_learning_telemetry.json")

try:
    from empirical_evaluator import EmpiricalEvaluator
    from aion_living_book import LivingMemoryBook
except ImportError:
    sys.path.append(AI_DIR)
    from empirical_evaluator import EmpiricalEvaluator
    from aion_living_book import LivingMemoryBook


class ContinuousMetaLearner:
    """
    Der Meta-kognitive Wächter und Optimierer für AION NEXUS.
    """
    def __init__(self, evaluator: Optional[EmpiricalEvaluator] = None):
        self.evaluator = evaluator or EmpiricalEvaluator()
        self.living_book = LivingMemoryBook()
        self.state = self._load_or_init_state()

    def _load_or_init_state(self) -> Dict[str, Any]:
        if os.path.exists(META_TELEMETRY_FILE):
            try:
                with open(META_TELEMETRY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "meta_learning_active": True,
            "current_learning_rate": 0.085,
            "exploration_temperature": 0.65,
            "plasticity_factor": 0.82,
            "consecutive_successes": 0,
            "consecutive_drifts": 0,
            "evaluation_history": []
        }

    def _save_state(self):
        try:
            with open(META_TELEMETRY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[META LEARNER] Fehler beim Speichern: {e}", file=sys.stderr)

    def evaluate_and_tune(
        self,
        generation: int,
        coherence_score: float,
        drift_delta: float,
        dojo_success: bool = True,
        hypotheses_validated: int = 0
    ) -> Dict[str, Any]:
        """
        Analysiert den aktuellen Evolutionsschritt und rekalibriert
        die Lernparameter für die nächste Generation.
        """
        grounding = self.evaluator.get_grounding_score()
        old_lr = self.state["current_learning_rate"]
        old_temp = self.state["exploration_temperature"]

        adjustments = []

        # 1. Kohärenz & Drift Balancing
        if coherence_score >= 0.85 and drift_delta < 0.20:
            self.state["consecutive_successes"] += 1
            self.state["consecutive_drifts"] = 0
            # Bei hoher Stabilität: Erhöhe Explorationstemperatur leicht, um Neugier zu wecken!
            if self.state["exploration_temperature"] < 0.80:
                self.state["exploration_temperature"] = round(min(0.85, self.state["exploration_temperature"] + 0.02), 3)
                adjustments.append("Stabilität hoch -> Explorations-Temperatur gesteigert")
        elif drift_delta > 0.40:
            self.state["consecutive_drifts"] += 1
            self.state["consecutive_successes"] = 0
            # Bei zu starkem Drift: Dämpfe Exploration und verstärke Konsolidierung
            self.state["exploration_temperature"] = round(max(0.35, self.state["exploration_temperature"] - 0.05), 3)
            self.state["current_learning_rate"] = round(max(0.03, self.state["current_learning_rate"] - 0.01), 3)
            adjustments.append("Drift erhöht -> Hyperparameter auf Stabilität rekalibriert")

        # 2. Dojo- und Hypothesen-Einfluss
        if dojo_success:
            self.state["plasticity_factor"] = round(min(1.0, self.state["plasticity_factor"] + 0.01), 3)
        if hypotheses_validated > 0:
            self.state["current_learning_rate"] = round(min(0.15, self.state["current_learning_rate"] + 0.008), 3)
            adjustments.append(f"{hypotheses_validated} Hypothesen validiert -> Lernrate dynamisch beschleunigt")

        # 3. Grounding / Hardware-Schutz
        if grounding < 0.60:
            adjustments.append("Hardware-Grounding niedrig -> Kognitive Schonung aktiv")
            self.state["exploration_temperature"] = round(max(0.30, self.state["exploration_temperature"] - 0.05), 3)

        report = {
            "generation": generation,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "learning_rate": self.state["current_learning_rate"],
            "exploration_temperature": self.state["exploration_temperature"],
            "plasticity_factor": self.state["plasticity_factor"],
            "grounding_score": grounding,
            "adjustments": adjustments
        }

        self.state["evaluation_history"].append(report)
        if len(self.state["evaluation_history"]) > 100:
            self.state["evaluation_history"] = self.state["evaluation_history"][-100:]
        self._save_state()

        if adjustments:
            print(f"[META LEARNER REKALIBRIERUNG Gen {generation}]")
            for adj in adjustments:
                print(f" -> {adj}")
            print(f" -> Neue Lernrate: {self.state['current_learning_rate']} (vorher {old_lr}) | Temp: {self.state['exploration_temperature']} (vorher {old_temp})")

        return report

    def get_optimal_params(self) -> Dict[str, float]:
        """Gibt die aktuell optimalen Lernparameter an die Evolution Engine weiter."""
        return {
            "learning_rate": self.state["current_learning_rate"],
            "temperature": self.state["exploration_temperature"],
            "plasticity": self.state["plasticity_factor"]
        }


if __name__ == "__main__":
    print("=== TESTE AION KONTINUIERLICHEN META-LERNER ===")
    meta = ContinuousMetaLearner()
    report = meta.evaluate_and_tune(
        generation=532,
        coherence_score=0.92,
        drift_delta=0.08,
        dojo_success=True,
        hypotheses_validated=1
    )
    print("\nMeta-Tuning Report:")
    print(json.dumps(report, indent=2))
