import sys
print("Python version:", sys.version)
print("\nPython path:")
for path in sys.path:
    print(f"  - {path}")

print("\nAttempting to import camel_router...")
try:
    import camel_router
    print("✅ Successfully imported camel_router!")
    print(f"Version: {camel_router.__version__}")
except Exception as e:
    print(f"❌ Error importing camel_router: {e}")
