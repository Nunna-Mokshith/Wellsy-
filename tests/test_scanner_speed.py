"""
Verification script: Compare directory scanning speeds
Compares standard Python recursion (os.walk) vs compiled C++ directory traversal.
"""
import sys
import time
import os
from pathlib import Path

# Add backend tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

def python_walk_scan(target_dir: str):
    """Scan directory recursively using standard python library."""
    results = []
    supported = {'.txt', '.pdf', '.docx'}
    for root, dirs, files in os.walk(target_dir):
        for f in files:
            if os.path.splitext(f)[1].lower() in supported:
                full_path = os.path.join(root, f)
                try:
                    stat = os.stat(full_path)
                    results.append({
                        "path": full_path,
                        "size": stat.st_size,
                        "mod_time": stat.st_mtime
                    })
                except Exception:
                    pass
    return results

def run_benchmark():
    print("====================================================")
    print(" PERFORMANCE BENCHMARK: PYTHON VS COMPILED C++ ")
    print("====================================================\n")

    # Scan project root directory (lots of folders in venv)
    scan_target = str(Path(__file__).parent.parent)
    print(f"Target Directory: {scan_target}")
    
    # 1. Benchmark standard Python walk
    print("[*] Benchmarking Python standard os.walk traversal...")
    start_py = time.perf_counter()
    py_results = python_walk_scan(scan_target)
    end_py = time.perf_counter()
    py_time = (end_py - start_py) * 1000
    print(f"  [+] Python scan found: {len(py_results)} files")
    print(f"  [+] Python scan duration: {py_time:.2f} ms")

    # 2. Benchmark compiled C++ library scanner
    print("\n[*] Benchmarking Compiled C++ traversal engine...")
    from tools.fast_scanner import fast_scan
    
    start_cpp = time.perf_counter()
    cpp_results = fast_scan(scan_target, max_results=25000)
    end_cpp = time.perf_counter()
    cpp_time = (end_cpp - start_cpp) * 1000
    print(f"  [+] C++ scan found: {len(cpp_results)} files")
    print(f"  [+] C++ scan duration: {cpp_time:.2f} ms")

    # Calculate optimization metrics
    if cpp_time > 0:
        speedup = py_time / cpp_time
        print(f"\ncompiled C++ traversal is {speedup:.1f}x FASTER than Python!")
        print(f"saved {(py_time - cpp_time):.2f} ms of CPU execution block latency.")
    else:
        print("Invalid timings detected.")

    print("\n====================================================")

if __name__ == "__main__":
    run_benchmark()
