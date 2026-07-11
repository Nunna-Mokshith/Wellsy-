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
        
        print("[3] Navigating to AUMS index...")
        await page.goto("https://aumsam.amrita.edu/aums/Jsp/Core_Common/index.jsp?task=off", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)
        await page.screenshot(path=os.path.join(DOWNLOAD_DIR, "js_0_start.png"))
        
        # Click the Main tab first to ensure Main tab menu is active in case it's on LMS
        print("[4] Clicking Main menu tab...")
        try:
            await page.evaluate("document.querySelector('a[href=\"#quick_sidebar-Main_tab_1\"]').click()")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Error clicking Main tab: {e}")
            
        print("[5] Executing JS click on 'View Attendance' link...")
        try:
            # We will click the anchor link inside li with data-id="m79"
            await page.evaluate("document.querySelector('li[data-id=\"m79\"] > a').click()")
            print("JS click executed on View Attendance link!")
        except Exception as e:
            print(f"JS click on link failed: {e}")
            
        try:
            # Also try clicking the li itself
            await page.evaluate("document.querySelector('li[data-id=\"m79\"]').click()")
            print("JS click executed on li[data-id='m79']!")
        except Exception as e:
            print(f"JS click on li failed: {e}")
            
        await asyncio.sleep(5)
        await page.screenshot(path=os.path.join(DOWNLOAD_DIR, "js_1_after_click.png"))
        
        print("=== Checking current URL and frames ===")
        print(f"Current URL: {page.url}")
        
        for i, frame in enumerate(page.frames):
            print(f"Frame {i}: url={frame.url}")
            try:
                frame_text = await frame.inner_text('body')
                if len(frame_text.strip()) > 0:
                    print(f"--- Frame {i} Text (first 500 chars) ---")
                    print(frame_text[:500])
                    
                    # Look for selects
                    selects = await frame.locator('select').all()
                    if len(selects) > 0:
                        print(f"    Dropdowns in Frame {i}: {len(selects)}")
                        for s_idx, select in enumerate(selects):
                            name = await select.get_attribute('name') or await select.get_attribute('id') or f"Select {s_idx}"
                            options = await select.inner_text()
                            print(f"      Dropdown '{name}': {options.strip().replace('\n', ' | ')}")
            except Exception as e:
                print(f"  Error reading frame {i}: {e}")
                
        await browser.close()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
