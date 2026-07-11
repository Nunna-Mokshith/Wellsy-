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
        
        # Wait for the frame to load
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
            
        if frame:
            # Wait for frame body to have content
            await asyncio.sleep(2)
            
            # Select Semester "4"
            print("Selecting Semester 4...")
            # Let's verify selector exists in frame
            try:
                await frame.wait_for_selector('select[name="htmlPageTopContainer_selectSem"]', timeout=5000)
                await frame.select_option('select[name="htmlPageTopContainer_selectSem"]', '4')
                print("Semester 4 selected successfully!")
            except Exception as e:
                print(f"Error selecting Sem 4: {e}")
                
            await asyncio.sleep(3)
            await page.screenshot(path=os.path.join(DOWNLOAD_DIR, "select_sem_4.png"))
            
            # Wait for Course select to populate
            try:
                await frame.wait_for_selector('select[name="htmlPageTopContainer_selectCourse"]', timeout=5000)
                course_select = frame.locator('select[name="htmlPageTopContainer_selectCourse"]')
                
                # Check options in dropdown
                options_elements = await course_select.locator('option').all()
                print(f"Found {len(options_elements)} courses:")
                target_value = None
                for opt in options_elements:
                    val = await opt.get_attribute('value')
                    txt = await opt.inner_text()
                    print(f"  Option value='{val}', text='{txt}'")
                    if "mathematics" in txt.lower() and "intelligent" in txt.lower():
                        target_value = val
                        print(f"  [!] Found target course! Value: {target_value}")
                        
                if target_value:
                    print(f"Selecting Course value='{target_value}'...")
                    await frame.select_option('select[name="htmlPageTopContainer_selectCourse"]', target_value)
                    await asyncio.sleep(3)
                    await page.screenshot(path=os.path.join(DOWNLOAD_DIR, "select_course.png"))
                    
                    # Print frame text to see the attendance report!
                    frame_text = await frame.inner_text('body')
                    print("=== Frame Text After Course Select ===")
                    print(frame_text)
                    
                    # Let's save the frame HTML for analysis
                    frame_html = await frame.inner_html('body')
                    with open("d:\\Wellsy\\downloads\\attendance_frame.html", "w", encoding="utf-8") as f:
                        f.write(frame_html)
                    print("Frame HTML written to downloads/attendance_frame.html")
                else:
                    print("Could not find Mathematics for Intelligent Systems 4 in course list.")
            except Exception as e:
                print(f"Error handling course select: {e}")
        else:
            print("Frame 1 not found. Available frames:")
            for i, f in enumerate(page.frames):
                print(f"  Frame {i}: {f.url}")
            await page.screenshot(path=os.path.join(DOWNLOAD_DIR, "frame_error.png"))
            
        await browser.close()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
