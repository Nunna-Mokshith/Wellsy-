"""
Wellsy CLI — Command Line Interface
Interact with the running Wellsy daemon directly from your terminal.

Usage:
  python wellsy.py "play some jazz on spotify"
  python wellsy.py chat
  python wellsy.py status
  python wellsy.py memory
  python wellsy.py schedule
"""
import sys
import json
import argparse
import urllib.request
import urllib.error

WELLSY_URL = "http://localhost:8765"


def check_daemon_running() -> bool:
    """Check if the Wellsy backend daemon is alive."""
    try:
        req = urllib.request.urlopen(f"{WELLSY_URL}/api/health", timeout=2)
        if req.status == 200:
            return True
    except Exception:
        pass
    return False


def get_status():
    """Print current Wellsy daemon status and system stats."""
    if not check_daemon_running():
        print("[!] Wellsy daemon is NOT running. Start it with: python backend/main.py")
        return

    try:
        req = urllib.request.urlopen(f"{WELLSY_URL}/api/system", timeout=3)
        sys_data = json.loads(req.read().decode())
        
        req_agents = urllib.request.urlopen(f"{WELLSY_URL}/api/agents", timeout=3)
        agents_data = json.loads(req_agents.read().decode())

        req_mem = urllib.request.urlopen(f"{WELLSY_URL}/api/memory/stats", timeout=3)
        mem_data = json.loads(req_mem.read().decode())

        print("========================================")
        print("   WELLSY COMMAND CENTER STATUS")
        print("========================================")
        print(f"  Daemon State : ONLINE (http://localhost:8765)")
        print(f"  CPU Usage    : {sys_data.get('cpu', 0)}%")
        print(f"  RAM Usage    : {sys_data.get('ram', 0)}%")
        print(f"  Disk Usage   : {sys_data.get('disk', 0)}%")
        print(f"  Total Memory : {mem_data.get('total_memories', 0)} entries")
        print("  Active Agents:")
        for ag in agents_data.get("agents", []):
            print(f"    • {ag['icon']} {ag['name']}: {ag['status'].upper()}")
        print("========================================\n")
    except Exception as e:
        print(f"[!] Error fetching status: {e}")


def get_memory():
    """List stored memories."""
    if not check_daemon_running():
        print("[!] Wellsy daemon is NOT running.")
        return
    try:
        req = urllib.request.urlopen(f"{WELLSY_URL}/api/memory/stats", timeout=3)
        data = json.loads(req.read().decode())
        print(f"\n[+] Total Stored Memories: {data.get('total_memories', 0)}")
        print("  By Category:", data.get('by_type', {}))
    except Exception as e:
        print(f"[!] Error fetching memory: {e}")


def get_schedule():
    """List scheduled background tasks."""
    if not check_daemon_running():
        print("[!] Wellsy daemon is NOT running.")
        return
    try:
        req = urllib.request.urlopen(f"{WELLSY_URL}/api/schedules", timeout=3)
        data = json.loads(req.read().decode())
        schedules = data.get("schedules", [])
        print("\n[+] Active Scheduled Background Tasks:")
        if not schedules:
            print("  No tasks currently scheduled.")
        for s in schedules:
            status = "ENABLED" if s.get("enabled") else "DISABLED"
            print(f"  • ID #{s['id']}: [{s['schedule_type']}] '{s['title']}' at {s['trigger_time']} ({status})")
    except Exception as e:
        print(f"[!] Error fetching schedule: {e}")


def execute_command(command_text: str):
    """Send a single prompt command to Wellsy and stream/print response."""
    if not check_daemon_running():
        print("[!] Wellsy daemon is NOT running. Starting background server...")
        # Fallback inline run
        from agent.brain import chat
        import asyncio
        resp, status = asyncio.run(chat(command_text))
        print(f"\nWellsy > {resp}\n")
        return

    # Call backend HTTP or WS
    from agent.brain import chat
    import asyncio
    print(f"\nUser > {command_text}")
    print("[Wellsy is processing...]")
    resp, status = asyncio.run(chat(command_text))
    print(f"\nWellsy > {resp}\n")


def start_chat_repl():
    """Interactive CLI terminal chat REPL."""
    print("========================================")
    print("   WELLSY INTERACTIVE TERMINAL CLI")
    print("   Type 'exit' or 'quit' to stop.")
    print("========================================\n")
    
    from agent.brain import chat
    import asyncio
    
    history = []
    while True:
        try:
            user_input = input("You > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Goodbye, Moksh!")
                break
            
            resp, status = asyncio.run(chat(user_input, history=history))
            print(f"\nWellsy > {resp}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting Wellsy CLI.")
            break


def main():
    parser = argparse.ArgumentParser(description="Wellsy CLI — Command Line Interface")
    parser.add_argument("command", nargs="?", help="Command or query for Wellsy (e.g. 'play jazz')")
    parser.add_argument("--status", action="store_true", help="Show Wellsy daemon & system status")
    parser.add_argument("--memory", action="store_true", help="View stored memory stats")
    parser.add_argument("--schedule", action="store_true", help="View active scheduled tasks")
    parser.add_argument("--chat", action="store_true", help="Start interactive CLI REPL session")

    args = parser.parse_args()

    if args.status:
        get_status()
    elif args.memory:
        get_memory()
    elif args.schedule:
        get_schedule()
    elif args.chat:
        start_chat_repl()
    elif args.command:
        execute_command(args.command)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
