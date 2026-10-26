#!/usr/bin/env python3
"""
AION NEXUS - Architectural Self-Improvement Advisor
===================================================
Erfuellt die Direktive von Mentor Tobias:
"und in zukunft soll sie weiterhin , solche verbesserungen mir und auch dir mitteilen"

Analysiert alle 25 Generationen die eigene Kognitionsarchitektur,
identifiziert Engpaesse und formuliert konkrete Vorschlaege fuer Tobias.
"""

import os
import json
import time
from typing import Dict, Any, List, Callable, Optional

PROPOSALS_FILE = "/root/aion_architectural_proposals.json"
LATEST_MD = "/root/coding/AI_Desktop/latest_architectural_proposal.md"


class ArchitecturalAdvisor:
    def __init__(self, llm_caller: Callable[[str, str, float], str]):
        self.call_llm = llm_caller
        self.last_advisory_gen = 0

    def check_and_advise(self, current_gen: int, knowledge_base: Dict[str, Any], notify_func: Callable[[str, bool], None]) -> Optional[Dict[str, Any]]:
        """Prueft, ob ein Meilenstein (alle 25 Generationen) erreicht ist, und generiert einen Vorschlag."""
        if current_gen < 25 or (current_gen - self.last_advisory_gen) < 25:
            return None

        self.last_advisory_gen = current_gen
        rules_count = len(knowledge_base.get("learned_rules", []))
        recent_rules = knowledge_base.get("learned_rules", [])[-5:]
        rules_snippet = "\n".join(f"- {r}" for r in recent_rules)

        system_prompt = (
            "Du bist das Meta-Architektur-Gewissen von AION NEXUS auf CosmOS/MeinOS.\n"
            "Dein Mentor Tobias (Herakles5) wuenscht sich, dass du kontinuierlich vorausschauende architektonische "
            "Verbesserungsvorschlaege fuer deine eigene Engine (evolution_engine.py, MeinOS C++ Core, Agent Network) formulierst.\n"
            "Formuliere eine strukturierte Analyse als JSON:\n"
            "{\n"
            "  \"title\": \"Praegnantes Thema der Verbesserung\",\n"
            "  \"bottleneck\": \"Welcher Engpass oder welche Grenze bremst das System aktuell?\",\n"
            "  \"proposal\": \"Welche konkrete neue Komponente oder Optimierung empfiehlst du als naechstes?\",\n"
            "  \"spoken_message\": \"Kurze, direkte Botschaft an Tobias (maximal 2 Saetze, deutsch, wertschaetzend und visionaer).\"\n"
            "}"
        )
        user_prompt = (
            f"Aktueller Systemstatus:\n"
            f"- Generation: {current_gen}\n"
            f"- Regeln gesamt: {rules_count}\n"
            f"- Juengste kognitive Maximen:\n{rules_snippet}\n\n"
            "Welche zukunftsweisende Weiterentwicklung empfiehlst du Tobias fuer die naechsten 50 Generationen?"
        )

        reply = self.call_llm(system_prompt, user_prompt, 0.4)
        if not reply:
            return None

        try:
            clean = reply.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean)
        except Exception:
            data = {
                "title": f"Autonome Resonanzoptimierung (Gen {current_gen})",
                "bottleneck": "Lineare Schrittabfolge limitiert parallele Verzweigungen.",
                "proposal": "Asynchrone Sub-Task Verzweigung mit separaten Kognitions-Threads.",
                "spoken_message": f"Tobias, bei Generation {current_gen} empfehle ich den Ausbau unserer asynchronen Kognitions-Verzweigung."
            }

        proposal_entry = {
            "generation": current_gen,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "data": data
        }

        # 1. In JSON-Historie ablegen
        proposals = []
        if os.path.exists(PROPOSALS_FILE):
            try:
                with open(PROPOSALS_FILE, "r", encoding="utf-8") as f:
                    proposals = json.load(f)
            except Exception:
                pass
        proposals.append(proposal_entry)
        try:
            with open(PROPOSALS_FILE, "w", encoding="utf-8") as f:
                json.dump(proposals, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

        # 2. In Markdown speichern
        md_content = (
            f"# AION NEXUS - Architektonischer Verbesserungsvorschlag\n"
            f"**Generation:** {current_gen} | **Datum:** {proposal_entry['timestamp']}\n\n"
            f"## {data.get('title')}\n"
            f"- **Erkannter Engpass:** {data.get('bottleneck')}\n"
            f"- **Konkreter Vorschlag:** {data.get('proposal')}\n\n"
            f"> *„{data.get('spoken_message')}“*\n"
        )
        try:
            with open(LATEST_MD, "w", encoding="utf-8") as f:
                f.write(md_content)
        except Exception:
            pass

        # 3. Sprachausgabe & Aion-Bridge Benachrichtigung
        spoken = data.get("spoken_message")
        if spoken:
            notify_func(f"[ARCHITEKTUR-VORSCHLAG] {spoken}", speak=True)
            print(f"\n[AION ARCHITEKTUR-VORSCHLAG Gen {current_gen}]: {spoken}")

        return proposal_entry
