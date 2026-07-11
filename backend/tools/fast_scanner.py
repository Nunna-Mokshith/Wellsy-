"""
Wellsy Fast File Traversal Binding Core
Loads compiled scanner.dll and binds functions to Python types using ctypes.
"""
import ctypes
import os
from pathlib import Path
from typing import List, Dict, Any

# Map structure exactly to C++ struct layout
class FileMetadata(ctypes.Structure):
    _fields_ = [
        ("path", ctypes.c_char * 512),
        ("mod_time", ctypes.c_double),
        ("size", ctypes.c_int64)
    ]

# Setup dll loader
DLL_PATH = Path(__file__).parent / "scanner.dll"
_scanner_dll = None

def get_scanner_dll():
    """Lazy load compiled shared library."""
    global _scanner_dll
    if _scanner_dll is None:
        if not DLL_PATH.exists():
            raise FileNotFoundError(f"Scanner library not found at: {DLL_PATH}")
        _scanner_dll = ctypes.CDLL(str(DLL_PATH))
        # Configure function arguments and return types
        _scanner_dll.scan_directory.argtypes = [
            ctypes.c_char_p,
            ctypes.POINTER(FileMetadata),
            ctypes.c_int
        ]
        _scanner_dll.scan_directory.restype = ctypes.c_int
    return _scanner_dll


def fast_scan(directory_path: str, max_results: int = 5000) -> List[Dict[str, Any]]:
    """Recursively scan a directory using compiled C++ shared library traversal.
    
    Returns lists containing path names, sizes, and modification timestamps.
    """
    dll = get_scanner_dll()
    
    # Initialize output array buffer in memory
    results_array = (FileMetadata * max_results)()
    
    # Run scan
    count = dll.scan_directory(
        directory_path.encode('utf-8', errors='replace'),
        results_array,
        max_results
    )
    
    if count < 0:
        if count == -1:
            raise FileNotFoundError(f"Target directory invalid or not exists: {directory_path}")
        raise RuntimeError(f"C++ Traversal library failed with internal error code: {count}")
        
    outputs = []
    for i in range(count):
        entry = results_array[i]
        # Decode path string safely
        path_str = entry.path.decode('utf-8', errors='replace')
        outputs.append({
            "path": path_str,
            "size": entry.size,
            "mod_time": entry.mod_time
        })
        
    return outputs
