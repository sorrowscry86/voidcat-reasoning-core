import ast


def check_syntax(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        # Try to parse the AST
        ast.parse(content)
        print("Syntax is valid")
        return True

    except SyntaxError as e:
        print("Syntax Error:")
        print(f"  Line {e.lineno}: {e.text}")
        print(f"  Error: {e.msg}")
        if e.offset:
            print(f"  Position: {' ' * (e.offset-1)}^")
        return False
    except Exception as e:
        print(f"Other error: {e}")
        return False


if __name__ == "__main__":
    filename = (
        r"D:\03_Development\Active_Projects\voidcat-reasoning-core\enhanced_engine.py"
    )
    check_syntax(filename)
