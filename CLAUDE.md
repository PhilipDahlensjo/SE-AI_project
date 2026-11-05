# CLAUDE.md

# Part 1: Project context – EnergyPilot

## What it is
EnergyPilot is a proactive agentic home energy optimizer. The resident states an intent
("laundry done by 07:00, keep the cost low") and the agent schedules flexible appliances
(washing machine, dryer, dishwasher, one climate device) to the cheapest suitable hours.
It predicts electricity prices and household usage, proposes a schedule that the resident accepts or changes,
and explains every decision. The final demo for LG is on **Dec. 11, 2026**.

## Two courses, one project
- **CSE406 Software Engineering** (Hanyang University, group "EnergyPilot"): the whole system.
  Members: Emil Ljungdell (Customer), Philip Dahlensjö (User), Jasmin Hansson (Software developer),
  Filip Kadmark (Development manager).
- **ITE351 AI & Applications** (Group 12, AI + SE): a sub-project of the SE system, the forecasting part.
  Members: Filip Kadmark, Philip Dahlensjö, Jasmin Hansson, Lucas Roy-Picard.
- The member lists differ by one person (Emil is SE only, Lucas is AI only). Keep this in mind
  when writing author lists for each course.

## Key design rules
- The language model is optional and only reads free-text intents (R2, a Could). It **never decides start
  times**. A deterministic scheduler calculates them, so the result is testable. Explanations are text
  templates filled with numbers from the scheduler.
- Every plan is checked against hard rules (deadlines, quiet hours, safety) before it runs.
- Manual override by the user always wins.
- Appliances, prices and usage are simulated behind an interface, so real devices can replace them later.

## AI course part (ITE351)
- Idea (submitted Nov. 4): use machine learning to forecast electricity prices and household
  energy use for the coming day, compare a few forecasting methods step by step, and use the
  forecasts to decide when appliances run and how much a household saves.
- Possible data (not decided): hourly day-ahead prices from Nord Pool / ENTSO-E, and the UCI
  "Individual Household Electric Power Consumption" dataset (sub-meters split kitchen and laundry room).
- Note: the UCI data is one French household (2006–2010) and the prices are from other years, so the two
  cannot be joined by date. Use them as typical daily/weekly patterns. Check the data access terms first.
- The repo README is the course blog. Progress is reported there.

## SE course deliverables
- A. Proposal/Requirements: done (Oct. 23/30).
- B. Specification: due **Nov. 6 / Nov. 13**. Written in LaTeX (IEEE template) in `main.tex`
  at the repo root (A and B in one document, compiled to `EnergyPilot_A_B.pdf`).
  Contains: updated intro/requirements, III. Development environment (platform, language and why,
  cost estimate, versions/OS/hardware, commercial cloud such as AWS/GCP is a bonus, existing
  software/algorithms with references, task distribution), IV. Specifications (for each
  requirement: implementation at pseudocode level, diagrams recommended).
- C. Design and D. Implementation are submitted together later. E. Presentation, user guide, installation guide.
- The professor asked us **not** to split requirements into FR/NFR at this stage. `main.tex` uses
  one list, R1–R9, and section IV has one specification per requirement with the same numbering.
  R4 (price and usage forecasting) is the AI course part. `main.tex` is the source of truth for
  the requirements; keep this file in sync if they change.

## Repository and workflow
- One shared GitHub repo for both courses: `SE-AI_project`.
- Now: `README.md` (AI course blog), `main.tex` + `EnergyPilot_A_B.pdf` (SE documents), `CLAUDE.md`.
- Planned when coding starts: `ai/` (forecasting) and `app/` (Streamlit app with scheduler and simulator).
  Don't move `main.tex` without asking the group.
- Stack (decided in B, Nov. 5): Python 3.12 only, Streamlit for the interface, SQLite (one file) for data,
  pandas/NumPy/scikit-learn, pytest. Run locally with `streamlit run app.py`. No login, no Docker, no separate
  frontend or API server; cloud is an optional bonus. Ask the group before adding anything else.
- Work on a branch and open a pull request. Never push directly to `main`. Another member reviews.
- Tasks are tracked as GitHub Issues. Discussions happen in Slack, but decisions are written into the repo.
- All members use Claude Pro. Each member must be able to explain their own part at the demo.

---

# Part 2: Coding guidelines (from Andrej Karpathy, suggested by the professor)

Source: https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
