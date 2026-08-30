"""Command-line expense splitter (scaffold).

Settlement math is not implemented yet. Subcommands parse arguments and
call stub handlers that print "not implemented".
"""

from __future__ import annotations

import argparse
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


def add_participant(name: str) -> Participant:
    """Add a participant to the group.

    Settlement and persistence are not implemented yet.
    """
    print("not implemented")
    return Participant(name=name)


def add_expense(
    payer: str,
    amount: float,
    description: str,
    participants: list[str],
) -> Expense:
    """Record a shared expense.

    Settlement and persistence are not implemented yet.
    """
    print("not implemented")
    return Expense(
        payer=payer,
        amount=amount,
        description=description,
        participants=participants,
    )


def report() -> None:
    """Print a balances and settlements report.

    Settlement math is not implemented yet.
    """
    print("not implemented")


def build_parser() -> argparse.ArgumentParser:
    """Build the argparse CLI with add-participant, add-expense, and report."""
    parser = argparse.ArgumentParser(
        description="Track shared expenses and (later) settle balances.",
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
    """Parse CLI arguments and dispatch to stub handlers."""
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
