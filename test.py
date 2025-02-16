import random

def generate_txt_file(rows, cols, filename="output.txt"):
    with open(filename, "w") as f:
        for _ in range(rows):
            line = "\t".join(str(random.randint(0, 65535)) for _ in range(cols))
            f.write(line + "\n")

if __name__ == "__main__":
    # Set desired values directly
    num_rows = 300  # Example: 10 rows
    num_cols = 2700   # Example: 5 columns
    file_name = "test.txt"

    generate_txt_file(num_rows, num_cols, file_name)
    print(f"File '{file_name}' generated successfully.")
