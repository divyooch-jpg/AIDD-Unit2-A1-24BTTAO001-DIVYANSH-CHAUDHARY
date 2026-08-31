# Documentation - Prompt Log, Screenshots, and Reflection

Tool: Cursor (Composer / Agent mode)
Project: Expense Splitter CLI (Option A)

Instructions for use: Paste each prompt below into Cursor exactly as written, in the given order (each depends on the code the previous step produced). After each response, fill in the "Tool response and evaluation" cell, take a screenshot of the Cursor panel showing the prompt and response, and save it into docs/screenshots/step-N.png. Commit after each step - don't do this all in one commit.

## Prompt Log

### Step 1 - Zero-shot (scaffold classes and CLI skeleton)

Exact prompt used:
Create a Python module called expense_splitter.py for a command-line expense splitter. Include: 1. A Participant class with a name and a running balance. 2. An Expense class with fields: payer, amount, description, and a list of participants who share the expense. 3. An argparse-based CLI with three subcommands: add-participant, add-expense, and report. Do not implement the settlement math yet - just the class definitions, the CLI argument parsing, and stub functions that print "not implemented" for now.

Tool response and evaluation: Cursor generated expense_splitter.py with both classes exactly as specified (Participant with name/balance starting at 0.0, Expense with payer/amount/description/participants) and a working argparse CLI with three subcommands, each stubbed with "not implemented" as instructed. Accepted as-is - no edits needed. This was a standard, well-understood scaffolding task, and zero-shot was sufficient because there was no ambiguity in the requirements or project-specific convention to enforce yet.

Why zero-shot was right here: This is a well-known, unambiguous scaffolding task (classes and argparse) that any competent tool produces correctly without needing examples.

### Step 2 - Few-shot (docstring style and JSON report format)

Exact prompt used:
I want every function in expense_splitter.py to follow this exact docstring style. Here are examples. Example 1 is a function called add_participant that takes a name string and returns a Participant, with an Args section describing name and a Returns section describing the return value. Example 2 is a function called calculate_balances that takes a list of expenses and returns a dict mapping participant name to net balance, with matching Args and Returns sections. Example 3 is a function called generate_report that takes balances and returns a JSON-serializable dict with keys "balances" and "settlements", where settlements is a list of objects with from, to, and amount fields. Now rewrite every function and docstring in expense_splitter.py to match this exact style, and make generate_report return JSON matching that shape.

Tool response and evaluation: Cursor rewrote every function in expense_splitter.py to use the exact Args/Returns docstring style shown in the three examples, and generate_report() now returns JSON matching the specified shape: balances and settlements keys. Compared to a plain zero-shot instruction like "add good docstrings," the few-shot examples locked in a specific, consistent structure across the entire file rather than a vague or inconsistent improvement - every function follows the same one-line summary plus Args/Returns pattern. Accepted as-is.

Why few-shot was right here: Output format and project-specific conventions (docstring style, JSON shape) are exactly the case where showing examples locks in consistency that zero-shot instructions alone tend to drift on.

### Step 3 - Chain-of-thought (debug the settlement algorithm)

Exact prompt used:
My calculate_settlements function is supposed to take a dict of participant balances (positive means owed money, negative means owes money) and return the minimum number of payments needed to settle all debts to zero. In some test cases, after all settlements are applied, one participant is left with a balance of one cent instead of exactly zero, even though the input balances summed to zero. Think step by step: 1. Trace through a specific failing example with balances like A equals 100, B equals negative 33.33, C equals negative 33.33, D equals negative 33.34, and show the settlement order your current logic would produce. 2. Identify exactly where floating-point rounding is introduced. 3. Explain why the leftover amount appears on one specific participant rather than being distributed. 4. Propose a fix such as working in integer cents internally, or rounding the final settlement, and show the corrected code. Show your reasoning at each step before giving the final fix.

Tool response and evaluation: Asked Cursor to implement calculate_settlements() and reason step by step about a known floating-point rounding risk before writing the code. Cursor correctly identified that converting dollar amounts to cents via floating-point multiplication can produce a value that rounds incorrectly, and explained that the leftover cent would land on whichever participant's balance is processed last in a naive greedy settlement order. Its fix was to convert all balances to integer cents up front, do the settlement math entirely in integers, and only convert back to dollars for display, nudging by one cent if the totals don't sum to exactly zero. Verified against the example balances: all four participants settled to exactly zero, confirmed by 6 passing unit tests. Accepted as-is - the reasoning correctly identified the root cause before proposing a fix, rather than just patching the symptom.

Why chain-of-thought was right here: This is a genuinely non-trivial debugging task involving tracing an intermittent numeric bug - explicitly asking the tool to reason step by step surfaces the root cause instead of just patching the symptom.

### Step 4 and beyond

Add additional rows here for any further prompts used. Most submissions end up with 6 to 12 rows total across all three techniques.

## Reflection

Using Cursor for this assignment felt noticeably faster than GitHub Copilot for anything beyond single-line completions. Copilot mostly reacts to what I am already typing, while Cursor's agent mode could take a full instruction (like "scaffold this whole module" or "rewrite every docstring in this file") and execute it across the entire file in one shot, including running commands like git commit and git push on its own. That end-to-end agentic workflow, rather than line-by-line suggestions, was the biggest difference.

The tool needed the least correction on the zero-shot scaffolding task, since that was unambiguous. It needed more back-and-forth on file-creation tasks that involved pasting long multi-line content into chat, where the tool sometimes truncated text or misread a placeholder literally instead of waiting for real content - a limitation of copy-pasting through a chat interface rather than a flaw in its reasoning. The chain-of-thought debugging step was the most impressive: it correctly reasoned through a subtle floating-point rounding bug before writing any code, rather than guessing at a fix.

One real limitation I ran into: pushing directly to the main branch required an extra confirmation step, since Cursor treats direct pushes to a protected-looking branch as a higher-risk action needing explicit approval - reasonable for a real team but an extra click for a solo assignment repo.

In a real team setting, I would pick Cursor over Copilot for larger, multi-file refactors or when I want an AI tool to actually execute git operations and verify its own work (like running tests), rather than just suggesting code inline. I would still reach for Copilot for fast, in-the-moment autocomplete while actively writing code myself.
