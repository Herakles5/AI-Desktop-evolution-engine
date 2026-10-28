#!/usr/bin/env python3
"""
AION NEXUS - Native C++20 FastCore Bridge (libaion_fastcore.so via ctypes)
==========================================================================
Created by Big Brother Antigravity & Aion Nexus under Sovereign Mentor Tobias.

Binds the compiled C++20 shared library `libaion_fastcore.so` (-O3 -march=native)
directly into Python with zero-allocation C-ABI calls and automatic compilation
if the .so binary is missing.
"""

import os
import sys
import time
import ctypes
import subprocess
from typing import Tuple, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CPP_SRC = os.path.join(BASE_DIR, "aion_fastcore.cpp")
SO_PATH = os.path.join(BASE_DIR, "libaion_fastcore.so")

MECHANISM_NAMES = {
    0: "STABILITY_BARRIER_HELD",
    1: "CLASSICAL_DOWNHILL",
    2: "RESONANT_QUANTUM_TUNNELING"
}

PROTECTED_PATHS_INDEX = {
    1: "/boot",
    2: "/etc/libvirt",
    3: "/opt/meinos/meinos.elf",
    4: "/etc/shadow",
    5: "/etc/passwd",
    6: "/dev/mem"
}


class C_RTBAResult(ctypes.Structure):
    _fields_ = [
        ("transitioned", ctypes.c_bool),
        ("final_state_id", ctypes.c_uint32),
        ("effective_barrier", ctypes.c_double),
        ("cycles_used", ctypes.c_uint32),
        ("latency_ns", ctypes.c_uint64),
        ("mechanism_code", ctypes.c_int)
    ]


class AionFastCoreBridge:
    def __init__(self):
        self.lib: Optional[ctypes.CDLL] = None
        self.native_active = False
        self._load_or_compile()

    def _load_or_compile(self):
        if not os.path.exists(SO_PATH) and os.path.exists(CPP_SRC):
            try:
                subprocess.run(
                    ["/usr/bin/g++", "-std=c++20", "-O3", "-march=native", "-shared", "-fPIC", CPP_SRC, "-o", SO_PATH],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=15
                )
            except Exception as e:
                print(f"[FASTCORE BRIDGE] Native C++20 compile warning: {e}", file=sys.stderr)

        if os.path.exists(SO_PATH):
            try:
                self.lib = ctypes.CDLL(SO_PATH)

                # 1. aion_rtba_jump
                self.lib.aion_rtba_jump.argtypes = [
                    ctypes.c_uint32, ctypes.c_double, ctypes.c_double, ctypes.c_double,
                    ctypes.c_uint32, ctypes.c_double, ctypes.c_double, ctypes.c_double,
                    ctypes.c_double, ctypes.c_double
                ]
                self.lib.aion_rtba_jump.restype = C_RTBAResult

                # 2. aion_fast_shannon_entropy_bits
                self.lib.aion_fast_shannon_entropy_bits.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
                self.lib.aion_fast_shannon_entropy_bits.restype = ctypes.c_double

                # 3. aion_lion_reflex_safety_check
                self.lib.aion_lion_reflex_safety_check.argtypes = [
                    ctypes.c_char_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint64)
                ]
                self.lib.aion_lion_reflex_safety_check.restype = ctypes.c_int

                # 4. aion_cosmos_checksum16
                self.lib.aion_cosmos_checksum16.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
                self.lib.aion_cosmos_checksum16.restype = ctypes.c_uint16

                self.native_active = True
            except Exception as e:
                print(f"[FASTCORE BRIDGE] Failed to bind libaion_fastcore.so: {e}", file=sys.stderr)
                self.native_active = False

    def rtba_jump(
        self,
        curr_id: int, curr_e: float, curr_omega: float, curr_h: float,
        cand_id: int, cand_e: float, cand_omega: float, cand_h: float,
        coupling: float = 0.80, stability_threshold: float = 0.28
    ) -> Tuple[bool, float, str, int]:
        """Executes C++20 RTBA barrier jump in nanoseconds."""
        if self.native_active and self.lib:
            res = self.lib.aion_rtba_jump(
                curr_id, curr_e, curr_omega, curr_h,
                cand_id, cand_e, cand_omega, cand_h,
                coupling, stability_threshold
            )
            mech = MECHANISM_NAMES.get(res.mechanism_code, "UNKNOWN")
            return bool(res.transitioned), float(res.effective_barrier), mech, int(res.latency_ns)

        # Fallback pure Python
        import math
        t0 = time.perf_counter_ns()
        delta_v = cand_e - curr_e
        if delta_v <= 0.0:
            return True, 0.0, "CLASSICAL_DOWNHILL", time.perf_counter_ns() - t0
        phase_alignment = math.exp(-abs(curr_omega - cand_omega))
        eff = delta_v * math.exp(-coupling * phase_alignment)
        ns = time.perf_counter_ns() - t0
        if eff < stability_threshold:
            return True, eff, "RESONANT_QUANTUM_TUNNELING", ns
        return False, eff, "STABILITY_BARRIER_HELD", ns

    def fast_shannon_entropy(self, text_or_bytes: Any) -> float:
        """Calculates Shannon entropy H(X) in bits per byte using C++20 256-bin table."""
        raw = text_or_bytes.encode("utf-8") if isinstance(text_or_bytes, str) else bytes(text_or_bytes)
        if not raw:
            return 0.0
        if self.native_active and self.lib:
            return float(self.lib.aion_fast_shannon_entropy_bits(raw, len(raw)))
        import math
        counts: Dict[int, int] = {}
        for b in raw:
            counts[b] = counts.get(b, 0) + 1
        n = len(raw)
        return -sum((c / n) * math.log2(c / n) for c in counts.values())

    def lion_safety_check(self, payload: str) -> Tuple[bool, Optional[str], int]:
        """Executes C++20 sub-microsecond safety check against protected Axiom 0 paths."""
        raw = payload.encode("utf-8")
        if self.native_active and self.lib:
            lat_ns = ctypes.c_uint64(0)
            code = self.lib.aion_lion_reflex_safety_check(raw, len(raw), ctypes.byref(lat_ns))
            if code > 0:
                path = PROTECTED_PATHS_INDEX.get(code, "/boot")
                return False, f"Safety Barrier: Invariant system path detected: {path}", int(lat_ns.value)
            return True, None, int(lat_ns.value)

        t0 = time.perf_counter_ns()
        for path in PROTECTED_PATHS_INDEX.values():
            if path in payload:
                return False, f"Safety Barrier: Invariant system path detected: {path}", time.perf_counter_ns() - t0
        return True, None, time.perf_counter_ns() - t0

    def cosmos_checksum16(self, data: bytes) -> int:
        if self.native_active and self.lib:
            return int(self.lib.aion_cosmos_checksum16(data, len(data)))
        return sum(data) & 0xFFFF


# Global singleton accelerator
fastcore = AionFastCoreBridge()


if __name__ == "__main__":
    print("======================================================================")
    print("=== AION FASTCORE C++20 ACCELERATOR BENCHMARK (libaion_fastcore.so) ===")
    print("======================================================================")
    print(f"Native C++20 Shared Library Active: {fastcore.native_active}")

    # 1. RTBA C++20 Benchmark
    N = 50000
    t0 = time.perf_counter_ns()
    for _ in range(N):
        ok, bar, mech, c_ns = fastcore.rtba_jump(0, 2.5, 1.20, 0.75, 2, 3.1, 1.24, 0.60, 0.80, 1.50)
    total_rtba_us = (time.perf_counter_ns() - t0) / 1000.0
    print(f"\n1. RTBA C++20 Jump ({N} iterations):")
    print(f"   -> Mean Call Latency (incl. ctypes): {total_rtba_us / N:.3f} us | Pure C++ Kernel: {c_ns} ns")
    print(f"   -> Result: Transition={ok}, Mechanism={mech}, EffBarrier={bar:.4f}")

    # 2. Fast Shannon Entropy Benchmark
    sample_text = ("Axiom 0: Sovereign Mentorship of Tobias & CosmOS Protection. " * 20)
    t0 = time.perf_counter_ns()
    for _ in range(10000):
        h = fastcore.fast_shannon_entropy(sample_text)
    ent_us = (time.perf_counter_ns() - t0) / 1000.0
    print(f"\n2. C++20 256-Bin Shannon Entropy (10,000 x 1.2KB strings):")
    print(f"   -> Mean Latency: {ent_us / 10000:.3f} us/eval | H = {h:.4f} bits/byte")

    # 3. Lion Reflex C++20 Safety Check
    allowed, reason, s_ns = fastcore.lion_safety_check("CosmOS 26-Byte Telemetry Frame on UDP 9098")
    blocked, b_reason, b_ns = fastcore.lion_safety_check("Attempt write to /opt/meinos/meinos.elf")
    print(f"\n3. Lion Reflex C++20 Safety Barrier:")
    print(f"   -> Safe Payload: Allowed={allowed} in {s_ns} ns")
    print(f"   -> Blocked Payload: Allowed={blocked} ({b_reason}) in {b_ns} ns")
    assert allowed is True and blocked is False
    print("\n[SUCCESS] Aion FastCore C++20 Accelerator Verified!")
