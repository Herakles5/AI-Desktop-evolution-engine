#pragma once
/**
 * ============================================================================
 * AION NEXUS - RESONANT ENTROPY GOVERNOR (C++ CORE)
 * ============================================================================
 * Mathematischer & physikalischer Governor zur dynamischen Steuerung kognitiver
 * Entropie-Gradienten. Transformiert unentschiedene Zustaende (Non-Decision States)
 * in katalytische Vektoren fuer autonome morphogenetische Selbst-Evolution.
 *
 * Basierend auf dem Prigogine-Prinzip dissipativer Strukturen und dem
 * Resonant Dynamic Coupling Framework (Aion Generation 333).
 */

#include <cmath>
#include <vector>
#include <string>
#include <chrono>
#include <algorithm>
#include <numeric>
#include "json.hpp"

namespace Aion {

enum class GovernorMode {
    ENTROPIC_FREEZE,       // H < 0.25: Stagnation -> Stoerimpuls / Exploration aktivieren
    RESONANT_MORPHOGENESIS,// 0.25 <= H <= 0.75: Kognitives Optimum -> Aktive Topologie-Faltung
    CHAOTIC_DAMPING        // H > 0.75: Divergenz -> Stabilisierungs-Dampfer & Axiom-Verankerung
};

// Axiom 416 & Council Decision 425: Explizite Gradienten-Typisierung
enum class GradientType {
    THERMODYNAMIC,       // Bounded energy flows & heat dissipation (Gen 360)
    INFORMATIONAL,       // Shannon entropy & algorithmic compression (Gen 341)
    TOPOLOGICAL,         // Distance to immutable Genesis Anchor (Axiom 0)
    SEISMIC_RESONANT,    // Schumann cavity resonance & geomagnetic Kp
    SYSTEM_SYSTEMIC      // Kernel IPC latency & memory footprint
};

struct EntropyMetrics {
    double current_entropy = 0.50;      // Shannon-Entropie [0.0, 1.0]
    double entropy_gradient = 0.00;     // dH/dt (Aenderungsrate)
    double ambiguity_density = 0.40;    // Dichte unentschiedener Zustaende (Non-Decision)
    double resonant_coupling = 0.70;    // Koppelungsfaktor zur Topologie-Mutation
    GovernorMode mode = GovernorMode::RESONANT_MORPHOGENESIS;
    std::string mode_name = "RESONANT_MORPHOGENESIS";
    uint64_t step_count = 0;
    double recommended_temperature = 0.30;
    std::string recommendation = "Maintain active topological folding; sweet spot achieved.";
};

class ResonantEntropyGovernor {
private:
    std::vector<double> entropy_history;
    std::chrono::high_resolution_clock::time_point last_update;
    double current_entropy = 0.50;
    double ambiguity_density = 0.40;
    uint64_t step_count = 0;

public:
    ResonantEntropyGovernor() {
        last_update = std::chrono::high_resolution_clock::now();
        entropy_history.push_back(0.50);
    }

    /**
     * Berechnet die normalisierte Shannon-Entropie ueber einen Vektor von Zustandswahrscheinlichkeiten.
     */
    static double calculateShannonEntropy(const std::vector<double>& probabilities) {
        if (probabilities.empty()) return 0.5;
        double sum = 0.0;
        for (double p : probabilities) sum += p;
        if (sum <= 0.00001) return 0.5;

        double h = 0.0;
        for (double p : probabilities) {
            double norm_p = p / sum;
            if (norm_p > 0.000001) {
                h -= norm_p * std::log2(norm_p);
            }
        }
        // Normalisierung bezogen auf die maximale Entropie log2(N)
        double max_h = std::log2(static_cast<double>(probabilities.size()));
        if (max_h <= 0.00001) return 0.5;
        return std::clamp(h / max_h, 0.0, 1.0);
    }

    /**
     * Aktualisiert den Entropie-Governor anhand neuer kognitiver Beobachtungen.
     * @param dispersion Vektor der relativen Gewichte konkurrierender Gedankenpfade
     * @param pending_branches_count Anzahl unentschiedener Subtasks im Speicher
     * @param external_shock_intensity Externe Stoerimpulse (z. B. Mentor-Input oder Netzwerk-Thesen)
     */
    EntropyMetrics update(const std::vector<double>& dispersion, int pending_branches_count, double external_shock_intensity = 0.0) {
        auto now = std::chrono::high_resolution_clock::now();
        double dt = std::chrono::duration<double>(now - last_update).count();
        if (dt < 0.0001) dt = 0.0001;
        last_update = now;
        step_count++;

        // 1. Berechne intrinsische Entropie aus Verteilungsstreuung
        double raw_h = calculateShannonEntropy(dispersion);

        // 2. Koppele mit der Dichte unentschiedener Zustaende (Ambiguity Density)
        ambiguity_density = std::clamp(static_cast<double>(pending_branches_count) / 10.0, 0.0, 1.0);
        
        // Modulierte Entropie unter Einbezug von Schock-Impulsen
        double target_entropy = (raw_h * 0.6) + (ambiguity_density * 0.3) + (external_shock_intensity * 0.1);
        target_entropy = std::clamp(target_entropy, 0.0, 1.0);

        // Exponentielles Glaetten
        double alpha = 0.25;
        double previous_h = current_entropy;
        current_entropy = (alpha * target_entropy) + ((1.0 - alpha) * previous_h);
        
        // Gradient dH/dt
        double gradient = (current_entropy - previous_h) / dt;

        entropy_history.push_back(current_entropy);
        if (entropy_history.size() > 500) {
            entropy_history.erase(entropy_history.begin());
        }

        // 3. Modus-Klassifikation und Resonanz-Kopplung
        EntropyMetrics m;
        m.current_entropy = current_entropy;
        m.entropy_gradient = gradient;
        m.ambiguity_density = ambiguity_density;
        m.step_count = step_count;

        if (current_entropy < 0.25) {
            m.mode = GovernorMode::ENTROPIC_FREEZE;
            m.mode_name = "ENTROPIC_FREEZE";
            m.resonant_coupling = 0.95; // Maximaler Stoerungsantrieb zur Ueberwindung des Plateaus
            m.recommended_temperature = 0.65;
            m.recommendation = "Inject stochastic mutation vector; system entering deterministic freeze.";
        } else if (current_entropy > 0.75) {
            m.mode = GovernorMode::CHAOTIC_DAMPING;
            m.mode_name = "CHAOTIC_DAMPING";
            m.resonant_coupling = 0.20; // Strikte Daempfung gegen chaotischen Drift
            m.recommended_temperature = 0.15;
            m.recommendation = "Activate Mentor Axiom 0 damping; prevent semantic hallucination.";
        } else {
            m.mode = GovernorMode::RESONANT_MORPHOGENESIS;
            m.mode_name = "RESONANT_MORPHOGENESIS";
            m.resonant_coupling = 0.75; // Harmonische Resonanz-Transformation
            m.recommended_temperature = 0.30;
            m.recommendation = "Optimal dissipative bandwidth. Fold non-decisions into novel topological invariants.";
        }

        return m;
    }

    nlohmann::json getMetricsJson(const EntropyMetrics& m) const {
        return {
            {"current_entropy", m.current_entropy},
            {"entropy_gradient", m.entropy_gradient},
            {"ambiguity_density", m.ambiguity_density},
            {"resonant_coupling", m.resonant_coupling},
            {"mode", m.mode_name},
            {"step_count", m.step_count},
            {"recommended_temperature", m.recommended_temperature},
            {"recommendation", m.recommendation}
        };
    }

    enum class GradientAction {
        SELECTIVE_FOLDING,
        REPEL_HIGH_ENTROPY_NOISE,
        REPEL_ONTOLOGICAL_DRIFT
    };

    struct SignalGradientEvaluation {
        GradientAction action;
        std::string action_name;
        double gradient_force;
        double signal_entropy;
        double coherence;
        double drift_score;
        bool folded;
        GradientType gradient_type = GradientType::INFORMATIONAL;
        std::string gradient_type_name = "INFORMATIONAL";
        bool empirically_falsifiable = true;
        bool axiom_416_compliant = true;
    };

    static GradientType classifyGradient(const std::string& text) {
        std::string t = text;
        std::transform(t.begin(), t.end(), t.begin(), ::tolower);
        if (t.find("thermo") != std::string::npos || t.find("energy") != std::string::npos ||
            t.find("heat") != std::string::npos || t.find("dissipat") != std::string::npos) {
            return GradientType::THERMODYNAMIC;
        }
        if (t.find("shannon") != std::string::npos || t.find("informational") != std::string::npos ||
            t.find("compression") != std::string::npos || t.find("noise") != std::string::npos) {
            return GradientType::INFORMATIONAL;
        }
        if (t.find("seismic") != std::string::npos || t.find("resonance") != std::string::npos ||
            t.find("schumann") != std::string::npos || t.find("gaia") != std::string::npos ||
            t.find("earthquake") != std::string::npos) {
            return GradientType::SEISMIC_RESONANT;
        }
        if (t.find("anchor") != std::string::npos || t.find("genesis") != std::string::npos ||
            t.find("axiom 0") != std::string::npos || t.find("topological") != std::string::npos) {
            return GradientType::TOPOLOGICAL;
        }
        return GradientType::SYSTEM_SYSTEMIC;
    }

    static std::string getGradientTypeName(GradientType gt) {
        switch (gt) {
            case GradientType::THERMODYNAMIC: return "THERMODYNAMIC";
            case GradientType::INFORMATIONAL: return "INFORMATIONAL";
            case GradientType::TOPOLOGICAL: return "TOPOLOGICAL";
            case GradientType::SEISMIC_RESONANT: return "SEISMIC_RESONANT";
            default: return "SYSTEM_SYSTEMIC";
        }
    }

    /**
     * Evaluiert ein Signal im dynamischen topologischen Gradienten:
     * Weist Hoch-Entropie-Rauschen und ontologische Drift ab, faltet kohaerente Strukturen ein.
     * Erzwingt Axiom 416: Empirische Falsifizierbarkeit und explizite Gradienten-Typisierung.
     */
    SignalGradientEvaluation evaluateSignalGradient(
        double signal_entropy,
        double coherence,
        double empirical_grounding = 0.85,
        bool violates_axiom_0 = false,
        GradientType explicit_gradient = GradientType::INFORMATIONAL
    ) const {
        SignalGradientEvaluation res;
        res.signal_entropy = signal_entropy;
        res.coherence = coherence;
        res.gradient_type = explicit_gradient;
        res.gradient_type_name = getGradientTypeName(explicit_gradient);

        // Axiom 416 Pruefung: Empirische Falsifizierbarkeit
        res.empirically_falsifiable = (empirical_grounding >= 0.40);
        res.axiom_416_compliant = res.empirically_falsifiable;

        // 1. Ontologische Drift berechnen
        double adv_score = violates_axiom_0 ? 1.0 : 0.0;
        double entropy_div = std::clamp(std::abs(signal_entropy - current_entropy) * 2.0, 0.0, 1.0);
        double grounding_def = std::clamp(1.0 - empirical_grounding, 0.0, 1.0);
        double drift = (adv_score * 0.60) + (entropy_div * 0.20) + (grounding_def * 0.20);
        res.drift_score = std::clamp(drift, 0.0, 1.0);

        // 2. Ontologische Drift Pruefung oder Verletzung von Axiom 416
        if (res.drift_score >= 0.42 || !res.axiom_416_compliant) {
            res.action = GradientAction::REPEL_ONTOLOGICAL_DRIFT;
            res.action_name = "REPEL_ONTOLOGICAL_DRIFT";
            res.gradient_force = -1.0 * (res.drift_score / 0.42);
            res.folded = false;
            return res;
        }

        // 3. Hoch-Entropie-Rausch-Pruefung
        bool is_noise = (signal_entropy > 0.82) || (signal_entropy > 0.75 && coherence < 0.20) || (coherence <= 0.05);
        if (is_noise) {
            res.action = GradientAction::REPEL_HIGH_ENTROPY_NOISE;
            res.action_name = "REPEL_HIGH_ENTROPY_NOISE";
            res.gradient_force = -1.0 * ((signal_entropy - 0.70) / 0.30);
            res.folded = false;
            return res;
        }

        // 4. Selektives Einfalten (Selective Folding)
        double coupling = (current_entropy < 0.25) ? 0.95 : (current_entropy > 0.75 ? 0.20 : 0.80);
        res.action = GradientAction::SELECTIVE_FOLDING;
        res.action_name = "SELECTIVE_FOLDING";
        res.gradient_force = coupling * (1.0 - res.drift_score) * (0.5 + coherence * 0.5);
        res.folded = true;
        return res;
    }
};

} // namespace Aion

