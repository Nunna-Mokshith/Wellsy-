"""
Test script for Wellsy Multi-Agent Architecture
Tests routing to OSAgent, MediaAgent, CommsAgent, ResearchAgent.
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.brain import chat

async def run_tests():
    print("==================================================")
    print("   Testing Wellsy Multi-Agent Router Architecture ")
    print("==================================================\n")

    test_queries = [
        ("OSAgent Test", "What is my current CPU and RAM usage?"),
        ("MediaAgent Test", "Can you pause Spotify playback?"),
        ("CommsAgent Test", "Check my recent WhatsApp messages from Alex"),
        ("ResearchAgent Test", "Search for pictures of futuristic artificial intelligence"),
    ]

    for label, query in test_queries:
        print(f"--- [{label}] ---")
        print(f"User: {query}")
        try:
            res, status = await chat(query)
            print(f"Wellsy: {res}\n")
        except Exception as e:
            print(f"Error during test: {e}\n")

if __name__ == "__main__":
    asyncio.run(run_tests())
