import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto("https://aumsam.amrita.edu/cas/login", wait_until="networkidle")
        await page.fill('input[name="username"]', 'am.en.u4rae24047')
        await page.fill('input[name="password"]', '95052')
        await page.click('button[type="submit"], input[type="submit"], #fm1 .btn-block, .btn')
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)
        
        await page.goto("https://aumsam.amrita.edu/aums/Jsp/Core_Common/index.jsp?task=off", wait_until="networkidle")
        await asyncio.sleep(3)
        
        html = await page.content()
        with open("d:\\Wellsy\\downloads\\page_dom.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        print("HTML written to downloads/page_dom.html")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
