import sys
sys.path.append("/data/data/com.termux/files/usr/lib/python3.12/site-packages")
from patchright.async_api import async_playwright
from quart import Quart, request, jsonify
import asyncio

app = Quart(__name__)


async def create_browser():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--start-minimized"
        ]
    )
    return playwright, browser


async def main(url=None, sitekey=None):
    url = url + "/" if not url.endswith("/") else url

    
    with open("page.html") as f:
        page_data = f.read()
    stub = f"<div class=\"cf-turnstile\" data-sitekey=\"{sitekey}\"></div>"
    page_data = page_data.replace("<!-- cf turnstile -->", stub)

    
    playwright, browser = await create_browser()
    context = await browser.new_context()
    page = await context.new_page()

    
    await page.route(url, lambda route: route.fulfill(body=page_data, status=200))
    await page.goto(url)
    await page.eval_on_selector("//div[@class='cf-turnstile']", "el => el.style.width = '70px'")

    turnstile_value = None
    
    while True:
        turnstile_check = await page.input_value("[name=cf-turnstile-response]")
        if turnstile_check == "":
            await page.click("//div[@class='cf-turnstile']")
        else:
            element = await page.query_selector("[name=cf-turnstile-response]")
            turnstile_value = await element.get_attribute("value") if element else None
            break

    
    await page.close()
    await context.close()
    await browser.close()
    await playwright.stop()

    
    return {"result": turnstile_value}


@app.route('/turnstile', methods=['GET'])
async def process_turnstile():
    url = request.args.get('url')
    sitekey = request.args.get('sitekey')

    if not url or not sitekey:
        return jsonify({"error": "Both 'url' and 'sitekey' are required"}), 400

    
    try:
        turnstile_solver = await main(url=url, sitekey=sitekey)
        return jsonify(turnstile_solver), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=200)
