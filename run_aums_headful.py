import asyncio
import os
from playwright.async_api import async_playwright

DOWNLOAD_DIR = r"D:\Wellsy\downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def main():
    async with async_playwright() as p:
        print("Launching headful Chrome...")
        # Launching user's actual Chrome executable headfully
        browser = await p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=False,
            slow_mo=1000 # slow_mo so the user can see what's happening
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            accept_downloads=True
        )
        page = await context.new_page()
        
        print("[1] Navigating to AUMS login...")
        await page.goto("https://aumsam.amrita.edu/cas/login", wait_until="networkidle", timeout=45000)
        
        print("[2] Logging in...")
        await page.fill('input[name="username"]', 'am.en.u4rae24047')
        await page.fill('input[name="password"]', '95052')
        await page.click('button[type="submit"], input[type="submit"], #fm1 .btn-block, .btn')
        
        print("[3] Waiting for login redirect...")
        await page.wait_for_load_state("networkidle", timeout=30000)
        await asyncio.sleep(3)
        
        print("[4] Navigating to AUMS main index...")
        await page.goto("https://aumsam.amrita.edu/aums/Jsp/Core_Common/index.jsp?task=off", wait_until="networkidle", timeout=45000)
        await asyncio.sleep(5)
        
        # Check if "View Attendance" is visible. If not, click hamburger menu
        view_attendance = page.locator('a:has-text("View Attendance")').first
        if not await view_attendance.is_visible():
            print("Sidebar collapsed. Expanding sidebar via hamburger click at (15, 40)...")
            await page.mouse.click(15, 40)
            await asyncio.sleep(3)
            
        print("[5] Clicking 'View Attendance'...")
        await page.locator('a:has-text("View Attendance")').first.click()
        await asyncio.sleep(5)
        
        print("[6] Capturing attendance page info...")
        await page.screenshot(path=os.path.join(DOWNLOAD_DIR, "04_attendance_page.png"))
        
        # Let's inspect the attendance page.
        # We need to find "Mathematics for Intelligent Systems 4" and download it.
        # Let's dump all text and input elements of the page (including inside iframes).
        print("=== Checking main page and frames ===")
        for i, frame in enumerate(page.frames):
            print(f"Frame {i} URL: {frame.url}")
            try:
                frame_text = await frame.inner_text('body')
                print(f"--- Frame {i} Text Snippet ---")
                print(frame_text[:1000])
                
                # Check for select dropdowns
                selects = await frame.locator('select').all()
                for idx, select in enumerate(selects):
                    name = await select.get_attribute('name') or await select.get_attribute('id') or f"Select {idx}"
                    options = await select.inner_text()
                    print(f"  Select dropdown '{name}' options:")
                    print(options.strip().replace('\n', ' | '))
                    
            except Exception as e:
                print(f"  Could not inspect Frame {i}: {e}")
                
        # Keep browser open for 20 seconds so user can see it
        print("Done. Keeping browser open for 20 seconds...")
        await asyncio.sleep(20)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
