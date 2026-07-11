import asyncio
import os
from playwright.async_api import async_playwright

DOWNLOAD_DIR = r"D:\Wellsy\downloads"
pdf_path = os.path.join(DOWNLOAD_DIR, "Attendance_Report.pdf")

async def main():
    if not os.path.exists(pdf_path):
        print(f"Error: Attendance report PDF not found at {pdf_path}")
        return

    async with async_playwright() as p:
        print("Launching headful Chrome for WhatsApp Web...")
        user_data_dir = r"D:\Wellsy\whatsapp_profile"
        os.makedirs(user_data_dir, exist_ok=True)
        
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=False,
            viewport={"width": 1280, "height": 800},
            slow_mo=1000
        )
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        print("[1] Navigating to WhatsApp Web...")
        try:
            await page.goto("https://web.whatsapp.com/", wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"Initial navigation warning: {e}. Waiting 10 seconds anyway...")
            await asyncio.sleep(10)
        
        print("[2] Waiting for login...")
        print(">>> IF YOU ARE NOT LOGGED IN, PLEASE SCAN THE QR CODE ON THE BROWSER WINDOW NOW! <<<")
        
        # Wait up to 120 seconds for login to complete (indicated by the search box appearing)
        search_box = None
        for attempt in range(120):
            try:
                search_box = page.locator('div[contenteditable="true"][data-tab="3"]').first
                if await search_box.is_visible():
                    print("Logged in successfully!")
                    break
            except Exception:
                pass
            await asyncio.sleep(1)
            
        if not search_box or not await search_box.is_visible():
            print("Error: Log in timeout. Search box not found.")
            await browser.close()
            return
            
        print("[3] Searching for 'Teddy'...")
        await search_box.click()
        await search_box.fill("Teddy")
        await asyncio.sleep(3)
        
        print("[4] Selecting chat...")
        teddy_chat = page.locator('span[title="Teddy"]').first
        if await teddy_chat.is_visible():
            await teddy_chat.click()
            print("Chat 'Teddy' opened.")
        else:
            print("Could not find chat named 'Teddy' in list. Trying to find contact via text locator...")
            try:
                await page.click('span:has-text("Teddy")')
                print("Chat opened via text locator.")
            except Exception as e:
                print(f"Error opening chat: {e}")
                await browser.close()
                return
                
        await asyncio.sleep(3)
        
        print("[5] Uploading attendance report...")
        uploaded = False
        try:
            inputs = await page.locator('input[type="file"]').all()
            print(f"Found {len(inputs)} file inputs.")
            for idx, inp in enumerate(inputs):
                accept = await inp.get_attribute("accept")
                print(f"  Input {idx} accept='{accept}'")
                if accept is None or "*" in accept or "pdf" in accept or "document" in accept:
                    print(f"  Attempting upload on input {idx}...")
                    await inp.set_input_files(pdf_path)
                    uploaded = True
                    break
            
            if not uploaded and len(inputs) > 0:
                print("Using the first file input as fallback...")
                await inputs[0].set_input_files(pdf_path)
                uploaded = True
        except Exception as e:
            print(f"Direct file upload error: {e}")
            
        if not uploaded:
            print("Fallback: Clicking Attach button first...")
            try:
                attach_btn = page.locator('span[data-icon="plus"]').first
                if not await attach_btn.is_visible():
                    attach_btn = page.locator('div[role="button"][title="Attach"]').first
                await attach_btn.click()
                await asyncio.sleep(2)
                
                inputs = await page.locator('input[type="file"]').all()
                if len(inputs) > 0:
                    await inputs[0].set_input_files(pdf_path)
                    uploaded = True
                    print("Uploaded successfully after clicking Attach!")
            except Exception as e2:
                print(f"Fallback upload failed: {e2}")
                
        if not uploaded:
            print("Error: Could not upload file.")
            await browser.close()
            return
            
        await asyncio.sleep(4)
        
        print("[6] Sending message...")
        try:
            send_btn = page.locator('span[data-icon="send"]').first
            await send_btn.click()
            print("Send button clicked!")
        except Exception as e:
            print(f"Could not click send button: {e}. Pressing Enter instead...")
            await page.keyboard.press("Enter")
            
        await asyncio.sleep(8)
        print("Success! File sent to Teddy via WhatsApp.")
        
        await browser.close()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
