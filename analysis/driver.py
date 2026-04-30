from analysis.correlation_engine import correlate, write_csv

rows = correlate(r"C:\Users\212805796\Documents\Automation\Darwin log compare\output\normalized_logs.json")
write_csv(rows, r"C:\Users\212805796\Documents\Automation\Darwin log compare\output\correlation_table.csv")

print("✅ Correlation table generated:", len(rows), "rows")

