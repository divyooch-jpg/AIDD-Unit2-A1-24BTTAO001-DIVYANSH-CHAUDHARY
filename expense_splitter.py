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


def _dollars_to_cents(amount: float) -> int:
    """Convert a dollar amount to an integer number of cents.

    Args:
        amount: Dollar amount, which may be a binary float.

    Returns:
        The nearest integer cent value.
    """
    return int(round(amount * 100))


def _cents_to_dollars(cents: int) -> float:
    """Convert an integer cent amount back to dollars.

    Args:
        cents: Amount in whole cents.

    Returns:
        The dollar amount as a float with at most two decimal places of meaning.
    """
    return cents / 100.0


def calculate_settlements(balances: dict[str, float]) -> list[dict]:
    """Compute the minimum payments needed to settle all debts to zero.

    Internally converts balances to integer cents so greedy matching cannot
    leave a leftover $0.01 from binary floating-point representation.

    Args:
        balances: Net balance per participant (positive = owed money, negative = owes money).

    Returns:
        A list of {"from": str, "to": str, "amount": float} payment objects.
    """
    cents: dict[str, int] = {
        name: _dollars_to_cents(amount) for name, amount in balances.items()
    }
    remainder = sum(cents.values())
    if remainder != 0:
        # Rounding each balance independently can be off by a cent. Fold that
        # residue into the participant with the largest absolute balance so
        # the integer ledger still sums to zero before matching.
        anchor = max(cents, key=lambda name: abs(cents[name]))
        cents[anchor] -= remainder

    debtors = sorted(
        [(name, amount) for name, amount in cents.items() if amount < 0],
        key=lambda item: item[1],
    )
    creditors = sorted(
        [(name, amount) for name, amount in cents.items() if amount > 0],
        key=lambda item: item[1],
        reverse=True,
    )

    settlements: list[dict] = []
    i = 0
    j = 0
    while i < len(debtors) and j < len(creditors):
        debtor_name, debtor_cents = debtors[i]
        creditor_name, creditor_cents = creditors[j]
        payment_cents = min(-debtor_cents, creditor_cents)
        if payment_cents > 0:
            settlements.append(
                {
                    "from": debtor_name,
                    "to": creditor_name,
                    "amount": _cents_to_dollars(payment_cents),
                }
            )
        debtor_cents += payment_cents
        creditor_cents -= payment_cents
        debtors[i] = (debtor_name, debtor_cents)
        creditors[j] = (creditor_name, creditor_cents)
        if debtor_cents == 0:
            i += 1
        if creditor_cents == 0:
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
