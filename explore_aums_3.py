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
        await page.goto("https://aumsam.amrita.edu/cas/login", wait_until="networkidle", timeout=30000)
        
        print("[2] Filling credentials...")
        await page.fill('input[name="username"]', 'am.en.u4rae24047')
        await page.fill('input[name="password"]', '95052')
        await page.click('button[type="submit"], input[type="submit"], #fm1 .btn-block, .btn')
        
        print("[3] Waiting for login response...")
        await page.wait_for_load_state("networkidle", timeout=30000)
        await asyncio.sleep(3)
        
        print("[4] Navigating to AUMS index...")
        await page.goto("https://aumsam.amrita.edu/aums/Jsp/Core_Common/index.jsp?task=off", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(5)
        
        print("[5] Clicking 'View Attendance'...")
        clicked = False
        try:
            elem = page.locator('a:has-text("View Attendance")').first
            if await elem.is_visible(timeout=5000):
                await elem.click()
                clicked = True
                print("Successfully clicked View Attendance link!")
            else:
                print("View Attendance link not visible via standard locator")
        except Exception as e:
            print(f"Error locating View Attendance link: {e}")
            
        if not clicked:
            # Try to find all links and click the one with text "View Attendance"
            try:
                links = await page.locator('a').all()
                for link in links:
                    txt = await link.inner_text()
                    if "view attendance" in txt.lower():
                        print(f"Found link by iteration: '{txt}', clicking...")
                        await link.click()
                        clicked = True
                        break
            except Exception as e:
                print(f"Error in fallback iteration: {e}")
                
        if clicked:
            await asyncio.sleep(5)
            await page.screenshot(path=os.path.join(DOWNLOAD_DIR, "04_attendance_loaded.png"))
            print(f"URL after click: {page.url}")
            
            # Print page text
            body_text = await page.inner_text('body')
            print("=== Page Text ===")
            print(body_text[:1000])
            
            # Check frames
            print("Checking frames...")
            for i, frame in enumerate(page.frames):
                print(f"Frame {i}: url={frame.url}")
                try:
                    frame_text = await frame.inner_text('body')
                    print(f"  Frame {i} Text (first 500 chars):")
                    print(frame_text[:500])
                    
                    # Look for academic year, semester, or subject dropdowns/selects in frame
                    selects = await frame.locator('select').all()
                    print(f"  Frame {i} has {len(selects)} dropdowns:")
                    for idx, s in enumerate(selects):
                        html = await s.inner_html()
                        print(f"    Dropdown {idx}: {html[:300]}")
                        
                except Exception as e:
                    print(f"  Error reading frame {i}: {e}")
        else:
            print("Failed to click View Attendance.")
            
        await browser.close()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
