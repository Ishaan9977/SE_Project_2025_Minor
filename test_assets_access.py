"""
Quick test to verify assets are accessible
"""
import os

print("Testing asset files...")
print("-" * 50)

assets_dir = "assets"
files_to_check = [
    "steering_wheel.png",
    "left.png",
    "right.png",
    "up.png",
    "background.jpg"
]

for filename in files_to_check:
    filepath = os.path.join(assets_dir, filename)
    exists = os.path.exists(filepath)
    if exists:
        size = os.path.getsize(filepath)
        print(f"✓ {filename:20s} - EXISTS ({size:,} bytes)")
    else:
        print(f"✗ {filename:20s} - NOT FOUND")

print("-" * 50)
print("\nAssets directory contents:")
if os.path.exists(assets_dir):
    for item in os.listdir(assets_dir):
        filepath = os.path.join(assets_dir, item)
        size = os.path.getsize(filepath)
        print(f"  - {item:25s} ({size:,} bytes)")
else:
    print("  Assets directory not found!")

print("\nCurrent working directory:", os.getcwd())
