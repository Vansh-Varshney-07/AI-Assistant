"""
wayfinder/workers/run_tests.py
------------------------------
Lightweight offline test runner for all Wayfinder worker contract tests.
Executes test classes and test functions without external dependencies.
"""
import importlib
from pathlib import Path
import sys

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

def main() -> int:
    root = Path(__file__).parent
    test_files = sorted(root.glob("*/test_worker.py"))
    
    total = 0
    passed = 0
    failed = 0
    failures = []

    print(f"Found {len(test_files)} worker test suites under {root}.\n")

    for tf in test_files:
        worker_dir = tf.parent.name
        mod_name = f"wayfinder.workers.{worker_dir}.test_worker"
        print(f"--- Running {worker_dir} ({mod_name}) ---")
        try:
            mod = importlib.import_module(mod_name)
        except Exception as e:
            print(f"  [ERROR] Could not import {mod_name}: {e}")
            failed += 1
            failures.append((mod_name, "import", str(e)))
            continue

        # Run test classes
        for attr_name in dir(mod):
            obj = getattr(mod, attr_name)
            if isinstance(obj, type) and attr_name.startswith("Test"):
                try:
                    instance = obj()
                except Exception as e:
                    print(f"  [FAIL] Failed to instantiate {attr_name}: {e}")
                    failed += 1
                    failures.append((mod_name, attr_name, str(e)))
                    continue

                for method_name in dir(instance):
                    if method_name.startswith("test_"):
                        total += 1
                        try:
                            getattr(instance, method_name)()
                            passed += 1
                            print(f"  [PASS] {attr_name}.{method_name}")
                        except Exception as e:
                            failed += 1
                            print(f"  [FAIL] {attr_name}.{method_name}: {e}")
                            failures.append((mod_name, f"{attr_name}.{method_name}", str(e)))

            elif callable(obj) and attr_name.startswith("test_"):
                total += 1
                try:
                    obj()
                    passed += 1
                    print(f"  [PASS] {attr_name}")
                except Exception as e:
                    failed += 1
                    print(f"  [FAIL] {attr_name}: {e}")
                    failures.append((mod_name, attr_name, str(e)))

        print()

    print(f"Summary: {total} tests run, {passed} passed, {failed} failed.")
    if failures:
        print("\nFailures:")
        for suite, name, err in failures:
            print(f"  - {suite} -> {name}: {err}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
