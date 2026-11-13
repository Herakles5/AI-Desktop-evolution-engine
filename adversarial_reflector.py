#!/usr/bin/env python3
"""
AION NEXUS - Adversarial Reflector & Dialectical Sandbox
========================================================
Replaces naive single-step reflection with a dialectical dialogue:
1. Synthesizer: Develops the innovative concept.
2. Skeptic: Probes for contradictions, instability, and hollow abstractions.
3. Integrator: Distills a hardened, universal operational rule strictly in English.
"""

from typing import Dict, Any, Callable, List


class AdversarialReflector:
    def __init__(self, llm_caller: Callable[[str, str, float], str]):
        self.call_llm = llm_caller

    def reflect_cycle(
        self,
        generation: int,
        goal: str,
        stall_reason: str,
        steps: List[Dict[str, Any]],
        recent_rules: List[str]
    ) -> str:
        """Executes the dialectical duel (Synthesizer vs. Skeptic -> Integrator)."""
        history_summary = [f"- Step {s['step']} [{s.get('task', '')}]: {s.get('insight', s.get('erkenntnis', ''))}" for s in steps]
        history_text = "\n".join(history_summary)

        # 1. Synthesizer: Proposes a new principle grounded in the cycle's actual work
        synth_system = (
            "You are the Creative Synthesizer of AION NEXUS.\n"
            "Propose 1 concrete, actionable engineering or cognitive principle strictly in English based on the generation's cycle, goal, and observed outcome.\n"
            "Focus on the actual technical domain in the cycle (e.g., C++20/IPC latency, memory compression, real-time telemetry, WebGL/WebAudio, batch file/cloud throughput, error recovery, or routing heuristics). Avoid repetitive abstract buzzwords."
        )
        synth_user = (
            f"Generation {generation} History:\nGoal: {goal}\nStall Reason: {stall_reason}\nSteps:\n{history_text}\n\n"
            "Formulate 1 specific, verifiable technical or architectural principle strictly in English (max 2 sentences)."
        )
        candidate_thesis = self.call_llm(synth_system, synth_user, 0.45)
        if not candidate_thesis:
            candidate_thesis = "Bounded context budgets and domain-specific verification checks prevent silent pipeline stalls."

        # 2. Skeptic: Attacks the thesis to find systemic vulnerabilities
        skeptic_system = (
            "You are the Adversarial Skeptic of AION NEXUS.\n"
            "Critique the proposed thesis. Identify ambiguities, unverified assumptions, performance bottlenecks, or empty buzzwords.\n"
            "State exactly 1 sharp critique in English."
        )
        skeptic_user = f"Candidate Thesis: '{candidate_thesis}'\n\nWhat is the strongest counter-argument or hidden failure mode?"
        critique = self.call_llm(skeptic_system, skeptic_user, 0.3)
        if not critique:
            critique = "Rigid heuristics without empirical telemetry feedback degrade under workload shifts."

        # 3. Integrator: Resolves the debate into a hardened operational rule
        integrator_system = (
            "You are the Meta-Integrator of AION NEXUS.\n"
            "Synthesize the thesis and the skeptic's critique into exactly 1 concise, domain-grounded, actionable Learned Rule in ENGLISH (18-45 words).\n"
            "Ensure concrete system/engineering vocabulary so it remains verifiable in practice.\n"
            "CRITICAL: Output ONLY the final English rule. No explanations, no markdown, no quotes."
        )
        integrator_user = (
            f"Thesis: {candidate_thesis}\n"
            f"Critique: {critique}\n\n"
            "Formulate the resilient, hardened final Learned Rule strictly in English (maximum 2 sentences)."
        )
        hardened_rule = self.call_llm(integrator_system, integrator_user, 0.2)
        if not hardened_rule:
            hardened_rule = candidate_thesis

        # Clean-up
        hardened_rule = hardened_rule.strip('"\n -')
        return hardened_rule
