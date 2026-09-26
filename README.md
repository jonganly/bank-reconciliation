# Bank Reconciliation Tool

A small Python tool that automates part of a manual bank reconciliation process
I carried out during my internships at RBK Chartered Accountants — checking a
bank statement against a company's own ledger to find matching transactions,
timing differences, and errors.

## The problem

At the end of each accounting period, a business needs to confirm that what
the bank says happened matches what's recorded in its own books. In practice
the two records rarely agree perfectly: a cheque can take a few days to
clear, an amount can be mistyped, or a bank fee can be charged that was never
separately recorded. Traditionally this is checked by a person, line by line.
This tool automates that check.

## Approach

- Two transaction records are loaded with pandas: a bank statement and the
  company's ledger (both synthetic data I generated myself — no real client
  information was used).
- Each ledger transaction is compared against the bank statement, looking for
  one with the same amount and a date within 5 days (a cheque or direct
  debit commonly takes a few days to clear).
- Every transaction ends up in one of three groups: matched, ledger-only
  (recorded but not yet on the bank), or bank-only (on the bank but not
  recorded).
- Results are exported to `reconciliation_report.xlsx`, one sheet per group.

## How to run it

1. Clone the repo and install dependencies:
```
   pip install -r requirements.txt
```
2. Run the script:
```
   python reconcile.py
```

3. Open `reconciliation_report.xlsx` in the project folder.

## Limitations

- Starts from clean CSV data, not a real bank statement PDF — a real
  deployment would need a separate step to extract structured data from a
  statement document.
- Matching is a simple one-pass process: once a bank transaction is matched,
  it can't be reused, but two unrelated transactions with the same amount
  inside the date window could be paired incorrectly. Transaction
  descriptions aren't used when deciding a match.
- Assumes one bank account and one currency.

## What I'd add next

- A parsing step to read real PDF bank statements.
- Using the transaction description as a tiebreaker when more than one bank
  transaction matches on amount and date.
- A command-line summary (counts and total value per group) so the result
  doesn't require opening Excel.