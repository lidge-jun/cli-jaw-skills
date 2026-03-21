---
name: brainstorming
description: Explore user intent, requirements, and design before implementation. Recommended before creative work such as new features or component design.
---

# Brainstorming Ideas Into Designs

## Goal

Clarify requirements and produce a design before jumping to code. Reduces wasted work from unexamined assumptions.

## Design Review

Present a design and get user feedback before implementation. The design can be brief for simple tasks. For trivial changes (rename, typo fix), skip directly to implementation.

## Checklist

1. **Explore project context** — check files, docs, recent commits
2. **Ask clarifying questions** — one at a time; prefer multiple-choice over open-ended
3. **Propose 2-3 approaches** — with trade-offs; lead with your recommendation
4. **Present design** — scale detail to complexity; check after each section
5. **Save design doc** — `docs/plans/YYYY-MM-DD-<topic>-design.md`
6. **Transition** — invoke writing-plans skill to create implementation plan

## Guidelines

- Scale sections to complexity — a few sentences if straightforward, more if nuanced
- Cover: architecture, components, data flow, error handling, testing
- Apply YAGNI — remove unnecessary features from designs

## After Approval

1. Save the design to `docs/plans/YYYY-MM-DD-<topic>-design.md`
2. Commit the design document
3. Invoke writing-plans to create the implementation plan
