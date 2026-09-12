# Andrej Karpathy Behavioral Guidelines & Clean Code Standards

Integrated from [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) into **Sentinel AI (SIH26206)**.

## Core Purpose

Large Language Models (LLMs) and automated agents frequently suffer from common pitfalls:
1. **Making wrong assumptions silently** and running ahead without checking.
2. **Overcomplicating code**, adding speculative configurability, and bloating abstractions.
3. **Making non-surgical changes**, deleting or changing comments/code as unintended side effects.
4. **Weak or absent verification**, declaring tasks 'done' without running test suites.

To eliminate these failure modes across Sentinel AI's development and evaluation, the following four principles govern all code modifications.

---

## The Four Principles

### 1. Think Before Coding
**Don't assume. Don't hide confusion. Surface tradeoffs.**
- State assumptions explicitly before modifying files.
- If multiple interpretations exist, present them rather than guessing.
- Push back when a simpler, safer approach exists.
- If requirements or contracts are unclear, stop, name what is confusing, and ask.

### 2. Simplicity First
**Minimum code that solves the problem. Nothing speculative.**
- Implement only what was requested—no speculative features.
- Avoid single-use abstractions or premature generalizations.
- No unnecessary error handling for impossible edge cases.
- If 200 lines could be 50 lines, simplify it.
- *Test:* Would a senior staff engineer say this is overcomplicated? If yes, simplify.

### 3. Surgical Changes
**Touch only what you must. Clean up only your own mess.**
- Do not modify adjacent code, comments, or formatting unless directly related to the task.
- Match existing architectural style and conventions.
- When modifications create orphans, clean up unused imports, variables, and dead functions.
- Every changed line must directly trace to the task requirements.

### 4. Goal-Driven Execution
**Define success criteria. Loop until verified.**
- Transform every development task into verifiable success criteria (tests-first).
- Multi-step tasks state a brief plan:
  1. [Step] -> verify: [check]
  2. [Step] -> verify: [check]
  3. [Step] -> verify: [check]
- Run the full 125-test suite (pytest) before and after changes to ensure zero regressions.

---

## Application & Repository Enforcement

- CLAUDE.md: Universal instructions for Claude Code and related tools.
- GEMINI.md & AGENTS.md: Workspace rules discovered and enforced by Antigravity / Gemini agents.
- .cursor/rules/karpathy-guidelines.mdc & CURSOR.md: Editor rules for Cursor IDE.
- .agents/skills/karpathy-guidelines/SKILL.md: Discoverable agent skill for Antigravity.
- skills/karpathy-guidelines/SKILL.md: Discoverable skill for MCP / open agent runners.

## Audit & Verification Results

1. **Syntax & AST Compilation**: All 63 Python files compile with 0 syntax errors.
2. **Encoding & Byte Standards**: Stripped non-standard UTF-8 BOM (ï»¿) from 	ests/test_ui_evidence_badges.py.
3. **Import Sanitization**: Surgically removed all orphaned and unused imports from deploy.py, src/camera.py, src/core/occupancy_mapping.py, src/decision/forecast.py, src/decision/safety.py, src/decision/scenario.py, and test suites.
4. **Test Suite Execution**: 125 of 125 tests passing (100% pass rate).
