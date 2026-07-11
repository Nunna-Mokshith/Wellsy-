"""
Wellsy Sandbox & RAG Verification Suite
Runs path injection tests to confirm sandbox blocking and populates RAG database to check vector matching.
"""
import sys
from pathlib import Path

# Add backend tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

def run_tests():
    print("====================================================")
    print(" RUNNING WELLSY SECURE MCP & RAG VERIFICATION ")
    print("====================================================\n")

    # 1. Test Sandbox Gate
    print("[*] Test 1: Verifying Sandbox Path Gate...")
    from mcp_server import check_path_sandbox
    
    # Valid Sandbox Paths
    try:
        valid_path = Path("D:/Wellsy/storage/test_doc.txt")
        check_path_sandbox(str(valid_path))
        print("  [+] Valid Sandbox Path Check: PASSED")
    except PermissionError as pe:
        print(f"  [-] Valid Sandbox Path Check: FAILED ({pe})")

    # Path Traversal Attempt
    try:
        invalid_path = Path("D:/Wellsy/storage/../../Windows/system32/cmd.exe")
        check_path_sandbox(str(invalid_path))
        print("  [-] Path Traversal Block Check: FAILED (Escaped!)")
    except PermissionError as pe:
        print(f"  [+] Path Traversal Block Check: PASSED (Successfully blocked: {pe})")

    # Accessing C: Windows directory
    try:
        forbidden_path = Path("C:/Windows/System32")
        check_path_sandbox(str(forbidden_path))
        print("  [-] External Drive Escape Block Check: FAILED")
    except PermissionError as pe:
        print(f"  [+] External Drive Escape Block Check: PASSED (Successfully blocked: {pe})")

    # 2. Test RAG Pipeline Ingestion & Embedding Retrieval
    print("\n[*] Test 2: Verifying local RAG pipeline & vector search...")
    from tools.rag_pipeline import index_file, query_rag, DB_PATH
    
    # Create a dummy test file in whitelisted storage
    test_storage_file = Path("D:/Wellsy/storage/jarvis_test.txt")
    test_storage_file.parent.mkdir(parents=True, exist_ok=True)
    test_storage_file.write_text(
        "Project Wellsy uses a local FastMCP server implementation to allow Antigravity to trigger Spotify commands "
        "and read local whitelisted document indexes using sqlite3 database records.",
        encoding="utf-8"
    )
    
    # Index document
    index_res = index_file(str(test_storage_file))
    print(f"  [+] Ingestion outcome: {index_res}")
    
    # Query database
    print("  [*] Querying local database for 'Spotify commands'...")
    query_results = query_rag("How does Antigravity trigger Spotify commands?")
    
    if query_results:
        best_match = query_results[0]
        print(f"  [+] Best match file: {best_match['file_name']}")
        print(f"  [+] Cosine similarity score: {best_match['similarity']:.4f}")
        print(f"  [+] Retrieved Content: \"{best_match['content']}\"")
        if best_match['similarity'] > 0.5:
            print("  [+] RAG retrieval quality check: PASSED")
        else:
            print("  [-] RAG retrieval quality check: FAILED (low similarity)")
    else:
        print("  [-] RAG retrieval query: FAILED (zero results matches)")

    # Cleanup
    if test_storage_file.exists():
        test_storage_file.unlink()

    print("\n====================================================")
    print(" VERIFICATION RUN COMPLETE")
    print("====================================================")

if __name__ == "__main__":
    run_tests()
