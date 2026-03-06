from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os

load_dotenv()

username = os.getenv("AK_USERNAME")
password = os.getenv("AK_PASSWORD")

if not username or not password:
    raise ValueError("AK_USERNAME and AK_PASSWORD must be set in .env file")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page()
    page.goto("https://www.altekamereren.org/", wait_until="networkidle")
    
    page.get_by_role("link", name="Logga in").first.click()
    page.wait_for_timeout(2000)
    
    page.wait_for_selector('input[type="password"]', state="visible", timeout=10000)
    
    page.fill('input[placeholder="Användarnamn"], input[name="username"], input[name="anvandarnamn"]', username)
    page.fill('input[type="password"], input[placeholder="Lösenord"]', password)
    
    page.locator('.modal').get_by_role("button", name="Logga in").first.click()
    
    page.wait_for_timeout(5000)
    
    if page.get_by_text("Logga ut").first.is_visible():
        print("Login successful!")
    else:
        print("Login may have failed - check manually.")
    
    print("\nNavigating to upcoming events...")
    page.goto("https://www.altekamereren.org/upcoming")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(5000)
    
    # Extract visible text which contains all events
    body_text = page.locator("body").inner_text()
    with open("events_text.txt", "w") as f:
        f.write(body_text)
    print(f"Saved events to events_text.txt ({len(body_text)} bytes)")
    
    html = page.content()
    with open("schema.html", "w") as f:
        f.write(html)
    print(f"Saved HTML to schema.html ({len(html)} bytes)")
    
    browser.close()
