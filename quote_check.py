def find_quote_issues(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")

    # Find all triple quotes
    triple_quote_positions = []
    for i, line in enumerate(lines):
        if '"""' in line:
            count = line.count('"""')
            for j in range(count):
                triple_quote_positions.append((i + 1, line.strip()))

    print("Triple quote positions:")
    for pos, line in triple_quote_positions:
        print(f"  Line {pos}: {line}")

    print(f"\nTotal triple quotes: {len(triple_quote_positions)}")
    if len(triple_quote_positions) % 2 != 0:
        print("WARNING: Odd number of triple quotes - likely unclosed docstring!")

    return len(triple_quote_positions) % 2 == 0


if __name__ == "__main__":
    filename = (
        r"D:\03_Development\Active_Projects\voidcat-reasoning-core\enhanced_engine.py"
    )
    find_quote_issues(filename)
