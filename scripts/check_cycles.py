import os
import sys
import importlib
import pkgutil
import traceback

def check_cycles(package_name):
    """
    Recursively imports all submodules in a package to trigger
    any import-time circular dependency errors.
    """
    print(f"Checking for cycles in package: {package_name}...")
    
    # Add project root to path
    sys.path.insert(0, os.getcwd())
    
    # Configure Django if needed (since models import require it)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    import django
    try:
        django.setup()
    except Exception as e:
        print(f"Django setup failed: {e}")
        return False

    failed = False
    checked_count = 0
    
    # recursive walk
    package = importlib.import_module(package_name)
    path = package.__path__
    prefix = package_name + "."

    for module_info in pkgutil.walk_packages(path, prefix):
        module_name = module_info.name
        try:
            importlib.import_module(module_name)
            checked_count += 1
        except ImportError as e:
            # Check if it looks like a circular import
            msg = str(e)
            if "circular import" in msg or "partially initialized" in msg:
                print(f"❌ CIRCULAR DEPENDENCY DETECTED in {module_name}: {e}")
                failed = True
            else:
                print(f"⚠️ Import Error in {module_name}: {e}")
                failed = True # Treat as failure
        except Exception as e:
            print(f"❌ Usage Error in {module_name}: {e}")
            traceback.print_exc()
            failed = True

    if not failed:
        print(f"✅ No circular dependencies found in {checked_count} modules.")
    else:
        print("❌ Cycle check FAILED.")
        
    return not failed

if __name__ == "__main__":
    success = check_cycles("tenants")
    sys.exit(0 if success else 1)
