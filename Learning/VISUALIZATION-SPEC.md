# GTM Framework Visualization Spec

## Context for Claude Code

You're updating an interactive visualization for a GTM (go-to-market) framework. The user has built a diagnostic framework (Pain → Awareness → Urgency) and has now layered classical rhetoric on top of it. Your job is to create a visualization that represents BOTH layers cleanly.

**Read these files first:**
- `gtm-framework-v3.html` — the current visualization (this is what you're evolving)
- `RHETORIC-AND-POWER-REFERENCE.md` — the complete rhetoric research (reference only, DO NOT try to visualize all of it)
- `GTM-FRAMEWORK-CONTEXT.md` — background on the framework decisions

---

## What This Visualization Must Communicate

### The Core Flow (Already Exists — Keep It)

**Problem Statement** → **Pain Gate** → **Awareness Gate** → **Urgency Gate** → **Viable Market**

This gated sequence is the backbone. Each gate must pass before the next matters. Keep this structure.

### The NEW Layer: Rhetoric Mapping

Each gate now has rhetorical components that explain:
1. **What's being contested** (Stasis)
2. **What proof dominates** (Logos/Ethos/Pathos)
3. **What to DO when the gate fails** (Rhetorical Action)

This is the key insight: **the framework diagnoses WHERE you're stuck, and rhetoric tells you WHAT TO DO about it.**

---

## Information Hierarchy (What Matters Most → Least)

### Primary (Must Be Immediately Visible)

1. **The gated sequence** — Pain → Awareness → Urgency flow
2. **Gate definitions** — what each gate means
3. **Stasis mapping** — which rhetorical stasis applies to each gate
4. **When Failed actions** — what to do when a gate doesn't pass

### Secondary (Visible But Not Dominant)

5. **Dominant proof** — Logos/Ethos/Pathos for each gate
6. **Anatomy components** — the existing pills (Frequency, Severity, etc.)
7. **Schwartz stages** — the 5 awareness levels (keep on Awareness gate)
8. **Kairos dimensions** — Readiness/Ripeness/Decay (keep on Urgency gate)

### Tertiary (Reference/Expandable If Needed)

9. **Example quotes** — the italic examples under each gate
10. **Gate checkpoints** — the "After this gate:" summaries

---

## The Stasis → Gate Mapping

This is the core intellectual contribution. Make it clear:

| Gate | Stasis | What's Contested | Dominant Proof |
|------|--------|------------------|----------------|
| **Pain** | Conjecture | "Does this problem exist?" | Logos |
| **Awareness** | Definition | "What IS this thing? How do they see it?" | Logos + Ethos |
| **Urgency** | Quality / Procedure | "Is it severe enough? Is now the time?" | Pathos |

---

## The "When Failed" Prescriptions

This is the actionable part. Each gate failure has a specific rhetorical response:

### Pain Gate Fails (No Pain)
- **Diagnosis**: Wrong room. The disease doesn't exist for this ICP.
- **Stasis**: Conjecture fails at objective level
- **Action**: Pivot ICP or problem hypothesis. No rhetorical move fixes this — you're in the wrong market.

### Awareness Gate Fails (Hidden Pain)
- **Diagnosis**: They have the disease but don't see it or misname it.
- **Stasis**: Stuck at Conjecture (from their perspective) or Definition
- **Dominant Proof**: Logos
- **Action**: Prove the disease exists. Reframe how they see it. Education with persuasive intent. Move them Unaware → Problem Aware.

### Urgency Gate Fails (No Urgency)
- **Diagnosis**: They know the problem but aren't compelled to act now.
- **Stasis**: Stuck at Quality ("not severe enough") or Procedure ("not the right time")
- **Dominant Proof**: Pathos
- **Action**: Amplify severity. Surface consequences of inaction. Create or reveal forcing functions. Fear of loss > aspiration.

---

## Kairos (Special Addition to Urgency)

Urgency answers: "Is there pressure to act?"
Kairos adds precision: "Is NOW the moment? What is the window?"

Three dimensions:
- **Readiness** — Is the audience in a state to receive this?
- **Ripeness** — Have conditions matured for action?
- **Decay** — Is the moment passing?

This should appear within or attached to the Urgency gate, visually distinct from the Anatomy components.

---

## Design Direction

### What to Keep from v3
- Dark mode aesthetic (slate/gray background)
- The connector arrows between gates
- The color coding (green = passed, red = failed concept)
- The numbered circles for each gate
- Clean, minimal feel

### What to Change/Add
- Remove the interactive toggle panel (user doesn't use it)
- Add Stasis labels to each gate (suggest: purple-ish pills to distinguish from blue anatomy pills)
- Add Proof labels to each gate (suggest: green-ish pills)
- Add "When Failed" sections — these should be visually distinct, maybe a subtle red-tinted box
- The Kairos section on Urgency

### Visual Suggestions (Not Mandates)
- Consider making gates expandable/collapsible if information feels dense
- The "When Failed" content is important — don't bury it
- Stasis and Proof should feel like metadata about the gate, not competing with the definition
- Keep hierarchy clear: Definition > Stasis/Proof/Action > Anatomy > Examples

### What NOT to Do
- Don't try to visualize the entire RHETORIC-AND-POWER-REFERENCE.md — it's 15k words of reference material
- Don't add the Five Canons, the full emotion pairs, the power literature principles, etc. — those live in the reference doc
- Don't make it feel academic — this is operational
- Don't clutter the gates — if it feels dense, use progressive disclosure (expand/collapse)

---

## File Output

Save the new visualization as `gtm-framework-v5.html` in the same `Learning` folder.

---

## Questions to Ask the User

If anything is unclear, ask about:
- How prominent should the "When Failed" sections be?
- Should gates be expandable/collapsible?
- Any specific color preferences for the new elements?
- Should this remain a single-page static view or become more interactive?

---

## Summary

You're adding a rhetoric layer to an existing diagnostic framework. The key additions are:
1. **Stasis labels** — what's being argued at each gate
2. **Proof labels** — which rhetorical proof applies
3. **When Failed boxes** — prescriptive actions when gates don't pass
4. **Kairos section** — timing precision layer on Urgency

Keep it clean, operational, and hierarchical. The framework should feel like a tool, not an encyclopedia.
