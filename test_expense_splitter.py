"""Tests for the expense splitter module."""

from __future__ import annotations

import pytest

from expense_splitter import (
    Expense,
    Participant,
    _expenses,
    _participants,
    add_participant,
    calculate_balances,
    calculate_settlements,
    generate_report,
)


@pytest.fixture(autouse=True)
def _reset_store() -> None:
    """Clear in-memory participants and expenses between tests."""
    _participants.clear()
    _expenses.clear()


def test_add_participant_name_and_zero_balance() -> None:
    participant = add_participant("Alice")

    assert isinstance(participant, Participant)
    assert participant.name == "Alice"
    assert participant.balance == 0.0


def test_calculate_balances_two_person_expense() -> None:
    add_participant("Alice")
    add_participant("Bob")
    expenses = [
        Expense(
            payer="Alice",
            amount=10.0,
            description="lunch",
            participants=["Alice", "Bob"],
        )
    ]

    balances = calculate_balances(expenses)

    assert balances["Alice"] == pytest.approx(5.0)
    assert balances["Bob"] == pytest.approx(-5.0)


def _apply_settlements(
    balances: dict[str, float],
    settlements: list[dict],
) -> dict[str, float]:
    remaining = dict(balances)
    for payment in settlements:
        remaining[payment["from"]] += payment["amount"]
        remaining[payment["to"]] -= payment["amount"]
    return remaining


def test_calculate_settlements_zeros_uneven_four_person_split() -> None:
    balances = {
        "Alice": 100.00,
        "Bob": -33.33,
        "Carol": -33.33,
        "Dave": -33.34,
    }

    settlements = calculate_settlements(balances)
    remaining = _apply_settlements(balances, settlements)

    assert settlements
    for payment in settlements:
        assert set(payment) == {"from", "to", "amount"}
        assert payment["amount"] > 0
    for name, amount in remaining.items():
        assert round(amount, 2) == 0.0, f"{name} left with {amount}"


def test_calculate_settlements_single_zero_balance() -> None:
    settlements = calculate_settlements({"Alice": 0.0})

    assert settlements == []


def test_calculate_settlements_empty_balances() -> None:
    settlements = calculate_settlements({})

    assert settlements == []


def test_generate_report_has_balances_and_settlements_keys() -> None:
    report = generate_report({"Alice": 5.0, "Bob": -5.0})

    assert set(report.keys()) == {"balances", "settlements"}
    assert report["balances"] == {"Alice": 5.0, "Bob": -5.0}
    assert isinstance(report["settlements"], list)
