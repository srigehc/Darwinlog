import os

input_file = r"C:\Users\212805796\Documents\Automation\Darwin log compare\sbxLog.xml"
output_file = r"C:\Users\212805796\Documents\Automation\Darwin log compare\sbxLog_trimmed.xml"

size_limit = 200 * 1024 * 1024  # 200 MB
written_size = 0

with open(input_file, "rb") as fin, open(output_file, "wb") as fout:
    fout.write(b"<root>\n")
    written_size += len(b"<root>\n")

    for line in fin:
        line_size = len(line)

        if written_size + line_size >= size_limit:
            break

        fout.write(line)
        written_size += line_size

    fout.write(b"\n</root>")

print("✅ Done. Trimmed file created.")