# GTM Market Viability Framework - Complete Context Document

**Purpose**: This document captures the full context, decisions, and reasoning behind the Market Viability Framework. Read this completely before continuing work. Do not ask the user to re-explain concepts covered here.

**Last Updated**: 2025-11-30

---

## Executive Summary

We built a framework to determine **market viability** - whether an opportunity exists before you try to capture it. The framework uses three gated variables: **Pain**, **Awareness**, and **Urgency**. These are sequential gates, not independent dials. Each must pass before the next matters.

The framework answers: "Is this market worth pursuing?" It does NOT answer: "Can we win in this market?" (that's execution - Fit, Size, Competition, etc.)

---

## The Three Variables (Gated Sequence)

### 1. PAIN
**Definition**: The problem exists and causes real suffering. Like a disease in medicine - it's there whether or not anyone has diagnosed it yet. This is objective. Either your ICP has this problem or they don't.

**Key Insight**: Pain is theoretical/objective. The disease exists in the population whether or not any individual knows they have it. Your job is to find where this disease lives.

**Gate Checkpoint**: We know the problem is real for this market.

**What it's NOT**:
- Not whether they've told you about it
- Not whether they're actively complaining
- Not whether they've budgeted for it

**Anatomy**:
| Component | Source | What It Measures |
|-----------|--------|------------------|
| Frequency | YC formula | How often: hourly, daily, weekly, monthly |
| Severity | SPIN ("depth and magnitude") | Intensity per instance |
| Scope | Sandler 3 Levels | WHO is affected: Technical → Business → Personal |
| Quantifiability | MEDDIC Metrics | Can you attach $, time, risk? Numbers vs. vague |

### 2. AWARENESS
**Definition**: They perceive the pain and can name it. They know they're sick. We understand how they think about it, what words they use, what they blame it on. Our frame and their frame are aligned.

**Key Insight**: This is about frame alignment. The market has its own vocabulary, mental models, and attributions for the pain. If you call it "revenue operations inefficiency" and they call it "my sales team sucks," you're misaligned. Awareness means you understand their frame.

**Gate Checkpoint**: We know the problem is real + we know how they see it.

**Eugene Schwartz's 5 Stages of Awareness** (color-coded in visualization):
1. **Unaware** (red) - Don't know they have a problem
2. **Problem Aware** (orange) - Know the problem, don't know solutions exist
3. **Solution Aware** (yellow) - Know solutions exist, don't know your product
4. **Product Aware** (lime) - Know your product, not yet convinced
5. **Most Aware** (green) - Fully aware, convinced, just need the right offer/moment

The stages progress from red to green. "Most Aware" = the end state where awareness is complete and they're ready to buy with the right trigger.

**Anatomy**: *(TBD)*

### 3. URGENCY
**Definition**: There's pressure to solve THIS pain NOW, not someday. The disease is progressing, the pain is acute, there's a deadline. They're not just aware - they're actively seeking treatment.

**Critical Clarification**: Urgency = urgency to solve THIS specific pain. NOT general purchase pressure or budget cycles. High Urgency + Low Pain is a logical contradiction in this framework - if they're urgent to buy something but don't have your pain, they're urgent about a DIFFERENT problem.

**Gate Checkpoint**: We know the problem is real + we know how they see it + they need to solve it now.

**What Creates Urgency**:
- Forcing functions (deadlines, regulatory changes, contract renewals)
- Acute pain (pain is getting worse, not chronic/stable)
- Opportunity cost (missing out on something time-sensitive)
- External pressure (board mandate, competitive threat)

**Anatomy**:
| Component | Source | What It Answers |
|-----------|--------|-----------------|
| Trigger | MEDDPICC ("business pressure") | What's creating the forcing function? |
| Deadline | MEDDPICC ("defined date") | When must they act? |
| Consequence | MEDDPICC ("significant business result") | What happens if they don't? |

---

## Why These Three Variables (And Not Others)

### Variables We Explicitly Rejected

**Trust**: Rejected. Trust is an execution variable. You build trust through the sales process. If Pain + Awareness + Urgency are high and you can't build trust, that's a sales execution problem, not a market viability problem.

**Fit**: Rejected. Fit (your solution actually solves their problem) is execution/product. The framework assumes you're testing a hypothesis - if you pass all three gates and can't close, either your product doesn't fit or your ICP is wrong.

**Risk**: Rejected. Risk tolerance/aversion is execution. Lowering perceived risk is a sales tactic (proof points, pilots, guarantees).

**Effort/Ability**: Rejected. The user argued that Ability collapses into Urgency: "If the pain is high enough, they find the money." A CRO with a bleeding problem will find budget. If they claim they can't, the pain isn't actually high, or the urgency isn't there.

**Problem (as separate from Pain)**: Rejected after discussion. "Problem" was proposed as a weaker version of Pain (problem exists but doesn't hurt). We collapsed this - if it doesn't hurt, it's not a viable market. Latent problems that don't cause suffering are nice-to-haves, not buying triggers.

### Why The Gated/Sequential Structure

**Key Insight**: These are NOT three independent dials you can tweak separately. They're a gated sequence where each step unlocks the next:

1. If Pain is low, nothing else matters - wrong ICP or wrong problem
2. If Pain is high but Awareness is low, you have a hidden pain - education/rhetoric required
3. If Pain + Awareness are high but Urgency is low, you have a chronic problem - long sales cycle

The "diagnosis" for each combination (see Diagnosis Matrix below) tells you what's actually wrong and what action to take.

---

## What This Framework Determines

**Scope**: Market Viability (does the opportunity exist?)

**NOT in scope**:
- GTM Viability (can you capture it?)
- Market Size
- Competitive dynamics
- Your ability to win
- Product-market fit

Think of it as: "Is there a fire, is there a building, and are people running out of it?" vs. "Do we have the right fire trucks and firefighters?"

---

## The Diagnosis Matrix

Each combination of High/Low across the three variables produces a specific diagnosis:

| Pain | Awareness | Urgency | Diagnosis |
|------|-----------|---------|-----------|
| High | High | High | **Viable Market.** All gates passed. Execute GTM. |
| Low | High | High | **No Pain.** Wrong ICP or wrong problem. They don't have this pain. |
| High | Low | High | **Hidden Pain.** They have it but don't see it. Education/rhetoric required. |
| High | High | Low | **No Urgency.** Chronic problem with no forcing function. Long sales cycle. |
| Low | Low | High | **Wrong Market.** No pain, no awareness. Urgency is for something else. |
| Low | High | Low | **Wrong Market.** They're aware of a problem you don't solve. |
| High | Low | Low | **Latent Market.** Pain exists but hidden and not urgent. Very heavy lift. |
| Low | Low | Low | **No Market.** Nothing here. Pivot ICP or product entirely. |

---

## Signal Mapping (Future Work)

Each variable maps to observable, researchable signals:

**Pain Signals**:
- Job postings mentioning the problem domain
- Technographic data (tools that indicate the pain)
- Industry reports on the problem
- Peer company behaviors

**Awareness Signals**:
- Search volume for problem-related terms
- Community discussions (Reddit, LinkedIn, forums)
- Analyst reports and press coverage
- How prospects describe the problem in discovery calls

**Urgency Signals**:
- Funding rounds (money to spend)
- Leadership changes (new mandate)
- Regulatory deadlines
- Contract renewal windows
- Public statements about priorities

This is where the framework becomes actionable for GTM research.

---

## Research Foundation

### Frameworks We Studied and Incorporated

**BJ Fogg's Behavior Model (B = MAP)**:
- Behavior = Motivation + Ability + Prompt
- We mapped: Motivation ~ Pain, Ability collapsed into Urgency, Prompt ~ Urgency triggers
- Key insight: All three must converge at the same moment

**Eugene Schwartz's 5 Stages of Awareness**:
- Unaware → Problem Aware → Solution Aware → Product Aware → Most Aware
- Directly incorporated into the Awareness gate as a spectrum
- Informs messaging and channel strategy

**Theory of Planned Behavior (Ajzen)**:
- Attitude toward behavior, Subjective norms, Perceived behavioral control
- Academic validation that intention requires multiple aligned factors

**MEDDIC/MEDDPICC**:
- Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, Champion, Competition
- User's position: "MEDDPICC will become table stakes with AI/automation in GTM"
- Our framework operates upstream of MEDDPICC - it determines if you should even engage

**Jobs-to-be-Done (Christensen)**:
- Progress a customer is trying to make in a circumstance
- Aligns with Pain - the job they're hiring a solution to do

---

## The Problem Statement

**What we landed on**: "Revenue is unpredictable."

**Why this matters**: We rejected abstract/VC-speak problem statements. A CRO/CFO/COO wouldn't say "we have a go-to-market efficiency problem." They say: "Revenue is unpredictable." "I can't forecast." "My pipeline is a black box."

This grounds the framework in real executive language, not consultant-speak.

---

## Visualization Decisions

### What We Tried and Rejected

1. **3D Isometric Cube**: User said "the 3d object makes it confusing" - difficult to interpret positions in 3D space

2. **Inverted Radar Chart (Pokemon stats style)**: User liked the direction but couldn't indicate high/low properly on the axes

3. **Triangle with sliders**: Better but still treated variables as independent dials

### What We Built

**Stepped/Gated Flow Diagram**:
- Problem statement at top: "Revenue is unpredictable"
- Three sequential blocks: Pain → Awareness → Urgency
- Each block has: Number, Title, Definition, Gate Checkpoint
- Connectors with arrows between blocks
- Outcome block at bottom (Viable/Not Viable)
- Interactive control panel to toggle High/Low for each variable
- Diagnosis updates dynamically based on combination

**Visual Treatment**:
- Dark mode (slate/gray background)
- Green = passed (border and subtle background tint)
- Red = failed (border and subtle background tint)
- Numbered circles that change color with pass/fail state
- Cumulative checkpoints showing compounding knowledge after each gate

**Awareness Stages** (added to Awareness block):
- Horizontal row of color-coded pills
- Red → Orange → Yellow → Lime → Green progression
- Shows Schwartz's 5 stages as a spectrum within the Awareness gate

---

## Key Philosophical Positions

### The User's Core Thesis

The user is building a GTM framework grounded in **classical rhetoric** that will become the foundation for an AI-native GTM system. Key beliefs:

1. **Decisions should be codified and traceable**: Every GTM action ties back to the hypothesis and the reasoning behind it

2. **Classical rhetoric provides the structure**: Stasis theory (diagnostic), Five Canons (process), Three Proofs (levers) map to GTM concepts

3. **MEDDPICC becomes table stakes**: AI/automation will handle qualification mechanics; differentiation comes from strategic hypothesis and rhetoric

4. **Pain, Awareness, Urgency are the theoretical primitives**: Everything else is execution

### Frame vs. Reality Distinction

The user drew a sharp distinction between:
- **Your Frame**: Your ICP hypothesis, your positioning, your beliefs about the market
- **Market Reality**: What's actually true about Pain, Awareness, Urgency in the market

The framework is a tool to test whether your frame aligns with market reality. If they don't align, you adjust your frame (ICP, positioning, product) - you can't change market reality.

---

## File Structure

After cleanup, the Learning folder contains:
- `gtm-framework-v3.html` - The interactive visualization
- `GTM-FRAMEWORK-CONTEXT.md` - This document

---

## For the Next Session

### What You Should Do First
1. Read this entire document
2. Open and review `gtm-framework-v3.html` to see the current state
3. Ask clarifying questions BEFORE proposing changes

### What the User Cares About
- Precision in language and concepts
- Grounding in real-world GTM, not abstractions
- Classical rhetoric integration (stasis, canons, proofs)
- Codified, traceable decision-making
- Building toward an AI-native GTM system

### What the User Does NOT Want
- Rehashing decisions already made
- Adding rejected variables (Trust, Fit, Risk, Effort)
- Treating the three variables as independent dials
- Abstract/VC-speak language
- Over-complicating the framework

### Likely Next Steps
- Signal mapping: Making each variable researchable with specific signals
- Rhetoric integration: Mapping classical rhetoric concepts to the framework
- UI refinements: The visualization is functional but may need polish
- Connecting to the broader GTM Factory system (HQ, Researchers, Generators)

---

## Appendix: Rejected Notation

The user explicitly said NOT to use variable notation from a previous document (`gtm-rhetoric-complete.md`) that used symbols like:
- pi (Pain Index)
- alpha (Awareness Level)
- P, W, T, U, R, E (various metrics)

Keep the framework conversational and readable. Use "Pain," "Awareness," "Urgency" - not symbols.

---

## Appendix: Medical Analogy

The user approved a medical analogy that runs through the framework:

- **Pain** = The disease exists (objective, population-level)
- **Awareness** = They know they're sick (subjective, individual-level)
- **Urgency** = The disease is progressing, they're seeking treatment (action-oriented)
- **Viable Market** = There are enough sick, aware, urgent patients to build a practice

This analogy helps clarify:
- Pain is objective (disease exists whether diagnosed or not)
- Awareness is about perception and naming
- Urgency is about action-readiness
- Your job is to find where the disease lives and reach those who are ready for treatment

---

**End of Document**

When continuing work, reference this document and the HTML file. Do not ask the user to re-explain concepts covered here.
