import asyncio
import os
import requests
from playwright.async_api import async_playwright

DOWNLOAD_DIR = r"D:\Wellsy\downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def main():
    async with async_playwright() as p:
        print("Launching browser to log in and get cookies...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("[1] Navigating to AUMS login page...")
        await page.goto("https://aumsam.amrita.edu/cas/login", wait_until="domcontentloaded")
        
        print("[2] Logging in...")
        await page.fill('input[name="username"]', 'am.en.u4rae24047')
        await page.fill('input[name="password"]', '95052')
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(3)
        
        print("[3] Navigating to AUMS index to ensure session is initialized...")
        await page.goto("https://aumsam.amrita.edu/aums/Jsp/Core_Common/index.jsp?task=off", wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        # Get cookies
        cookies = await context.cookies()
        await browser.close()
        
        print("[4] Downloading PDF via requests library using session cookies...")
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
            
        # Set user agent to match
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://aumsam.amrita.edu/aums/Jsp/Attendance/AttendanceReportStudent.jsp?action=UMS-ATD_INIT_ATDREPORTSTUD_SCREEN&isMenu=true"
        })
        
        # Form data matching the inputs in attendance_frame.html
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
        
        url = "https://aumsam.amrita.edu/aums/Jsp/Attendance/AttendanceReportStudent.jsp"
        print(f"Sending POST to {url}...")
        response = session.post(url, data=data, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Content-Type: {response.headers.get('Content-Type')}")
        print(f"Response Length: {len(response.content)} bytes")
        
        # Check if the response is PDF
        content_type = response.headers.get('Content-Type', '').lower()
        if "pdf" in content_type or response.content.startswith(b"%PDF"):
            pdf_path = os.path.join(DOWNLOAD_DIR, "Attendance_Report.pdf")
            with open(pdf_path, "wb") as f:
                f.write(response.content)
            print(f"Success! Saved PDF to {pdf_path}")
        else:
            print("Response is not a PDF. Saving as HTML for debugging...")
            debug_path = os.path.join(DOWNLOAD_DIR, "response_debug.html")
            with open(debug_path, "wb") as f:
                f.write(response.content)
            print(f"Debug file saved to {debug_path}")

if __name__ == "__main__":
    asyncio.run(main())
