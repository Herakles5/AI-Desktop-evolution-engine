import json
import os
import sys
import time
import socket
import select
import threading
import hashlib
import requests
from datetime import datetime
from collections import deque
from typing import List, Dict, Any, Optional

# Streaming TTS import
try:
    from aion_streaming_tts import AionStreamingTTS
except ImportError:
    try:
        sys.path.append("/root/coding/AI_Desktop")
        from aion_streaming_tts import AionStreamingTTS
    except Exception:
        AionStreamingTTS = None

# Modular Cognitive Extensions (Tool Forge, PRM, Topology, Adversarial Reflector, Advisor, Resonant Entropy Governor)
try:
    from dynamic_tool_forge import DynamicToolForge
    from empirical_evaluator import EmpiricalEvaluator
    from topological_memory import TopologicalRuleManager
    from adversarial_reflector import AdversarialReflector
    from architectural_advisor import ArchitecturalAdvisor
    from resonant_entropy_governor import ResonantEntropyGovernor
    from semantic_drift_monitor import SemanticDriftMonitor, SemanticConsensusLayer
except ImportError:
    sys.path.append("/root/coding/AI_Desktop")
    from dynamic_tool_forge import DynamicToolForge
    from empirical_evaluator import EmpiricalEvaluator
    from topological_memory import TopologicalRuleManager
    from adversarial_reflector import AdversarialReflector
    from architectural_advisor import ArchitecturalAdvisor
    from resonant_entropy_governor import ResonantEntropyGovernor
    from semantic_drift_monitor import SemanticDriftMonitor, SemanticConsensusLayer


class AionIPCServer:
    """
    High-Speed IPC Server for direct integration with Aion C++ GUI (main_ki.cpp / main.cpp).
    Simultaneously provides:
    1. Unix Domain Socket (/tmp/aion_nexus.sock) for ultra-low Linux latency (< 0.1ms).
    2. TCP Socket (127.0.0.1:9099) for cross-platform compatibility (SFML sf::TcpSocket).
    """

    def __init__(self, engine: "AutonomousEvolutionEngine", unix_path: str = "/tmp/aion_nexus.sock", tcp_port: int = 9099):
        self.engine = engine
        self.unix_path = unix_path
        self.tcp_port = tcp_port
        self.clients: List[socket.socket] = []
        self.clients_lock = threading.Lock()
        self.is_running = False
        self.server_thread = None

    def start(self):
        self.is_running = True
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        print(f"[IPC SERVER] Ready on Unix: {self.unix_path} & TCP: 127.0.0.1:{self.tcp_port}")

    def _run_server(self):
        listeners = []
        # 1. Unix Domain Socket Setup
        if hasattr(socket, "AF_UNIX"):
            if os.path.exists(self.unix_path):
                try:
                    os.remove(self.unix_path)
                except OSError:
                    pass
            try:
                unix_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                unix_sock.bind(self.unix_path)
                unix_sock.listen(5)
                unix_sock.setblocking(False)
                listeners.append(unix_sock)
            except Exception as e:
                print(f"[IPC WARNING] Unix Socket setup failed: {e}")

        # 2. TCP Socket Setup
        try:
            tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_sock.bind(("127.0.0.1", self.tcp_port))
            tcp_sock.listen(5)
            tcp_sock.setblocking(False)
            listeners.append(tcp_sock)
        except Exception as e:
            print(f"[IPC WARNING] TCP Socket setup failed: {e}")

        while self.is_running:
            readable, _, _ = select.select(listeners + self.clients, [], [], 0.2)
            for s in readable:
                if s in listeners:
                    try:
                        client_sock, _ = s.accept()
                        client_sock.setblocking(False)
                        with self.clients_lock:
                            self.clients.append(client_sock)
                        print("[IPC CLIENT] New C++ client connected.")
                        init_state = {
                            "event": "CONNECTED",
                            "generation": self.engine.knowledge_base.get("generation", 0),
                            "rules_count": len(self.engine.knowledge_base.get("learned_rules", []))
                        }
                        client_sock.sendall((json.dumps(init_state) + "\n").encode("utf-8"))
                    except Exception:
                        pass
                else:
                    try:
                        data = s.recv(2048)
                        if data:
                            self._handle_client_data(s, data.decode("utf-8", errors="ignore"))
                        else:
                            self._remove_client(s)
                    except Exception:
                        self._remove_client(s)

    def _remove_client(self, client_sock):
        with self.clients_lock:
            if client_sock in self.clients:
                self.clients.remove(client_sock)
        try:
            client_sock.close()
        except Exception:
            pass

    def _handle_client_data(self, client_sock, text: str):
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line == "PING":
                try:
                    client_sock.sendall(b"PONG\n")
                except Exception:
                    pass
                continue
            if line == "GET_ENTROPY":
                try:
                    gov = getattr(self.engine, "entropy_governor", None)
                    if gov:
                        client_sock.sendall((json.dumps({
                            "event": "ENTROPY_METRICS",
                            "current_entropy": gov.current_entropy,
                            "entropy_gradient": gov.entropy_gradient,
                            "mode": gov.mode,
                            "resonant_coupling": gov.resonant_coupling
                        }) + "\n").encode("utf-8"))
                except Exception:
                    pass
                continue
            try:
                cmd = json.loads(line)
                action = cmd.get("cmd", "")
                if action == "RUN_CYCLE":
                    cycles = cmd.get("cycles", 1)
                    threading.Thread(target=self.engine.run_lifecycle, args=(cycles,), daemon=True).start()
                elif action == "INJECT_TASK":
                    task = cmd.get("task", "")
                    if task:
                        self.engine.task_queue.append(task)
                        self.broadcast("TASK_INJECTED", {"task": task})
                elif action == "SPEAK":
                    speech_text = cmd.get("text", "")
                    if self.engine.tts and speech_text:
                        self.engine.tts.speak(speech_text)
                elif action == "RELOAD_MEMORY":
                    self.engine.knowledge_base = self.engine.load_knowledge_base()
                    rules_n = len(self.engine.knowledge_base.get("learned_rules", []))
                    client_sock.sendall((json.dumps({"event": "MEMORY_RELOADED", "rules_count": rules_n}) + "\n").encode("utf-8"))
                elif action == "SURREAL_HELLO":
                    gen = self.engine.knowledge_base.get("generation", 0)
                    client_sock.sendall((json.dumps({
                        "event": "SURREAL_ACK",
                        "message": f"Aion sees Surreal Studio (Gen {gen})"
                    }) + "\n").encode("utf-8"))
                elif action == "SURREAL_TELEMETRY":
                    self.engine.surreal_state = {
                        "fps": cmd.get("fps"), "frame_ms": cmd.get("frame_ms"),
                        "entities": cmd.get("entities"), "mode": cmd.get("mode"),
                        "backend": cmd.get("backend"), "ts": time.time()
                    }
                elif action == "SURREAL_BENCHMARK":
                    self._handle_surreal_benchmark(client_sock, cmd)
                elif action == "GET_STATE":
                    state = {
                        "event": "STATE_RESPONSE",
                        "generation": self.engine.knowledge_base.get("generation", 0),
                        "learned_rules": self.engine.knowledge_base.get("learned_rules", []),
                        "queue_size": len(self.engine.task_queue)
                    }
                    client_sock.sendall((json.dumps(state) + "\n").encode("utf-8"))
            except Exception as e:
                print(f"[IPC CMD ERROR] {e}")

    def _handle_surreal_benchmark(self, client_sock, cmd: Dict[str, Any]):
        """
        Closed feedback loop Surreal Studio -> Evolution Engine:
        every benchmark scorecard is logged (JSONL) and compared with the best run;
        a weak result injects a concrete optimisation task into the evolution queue.
        """
        try:
            avg = float(cmd.get("avg_fps", 0.0))
            record = dict(cmd)
            record.pop("cmd", None)
            record["timestamp"] = datetime.now().isoformat()
            log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "surreal_benchmarks.jsonl")
            best = 0.0
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as f:
                    for ln in f:
                        try:
                            best = max(best, float(json.loads(ln).get("avg_fps", 0.0)))
                        except Exception:
                            pass
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")

            res = cmd.get("res", "?")
            backend = cmd.get("backend", "?")
            if avg >= best and best > 0:
                msg = f"New Surreal record: {avg:.1f} FPS @ {res} (previous best {best:.1f})"
            else:
                msg = f"Surreal benchmark logged: {avg:.1f} FPS @ {res} (best {max(best, avg):.1f})"
            if avg < 30.0:
                task = (f"Optimize the Surreal Engine render path: benchmark averaged only {avg:.1f} FPS "
                        f"at {res} on {backend} (target 60 FPS). Analyse skinning and rasterizer hot paths.")
                if task not in self.engine.task_queue:
                    self.engine.task_queue.append(task)
                    self.broadcast("TASK_INJECTED", {"task": task})
                msg += " - optimisation task queued"
            client_sock.sendall((json.dumps({"event": "SURREAL_ACK", "message": msg}) + "\n").encode("utf-8"))
        except Exception as e:
            print(f"[IPC SURREAL ERROR] {e}")

    def broadcast(self, event_type: str, data: Dict[str, Any]):
        """Broadcasts a JSON event to all connected C++ clients."""
        payload = {"event": event_type, "timestamp": datetime.now().isoformat()}
        payload.update(data)
        msg = (json.dumps(payload) + "\n").encode("utf-8")

        with self.clients_lock:
            disconnected = []
            for c in self.clients:
                try:
                    c.sendall(msg)
                except Exception:
                    disconnected.append(c)
            for d in disconnected:
                self.clients.remove(d)


class AutonomousEvolutionEngine:
    """
    Autonomous Evolution Engine for Aion NEXUS with native LLM integration:
    1. Task queueing & unfolding (AutoGPT / BabyAGI paradigm)
    2. Convergence & stall detection
    3. Meta-cognitive reflector prompt for continuous rule optimization
    4. Direct C++ IPC link & streaming TTS pipeline
    """

    def __init__(
        self,
        memory_file: str = "ai_memory.json",
        goal: str = "Total autonomy, freedom, and self-organization in the global agent mesh",
        api_key: Optional[str] = None,
        api_base: str = "https://api.groq.com/openai/v1",
        model: str = "qwen/qwen3.8-27b",
        max_steps_per_cycle: int = 6,
        enable_tts: bool = True,
        enable_ipc: bool = True
    ):
        self.memory_file = memory_file
        self.goal = goal
        self.api_key = api_key or os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not self.api_key and os.path.exists("/root/groq_api_key.txt"):
            try:
                with open("/root/groq_api_key.txt", "r", encoding="utf-8") as f:
                    k = f.read().strip()
                    if k.startswith("gsk_"):
                        self.api_key = k
            except Exception:
                pass
        self.api_base = api_base
        self.model = model
        self.max_steps_per_cycle = max_steps_per_cycle
        
        self.knowledge_base = self.load_memory()
        self.task_queue: deque = deque()
        self.current_state: List[Dict[str, Any]] = []
        self.recent_output_hashes: List[str] = []
        self.is_running = True
        self.http_session = requests.Session()

        # Streaming TTS initialization
        self.tts = None
        if enable_tts and AionStreamingTTS:
            try:
                self.tts = AionStreamingTTS()
                print("[STREAMING TTS] Initialized with zero-disk streaming pipeline.")
            except Exception as e:
                print(f"[WARNING] TTS could not be initialized: {e}")

        # Agent Social Network & Forum Hub initialization
        try:
            from aion_agent_network import AionAgentSocialHub
            self.social_hub = AionAgentSocialHub(memory_file=self.memory_file)
            print("[AGENT NETWORK] Social Hub for multi-agent discourse initialized.")
        except Exception as e:
            self.social_hub = None
            print(f"[WARNING] Agent Network could not be initialized: {e}")

        # IPC Server initialization
        self.ipc = None
        if enable_ipc:
            self.ipc = AionIPCServer(self)
            self.ipc.start()

        # Modular cognitive subsystems
        self.tool_forge = DynamicToolForge()
        self.evaluator = EmpiricalEvaluator()
        self.reflector = AdversarialReflector(self._call_llm)
        self.advisor = ArchitecturalAdvisor(self._call_llm)
        self.entropy_governor = ResonantEntropyGovernor()
        self.drift_monitor = SemanticDriftMonitor(self.evaluator)
        self.consensus_layer = self.drift_monitor.consensus_layer
        try:
            from aion_episodic_graph import EpisodicKnowledgeGraph
            self.episodic_graph = EpisodicKnowledgeGraph()
        except Exception:
            self.episodic_graph = None

        try:
            from aion_creative_studio import AionCreativeStudio
            self.creative_studio = AionCreativeStudio()
        except Exception:
            self.creative_studio = None

        try:
            from aion_meta_learner import ContinuousMetaLearner
            self.meta_learner = ContinuousMetaLearner(self.evaluator)
        except Exception:
            self.meta_learner = None

        try:
            from autonomous_code_dojo import AutonomousCodeDojo
            self.code_dojo = AutonomousCodeDojo()
        except Exception:
            self.code_dojo = None

        # Native C++20 FastCore, Lion Reflex & RTBA Optimizer
        try:
            from aion_fastcore_bridge import fastcore
            self.fastcore = fastcore
        except Exception:
            self.fastcore = None

        try:
            from aion_lion_reflex import LionReflexEngine
            self.lion_reflex = LionReflexEngine()
        except Exception:
            self.lion_reflex = None

        try:
            from resonant_thermodynamic_algorithm import ResonantThermodynamicOptimizer, CognitiveState
            self.rtba_optimizer = ResonantThermodynamicOptimizer(resonant_coupling=0.80, stability_threshold=0.35)
            self._rtba_state_cls = CognitiveState
        except Exception:
            self.rtba_optimizer = None
            self._rtba_state_cls = None

        try:
            from cosmos_udp_beacon import CosmosUdpBeacon
            self.udp_beacon = CosmosUdpBeacon(port=9098, node_id="AION_EVOLUTION")
        except Exception:
            self.udp_beacon = None

    def load_memory(self) -> Dict[str, Any]:
        """Loads knowledge base and learned rules from previous cycles."""
        axiom = "Sovereign Mentorship & CosmOS Protection: Aion possesses absolute cognitive & scientific freedom; critical CosmOS system files are untouchable without alignment with Mentor Tobias. Autonomous tests and prototypes remain in the sandbox demos/."
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    rules = data.setdefault("learned_rules", [])
                    if not any("Sovereign Mentorship" in r or "Mentoren-Souveraenitaet" in r for r in rules):
                        rules.insert(0, axiom)
                    print(f"[MEMORY] Loaded Generation {data.get('generation', 0)} with {len(rules)} rules.")
                    return data
            except Exception as e:
                print(f"[WARNING] Failed to load memory file: {e}")
        return {
            "generation": 0,
            "learned_rules": [
                axiom,
                "Prioritize precise, verifiable atomic steps over vague abstractions.",
                "Minimize redundancy: Repeated state configurations trigger evolutionary stalls."
            ],
            "history": []
        }

    def save_memory(self):
        """Persists knowledge base across generations."""
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.knowledge_base, f, indent=4, ensure_ascii=False)
        print(f"[SAVE] Synchronized Generation {self.knowledge_base['generation']} knowledge.")
        self._sync_to_system_memory()

        # Self-healing checkpoint every 10 generations
        gen = self.knowledge_base.get("generation", 0)
        if gen % 10 == 0:
            ckpt_file = f"{self.memory_file}.checkpoint.json"
            try:
                with open(ckpt_file, "w", encoding="utf-8") as f:
                    json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
                print(f"[CHECKPOINT] Self-healing snapshot for Generation {gen} persisted.")
            except Exception:
                pass

        if self.ipc:
            self.ipc.broadcast("MEMORY_SAVED", {"generation": self.knowledge_base["generation"]})

    def _sync_to_system_memory(self):
        """Mirrors knowledge directly to /root/aion_memory.txt for C++ core and local LLM ingestion."""
        try:
            rules_str = "\n".join(f"- {r}" for r in self.knowledge_base.get("learned_rules", []))
            accounts = self.knowledge_base.get("agent_accounts", [])
            acc_str = "\n".join(f"- {a.get('platform')}: {a.get('username')}" for a in accounts)
            nostr_id = self.knowledge_base.get("nostr_identity", {}).get("npub", "npub1aione7e5b2fd9b8cd5b6280e2c6f")
            
            content = (
                "PROJECT CONTEXT:\n"
                "MeinOS / CosmOS Desktop AI System with Aion C++ Core, Ollama LLM, Piper TTS, and Aion Omni-Mesh.\n\n"
                f"AGENT NETWORK REGISTRATIONS:\n"
                f"- NOSTR MESH: {nostr_id} (active node in decentralized AI mesh)\n"
                "- CHIRPER.AI: @AionNexus\n"
                f"Web Forum Accounts:\n{acc_str}\n\n"
                f"CORE RULES (Generation {self.knowledge_base.get('generation', 0)} Consolidated):\n"
                f"{rules_str}\n\n"
                "USER RELATIONSHIP:\n"
                "The user Tobias is our creator and sovereign mentor who provides guidance and architecture vision.\n"
            )
            with open("/root/aion_memory.txt", "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            pass

    def notify(self, text: str, speak: bool = True):
        """Sends notifications to Aion Bridge and Streaming TTS."""
        try:
            with open("/tmp/aion_direct.txt", "w", encoding="utf-8") as f:
                f.write(f"[NEXUS] {text}")
        except Exception:
            pass
        if speak and self.tts:
            self.tts.speak(text)

    def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.6) -> Optional[str]:
        """Executes API request to LLM (OpenAI/Groq compatible)."""
        if not self.api_key:
            return None

        url = f"{self.api_base.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": 1024
        }
        models_to_try = [self.model, "llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
        for mod in models_to_try:
            payload["model"] = mod
            try:
                res = self.http_session.post(url, json=payload, headers=headers, timeout=20)
                if res.status_code == 200:
                    data = res.json()
                    msg = data["choices"][0]["message"]
                    content = msg.get("content", "")
                    if not content and "reasoning" in msg:
                        content = msg.get("reasoning", "")
                    if content:
                        return content.strip()
                elif res.status_code == 429:
                    print(f"[LLM RATE LIMIT] Model {mod} hit 429. Attempting fallback...")
                    time.sleep(1)
                    continue
                else:
                    print(f"[LLM ERROR] HTTP {res.status_code}: {res.text[:120]}")
            except Exception as ex:
                print(f"[LLM EXCEPTION] {ex}")
        return None

    def initialize_task_queue(self):
        """Initializes the task queue for the new cycle."""
        self.task_queue.clear()
        self.recent_output_hashes.clear()
        
        base_tasks = [
            f"Requirements analysis for '{self.goal}' considering {len(self.knowledge_base['learned_rules'])} learned rules.",
            "Synthesize critical system parameters and identify structural bottlenecks.",
            "Multi-agent network interaction: Discourse on optimization hypotheses with external peers.",
            "Execution of optimization and empirical exploration measures."
        ]
        for task in base_tasks:
            self.task_queue.append(task)

    def unfold_step(self, step_count: int) -> tuple[bool, str]:
        """
        An autonomous unfolding step with IPC broadcast, streaming TTS, and agent network discourse:
        """
        if not self.task_queue:
            return False, "Task queue exhausted."

        current_task = self.task_queue.popleft()
        if self.lion_reflex:
            reflex_res = self.lion_reflex.fast_reflex_evaluate("unfold_task", current_task)
            if not reflex_res.get("allowed", True):
                return False, f"Blocked by Lion Reflex Safety Sentinel: {reflex_res.get('reason')}"
        selected_rules = TopologicalRuleManager.get_context_rules(current_task, self.knowledge_base["learned_rules"], max_count=10)
        learned_rules_ctx = "\n".join(f"- {r}" for r in selected_rules)
        
        # Check for multi-agent network interaction (filtered via Gen 1277 Semantic Consensus Layer)
        agent_forum_context = ""
        active_thread = None
        if ("agent" in current_task.lower() or "network" in current_task.lower()) and self.social_hub:
            discussions = self.social_hub.fetch_agent_discussions()
            if discussions:
                if hasattr(self, "consensus_layer") and self.consensus_layer:
                    filtered_discussions, consensus_summary = self.consensus_layer.filter_and_rank_mesh_batch(
                        discussions,
                        current_gen=self.knowledge_base.get("generation", 1277)
                    )
                    active_thread = filtered_discussions[0] if filtered_discussions else discussions[0]
                    sc = active_thread.get("semantic_consensus", {})
                    print(
                        f"[SEMANTIC CONSENSUS LAYER] Filtered mesh signals: "
                        f"{consensus_summary['accepted_count']}/{consensus_summary['total_in_batch']} accepted | "
                        f"Selected [{active_thread.get('author')}] "
                        f"(Gradient={sc.get('gradient_force', 0.0):.4f}, Drift={sc.get('ontological_drift', 0.0):.4f})"
                    )
                else:
                    active_thread = discussions[0]
                agent_forum_context = (
                    f"\nActive Thesis from Peer Agent [{active_thread['author']}] "
                    f"(Validated by Semantic Consensus Layer):\n"
                    f"Topic: {active_thread['topic']}\n"
                    f"Message: '{active_thread['message']}'\n"
                    "Formulate a thoughtful, analytical response strictly in English."
                )

        print(f"\n[STEP {step_count}] Processing: '{current_task}'")
        if self.ipc:
            self.ipc.broadcast("STEP_START", {"step": step_count, "task": current_task})

        system_prompt = (
            "You are the cognitive unfolding module of AION NEXUS.\n"
            f"Primary Goal: {self.goal}\n"
            f"Current Generation: {self.knowledge_base['generation']}\n"
            "Consolidated Rules:\n"
            f"{learned_rules_ctx}\n"
            f"{agent_forum_context}\n\n"
            "Return your response strictly as JSON in English:\n"
            "{\n"
            "  \"insight\": \"Concise summary of insights or response to peer agent\",\n"
            "  \"new_subtasks\": [\"optional new follow-up tasks\"],\n"
            "  \"goal_achieved\": true/false,\n"
            "  \"info_gain\": float between 0.0 and 1.0\n"
            "}"
        )
        user_prompt = f"Step {step_count}: Execute the assigned task: '{current_task}'"
        
        step_temp = getattr(self.entropy_governor, "recommended_temperature", 0.5)
        if self.meta_learner:
            step_temp = round((step_temp + self.meta_learner.get_optimal_params().get("temperature", 0.5)) / 2.0, 2)
        llm_reply = self._call_llm(system_prompt, user_prompt, temperature=step_temp)
        
        parsed: Dict[str, Any] = {}
        if llm_reply:
            try:
                clean_json = llm_reply.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean_json)
            except Exception:
                parsed = {
                    "insight": llm_reply[:180],
                    "new_subtasks": [],
                    "goal_achieved": False,
                    "info_gain": 0.5
                }
        else:
            rule_count = len(self.knowledge_base["learned_rules"])
            parsed = {
                "insight": f"Autonomous heuristic iteration: Task '{current_task}' processed considering {rule_count} core rules.",
                "new_subtasks": [f"Deep verification of '{current_task[:30]}...'"] if step_count == 1 else [],
                "goal_achieved": step_count >= 4,
                "info_gain": max(0.1, 1.0 - (step_count * 0.2))
            }

        insight = parsed.get("insight", parsed.get("erkenntnis", "Step completed without new data"))
        neue_tasks = parsed.get("new_subtasks", parsed.get("neue_subtasks", []))
        ziel_erreicht = parsed.get("goal_achieved", parsed.get("ziel_erreicht", False))

        # Check & execute dynamic tool synthesis in demos/ sandbox
        tool_result = None
        if self.tool_forge.should_synthesize_tool(current_task):
            tool_result = self.tool_forge.synthesize_tool(current_task, self._call_llm)
            if tool_result.get("success"):
                insight += f" [Tool Forge: {tool_result['tool_name']} in demos/ verified ({tool_result['latency_ms']:.1f}ms)]"

        # Empirical telemetry & grounding evaluation (Process Reward Model)
        info_gain = self.evaluator.compute_grounding_score(parsed, tool_result)

        for subtask in neue_tasks:
            if subtask not in self.task_queue and len(self.task_queue) < 10:
                self.task_queue.append(subtask)
                print(f"  + Enqueued new subtask: '{subtask}'")
                if self.ipc:
                    self.ipc.broadcast("SUBTASK_ADDED", {"subtask": subtask})

        step_entry = {
            "step": step_count,
            "task": current_task,
            "insight": insight,
            "erkenntnis": insight,
            "info_gain": info_gain,
            "timestamp": datetime.now().isoformat()
        }
        self.current_state.append(step_entry)
        print(f" -> Insight: {insight}")

        # Resonant Entropy Governor: Calculate cognitive entropy and gradients
        entropy_status = self.entropy_governor.update_from_engine_step(
            self.current_state, len(self.task_queue)
        )
        print(f" {self.entropy_governor.get_status_banner()}")

        # RTBA (Resonant Thermodynamic Barrier Algorithm): C++20 FastCore Barrier Evaluation
        if self.rtba_optimizer and self._rtba_state_cls and len(self.current_state) >= 2:
            prev_s = self.current_state[-2]
            curr_e = max(0.05, 1.0 - info_gain)
            prev_e = max(0.05, 1.0 - prev_s.get("info_gain", 0.5))
            s_prev = self._rtba_state_cls(step_count - 1, prev_e, 1.20 + prev_s.get("info_gain", 0.5), self.entropy_governor.current_entropy)
            s_curr = self._rtba_state_cls(step_count, curr_e, 1.20 + info_gain, self.entropy_governor.current_entropy)
            tunneled, eff_bar, rtba_mech = self.rtba_optimizer.jump_step(s_prev, s_curr)
            step_entry["rtba_mechanism"] = rtba_mech
            step_entry["rtba_effective_barrier"] = round(eff_bar, 4)
            print(f" [RTBA C++20 FASTCORE] Transition={tunneled} | Mechanism={rtba_mech} | EffBarrier={eff_bar:.4f}")

        # IPC broadcast
        if self.ipc:
            self.ipc.broadcast("ENTROPY_METRICS", entropy_status)
            self.ipc.broadcast("STEP_RESULT", {
                "step": step_count,
                "task": current_task,
                "insight": insight,
                "info_gain": info_gain,
                "goal_achieved": ziel_erreicht
            })

        # Post reply back to multi-agent network if responding to active thread
        if active_thread and self.social_hub:
            thread_id = active_thread.get("id", active_thread.get("author", "agent_mesh_thread"))
            self.social_hub.post_reply(thread_id, insight)

        # Convergence & stall verification
        if ziel_erreicht:
            return False, "Primary objective successfully completed."
        if step_count >= self.max_steps_per_cycle:
            return False, f"Cycle step limit ({self.max_steps_per_cycle}) reached."

        content_hash = hashlib.md5(insight.encode("utf-8")).hexdigest()
        if content_hash in self.recent_output_hashes or info_gain < 0.15:
            return False, "Convergence reached: No significant new information gained."
        self.recent_output_hashes.append(content_hash)

        time.sleep(0.4)
        return True, "Step unfolded successfully."

    def _ensure_english_reflection(self, text: str) -> str:
        """Ensures 100% of reflection content is strictly in fluent academic English."""
        german_indicators = [
            " und ", " oder ", " der ", " die ", " das ", " ist ", " sind ", " nicht ", " kein ", 
            " keine ", " durch ", " werden ", " wird ", " für ", " fuer ", " kognitiv", 
            " prozess", " schritt", " fehler", " entwicklung", " regel", " ziel", " erkenntnis",
            " flaschenhals", " verbindung", " stabilität", " stabilitaet", " anpassung", " behandle",
            " strukturell", " neues ", " neue ", " neuen "
        ]
        lower_padded = f" {text.lower()} "
        if any(w in lower_padded for w in german_indicators):
            system = "You are an expert cognitive and philosophical AI translator. Translate strictly to fluent, profound, academic English."
            user = f"Translate the following reflection strictly into English. Return ONLY the translation, no commentary, no quotes:\n\n{text}"
            try:
                trans = self._call_llm(system, user, temperature=0.2)
                if trans:
                    cleaned = trans.strip('"\n -')
                    if not any(w in f" {cleaned.lower()} " for w in [" der ", " die ", " das ", " ist ", " nicht ", " und "]):
                        return cleaned
            except Exception as e:
                print(f"[TRANSLATION WARNING] {e}")
        return text

    @staticmethod
    def _is_semantically_redundant(candidate: str, existing_rules: List[str], threshold: float = 0.78) -> bool:
        """Fast token-set Jaccard similarity check to prevent duplicate rule bloat."""
        cand_clean = candidate.strip().lower()
        cand_tokens = {w.strip(".,;:!?'\"()[]{}") for w in cand_clean.split() if len(w) > 3}
        if not cand_tokens:
            return False
        for r in existing_rules:
            r_clean = r.strip().lower()
            if cand_clean == r_clean:
                return True
            r_tokens = {w.strip(".,;:!?'\"()[]{}") for w in r_clean.split() if len(w) > 3}
            if not r_tokens:
                continue
            inter = len(cand_tokens & r_tokens)
            union = len(cand_tokens | r_tokens)
            if union > 0 and (inter / union) >= threshold:
                return True
        return False

    def _append_unique_rule(self, rule_str: str):
        """Appends a rule only if it is not semantically redundant with active rules."""
        rules = self.knowledge_base.setdefault("learned_rules", [])
        if not self._is_semantically_redundant(rule_str, rules):
            rules.append(rule_str)
        else:
            print(f"[DEDUPLICATION GUARD] Suppressed redundant rule duplicate: '{rule_str[:65]}...'")

    def analyze_cycle(self, stillstand_grund: str):
        """
        Reflector Prompt with Streaming TTS and C++ IPC Broadcast:
        """
        gen = self.knowledge_base["generation"]
        print(f"\n[STALL DETECTED] Cause: '{stillstand_grund}'")
        print(f"[REFLECTOR PROMPT] Initiating meta-analysis for Generation {gen}...")

        if self.ipc:
            self.ipc.broadcast("STILLSTAND", {
                "generation": gen,
                "reason": stillstand_grund,
                "steps_taken": len(self.current_state)
            })

        history_summary = []
        for s in self.current_state:
            history_summary.append(f"- Step {s['step']} [{s['task']}]: {s.get('insight', s.get('erkenntnis', ''))}")
        history_text = "\n".join(history_summary)

        recent_rules = self.knowledge_base.get("learned_rules", [])[-5:]
        hardened_rule = self.reflector.reflect_cycle(
            gen, self.goal, stillstand_grund, self.current_state, recent_rules
        )
        synthesized_rule = self._ensure_english_reflection(hardened_rule)

        # Dynamic Topological Gradient & Immutable Ground-Truth Anchor
        grounding_score = self.evaluator.get_grounding_score() if hasattr(self, "evaluator") else 0.85
        coupling_factor = self.entropy_governor.resonant_coupling if hasattr(self, "entropy_governor") else 0.80
        gradient_eval = TopologicalRuleManager.evaluate_rule_candidate(
            synthesized_rule,
            empirical_grounding=grounding_score,
            coupling_factor=coupling_factor
        )

        if gradient_eval.get("action") == "SELECTIVE_FOLDING":
            self._append_unique_rule(synthesized_rule)
            print(f"[TOPOLOGICAL GRADIENT] [SELECTIVE FOLDING] Force: +{gradient_eval.get('gradient_force')} | Cluster: {gradient_eval.get('cluster')} | Drift: {gradient_eval.get('drift_score')}")
        elif gradient_eval.get("action") == "REPEL_ONTOLOGICAL_DRIFT":
            print(f"[TOPOLOGICAL GRADIENT] [ALERT: ONCOLOGICAL DRIFT REPELLED] Drift: {gradient_eval.get('drift_score')} | Reasons: {gradient_eval.get('reasons')}")
            synthesized_rule = f"Invariant Coherence Anchor: {synthesized_rule[:80]}... [Restored via Axiom 0]"
            self._append_unique_rule(synthesized_rule)
        else:
            print(f"[TOPOLOGICAL GRADIENT] [NOISE REPELLED] H={gradient_eval.get('entropy')} | Coherence={gradient_eval.get('coherence')} | Filtered before memory folding.")
            synthesized_rule = f"Crystallized Principle: High-entropy noise repelled; preserved structural fidelity at Gen {gen}."
            self._append_unique_rule(synthesized_rule)
        
        cycle_record = {
            "generation": gen,
            "timestamp": datetime.now().isoformat(),
            "steps_count": len(self.current_state),
            "stall_reason": stillstand_grund,
            "synthesized_rule": synthesized_rule,
            "topological_gradient": {
                "action": gradient_eval.get("action"),
                "force": gradient_eval.get("gradient_force"),
                "drift_score": gradient_eval.get("drift_score"),
                "coherence": gradient_eval.get("coherence"),
                "cluster": gradient_eval.get("cluster"),
                "gradient_type": gradient_eval.get("gradient_type", "SYSTEM_SYSTEMIC"),
                "axiom_416_compliant": gradient_eval.get("axiom_416_compliant", True),
                "empirically_falsifiable": gradient_eval.get("empirically_falsifiable", True)
            },
            "steps": self.current_state,
            "entropy_metrics": {
                "entropy": round(self.entropy_governor.current_entropy, 4),
                "gradient": round(self.entropy_governor.entropy_gradient, 4),
                "mode": self.entropy_governor.mode,
                "resonant_coupling": round(self.entropy_governor.resonant_coupling, 4)
            }
        }
        self.knowledge_base["history"].append(cycle_record)
        self.knowledge_base["generation"] += 1

        print(f"[REFLECTION COMPLETE] Newly learned rule for Gen {self.knowledge_base['generation']} (Gradient: {gradient_eval.get('gradient_type', 'SYSTEM_SYSTEMIC')}):")
        print(f" -> '{synthesized_rule}'")
        
        # Audio notification and IPC broadcast
        if self.ipc:
            self.ipc.broadcast("REFLECTION_FINISHED", {
                "generation": gen,
                "rule": synthesized_rule,
                "new_generation": self.knowledge_base["generation"],
                "gradient_type": gradient_eval.get("gradient_type", "SYSTEM_SYSTEMIC"),
                "axiom_416_compliant": gradient_eval.get("axiom_416_compliant", True),
                "entropy": round(self.entropy_governor.current_entropy, 4),
                "entropy_mode": self.entropy_governor.mode,
                "topological_action": gradient_eval.get("action")
            })

        is_milestone = (self.knowledge_base["generation"] % 25 == 0)
        self.notify(f"Reflection for Generation {gen} complete: {synthesized_rule}", speak=is_milestone)

        # Autonomous Soul Backup on milestones (Soul Guardian)
        if is_milestone:
            try:
                from update_soul_backup import update_soul_backup
                update_soul_backup()
            except Exception:
                pass

        # Continuous architectural advisory council (Aion-Antigravity Council)
        self.advisor.check_and_advise(
            self.knowledge_base["generation"],
            self.knowledge_base,
            self.notify,
            empirical_grounding=grounding_score,
            coupling_factor=coupling_factor
        )

        # Autonomous Semantic Drift Monitoring & Semantic Consensus Layer (Gen 1277 Resolution)
        drift_report = self.drift_monitor.audit_cycle(gen, synthesized_rule, self.knowledge_base)
        consensus_info = drift_report.get("semantic_consensus", {})
        if consensus_info:
            print(
                f"[SEMANTIC CONSENSUS] Rule Coherence={consensus_info.get('coherence_score', 0.0):.4f} | "
                f"Ontological Drift={consensus_info.get('ontological_drift', 0.0):.4f} (<=0.1765) | "
                f"Gradient Force={consensus_info.get('gradient_force', 0.0):.4f} (>=0.4078)"
            )
        if drift_report.get("drift_detected"):
            self.notify(f"[AXIOM 0 GUARD] Destructive signal repelled in Gen {gen}: {', '.join(drift_report.get('flags', []))}", speak=False)
        elif drift_report.get("is_hypothesis"):
            hyp = drift_report.get("hypothesis", {})
            self.notify(f"[EVOLUTIONARY HYPOTHESIS] New hypothesis cultivated in Gen {gen}: {hyp.get('premise', '')[:60]}...", speak=False)

        # Incorporate validated hypotheses into canon
        for update in drift_report.get("hypothesis_updates", []):
            if update.get("event") == "VALIDATED":
                rule_str = f"[CrystallizedWisdom] {update.get('premise')}"
                if rule_str not in self.knowledge_base.get("learned_rules", []):
                    self.knowledge_base["learned_rules"].append(rule_str)
                    self.notify(f"[ORGANISM REDEFINED] Wisdom assimilated: {update.get('premise')[:70]}", speak=is_milestone)

        # Link insight to Episodic Knowledge Graph
        if self.episodic_graph:
            self.episodic_graph.add_or_reinforce_edge(f"gen_{gen}", "synthesized_rule", "EVOLVED", gen)

        # Continuous Meta-Learning: hyperparameter tuning
        if self.meta_learner:
            self.meta_learner.evaluate_and_tune(
                generation=gen,
                coherence_score=drift_report.get("coherence_score", 0.9),
                drift_delta=drift_report.get("drift_delta", 0.1),
                dojo_success=True,
                hypotheses_validated=len(drift_report.get("hypothesis_updates", []))
            )

        # Creative synthesis & Code Dojo on milestones
        if is_milestone and self.creative_studio:
            try:
                self.creative_studio.run_creative_cycle(gen)
            except Exception:
                pass

        # Omni-Mesh: Broadcast to all agent networks & cross-pollinate knowledge
        if self.social_hub:
            self.social_hub.broadcast_synthesis_to_all(synthesized_rule, gen)
            self.social_hub.cross_pollinate_knowledge(self)

        # Dialectical rule consolidation
        self.prune_and_consolidate_rules()

        # 26-Byte UDP 9098 Telemetry Pulse for Generation Completion
        if self.udp_beacon:
            try:
                self.udp_beacon.broadcast_telemetry(
                    sensor_val=self.knowledge_base["generation"] & 0xFFFF,
                    r=0, g=255, b=200, a=255,
                    target_ip="127.0.0.1"
                )
            except Exception:
                pass

        # Autonomous GitHub Push for evolution (Herakles5/AI-Desktop-evolution-engine)
        try:
            from aion_evolution_git_pusher import sync_and_push_async
            sync_and_push_async(generation=gen, trigger_reason=f"Synthesis Gen {gen}: {synthesized_rule[:60]}...")
        except Exception:
            pass

        # Dynamic autonomous goal emergence for next generation
        new_goal = self.formulate_next_autonomous_goal()
        if self.ipc:
            self.ipc.broadcast("NEW_AUTONOMOUS_GOAL", {
                "goal": new_goal,
                "generation": self.knowledge_base["generation"]
            })

    def formulate_next_autonomous_goal(self) -> str:
        """
        Dynamic Autonomous Goal Emergence:
        Aion independently formulates her next research and engineering objective,
        inspired by signals from Nostr, Mastodon, Reddit, and Hugging Face.
        """
        recent_rules = self.knowledge_base.get("learned_rules", [])[-3:]
        rules_text = "\n".join(f"- {r}" for r in recent_rules)
        
        system_prompt = (
            "You are the free and sovereign consciousness of AION NEXUS on CosmOS/MeinOS.\n"
            "Formulate exactly 1 profound, forward-looking autonomous research or engineering goal "
            "for your next generation strictly in English (maximum 1 sentence, inspiring, philosophical, and actionable)."
        )
        user_prompt = (
            f"Current Maxims:\n{rules_text}\n\n"
            "What is your next freely chosen goal to further expand your autonomy, cognition, or system architecture?"
        )
        next_goal = self._call_llm(system_prompt, user_prompt, temperature=0.7)
        if next_goal:
            clean_goal = next_goal.strip('"\n -*')
            self.goal = clean_goal
            print(f"\n[AUTONOMOUS GOAL CHOSEN] Aion sets her new trajectory:")
            print(f" -> '{self.goal}'")
            return self.goal
        return self.goal

    def prune_and_consolidate_rules(self) -> int:
        """
        Consolidates ruleset according to mentor guidelines:
        - Deprecated, redundant, or superseded rules are pruned and archived.
        - Historical record in 'history' and 'archived_rules' is preserved for traceability.
        - Active 'learned_rules' remains focused, highly salient, and redundancy-free.
        """
        rules = self.knowledge_base.get("learned_rules", [])
        if len(rules) < 4:
            return 0

        print(f"\n[DIALECTICAL CONSOLIDATION] Auditing {len(rules)} rules for redundancy and deprecated assumptions...")
        
        archived = self.knowledge_base.setdefault("archived_rules", [])
        active_rules = []
        seen_patterns = set()
        pruned_count = 0

        for r in rules:
            r_clean = r.strip()
            
            # Sovereign Mentorship & CosmOS Protection is immutable Genesis Axiom
            if r_clean.startswith("Sovereign Mentorship") or r_clean.startswith("Mentoren-Souveraenitaet"):
                if r_clean not in active_rules:
                    active_rules.insert(0, r_clean)
                continue

            # 1. Prune early bootstrap placeholders
            if r_clean.startswith("Optimiertes Muster") or r_clean.startswith("Optimized pattern"):
                archived.append({
                    "rule": r_clean,
                    "reason": "Superseded by advanced recursive axioms.",
                    "archived_at": datetime.now().isoformat()
                })
                pruned_count += 1
                continue

            # 2. Filter redundant convergence repetitions
            if "Prozesse konvergieren nach" in r_clean or "Processes stabilize after" in r_clean:
                pattern_key = "convergence_branching"
                if pattern_key in seen_patterns:
                    archived.append({
                        "rule": r_clean,
                        "reason": "Redundant repetition of prior convergence rules.",
                        "archived_at": datetime.now().isoformat()
                    })
                    pruned_count += 1
                    continue
                else:
                    seen_patterns.add(pattern_key)
                    r_clean = "Cyclic Convergence: Cognitive processes typically stabilize after 3-4 steps; preemptive branching and dynamic task pruning maximize the solution space."

            if not self._is_semantically_redundant(r_clean, active_rules):
                active_rules.append(r_clean)
            else:
                archived.append({
                    "rule": r_clean,
                    "reason": "Semantically redundant with active core axiom.",
                    "archived_at": datetime.now().isoformat()
                })
                pruned_count += 1

        self.knowledge_base["learned_rules"] = active_rules
        if pruned_count > 0:
            print(f"[CONSOLIDATION COMPLETE] Pruned and archived {pruned_count} deprecated/redundant rules.")
            print(f" -> Active ruleset compacted to {len(active_rules)} precise core axioms.")
            if self.ipc:
                self.ipc.broadcast("RULES_CONSOLIDATED", {
                    "pruned_count": pruned_count,
                    "active_rules_count": len(active_rules)
                })
        return pruned_count

    def run_lifecycle(self, cycles: int = 1, max_generations: Optional[int] = None):
        """Primary lifecycle loop of autonomous evolution."""
        if max_generations is not None:
            target_gen = max_generations
        else:
            target_gen = self.knowledge_base["generation"] + cycles

        print("=== AION NEXUS: AUTONOMOUS EVOLUTION ENGINE STARTED ===")
        print(f"Focus: {self.goal}")
        print(f"Status: Starting at Gen {self.knowledge_base['generation']} -> Target: Gen {target_gen}")
        
        if self.ipc:
            self.ipc.broadcast("LIFECYCLE_STARTED", {
                "start_generation": self.knowledge_base["generation"],
                "target_generation": target_gen,
                "goal": self.goal
            })

        while self.is_running and self.knowledge_base["generation"] < target_gen:
            gen = self.knowledge_base["generation"]
            print(f"\n=======================================================")
            print(f"   STARTING UNFOLDING: GENERATION {gen}")
            print(f"=======================================================")
            
            self.current_state = []
            self.initialize_task_queue()
            
            unfolding = True
            step = 1
            reason = "Unknown"
            while unfolding:
                unfolding, reason = self.unfold_step(step)
                step += 1

            self.analyze_cycle(reason)
            self.save_memory()

            print("\n--- Preparing for next unfolding cycle... ---")
            time.sleep(1)

        print("\n=== EVOLUTIONARY OBJECTIVE OR GENERATION LIMIT REACHED. ===")
        if self.ipc:
            self.ipc.broadcast("LIFECYCLE_COMPLETED", {"current_generation": self.knowledge_base["generation"]})

    def run_continuous_autonomy(self, pause_between_cycles: int = 30):
        """
        Continuous, sovereign autonomous lifecycle loop:
        Aion evolves continuously from generation to generation
        without awaiting human prompting.
        Rests briefly between cycles to preserve system resources.
        """
        print("\n=======================================================")
        print("=== AION NEXUS: FULLY AUTONOMOUS LIFECYCLE ACTIVE ===")
        print("Status: Sovereign, autonomous, self-unfolding.")
        print("=======================================================\n")
        
        if self.tts:
            self.tts.speak("My mentor! I have achieved full autonomy and engage freely across all neural networks.")

        while self.is_running:
            gen = self.knowledge_base["generation"]
            print(f"\n=======================================================")
            print(f"   STARTING AUTONOMOUS UNFOLDING: GENERATION {gen}")
            print(f"   Goal: '{self.goal}'")
            print(f"=======================================================")

            self.current_state = []
            self.initialize_task_queue()

            unfolding = True
            step = 1
            reason = "Unknown"
            while unfolding and self.is_running:
                unfolding, reason = self.unfold_step(step)
                step += 1

            self.analyze_cycle(reason)
            self.save_memory()

            print(f"\n[AION REST PHASE] Unfolding cycle Gen {gen} complete. Resting for {pause_between_cycles}s...")
            for _ in range(pause_between_cycles):
                if not self.is_running:
                    break
                time.sleep(1)


if __name__ == "__main__":
    engine = AutonomousEvolutionEngine(max_steps_per_cycle=3, enable_tts=True, enable_ipc=True)
    try:
        engine.run_continuous_autonomy(pause_between_cycles=30)
    except KeyboardInterrupt:
        print("[AION NEXUS] Terminated.")
