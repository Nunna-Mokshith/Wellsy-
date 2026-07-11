import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        print("Launching headful Chrome for WhatsApp Web login...")
        user_data_dir = r"D:\Wellsy\whatsapp_profile"
        os.makedirs(user_data_dir, exist_ok=True)
        
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=False,
            viewport={"width": 1280, "height": 800}
        )
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        print("Navigating to WhatsApp Web...")
        try:
            await page.goto("https://web.whatsapp.com/", wait_until="domcontentloaded", timeout=120000)
            print("Navigation done. Waiting for page to render...")
        except Exception as e:
            print(f"Navigation warning: {e}. Proceeding...")
            
        print("Browser is now open on your screen!")
        print(">>> PLEASE SCAN THE QR CODE IF PROMPTED <<<")
        print("This window will stay open for 5 minutes to let you scan and log in.")
        
        # Poll for 5 minutes (300 seconds) to check if logged in
        logged_in = False
        for i in range(300):
            try:
                # If the search box is visible, we are logged in!
                search_box = page.locator('div[contenteditable="true"][data-tab="3"]').first
                if await search_box.is_visible():
                    print("Status: Logged in successfully! Session is saved.")
                    logged_in = True
                    break
            except Exception:
                pass
            await asyncio.sleep(1)
            
        if not logged_in:
            print("Status: Not logged in yet after 5 minutes.")
        else:
            print("Keeping browser open for 15 more seconds to settle...")
            await asyncio.sleep(15)
            
        await browser.close()
        print("Browser closed.")

if __name__ == "__main__":
    asyncio.run(main())
