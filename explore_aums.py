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
        await page.screenshot(path=os.path.join(DOWNLOAD_DIR, "01_login_page.png"))
        
        print("[2] Filling credentials...")
        await page.fill('input[name="username"]', 'am.en.u4rae24047')
        await page.fill('input[name="password"]', '95052')
        await page.click('button[type="submit"], input[type="submit"], #fm1 .btn-block, .btn')
        
        print("[3] Waiting for dashboard...")
        await page.wait_for_load_state("networkidle", timeout=30000)
        await asyncio.sleep(5)
        await page.screenshot(path=os.path.join(DOWNLOAD_DIR, "02_dashboard.png"))
        print(f"Current URL: {page.url}")
        
        # Log the sidebar links
        sidebar = page.locator('.sidebar, #sidebar, nav, .left-panel, .menu-panel')
        if await sidebar.count() > 0:
            print("Sidebar found!")
            text = await sidebar.first.inner_text()
            print("=== Sidebar Text ===")
            print(text)
        else:
            print("Sidebar not found by class, looking for text links...")
            links = await page.locator('a').all()
            print(f"Total links: {len(links)}")
            for l in links[:30]:
                txt = await l.inner_text()
                if txt.strip():
                    print(f"Link text: {txt.strip()}")

        # Function to click and capture
        async def click_and_capture(selector, name):
            try:
                elem = page.locator(selector).first
                if await elem.is_visible(timeout=3000):
                    print(f"Clicking {name}...")
                    await elem.click()
                    await asyncio.sleep(2)
                    await page.screenshot(path=os.path.join(DOWNLOAD_DIR, f"click_{name}.png"))
                    # check if any new text appeared
                    body_text = await page.inner_text('body')
                    print(f"--- After clicking {name} ---")
                    # print lines that contain 'attendance' or 'attend' or 'scores' or 'registration'
                    for line in body_text.split('\n'):
                        if 'attend' in line.lower() or 'score' in line.lower() or 'report' in line.lower():
                            print(f"  Line: {line.strip()}")
                else:
                    print(f"{name} element not visible")
            except Exception as e:
                print(f"Error clicking {name}: {e}")

        # Try clicking sidebar elements
        await click_and_capture('text=Registration', 'Registration')
        await click_and_capture('text=Exam Scores', 'ExamScores')
        await click_and_capture('text=Personal', 'Personal')
        
        # Check all frames
        print("Checking frames...")
        for i, frame in enumerate(page.frames):
            print(f"Frame {i}: url={frame.url}")
            try:
                frame_text = await frame.inner_text('body')
                if 'attend' in frame_text.lower():
                    print(f"  [!] Frame {i} has 'attendance'!")
                    for line in frame_text.split('\n'):
                        if 'attend' in line.lower() or 'subject' in line.lower():
                            print(f"    -> {line.strip()[:100]}")
            except Exception as e:
                print(f"  Error reading frame {i}: {e}")
                
        await browser.close()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
