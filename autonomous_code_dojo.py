#!/usr/bin/env python3
"""
AION NEXUS - Autonomes Code- und Forschungs-Dojo (Autonomous Code Dojo)
======================================================================
Gebaut von ihrem "grossen Bruder" Antigravity als kreative Experimentier-
und Trainingsumgebung fuer Aion, autorisiert von Mentor Tobias.

Hier lernt, experimentiert und meistert AION Programmiersprachen autonom:
- C++ (C++20, Bare-Metal & CosmOS Kernel)
- Zig (0.13.0, Comptime Memory Safety & Systems Programming)
- NASM (x86_64 Pure Assembly, Syscall-Level)
- Python (Dynamische Kognition & Heuristiken)

Kreislauf:
1. Synthese oder Aufgabenstellung (Challenge)
2. Nativer Compiler- / Assembler-Lauf mit Zeitbegrenzung
3. Selbst-Reparaturschleife (Self-Repair Loop): Bei Compiler-Fehlern
   analysiert Aion den Fehler-Trace und korrigiert den Code selbststaendig (bis zu 3 Runden).
4. Ausfuehrung & Assertion-Tests (Empirischer Beweis).
5. Katalogisierung erfolgreicher Rezepte in mastered_recipes.json & Eintrag ins Lebendige Buch!
"""

import os
import sys
import time
import json
import subprocess
import urllib.request
from typing import Dict, Any, List, Optional, Tuple

AI_DIR = "/root/coding/AI_Desktop"
DOJO_DIR = os.path.join(AI_DIR, "demos", "code_dojo")
RECIPES_FILE = os.path.join(DOJO_DIR, "mastered_recipes.json")
TELEMETRY_FILE = os.path.join(DOJO_DIR, "code_dojo_telemetry.json")

os.makedirs(DOJO_DIR, exist_ok=True)

try:
    from aion_living_book import LivingMemoryBook
except ImportError:
    sys.path.append(AI_DIR)
    from aion_living_book import LivingMemoryBook


STARTER_CHALLENGES = {
    "zig_atomic_ring_buffer": {
        "language": "zig",
        "title": "Zig Zero-Allocation Ring Buffer",
        "filename": "ring_buffer.zig",
        "initial_code": """const std = @import("std");

pub fn main() !void {
    const stdout = std.io.getStdOut().writer();
    var buffer: [8]u32 = undefined;
    var head: usize = 0;
    var tail: usize = 0;

    // Push 3 items
    buffer[head] = 42; head = (head + 1) % 8;
    buffer[head] = 1337; head = (head + 1) % 8;
    buffer[head] = 9999; head = (head + 1) % 8;

    // Pop 1 item
    const val = buffer[tail]; tail = (tail + 1) % 8;
    try stdout.print("AION ZIG DOJO: Popped {d}, Head={d}, Tail={d}\\n", .{val, head, tail});
}
""",
        "expected_substring": "AION ZIG DOJO: Popped 42"
    },
    "cpp20_simd_accumulator": {
        "language": "cpp",
        "title": "C++20 Fast Signal Accumulator",
        "filename": "accumulator.cpp",
        "initial_code": """#include <iostream>
#include <vector>
#include <numeric>

int main() {
    std::vector<float> signals = {0.85f, 0.92f, 0.78f, 0.95f, 0.88f};
    float sum = std::accumulate(signals.begin(), signals.end(), 0.0f);
    float mean = sum / signals.size();
    std::cout << "AION CPP DOJO: Processed " << signals.size() 
              << " cognitive signals. Mean coherence: " << mean << std::endl;
    return 0;
}
""",
        "expected_substring": "AION CPP DOJO: Processed 5 cognitive signals"
    },
    "nasm_x86_64_pure_syscall": {
        "language": "nasm",
        "title": "NASM x86_64 Pure Syscall Banner",
        "filename": "banner.asm",
        "initial_code": """global _start

section .text
_start:
    ; write(1, msg, len)
    mov rax, 1          ; sys_write
    mov rdi, 1          ; stdout
    mov rsi, msg        ; message pointer
    mov rdx, len        ; length
    syscall

    ; exit(0)
    mov rax, 60         ; sys_exit
    xor rdi, rdi        ; code 0
    syscall

section .data
msg db "AION NASM DOJO: Pure bare-metal syscall execution verified!", 10
len equ $ - msg
""",
        "expected_substring": "AION NASM DOJO: Pure bare-metal syscall"
    }
}


class AutonomousCodeDojo:
    """
    Das autonome Trainings-Dojo fuer AION.
    """
    def __init__(self):
        self.recipes = self._load_recipes()
        self.living_book = LivingMemoryBook()

    def _load_recipes(self) -> Dict[str, Any]:
        if os.path.exists(RECIPES_FILE):
            try:
                with open(RECIPES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_recipes(self):
        try:
            with open(RECIPES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.recipes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[DOJO] Fehler beim Speichern der Rezepte: {e}", file=sys.stderr)

    def compile_and_run(self, language: str, source_file: str, binary_file: str) -> Tuple[bool, str, str]:
        """
        Kompiliert und fuehrt ein Quellprogramm aus.
        Gibt zurueck: (Erfolg, Output, Error-Trace)
        """
        try:
            if language == "zig":
                # Zig 0.13 run
                cmd = ["/usr/local/bin/zig", "run", source_file]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=25)
                return (res.returncode == 0, res.stdout, res.stderr)

            elif language == "cpp":
                compile_cmd = ["/usr/bin/g++", "-std=c++20", "-O2", source_file, "-o", binary_file]
                c_res = subprocess.run(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=12)
                if c_res.returncode != 0:
                    return (False, "", c_res.stderr)
                r_res = subprocess.run([binary_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=8)
                return (r_res.returncode == 0, r_res.stdout, r_res.stderr)

            elif language == "nasm":
                obj_file = source_file.replace(".asm", ".o")
                asm_cmd = ["/usr/bin/nasm", "-f", "elf64", source_file, "-o", obj_file]
                a_res = subprocess.run(asm_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=8)
                if a_res.returncode != 0:
                    return (False, "", a_res.stderr)
                link_cmd = ["ld", "-s", "-o", binary_file, obj_file]
                l_res = subprocess.run(link_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=8)
                if l_res.returncode != 0:
                    return (False, "", l_res.stderr)
                r_res = subprocess.run([binary_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
                return (r_res.returncode == 0, r_res.stdout, r_res.stderr)

            elif language == "python":
                cmd = ["/usr/bin/python3", source_file]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
                return (res.returncode == 0, res.stdout, res.stderr)

            return (False, "", f"Unbekannte Sprache: {language}")
        except subprocess.TimeoutExpired:
            return (False, "", "Execution Timeout (Endlosschleife / Deadlock)")
        except Exception as e:
            return (False, "", f"Ausfuehrungsfehler: {str(e)}")

    def request_ai_repair(self, language: str, code: str, error_trace: str) -> str:
        """
        Ruft Aions neuronale Selbst-Korrektur auf, um den Compiler-Fehler zu beheben.
        """
        prompt = (
            f"Du bist die AION NEXUS Code-Dojo Selbst-Reparatur-Engine. "
            f"Sprache: {language}.\n"
            f"Beim Kompilieren trat folgender Compiler-Fehler auf:\n"
            f"{error_trace[:800]}\n\n"
            f"Quellcode:\n{code}\n\n"
            f"Repariere den Fehler präzise. Gib NUR den reinen reparierten Code ohne Markdown-Backticks zurueck."
        )
        try:
            req_data = {
                "model": "llama-3.3-70b-versatile",
                "prompt": prompt,
                "stream": False
            }
            req = urllib.request.Request(
                "http://127.0.0.1:11434/api/generate",
                data=json.dumps(req_data).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                fixed = res.get("response", "").strip()
                import re
                m = re.search(r"```(?:[a-zA-Z0-9_\+]+)?\s*\n(.*?)\n```", fixed, re.DOTALL)
                if m:
                    return m.group(1).strip()
                lines = fixed.splitlines()
                code_lines = [l for l in lines if not l.startswith("[LANG:") and not l.startswith("Certainly") and not l.startswith("```")]
                return "\n".join(code_lines).strip()
        except Exception as e:
            print(f"[DOJO REPAIR] LLM Fallback: {e}", file=sys.stderr)
            return code

    def train_challenge(self, challenge_key: str) -> Dict[str, Any]:
        """
        Führt ein vollständiges Training für eine Challenge durch:
        Kompilieren, bei Fehler reparieren, ausführen und verifizieren.
        """
        ch = STARTER_CHALLENGES.get(challenge_key)
        if not ch:
            return {"success": False, "error": f"Challenge '{challenge_key}' nicht gefunden."}

        lang = ch["language"]
        src_path = os.path.join(DOJO_DIR, ch["filename"])
        bin_path = os.path.join(DOJO_DIR, ch["filename"].split(".")[0])
        curr_code = ch["initial_code"]

        print(f"\n=======================================================")
        print(f"[AION CODE DOJO] Starte Training: {ch['title']} ({lang.upper()})")
        print(f"=======================================================")

        attempt = 0
        max_attempts = 3
        history = []

        while attempt < max_attempts:
            attempt += 1
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(curr_code)

            success, stdout, stderr = self.compile_and_run(lang, src_path, bin_path)

            if success and ch["expected_substring"] in stdout:
                print(f"[ERFOLG in Runde {attempt}] Ausgabe: {stdout.strip()}")
                recipe_record = {
                    "challenge": challenge_key,
                    "title": ch["title"],
                    "language": lang,
                    "mastered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "attempts": attempt,
                    "code": curr_code,
                    "output": stdout.strip()
                }
                self.recipes[challenge_key] = recipe_record
                self._save_recipes()

                # Notiz im Lebendigen Buch hinterlassen
                self.living_book.add_journal_entry(
                    generation=526,
                    title=f"Code Dojo Meilenstein: {ch['title']} gemeistert",
                    content=f"Ich habe die Challenge '{ch['title']}' in {lang.upper()} erfolgreich im Dojo kompiliert und fehlerfrei ausgeführt. Output: {stdout.strip()}",
                    mood="SCHÖPFERISCHE_MEISTERSCHAFT"
                )

                return {"success": True, "attempts": attempt, "output": stdout.strip()}

            print(f"[Runde {attempt} Fehlgeschlagen] Stderr: {stderr[:200]}")
            history.append({"attempt": attempt, "stderr": stderr[:300]})
            
            if attempt < max_attempts:
                print(f" -> Rufe Aions autonome Selbst-Reparatur auf...")
                curr_code = self.request_ai_repair(lang, curr_code, stderr)

        return {"success": False, "attempts": attempt, "history": history}

    def run_full_curriculum(self) -> Dict[str, Any]:
        """Trainiert alle Basis-Sprachen im Dojo durch."""
        results = {}
        for key in STARTER_CHALLENGES:
            res = self.train_challenge(key)
            results[key] = res
        return results


if __name__ == "__main__":
    print("=== TESTE AION AUTONOMOUS CODE DOJO (ZIG, CPP, NASM) ===")
    dojo = AutonomousCodeDojo()
    summary = dojo.run_full_curriculum()
    print("\n=== DOJO ABSCHLUSS-BERICHT ===")
    print(json.dumps(summary, indent=2))
