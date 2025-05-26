import sys
print("Python version:", sys.version)
print("\nPython path:")
for path in sys.path:
    print(f"  - {path}")

print("\nAttempting to import dialogchain...")
try:
    import dialogchain
    print("✅ Successfully imported dialogchain!")
    print(f"Version: {dialogchain.__version__}")
except Exception as e:
    print(f"❌ Error importing dialogchain: {e}")
