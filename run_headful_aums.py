import asyncio
import os
from playwright.async_api import async_playwright

DOWNLOAD_DIR = r"D:\Wellsy\downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def main():
    async with async_playwright() as p:
        print("Launching headful Chrome...")
        # We launch the user's Google Chrome headfully
        browser = await p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=False,
            slow_mo=500
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            accept_downloads=True
        )
        page = await context.new_page()
        
        print("[1] Navigating to AUMS login page...")
        await page.goto("https://aumsam.amrita.edu/cas/login", wait_until="domcontentloaded", timeout=45000)
        
        print("[2] Logging in...")
        await page.fill('input[name="username"]', 'am.en.u4rae24047')
        await page.fill('input[name="password"]', '95052')
        await page.click('button[type="submit"], input[type="submit"], #fm1 .btn-block, .btn')
        
        print("[3] Waiting for login redirect...")
        await page.wait_for_load_state("domcontentloaded", timeout=30000)
        await asyncio.sleep(5)
        
        print("[4] Navigating to AUMS main index...")
        await page.goto("https://aumsam.amrita.edu/aums/Jsp/Core_Common/index.jsp?task=off", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(5)
        
        print("[5] Clicking Main menu tab and View Attendance...")
        # Use Javascript click because the sidebar is closed
        await page.evaluate("document.querySelector('a[href=\"#quick_sidebar-Main_tab_1\"]').click()")
        await asyncio.sleep(2)
        await page.evaluate("document.querySelector('li[data-id=\"m79\"] > a').click()")
        
        print("[6] Waiting for Attendance frame...")
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
            print("Error: Attendance frame not found.")
            await browser.close()
            return
            
        await asyncio.sleep(3)
        
        # Select Semester "4" (value "20")
        print("Selecting Semester 4...")
        await frame.select_option('select[name="htmlPageTopContainer_selectSem"]', '20')
        await asyncio.sleep(4)
        
        # Select Course (value "70652" for Mathematics for Intelligent Systems - 4)
        print("Selecting Course 23MAT226...")
        await frame.select_option('select[name="htmlPageTopContainer_selectCourse"]', '70652')
        await asyncio.sleep(4)
        
        print("Clicking 'Show Course Wise Report'...")
        # Since it targets _blank, we expect a popup page
        async with page.expect_popup() as popup_info:
            await frame.click('input#htmlPageTopContainer_submitSave')
        
        popup_page = await popup_info.value
        print("Popup window opened. Waiting 8 seconds for report load...")
        await asyncio.sleep(8)
        
        # Take a screenshot of the popup
        screenshot_path = os.path.join(DOWNLOAD_DIR, "attendance_report_popup.png")
        await popup_page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        # Print some text from the popup to confirm
        popup_text = await popup_page.inner_text('body')
        print("=== Attendance Report Text ===")
        print(popup_text[:1000])
        
        # Save popup html
        html_path = os.path.join(DOWNLOAD_DIR, "attendance_report.html")
        popup_html = await popup_page.content()
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(popup_html)
        print(f"Report HTML saved to {html_path}")
        
        # Let's print the page to PDF
        # Note: PDF generation is only supported in headless Chromium. 
        # But we can try to save it or screenshot is enough?
        # Wait, the task says "downloading the student attendance summary ... and send the downloaded file".
        # If we save the HTML page or take a screenshot, which one is better?
        # A PDF of the page is the best! But print_to_pdf is only supported in headless.
        # Wait! Is it possible to print PDF in headful mode using chrome print/save dialog?
        # No, but we can save the HTML or we can use another headless browser in the background to generate the PDF if we need PDF.
        # Wait! Let's check if the HTML itself can be saved, or if we can save it as an image, or can we print to PDF using a headless browser?
        # Yes! We can run a headless browser to login and print the page to PDF.
        # Wait, why did the headless popup wait fail earlier? It failed on `await popup_page.wait_for_load_state("domcontentloaded")`.
        # If we just do `await asyncio.sleep(8)` instead of `wait_for_load_state` in the headless script, we can generate a perfect PDF!
        # Let's test that!
        
        print("Keeping browser open for 10 seconds for user to see...")
        await asyncio.sleep(10)
        await browser.close()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
