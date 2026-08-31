"""Command-line expense splitter."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field


@dataclass
class Participant:
    """A person in the expense group with a running balance."""

    name: str
    balance: float = 0.0


@dataclass
class Expense:
    """A shared expense paid by one participant and split among others."""

    payer: str
    amount: float
    description: str
    participants: list[str] = field(default_factory=list)


_participants: dict[str, Participant] = {}
_expenses: list[Expense] = []


def add_participant(name: str) -> Participant:
    """Add a new participant to the group.

    Args:
        name: Display name of the participant.

    Returns:
        The newly created Participant instance.
    """
    participant = Participant(name=name)
    _participants[name] = participant
    return participant


def add_expense(
    payer: str,
    amount: float,
    description: str,
    participants: list[str],
) -> Expense:
    """Record a shared expense paid by one person and split among others.

    Args:
        payer: Name of the person who paid.
        amount: Amount paid.
        description: What the expense was for.
        participants: Names of people who share this expense.

    Returns:
        The newly created Expense instance.
    """
    expense = Expense(
        payer=payer,
        amount=amount,
        description=description,
        participants=list(participants),
    )
    _expenses.append(expense)
    if payer not in _participants:
        add_participant(payer)
    for name in expense.participants:
        if name not in _participants:
            add_participant(name)
    return expense


def calculate_balances(expenses: list[Expense]) -> dict[str, float]:
    """Compute each participant's net balance.

    Args:
        expenses: All recorded expenses to include in the calculation.

    Returns:
        A mapping of participant name to net balance (positive = owed money, negative = owes money).
    """
    balances: dict[str, float] = {name: 0.0 for name in _participants}
    for expense in expenses:
        if not expense.participants:
            continue
        share = expense.amount / len(expense.participants)
        balances.setdefault(expense.payer, 0.0)
        balances[expense.payer] += expense.amount
        for name in expense.participants:
            balances.setdefault(name, 0.0)
            balances[name] -= share
    for name, participant in _participants.items():
        participant.balance = balances.get(name, 0.0)
    return balances


def calculate_settlements(balances: dict[str, float]) -> list[dict]:
    """Compute payments that settle all balances to zero.

    Args:
        balances: Net balance per participant (positive = owed money, negative = owes money).

    Returns:
        A list of {"from": str, "to": str, "amount": float} payment objects.
    """
    remaining = dict(balances)
    debtors = sorted(
        [(name, amount) for name, amount in remaining.items() if amount < 0],
        key=lambda item: item[1],
    )
    creditors = sorted(
        [(name, amount) for name, amount in remaining.items() if amount > 0],
        key=lambda item: item[1],
        reverse=True,
    )
    settlements: list[dict] = []
    i = 0
    j = 0
    while i < len(debtors) and j < len(creditors):
        debtor_name, debtor_amount = debtors[i]
        creditor_name, creditor_amount = creditors[j]
        amount = min(-debtor_amount, creditor_amount)
        if amount > 0:
            settlements.append(
                {"from": debtor_name, "to": creditor_name, "amount": amount}
            )
        debtor_amount += amount
        creditor_amount -= amount
        debtors[i] = (debtor_name, debtor_amount)
        creditors[j] = (creditor_name, creditor_amount)
        if abs(debtor_amount) < 1e-9:
            i += 1
        if abs(creditor_amount) < 1e-9:
            j += 1
    return settlements


def generate_report(balances: dict[str, float]) -> dict:
    """Build a JSON-serializable report of balances and settlements.

    Args:
        balances: Net balance per participant.

    Returns:
        A dict with keys "balances" (dict) and "settlements" (list of {"from": str, "to": str, "amount": float}).
    """
    return {
        "balances": dict(balances),
        "settlements": calculate_settlements(balances),
    }


def report() -> dict:
    """Print a JSON report of current balances and settlements.

    Returns:
        The JSON-serializable report dict that was printed.
    """
    balances = calculate_balances(_expenses)
    payload = generate_report(balances)
    print(json.dumps(payload, indent=2))
    return payload


def build_parser() -> argparse.ArgumentParser:
    """Build the argparse CLI with add-participant, add-expense, and report.

    Returns:
        The configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Track shared expenses and settle balances.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_participant_parser = subparsers.add_parser(
        "add-participant",
        help="Add a person to the expense group.",
    )
    add_participant_parser.add_argument(
        "--name",
        required=True,
        help="Participant name.",
    )

    add_expense_parser = subparsers.add_parser(
        "add-expense",
        help="Record an expense paid by one person and shared by others.",
    )
    add_expense_parser.add_argument(
        "--payer",
        required=True,
        help="Name of the person who paid.",
    )
    add_expense_parser.add_argument(
        "--amount",
        required=True,
        type=float,
        help="Amount paid.",
    )
    add_expense_parser.add_argument(
        "--description",
        required=True,
        help="What the expense was for.",
    )
    add_expense_parser.add_argument(
        "--participants",
        required=True,
        nargs="+",
        help="Names of people who share this expense (including the payer if they share).",
    )

    subparsers.add_parser(
        "report",
        help="Show balances and suggested settlements.",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    """Parse CLI arguments and dispatch to the matching handler.

    Args:
        argv: Optional argument list. If omitted, sys.argv is used.

    Returns:
        None.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "add-participant":
        add_participant(args.name)
    elif args.command == "add-expense":
        add_expense(
            payer=args.payer,
            amount=args.amount,
            description=args.description,
            participants=args.participants,
        )
    elif args.command == "report":
        report()


if __name__ == "__main__":
    main()
