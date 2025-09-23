#!/usr/bin/env python3
import argparse

def calculate_monthly_payment(loan_amount, annual_rate, years=30):
    """Calculate monthly payment for a fixed-rate loan."""
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12

    if monthly_rate == 0:
        return loan_amount / num_payments

    payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
              ((1 + monthly_rate) ** num_payments - 1)
    return payment

def breakdown_first_month(loan_amount, annual_rate, monthly_payment):
    """Breakdown of first month payment into interest and principal."""
    monthly_rate = annual_rate / 100 / 12
    interest = loan_amount * monthly_rate
    principal = monthly_payment - interest
    return interest, principal

def main():
    parser = argparse.ArgumentParser(description="Loan Payment Calculator (30-year fixed)")
    parser.add_argument("loan_amount", type=float, help="Loan amount (e.g., 300000)")
    parser.add_argument("interest_rate", type=float, help="Annual interest rate in % (e.g., 6.5)")
    args = parser.parse_args()

    loan_amount = args.loan_amount
    interest_rate = args.interest_rate

    monthly_payment = calculate_monthly_payment(loan_amount, interest_rate)
    interest, principal = breakdown_first_month(loan_amount, interest_rate, monthly_payment)

    print(f"\nLoan Amount: ${loan_amount:,.2f}")
    print(f"Interest Rate: {interest_rate:.3f}%")
    print(f"Term: 30 years (360 months)\n")

    print(f"Monthly Payment: ${monthly_payment:,.2f}")
    print(f"  - Interest (Month 1): ${interest:,.2f}")
    print(f"  - Principal (Month 1): ${principal:,.2f}")

if __name__ == "__main__":
    main()

