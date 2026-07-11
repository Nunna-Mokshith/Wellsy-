import asyncio
import os
import requests
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
        await page.goto("https://aumsam.amrita.edu/cas/login", wait_until="domcontentloaded", timeout=45000)
        
        print("[2] Logging in...")
        await page.fill('input[name="username"]', 'am.en.u4rae24047')
        await page.fill('input[name="password"]', '95052')
        await page.click('button[type="submit"], input[type="submit"], #fm1 .btn-block, .btn')
        
        print("[3] Waiting for login redirect...")
        await page.wait_for_load_state("domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        
        print("[4] Navigating to AUMS main index...")
        await page.goto("https://aumsam.amrita.edu/aums/Jsp/Core_Common/index.jsp?task=off", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(5)
        
        print("[5] Clicking Main menu and View Attendance...")
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
        print("Popup window opened. Waiting 5 seconds...")
        await asyncio.sleep(5)
        
        # Get cookies from browser context
        cookies = await context.cookies()
        
        await browser.close()
        
        print("[7] Fetching PDF using requests with session cookies...")
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
            
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://aumsam.amrita.edu/aums/Jsp/Attendance/AttendanceReportStudent.jsp?action=UMS-ATD_INIT_ATDREPORTSTUD_SCREEN&isMenu=true"
        })
        
        # Method A: Try GET request first
        pdf_url = "https://aumsam.amrita.edu/aums/AUMSReportServlet"
        print(f"Trying GET from {pdf_url}...")
        response = session.get(pdf_url, timeout=30)
        print(f"GET Response: {response.status_code}, Length: {len(response.content)} bytes, Content-Type: {response.headers.get('Content-Type')}")
        
        is_pdf = response.headers.get('Content-Type', '').lower() == "application/pdf" or response.content.startswith(b"%PDF")
        
        if not is_pdf:
            # Method B: Try POST request if GET is not a PDF
            print("GET response is not PDF. Trying POST request...")
            post_url = "https://aumsam.amrita.edu/aums/Jsp/Attendance/AttendanceReportStudent.jsp"
            data = {
                'htmlPageTopContainer_txtrollnumber': '',
                'htmlPageTopContainer_selectSem': '20',
                'htmlPageTopContainer_selectCourse': '70652',
                'htmlPageTopContainer_selectType': '1',
                'Page_refIndex_hidden': '2',
                'htmlPageTopContainer_status': '',
                'htmlPageTopContainer_action': 'UMS-ATD_SHOW_ATDREPORTSTUD_SCREEN',
                'htmlPageTopContainer_notify': '',
                'htmlPageTopContainer_hidrollNo': 'Student'
            }
            response = session.post(post_url, data=data, timeout=30)
            print(f"POST Response: {response.status_code}, Length: {len(response.content)} bytes, Content-Type: {response.headers.get('Content-Type')}")
            is_pdf = response.headers.get('Content-Type', '').lower() == "application/pdf" or response.content.startswith(b"%PDF")
            
        if is_pdf:
            pdf_path = os.path.join(DOWNLOAD_DIR, "Attendance_Report.pdf")
            with open(pdf_path, "wb") as f:
                f.write(response.content)
            print(f"Successfully saved PDF to {pdf_path}!")
        else:
            print("Failed to download PDF. Saving response content as debug.html...")
            debug_path = os.path.join(DOWNLOAD_DIR, "download_debug.html")
            with open(debug_path, "wb") as f:
                f.write(response.content)
            print(f"Debug HTML saved to {debug_path}")

if __name__ == "__main__":
    asyncio.run(main())
