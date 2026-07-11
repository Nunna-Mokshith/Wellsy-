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
        
        print("[4] Clicking Main menu tab and View Attendance...")
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
            print("Could not find the attendance frame.")
            await browser.close()
            return
            
        await asyncio.sleep(2)
        
        # Select Semester "4" (value "20")
        print("Selecting Semester 4...")
        await frame.select_option('select[name="htmlPageTopContainer_selectSem"]', '20')
        await asyncio.sleep(3)
        
        # Select Course (value "70652" for Mathematics for Intelligent Systems - 4)
        print("Selecting Course 23MAT226...")
        await frame.select_option('select[name="htmlPageTopContainer_selectCourse"]', '70652')
        await asyncio.sleep(3)
        
        # Let's try option 1: Attendance Summary (opens in the same frame/page or a new tab?)
        # Let's inspect the Javascript for checkValuesSummary:
        # function checkValuesSummary(actionValue) { ... formSubmit(actionValue); }
        # function formSubmit(actionValue) {
        #    getJadeControl("action").value=actionValue;
        #    if(actionValue == "UMS-ATD_SHOW_ATDREPORTSTUD_SCREEN")
        #        document.forms[0].target="_blank";
        #    else
        #        document.forms[0].target="_self";
        #    document.forms[0].submit();
        # }
        # So "Attendance Summary" (actionValue "UMS-ATD_SHOW_ATDSUMMARY_SCREEN") will target "_self" (inside the iframe itself!).
        # While "Show Course Wise Report" (actionValue "UMS-ATD_SHOW_ATDREPORTSTUD_SCREEN") will target "_blank" (opens in new tab!).
        
        print("Clicking 'Show Course Wise Report'...")
        # Since it targets _blank, we expect a popup page
        async with page.expect_popup() as popup_info:
            await frame.click('input#htmlPageTopContainer_submitSave')
        
        popup_page = await popup_info.value
        await popup_page.wait_for_load_state("domcontentloaded")
        print("Popup opened!")
        await asyncio.sleep(5)
        
        # Save popup screenshot and text
        await popup_page.screenshot(path=os.path.join(DOWNLOAD_DIR, "course_wise_report.png"))
        popup_text = await popup_page.inner_text('body')
        print("=== Popup Text (Course Wise Report) ===")
        print(popup_text[:1000])
        
        # Save popup html
        popup_html = await popup_page.content()
        with open(os.path.join(DOWNLOAD_DIR, "course_wise_report.html"), "w", encoding="utf-8") as f:
            f.write(popup_html)
            
        await popup_page.close()
        
        # Now let's try Clicking 'Attendance Summary' (which is submitted to the same frame)
        print("Clicking 'Attendance Summary'...")
        # Since it submits to the frame, we wait for navigation inside the frame or just wait
        await frame.click('input#htmlPageTopContainer_submitSummary')
        await asyncio.sleep(5)
        
        # Capture screenshot of main page to see the iframe update
        await page.screenshot(path=os.path.join(DOWNLOAD_DIR, "after_summary_click.png"))
        
        # Capture frame text
        frame_text_summary = await frame.inner_text('body')
        print("=== Frame Text After Summary Click ===")
        print(frame_text_summary[:1000])
        
        # Save frame html
        frame_html_summary = await frame.content()
        with open(os.path.join(DOWNLOAD_DIR, "attendance_summary.html"), "w", encoding="utf-8") as f:
            f.write(frame_html_summary)
            
        await browser.close()
        print("Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
