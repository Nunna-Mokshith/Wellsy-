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
        
        pdf_saved = asyncio.Event()
        
        # Async response handler on the context to catch the PDF bytes
        async def handle_response(response):
            if "AUMSReportServlet" in response.url:
                print(f"Intercepted response URL: {response.url}")
                try:
                    body = await response.body()
                    pdf_path = os.path.join(DOWNLOAD_DIR, "Attendance_Report.pdf")
                    with open(pdf_path, "wb") as f:
                        f.write(body)
                    print(f"Successfully saved PDF to {pdf_path} ({len(body)} bytes)!")
                    pdf_saved.set()
                except Exception as e:
                    print(f"Error reading response body: {e}")
        
        context.on("response", handle_response)
        
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
        
        print("[4] Clicking View Attendance...")
        await page.evaluate("document.querySelector('a[href=\"#quick_sidebar-Main_tab_1\"]').click()")
        await asyncio.sleep(2)
        await page.evaluate("document.querySelector('li[data-id=\"m79\"] > a').click()")
        
        print("[5] Waiting for Attendance frame...")
        frame = None
        for attempt in range(15):
            for f in page.frames:
                if "AttendanceReportStudent.jsp" in f.url:
                    frame = f
                    break
            if frame:
                print(f"Frame found on attempt {attempt+1}!")
                break
            await asyncio.sleep(1)
            
        if not frame:
            print("Frame not found")
            await browser.close()
            return
            
        await asyncio.sleep(2)
        print("Selecting Semester 4...")
        await frame.select_option('select[name="htmlPageTopContainer_selectSem"]', '20')
        await asyncio.sleep(3)
        
        print("Selecting Course...")
        await frame.select_option('select[name="htmlPageTopContainer_selectCourse"]', '70652')
        await asyncio.sleep(3)
        
        print("Clicking 'Show Course Wise Report'...")
        await frame.click('input#htmlPageTopContainer_submitSave')
        
        print("Waiting for PDF to download/intercept...")
        try:
            # Wait for the PDF to be intercepted, max 15 seconds
            await asyncio.wait_for(pdf_saved.wait(), timeout=15)
            print("PDF interception check complete!")
        except asyncio.TimeoutError:
            print("Timed out waiting for PDF interception.")
            
        await browser.close()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
