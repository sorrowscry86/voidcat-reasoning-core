def find_unmatched_quotes(filename):
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    in_multiline_docstring = False
    docstring_start_line = None

    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()

        # Count triple quotes in this line
        triple_quote_count = line.count('"""')

        if triple_quote_count > 0:
            print(f"Line {line_num}: {triple_quote_count} triple quotes - {stripped}")

            # Handle different cases
            if triple_quote_count == 1:
                if not in_multiline_docstring:
                    # Starting a multiline docstring
                    in_multiline_docstring = True
                    docstring_start_line = line_num
                    print(f"  -> Starting multiline docstring")
                else:
                    # Ending a multiline docstring
                    in_multiline_docstring = False
                    print(
                        f"  -> Ending multiline docstring (started at line {docstring_start_line})"
                    )
                    docstring_start_line = None
            elif triple_quote_count == 2:
                # Single-line docstring
                print(f"  -> Single-line docstring")
            elif triple_quote_count % 2 == 1:
                # Odd number > 1, complex case
                print(f"  -> Complex case with {triple_quote_count} quotes")

    if in_multiline_docstring:
        print(
            f"\nERROR: Unclosed multiline docstring starting at line {docstring_start_line}"
        )
        return False
    else:
        print(f"\nAll docstrings appear to be properly closed")
        return True


if __name__ == "__main__":
    filename = (
        r"D:\03_Development\Active_Projects\voidcat-reasoning-core\enhanced_engine.py"
    )
    find_unmatched_quotes(filename)
