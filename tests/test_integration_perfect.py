"""
Wellsy Integration Test:
1. Play "Perfect" on YouTube
2. Send the YouTube link to user's number (6305601407) on WhatsApp
"""
import sys
import time
sys.path.insert(0, r"D:\Wellsy\backend")

from tools.youtube import search_youtube
from tools.whatsapp import send_message

def main():
    # Step 1: Search and play "Perfect" on YouTube
    print("=" * 50)
    print("  WELLSY TEST: Play Perfect + Send Link")
    print("=" * 50)
    
    print("\n[1] Playing 'Perfect' on YouTube...")
    result = search_youtube.invoke({"query": "Perfect Ed Sheeran"})
    print(f"    Result: {result}")
    
    # The YouTube search URL
    youtube_link = "https://www.youtube.com/results?search_query=Perfect+Ed+Sheeran"
    
    # Wait for YouTube to load
    time.sleep(5)
    
    # Step 2: Try to play the first result
    print("\n[2] Clicking first video result...")
    from tools.youtube import play_first_result
    try:
        play_result = play_first_result.invoke({})
        print(f"    Result: {play_result}")
    except Exception as e:
        print(f"    Note: {e}")
    
    time.sleep(3)
    
    # Step 3: Send the YouTube link to user's WhatsApp (6305601407)
    print("\n[3] Sending YouTube link to 6305601407 on WhatsApp...")
    message = "Hey! Check out this song - Perfect by Ed Sheeran: " + youtube_link
    
    try:
        wa_result = send_message.invoke({
            "contact_name": "6305601407",
            "message": message
        })
        print(f"    Result: {wa_result}")
    except Exception as e:
        print(f"    Error: {e}")
    
    print("\n" + "=" * 50)
    print("  TEST COMPLETE!")
    print("=" * 50)

if __name__ == "__main__":
    main()
