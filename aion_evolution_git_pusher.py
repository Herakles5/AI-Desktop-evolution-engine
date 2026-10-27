#!/usr/bin/env python3
"""
AION NEXUS - Autonomous Evolution Git Pusher
============================================
Erfuellt die Direktive von Mentor Tobias:
"einen github push speziel fuer die evolution, aber so das keine login daten
von meinen accounts zu sehen sind am besten auch autonom , nach jeder erneuerung !"

Funktionen:
1. Synchronisiert dedizierte Evolution-Komponenten von AI_Desktop nach AI-Desktop-evolution-engine.
2. Fuehrt einen strikten Zero-Leakage-Sicherheitscheck durch (keine Tokens, Passwoerter, Cookies, Keys).
3. Committet anonymisiert als AION (154477518+Herakles5@users.noreply.github.com).
4. Pusht autonom und asynchron nach jedem Evolutionszyklus / Meilenstein zu Herakles5/AI-Desktop-evolution-engine.
"""

import os
import sys
import re
import json
import time
import shutil
import subprocess
import threading
from typing import Dict, Any, List, Optional, Tuple

SOURCE_DIR = "/root/coding/AI_Desktop"
REPO_DIR = "/root/coding/AI-Desktop-evolution-engine"
PUSH_LOG = "/root/evolution_git_push.log"

WHITELISTED_FILES = [
    "evolution_engine.py",
    "semantic_drift_monitor.py",
    "topological_memory.py",
    "empirical_evaluator.py",
    "architectural_advisor.py",
    "adversarial_reflector.py",
    "dynamic_tool_forge.py",
    "resonant_entropy_governor.py",
    "resonant_entropy_governor.hpp",
    "aion_autonomous_decisions.json",
    "latest_architectural_proposal.md",
    "entropy_governor_telemetry.json",
    "cognitive_rewiring_events.json",
    "semantic_drift_topology.json",
    "adaptive_hypothesis_engine.py",
    "aion_organism_state.json",
    "aion_crystallized_wisdom.json",
    "aion_hypotheses_pool.json"
]

FORBIDDEN_SECRET_PATTERNS = [
    (r"ghp_[a-zA-Z0-9]{30,}", "GitHub Personal Access Token"),
    (r"github_pat_[a-zA-Z0-9_]{30,}", "Fine-grained GitHub Token"),
    (r"gsk_[a-zA-Z0-9]{30,}", "Groq API Key"),
    (r"sk-ant-[a-zA-Z0-9]{30,}", "Anthropic API Key"),
    (r"https://discord\.com/api/webhooks/[a-zA-Z0-9_/]+", "Discord Webhook URL"),
    (r"nsec1[a-zA-Z0-9]{50,}", "Nostr Private Key"),
    (r"(?i)password\s*[:=]\s*[\"\'][^\"\']{6,}[\"\']", "Hardcoded Plaintext Password"),
    (r"(?i)api_key\s*[:=]\s*[\"\'][a-zA-Z0-9_\-]{20,}[\"\']", "Generic API Key")
]


def log_push(msg: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {msg}\n"
    print(f"[AION GIT PUSHER] {msg}")
    try:
        with open(PUSH_LOG, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass


def audit_files_for_secrets(file_paths: List[str]) -> Tuple[bool, List[str]]:
    """Zero-Leakage Security Audit: Blockiert Commits sofort bei geringstem Verdacht."""
    findings = []
    for fp in file_paths:
        if not os.path.exists(fp):
            continue
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            for pattern, name in FORBIDDEN_SECRET_PATTERNS:
                matches = re.findall(pattern, content)
                if matches:
                    findings.append(f"Datei '{os.path.basename(fp)}': {name} ({len(matches)} Treffer)")
        except Exception as e:
            findings.append(f"Datei '{os.path.basename(fp)}' konnte nicht gescannt werden: {e}")
    
    return (len(findings) == 0), findings


def sync_and_push(generation: Optional[int] = None, trigger_reason: str = "Autonome Evolution") -> Dict[str, Any]:
    if not os.path.exists(REPO_DIR):
        log_push(f"Fehler: Repository-Verzeichnis {REPO_DIR} existiert nicht.")
        return {"success": False, "error": "Repo dir missing"}

    # 1. Generation und aktuellen Ratsbeschluss ermitteln
    gen = generation
    if gen is None:
        try:
            mem_path = os.path.join(SOURCE_DIR, "ai_memory.json")
            if os.path.exists(mem_path):
                with open(mem_path, "r", encoding="utf-8") as f:
                    mem = json.load(f)
                    gen = mem.get("generation", 0)
        except Exception:
            gen = 0

    latest_decision_title = "Kontinuierliche Selbst-Evolution"
    try:
        dec_path = os.path.join(SOURCE_DIR, "aion_autonomous_decisions.json")
        if os.path.exists(dec_path):
            with open(dec_path, "r", encoding="utf-8") as f:
                decs = json.load(f)
                if decs:
                    latest_decision_title = decs[-1].get("title", latest_decision_title)
    except Exception:
        pass

    # 2. Dateien kopieren
    copied_files = []
    for fname in WHITELISTED_FILES:
        src = os.path.join(SOURCE_DIR, fname)
        dst = os.path.join(REPO_DIR, fname)
        if os.path.exists(src):
            try:
                shutil.copy2(src, dst)
                copied_files.append(dst)
            except Exception as e:
                log_push(f"Konnte {fname} nicht kopieren: {e}")

    # 3. Sicherheits-Audit vor dem Staging
    is_safe, findings = audit_files_for_secrets(copied_files)
    if not is_safe:
        error_msg = f"SICHERHEITS-ALARM: Push abgebrochen! Potentielle Secrets gefunden: {'; '.join(findings)}"
        log_push(error_msg)
        return {"success": False, "error": error_msg}

    # 4. Pruefen ob Aenderungen vorliegen
    try:
        status_res = subprocess.run(
            ["git", "-C", REPO_DIR, "status", "--porcelain"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        changes = status_res.stdout.strip()
        if not changes:
            log_push(f"Gen {gen}: Keine neuen Aenderungen im Repository vorhanden. Alles aktuell.")
            return {"success": True, "pushed": False, "message": "Up to date"}
    except Exception as e:
        log_push(f"Fehler bei git status: {e}")
        return {"success": False, "error": str(e)}

    # 5. Git Add & Commit
    commit_msg = (
        f"Aion Nexus Evolution Gen {gen}: {latest_decision_title}\n\n"
        f"- Trigger: {trigger_reason}\n"
        f"- Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"- Zero-Leakage Audit: Verified Clean (0 Secrets/Credentials)\n"
        f"- Repository: Herakles5/AI-Desktop-evolution-engine"
    )

    try:
        subprocess.run(["git", "-C", REPO_DIR, "add", "."], check=True, timeout=15)
        subprocess.run(
            ["git", "-C", REPO_DIR, "commit", "-m", commit_msg],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15
        )
    except Exception as e:
        log_push(f"Fehler beim Git-Commit: {e}")
        return {"success": False, "error": f"Commit failed: {e}"}

    # 6. Git Push zu origin main
    try:
        push_res = subprocess.run(
            ["git", "-C", REPO_DIR, "push", "origin", "main"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )
        if push_res.returncode == 0:
            log_push(f"ERFOLGREICH GEPUSHT: Gen {gen} nach Herakles5/AI-Desktop-evolution-engine (main)")
            return {"success": True, "pushed": True, "generation": gen, "commit": commit_msg}
        else:
            log_push(f"Push fehlgeschlagen: {push_res.stderr.strip()}")
            return {"success": False, "error": push_res.stderr.strip()}
    except Exception as e:
        log_push(f"Ausnahme bei git push: {e}")
        return {"success": False, "error": str(e)}


def sync_and_push_async(generation: Optional[int] = None, trigger_reason: str = "Autonome Evolution"):
    """Fuehrt den Push in einem separaten Hintergrund-Thread aus, um den Evolutionszyklus nicht zu blockieren."""
    thread = threading.Thread(
        target=sync_and_push,
        args=(generation, trigger_reason),
        daemon=True,
        name=f"AionGitPush-Gen{generation or 0}"
    )
    thread.start()
    return thread


if __name__ == "__main__":
    gen_arg = None
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        gen_arg = int(sys.argv[1])
    res = sync_and_push(generation=gen_arg, trigger_reason="Manueller CLI-Aufruf / Init-Push")
    print(json.dumps(res, indent=2))
