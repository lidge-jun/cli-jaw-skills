---
name: ux-researcher
description: "UX research toolkit: data-driven persona generation, customer journey mapping, usability testing frameworks, research synthesis. Use when planning user research, creating personas, mapping journeys, or validating designs."
---

# UX Researcher

Generate personas from data, create journey maps, plan usability tests, and synthesize research into actionable design recommendations.

---

## 1. Persona Generation

### Data Requirements

```json
[{
  "user_id": "user_1",
  "age": 32,
  "usage_frequency": "daily",
  "features_used": ["dashboard", "reports"],
  "primary_device": "desktop",
  "tech_proficiency": 7,
  "pain_points": ["slow loading", "confusing UI"]
}]
```

### Archetypes

| Archetype | Signals | Design Focus |
|-----------|---------|--------------|
| Power User | Daily use, 10+ features | Efficiency, shortcuts, customization |
| Casual User | Weekly use, 3–5 features | Simplicity, guidance, progressive disclosure |
| Business User | Work context, team use | Collaboration, reporting, admin |
| Mobile-First | Mobile primary device | Touch-friendly, offline, speed |

### Validation
- Show persona to 3–5 real users: "Does this sound like you?"
- Cross-check with support tickets
- Verify against analytics data

---

## 2. Journey Mapping

### Scope Definition

| Element | Define |
|---------|--------|
| Persona | Which user type |
| Goal | What they're trying to achieve |
| Start | Trigger that begins journey |
| End | Success criteria |
| Timeframe | Hours / days / weeks |

### Typical B2B SaaS Stages

```
Awareness → Evaluation → Onboarding → Adoption → Advocacy
```

### Each Stage Contains

```
Stage: [Name]
├── Actions: What does user do?
├── Touchpoints: Where do they interact?
├── Emotions: How do they feel? (1–5)
├── Pain Points: What frustrates them?
└── Opportunities: Where can we improve?
```

### Opportunity Priority Score

**Score = Frequency × Severity × Solvability**

---

## 3. Usability Testing

### Research Question Design

| Vague | Testable |
|-------|----------|
| "Is it easy to use?" | "Can users complete checkout in <3 min?" |
| "Do users like it?" | "Will users choose Design A or B?" |
| "Does it make sense?" | "Can users find settings without hints?" |

### Method Selection

| Method | Participants | Duration | Best For |
|--------|--------------|----------|----------|
| Moderated remote | 5–8 | 45–60 min | Deep insights |
| Unmoderated remote | 10–20 | 15–20 min | Quick validation |
| Guerrilla | 3–5 | 5–10 min | Rapid feedback |

### Success Metrics

| Metric | Target |
|--------|--------|
| Completion rate | >80% |
| Time on task | <2× expected |
| Error rate | <15% |
| Satisfaction | >4/5 |

### Task Design

```
SCENARIO: "Imagine you're planning a trip to Paris..."
GOAL: "Book a hotel for 3 nights in your budget."
SUCCESS: "You see the confirmation page."
```

Progression: Warm-up → Core → Secondary → Edge case → Free exploration

---

## 4. Research Synthesis

### Coding Data

Tag each data point:
- `[GOAL]` — What they want to achieve
- `[PAIN]` — What frustrates them
- `[BEHAVIOR]` — What they actually do
- `[CONTEXT]` — When/where they use product
- `[QUOTE]` — Direct user words

### Clustering

Group users by behavioral patterns → identify segments → size each segment:

| Cluster | Users | % | Persona Priority |
|---------|-------|---|-----------------|
| Power Users | 18 | 36% | Primary |
| Business Users | 15 | 30% | Primary |
| Casual Users | 12 | 24% | Secondary |

### Extracting Findings

For each theme:
1. Finding statement
2. Supporting evidence (quotes, data)
3. Frequency (X/Y participants)
4. Business impact
5. Recommendation

### Prioritization

| Factor | Score 1–5 |
|--------|-----------|
| Frequency | How often does this occur? |
| Severity | How much does it hurt? |
| Breadth | How many users affected? |
| Solvability | Can we fix this? |

---

## Quick Reference: Research Methods

| Question Type | Method | Sample Size |
|---------------|--------|-------------|
| "What do users do?" | Analytics, observation | 100+ events |
| "Why do they do it?" | Interviews | 8–15 users |
| "How well can they?" | Usability test | 5–8 users |
| "What do they prefer?" | Survey, A/B test | 50+ users |
| "What do they feel?" | Diary study | 10–15 users |

---

## Usability Issue Severity

| Level | Definition | Action |
|-------|------------|--------|
| 4 — Critical | Prevents task completion | Fix immediately |
| 3 — Major | Significant difficulty | Fix before release |
| 2 — Minor | Causes hesitation | Fix when possible |
| 1 — Cosmetic | Noticed, not problematic | Low priority |
