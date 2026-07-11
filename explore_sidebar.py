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
        
        # Dump potential sidebar toggle elements
        print("[5] Searching for sidebar toggle button...")
        toggles = [
            'button', '.menu-toggle', '#menu-toggle', '.sidebar-toggle', '#sidebar-toggle', 
            'i.fa-bars', '.navbar-toggle', '[id*="toggle"]', '[class*="toggle"]', '[id*="menu"]', '[class*="menu"]'
        ]
        
        # Find all elements matching button or clickables
        elements = await page.locator('button, a, div[role="button"], span').all()
        print(f"Total interactive elements: {len(elements)}")
        for el in elements:
            try:
                html = await el.outer_html()
                # If it looks like a menu toggle, print it
                if any(x in html.lower() for x in ['toggle', 'menu', 'sidebar', 'collapse', 'bar', 'hamburger', 'nav']):
                    # Check if it has a class or id or inline styles
                    print(f"Candidate element: {html[:200]}")
            except:
                pass
                
        # Let's try to click the hamburger button.
        # In the screenshot, it's at the very top-left of the sidebar.
        # We can also click by coordinates!
        # In a 1280x800 viewport:
        # Looking at 03_dashboard_loaded.png, the hamburger menu is in the orange bar on the left, near the top.
        # Let's find its position or just click at x=15, y=40.
        print("Clicking at coordinates x=15, y=40 (hamburger menu)...")
        await page.mouse.click(15, 40)
        await asyncio.sleep(3)
        await page.screenshot(path=os.path.join(DOWNLOAD_DIR, "after_coords_click.png"))
        
        # Let's try clicking some common class selectors
        for selector in ['.sidebar-toggle', '#sidebarCollapse', '.menu-toggle', 'a.sidebar-toggle']:
            try:
                locator = page.locator(selector).first
                if await locator.is_visible(timeout=1000):
                    print(f"Clicking visible selector: {selector}")
                    await locator.click()
                    await asyncio.sleep(3)
                    await page.screenshot(path=os.path.join(DOWNLOAD_DIR, f"after_{selector.replace('.', '').replace('#', '')}.png"))
            except:
                pass
                
        await browser.close()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
