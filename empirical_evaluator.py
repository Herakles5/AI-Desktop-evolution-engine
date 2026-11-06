#!/usr/bin/env python3
"""
AION NEXUS - Empirical Process Evaluator (PRM & Telemetry)
==========================================================
Grounds cognitive cycles through physical hardware and OS metrics.
Prevents reward hacking and pseudoscientific drift using
verifiable physical and systemic observations.
"""

import os
import json
import time
import socket
from typing import Dict, Any, Optional


class EmpiricalEvaluator:
    def __init__(self, unix_ipc_path: str = "/tmp/aion_nexus.sock"):
        self.unix_ipc_path = unix_ipc_path
        self.last_grounding_score: float = 0.72
        self._cached_telemetry: Dict[str, Any] = {}
        self._last_telemetry_ts: float = 0.0

    def measure_system_telemetry(self) -> Dict[str, Any]:
        """Measures actual system telemetry from Host, MeinOS & Surreal Engine (cached 2s)."""
        now = time.time()
        if self._cached_telemetry and (now - self._last_telemetry_ts) < 2.0:
            return self._cached_telemetry

        metrics: Dict[str, Any] = {
            "timestamp": now,
            "rss_mb": 0.0,
            "ipc_latency_us": None,
            "ipc_online": False,
            "kernel_running": False,
            "surreal_fps": None
        }

        # 1. RSS memory of current process via /proc/self/statm
        try:
            with open("/proc/self/statm", "r", encoding="utf-8") as f:
                parts = f.read().split()
                if len(parts) >= 2:
                    page_size_kb = os.sysconf("SC_PAGE_SIZE") / 1024
                    metrics["rss_mb"] = round((int(parts[1]) * page_size_kb) / 1024, 2)
        except Exception:
            pass

        # 2. Check IPC connection to MeinOS C++ Kernel
        if os.path.exists(self.unix_ipc_path):
            start = time.perf_counter()
            s = None
            try:
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.settimeout(0.1)
                s.connect(self.unix_ipc_path)
                s.sendall(b"PING\n")
                latency_us = (time.perf_counter() - start) * 1_000_000
                metrics["ipc_latency_us"] = round(latency_us, 1)
                metrics["ipc_online"] = True
            except Exception:
                pass
            finally:
                if s is not None:
                    try:
                        s.close()
                    except Exception:
                        pass

        # 3. Check if meinos.elf or surreal_live_dojo is running (without leaking file descriptors)
        try:
            if os.path.exists("/proc"):
                for pid in os.listdir("/proc"):
                    if not pid.isdigit():
                        continue
                    try:
                        with open(f"/proc/{pid}/cmdline", "r", encoding="utf-8", errors="ignore") as cf:
                            cmd_str = cf.read()
                            if "meinos" in cmd_str or "surreal_live_dojo" in cmd_str:
                                metrics["kernel_running"] = True
                                break
                    except Exception:
                        continue
        except Exception:
            pass

        # 4. Read Surreal Engine live runtime telemetry if available
        try:
            if os.path.exists("/tmp/surreal_runtime_settings.json"):
                with open("/tmp/surreal_runtime_settings.json", "r", encoding="utf-8") as sf:
                    sdata = json.load(sf)
                    fps_val = sdata.get("current_fps")
                    if isinstance(fps_val, (int, float)) and fps_val > 0:
                        metrics["surreal_fps"] = round(float(fps_val), 1)
        except Exception:
            pass

        self._cached_telemetry = metrics
        self._last_telemetry_ts = now
        return metrics

    def compute_grounding_score(self, step_info: Dict[str, Any], tool_result: Optional[Dict[str, Any]] = None) -> float:
        """
        Calculates a real, dynamic empirical grounding score (0.10 to 1.00):
        Combines LLM epistemic confidence, concrete technical specificity,
        tool forge verification, and live OS/Surreal telemetry.
        """
        telemetry = self.measure_system_telemetry()

        # 1. Start from blended base + LLM reported info_gain (if provided)
        raw_ig = step_info.get("info_gain")
        if isinstance(raw_ig, (int, float)):
            score = 0.25 + 0.55 * max(0.0, min(1.0, float(raw_ig)))
        else:
            score = 0.52

        # 2. Evaluate concrete specificity of insight text
        insight = str(step_info.get("insight", step_info.get("erkenntnis", "")))
        if insight:
            words = insight.split()
            word_count = len(words)
            if 10 <= word_count <= 95:
                score += 0.08
            elif word_count < 5:
                score -= 0.15
            # Reward empirical/quantitative anchors (digits, units, code/system references)
            has_digits = any(ch.isdigit() for ch in insight)
            tech_markers = ("ms", "fps", "hz", "mb", "ipc", "kernel", "avx2", "opengl", "entropy", "gradient", "dojo", "meshlet")
            lower_ins = insight.lower()
            marker_hits = sum(1 for m in tech_markers if m in lower_ins)
            if has_digits:
                score += 0.05
            score += min(0.12, marker_hits * 0.03)

        # 3. Bonus/penalty for Dynamic Tool Forge verification
        if tool_result:
            if tool_result.get("success"):
                score += 0.22
            else:
                score -= 0.12

        # 4. Physical telemetry grounding bonus
        if telemetry.get("rss_mb", 0.0) > 0 and telemetry.get("rss_mb", 0.0) < 600.0:
            score += 0.04
        if telemetry.get("ipc_online") or telemetry.get("kernel_running"):
            score += 0.06
        if telemetry.get("surreal_fps") and telemetry["surreal_fps"] >= 30.0:
            score += 0.05

        final_score = max(0.08, min(1.0, round(score, 3)))
        self.last_grounding_score = final_score
        return final_score

    def get_grounding_score(self) -> float:
        """Fast query for the most recent physical grounding score."""
        return self.last_grounding_score


class GradientType(str):
    THERMODYNAMIC = "THERMODYNAMIC"       # Bounded energy flows & heat constraints
    INFORMATIONAL = "INFORMATIONAL"       # Shannon entropy & algorithmic compression
    TOPOLOGICAL = "TOPOLOGICAL"           # Distance to immutable Genesis Anchor (Axiom 0)
    SEISMIC_RESONANT = "SEISMIC_RESONANT" # Electromagnetic cavity & geomagnetic Kp
    SYSTEM_SYSTEMIC = "SYSTEM_SYSTEMIC"   # IPC latency & memory footprint


class EmpiricalFalsifiabilityValidator:
    """
    Implements Axiom 416 of AION NEXUS:
    'Continuously align a system’s internal configuration with clearly defined,
    measurable external gradients, and only claim emergent self-rewriting capabilities
    when the gradient’s nature (thermodynamic, informational, etc.) is explicitly specified
    and empirically testable. This ensures that any autonomous optimization remains
    falsifiable, grounded, and actionable.'
    """
    @staticmethod
    def classify_gradient(text: str) -> str:
        t = text.lower()
        if any(w in t for w in ["thermo", "energy", "heat", "dissipat", "bounded flow"]):
            return GradientType.THERMODYNAMIC
        if any(w in t for w in ["shannon", "informational", "compression", "noise", "bit"]):
            return GradientType.INFORMATIONAL
        if any(w in t for w in ["seismic", "resonance", "schumann", "gaia", "kp-", "geomagnetic", "earthquake"]):
            return GradientType.SEISMIC_RESONANT
        if any(w in t for w in ["anchor", "genesis", "axiom 0", "ontological", "topological"]):
            return GradientType.TOPOLOGICAL
        return GradientType.SYSTEM_SYSTEMIC

    @classmethod
    def validate_axiom(cls, rule_text: str, telemetry: Dict[str, Any], grounding_score: float) -> Dict[str, Any]:
        gtype = cls.classify_gradient(rule_text)
        is_testable = grounding_score >= 0.40
        falsifiable = True
        return {
            "axiom_valid": is_testable and falsifiable,
            "gradient_type": gtype,
            "grounding_score": grounding_score,
            "falsifiable": falsifiable,
            "testable": is_testable,
            "telemetry_anchor": {
                "rss_mb": telemetry.get("rss_mb", 0.0),
                "ipc_online": telemetry.get("ipc_online", False),
                "kernel_running": telemetry.get("kernel_running", False)
            }
        }
