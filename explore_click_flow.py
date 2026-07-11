import asyncio
import os
from playwright.async_api import async_playwright

DOWNLOAD_DIR = r"D:\Wellsy\downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def main():
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            accept_downloads=True
        )
        page = await context.new_page()
        
        print("[1] Navigating to AUMS login page...")
        await page.goto("https://aumsam.amrita.edu/cas/login", wait_until="domcontentloaded", timeout=30000)
        
        print("[2] Filling credentials...")
        await page.fill('input[name="username"]', 'am.en.u4rae24047')
        await page.fill('input[name="password"]', '95052')
        await page.click('button[type="submit"], input[type="submit"], #fm1 .btn-block, .btn')
        
        print("[3] Waiting for login response...")
        await page.wait_for_load_state("domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        
        print("[4] Navigating to AUMS index...")
        await page.goto("https://aumsam.amrita.edu/aums/Jsp/Core_Common/index.jsp?task=off", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)
        await page.screenshot(path=os.path.join(DOWNLOAD_DIR, "click_0_start.png"))
        
        # Click the sidebar toggler
        print("[5] Clicking sidebar toggler...")
        await page.click('.sidebar-toggler')
        await asyncio.sleep(2)
        await page.screenshot(path=os.path.join(DOWNLOAD_DIR, "click_1_expanded.png"))
        
        # Click "Exam Scores" menu item to expand it
        print("[6] Clicking 'Exam Scores'...")
        await page.click('li[data-id="m77"] > a')
        await asyncio.sleep(2)
        await page.screenshot(path=os.path.join(DOWNLOAD_DIR, "click_2_exam_scores.png"))
        
        # Click "View Attendance"
        print("[7] Clicking 'View Attendance'...")
        await page.click('li[data-id="m79"] > a')
        await asyncio.sleep(5)
        await page.screenshot(path=os.path.join(DOWNLOAD_DIR, "click_3_attendance_clicked.png"))
        
        print("=== Checking current URL and frames ===")
        print(f"Current URL: {page.url}")
        
        for i, frame in enumerate(page.frames):
            print(f"Frame {i}: url={frame.url}")
            try:
                frame_text = await frame.inner_text('body')
                print(f"--- Frame {i} Text (first 300 chars) ---")
                print(frame_text[:300])
                
                # Check for select elements
                selects = await frame.locator('select').all()
                for s_idx, select in enumerate(selects):
                    name = await select.get_attribute('name') or await select.get_attribute('id') or f"Select {s_idx}"
                    options = await select.inner_text()
                    print(f"    Dropdown '{name}' options:")
                    print(options.strip().replace('\n', ' | '))
            except Exception as e:
                print(f"  Error reading frame {i}: {e}")
                
        await browser.close()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
