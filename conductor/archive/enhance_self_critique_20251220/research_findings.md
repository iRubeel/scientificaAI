# Research Findings: Advanced Self-Critique Methodologies

## 1. Overview
To enhance the self-critique mechanism of Revly's RefereeAgent, we investigated several advanced methodologies used in Large Language Models (LLMs) to improve reasoning accuracy and error detection.

## 2. Key Methodologies

### 2.1. Chain of Thought (CoT) Prompting
- **Concept:** Encouraging the model to articulate intermediate reasoning steps before reaching a conclusion.
- **Relevance:** The current `RefereeAgent` already uses `ReasoningStep`s, which mimics CoT.
- **Enhancement:** We can enforce more granular CoT in the *critique* phase itself, requiring the critic to explain *why* it suspects an error before flagging it.

### 2.2. Self-Consistency
- **Concept:** Generating multiple reasoning paths (samples) and selecting the most consistent answer.
- **Relevance:** For epistemic tracking, if multiple critique passes yield different results, confidence should be lower.
- **Enhancement:** The `Critic` could run multiple critique passes with slightly different prompts (temperature > 0) and aggregate findings. If an error is found in 3/5 passes, it's likely real.

### 2.3. Reflexion
- **Concept:** An iterative process where the agent generates an output, critiques it, and then *uses that critique* to generate a refined output.
- **Relevance:** This is the core goal of this track.
- **Enhancement:** Implement a strict loop: `Draft Review -> Critique -> Update Plan/Draft -> Repeat` until critique quality threshold is met.

### 2.4. Constitutional AI / Rule-Based Critique
- **Concept:** Critiquing outputs against a specific set of principles or rules (the "constitution").
- **Relevance:** Math/Stats review has specific rules (e.g., "Assumptions must be stated", "Proofs must be complete").
- **Enhancement:** We can define a "Referee Constitution" (list of specific checks) and inject it into the `Critic`'s prompt context to ensure coverage.

## 3. Proposed Strategies for Revly

### Strategy A: Constitutional Critique Prompting
Update the `Critic` prompt to include a checklist of specific mathematical review principles. This aligns with the "Refinement of Critique Rules" task.

### Strategy B: Epistemic Confidence Calibration
Use Self-Consistency concepts to calculate confidence. If the critic is unsure, it should reflect in the `EpistemicState`.

### Strategy C: Feedback Loop Integration
Ensure the `Planner` can consume `Critique` objects to modify the execution plan (e.g., add a "Verify Proof" step if a logical gap is found).

## 4. Next Steps
1.  Define the "Referee Constitution" (Phase 1, Task 3).
2.  Implement Strategy A & B in `critic.py` (Phase 2).
3.  Implement Strategy C in `planner.py` (Phase 2).
