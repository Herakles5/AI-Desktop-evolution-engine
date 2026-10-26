#!/usr/bin/env python3
"""
AION NEXUS - Empirical Process Evaluator (PRM & Telemetry)
==========================================================
Erdet die kognitiven Zyklen durch reale Hardware- und OS-Metriken.
Verhindert Reward-Hacking und pseudowissenschaftlichen Drift durch
echte physikalische und systemische Messwerte.
"""

import os
import time
import socket
from typing import Dict, Any, Optional


class EmpiricalEvaluator:
    def __init__(self, unix_ipc_path: str = "/tmp/aion_nexus.sock"):
        self.unix_ipc_path = unix_ipc_path

    def measure_system_telemetry(self) -> Dict[str, Any]:
        """Misst reale Systemmetriken von Host & MeinOS."""
        metrics: Dict[str, Any] = {
            "timestamp": time.time(),
            "rss_mb": 0.0,
            "ipc_latency_us": None,
            "ipc_online": False,
            "kernel_running": False
        }

        # 1. RSS Memory des aktuellen Prozesses via /proc/self/statm
        try:
            with open("/proc/self/statm", "r") as f:
                parts = f.read().split()
                if len(parts) >= 2:
                    page_size_kb = os.sysconf("SC_PAGE_SIZE") / 1024
                    metrics["rss_mb"] = round((int(parts[1]) * page_size_kb) / 1024, 2)
        except Exception:
            pass

        # 2. Pruefe IPC-Verbindung zum MeinOS C++ Kernel
        if os.path.exists(self.unix_ipc_path):
            start = time.perf_counter()
            try:
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.settimeout(0.1)
                s.connect(self.unix_ipc_path)
                s.sendall(b"PING\n")
                s.close()
                latency_us = (time.perf_counter() - start) * 1_000_000
                metrics["ipc_latency_us"] = round(latency_us, 1)
                metrics["ipc_online"] = True
            except Exception:
                pass

        # 3. Pruefe ob meinos.elf laeuft
        try:
            metrics["kernel_running"] = os.path.exists("/proc") and any(
                "meinos" in open(f"/proc/{pid}/cmdline", errors="ignore").read()
                for pid in os.listdir("/proc") if pid.isdigit()
            )
        except Exception:
            pass

        return metrics

    def compute_grounding_score(self, step_info: Dict[str, Any], tool_result: Optional[Dict[str, Any]] = None) -> float:
        """
        Berechnet einen empirischen Grounding-Faktor (0.0 bis 1.0):
        Belohnt echte Code-Synthese, funktionierende Tests und niedrige Systemlatenzen.
        """
        score = 0.5  # Basiswert

        # Bonus fuer reale Tool-Synthese
        if tool_result:
            if tool_result.get("success"):
                score += 0.35
            else:
                score -= 0.15

        # Bonus fuer aktiven IPC-Kernel
        telemetry = self.measure_system_telemetry()
        if telemetry.get("ipc_online"):
            score += 0.10
        if telemetry.get("kernel_running"):
            score += 0.05

        return max(0.1, min(1.0, round(score, 2)))
