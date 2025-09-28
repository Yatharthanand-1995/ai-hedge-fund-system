#!/usr/bin/env python3
"""
Copy essential components from trading_platform to ai_hedge_fund_system
"""

import os
import shutil
from pathlib import Path

def main():
    # Define paths
    source_base = Path("/Users/yatharthanand/trading_platform/trading_platform")
    dest_base = Path("/Users/yatharthanand/ai_hedge_fund_system")

    # Create src structure
    src_dir = dest_base / "src"
    src_dir.mkdir(exist_ok=True)

    # Copy cache module
    cache_dir = src_dir / "cache"
    cache_dir.mkdir(exist_ok=True)

    # Copy stock_cache.py
    src_cache_file = source_base / "src" / "cache" / "stock_cache.py"
    if src_cache_file.exists():
        shutil.copy2(src_cache_file, cache_dir / "stock_cache.py")
        print(f"✅ Copied stock_cache.py")
    else:
        print(f"❌ Missing: {src_cache_file}")

    # Create __init__.py files
    (src_dir / "__init__.py").touch()
    (cache_dir / "__init__.py").touch()
    print(f"✅ Created __init__.py files for src structure")

    # Copy core module
    core_dir = src_dir / "core"
    core_dir.mkdir(exist_ok=True)

    # Copy proven_signal_engine.py
    src_core_file = source_base / "src" / "core" / "proven_signal_engine.py"
    if src_core_file.exists():
        shutil.copy2(src_core_file, core_dir / "proven_signal_engine.py")
        print(f"✅ Copied proven_signal_engine.py")
    else:
        print(f"❌ Missing: {src_core_file}")

    (core_dir / "__init__.py").touch()

    # Copy data module
    data_dir = src_dir / "data"
    data_dir.mkdir(exist_ok=True)

    # Copy realtime_provider.py
    src_data_file = source_base / "src" / "data" / "realtime_provider.py"
    if src_data_file.exists():
        shutil.copy2(src_data_file, data_dir / "realtime_provider.py")
        print(f"✅ Copied realtime_provider.py")
    else:
        print(f"❌ Missing: {src_data_file}")

    (data_dir / "__init__.py").touch()

    # Copy api module
    api_dir = src_dir / "api"
    api_dir.mkdir(exist_ok=True)

    # Copy stock_picker_api.py
    src_api_file = source_base / "src" / "api" / "stock_picker_api.py"
    if src_api_file.exists():
        shutil.copy2(src_api_file, api_dir / "stock_picker_api.py")
        print(f"✅ Copied stock_picker_api.py")
    else:
        print(f"❌ Missing: {src_api_file}")

    (api_dir / "__init__.py").touch()

    print(f"\n✅ Migration completed successfully!")
    print(f"Created src/ module structure with essential components")

if __name__ == "__main__":
    main()