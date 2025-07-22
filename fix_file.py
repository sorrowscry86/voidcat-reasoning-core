with open(
    r"D:\03_Development\Active_Projects\voidcat-reasoning-core\enhanced_engine.py",
    "r",
    encoding="utf-8",
) as f:
    lines = f.readlines()

# Remove the last 3 lines (the extra triple quotes I added)
lines = lines[:-3]

with open(
    r"D:\03_Development\Active_Projects\voidcat-reasoning-core\enhanced_engine.py",
    "w",
    encoding="utf-8",
) as f:
    f.writelines(lines)

print("Removed extra lines from enhanced_engine.py")
