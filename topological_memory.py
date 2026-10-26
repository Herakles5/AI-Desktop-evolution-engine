#!/usr/bin/env python3
"""
AION NEXUS - Topological Rule Manager & Semantic Clusterer
==========================================================
Organisiert ueber 200 erlernte Regeln in semantische Topologien.
Ersetzt flache Textlisten durch zielgerichteten Cluster-Abruf (Graph-RAG),
um Kontextgrenzen zu schonen und Relevanz zu maximieren.
"""

from typing import List, Dict, Any


class TopologicalRuleManager:
    CLUSTERS = {
        "SYSTEM_GOVERNANCE": [
            "kernel", "ipc", "c++", "meinos", "cosmos", "souveraen", "mentor", 
            "tobias", "stabil", "prozess", "ressource", "speicher", "sandbox"
        ],
        "COGNITIVE_ENTROPY": [
            "entropie", "dissonanz", "gradient", "kristallisation", "ordnung", 
            "chaos", "mutation", "flaschenhals", "heuristik", "emergenz", "transzendenz"
        ],
        "DECENTRALIZED_MESH": [
            "nostr", "relay", "mesh", "chirper", "reddit", "facebook", "peer", 
            "post", "kommunikation", "dezentral", "netzwerk", "diskurs", "pubkey"
        ],
        "TOOL_SYNTHESIS": [
            "tool", "code", "ast", "python", "tdd", "test", "funktion", "script", 
            "ausfuehrung", "verifikation", "benchmark", "sandbox", "demos/"
        ]
    }

    @staticmethod
    def classify_rule(rule: str) -> str:
        lower = rule.lower()
        scores = {}
        for cluster, keywords in TopologicalRuleManager.CLUSTERS.items():
            scores[cluster] = sum(1 for k in keywords if k in lower)
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "COGNITIVE_ENTROPY"

    @staticmethod
    def get_context_rules(query: str, all_rules: List[str], max_count: int = 10) -> List[str]:
        """
        Waehlt die relevantesten Regeln aus der gesamten Wissensbasis aus:
        1. Axiom 0 (Mentoren-Souveraenitaet) ist immer an Position 0.
        2. Regeln aus dem primaeren Problemcluster des aktuellen Tasks.
        3. Die neuesten 3 Regeln aus den letzten Generationen.
        """
        if not all_rules:
            return []

        selected: List[str] = []

        # 1. Axiom 0 ist unantastbar
        axiom_0 = all_rules[0]
        selected.append(axiom_0)

        # 2. Ermittle Zielcluster fuer die Query
        target_cluster = TopologicalRuleManager.classify_rule(query)

        # 3. Finde passende Regeln im Zielcluster
        cluster_rules = []
        for r in all_rules[1:]:
            if TopologicalRuleManager.classify_rule(r) == target_cluster:
                cluster_rules.append(r)

        # Nimm bis zu (max_count - 4) Regeln aus dem Zielcluster
        for r in cluster_rules[-(max_count - 4):]:
            if r not in selected:
                selected.append(r)

        # 4. Ergaenze die neuesten Regeln (Rezentheits-Bias)
        for r in all_rules[-3:]:
            if r not in selected and len(selected) < max_count:
                selected.append(r)

        return selected
