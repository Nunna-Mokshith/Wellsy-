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
        
        print("[2] Logging in...")
        await page.fill('input[name="username"]', 'am.en.u4rae24047')
        await page.fill('input[name="password"]', '95052')
        await page.click('button[type="submit"], input[type="submit"], #fm1 .btn-block, .btn')
        await page.wait_for_load_state("domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        
        print("[3] Navigating DIRECTLY to Attendance Report URL...")
        attendance_url = "https://aumsam.amrita.edu/aums/Jsp/Attendance/AttendanceReportStudent.jsp?action=UMS-ATD_INIT_ATDREPORTSTUD_SCREEN&isMenu=true"
        await page.goto(attendance_url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)
        
        await page.screenshot(path=os.path.join(DOWNLOAD_DIR, "attendance_direct.png"))
        print(f"Current URL: {page.url}")
        
        # Check text
        body_text = await page.inner_text('body')
        print("=== Page Text ===")
        print(body_text[:1500])
        
        # Look for select dropdowns
        selects = await page.locator('select').all()
        print(f"Dropdowns found: {len(selects)}")
        for idx, select in enumerate(selects):
            name = await select.get_attribute('name') or await select.get_attribute('id') or f"Select {idx}"
            options = await select.inner_text()
            print(f"  Dropdown '{name}': {options.strip().replace('\n', ' | ')}")
            
        await browser.close()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
