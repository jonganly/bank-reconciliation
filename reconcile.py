import pandas as pd

ledger = pd.read_csv("data/ledger.csv", parse_dates=["Date"])
bank = pd.read_csv("data/bank_statement.csv", parse_dates=["Date"])

DATE_TOLERANCE_DAYS = 5

# Track which bank rows have already been paired up, so the same bank
# transaction can't get matched to two different ledger transactions.
bank_matched = [False] * len(bank)

matched_pairs = []
ledger_only = []

for ledger_idx, ledger_row in ledger.iterrows():
    found_match = False
    for bank_idx, bank_row in bank.iterrows():
        if bank_matched[bank_idx]:
            continue  # already paired with something else, skip it

        same_amount = round(ledger_row["Amount"], 2) == round(bank_row["Amount"], 2)
        days_apart = abs((ledger_row["Date"] - bank_row["Date"]).days)
        close_enough_dates = days_apart <= DATE_TOLERANCE_DAYS

        if same_amount and close_enough_dates:
            matched_pairs.append({
                "Date": ledger_row["Date"],
                "Ledger Description": ledger_row["Description"],
                "Bank Description": bank_row["Description"],
                "Amount": ledger_row["Amount"],
                "Days Apart": days_apart,
            })
            bank_matched[bank_idx] = True
            found_match = True
            break

    if not found_match:
        ledger_only.append(ledger_row)

bank_only = bank[[not m for m in bank_matched]]

print(f"Matched: {len(matched_pairs)}")
print(f"Ledger only: {len(ledger_only)}")
print(f"Bank only: {len(bank_only)}")
print("\n--- Ledger only (recorded but not on the bank) ---")
for row in ledger_only:
    print(row["Date"].date(), "|", row["Description"], "|", row["Amount"])

print("\n--- Bank only (on the bank but not recorded) ---")
print(bank_only[["Date", "Description", "Amount"]].to_string(index=False))

print("\n--- Matched pairs with the biggest date gaps ---")
matched_df = pd.DataFrame(matched_pairs)
print(matched_df.sort_values("Days Apart", ascending=False).head(5).to_string(index=False))
ledger_only_df = pd.DataFrame(ledger_only)
bank_only = bank_only.copy()

matched_df["Date"] = matched_df["Date"].dt.strftime("%d/%m/%Y")
ledger_only_df["Date"] = ledger_only_df["Date"].dt.strftime("%d/%m/%Y")
bank_only["Date"] = bank_only["Date"].dt.strftime("%d/%m/%Y")

def autofit_columns(worksheet, dataframe):
    for i, column in enumerate(dataframe.columns):
        max_length = len(str(column))
        for value in dataframe[column]:
            max_length = max(max_length, len(str(value)))
        col_letter = worksheet.cell(row=1, column=i + 1).column_letter
        worksheet.column_dimensions[col_letter].width = max_length + 2

with pd.ExcelWriter("reconciliation_report.xlsx") as writer:
    matched_df.to_excel(writer, sheet_name="Matched", index=False)
    autofit_columns(writer.sheets["Matched"], matched_df)

    ledger_only_df.to_excel(writer, sheet_name="Ledger Only", index=False)
    autofit_columns(writer.sheets["Ledger Only"], ledger_only_df)

    bank_only.to_excel(writer, sheet_name="Bank Only", index=False)
    autofit_columns(writer.sheets["Bank Only"], bank_only)

print("\nReport written to reconciliation_report.xlsx")