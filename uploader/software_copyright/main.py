import asyncio
import json
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

COOKIE_FILE = Path("cookies/copyright_cookie.json")
COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_info():
    data = Path("info.txt").read_text().strip().splitlines()
    return {
        "fullname": data[0],
        "shortname": data[1],
        "version": data[2],
        "hardware_dev": data[3],
        "hardware_run": data[4],
        "os_dev": data[5],
        "dev_tools": data[6],
        "runtime_platform": data[7],
        "support_software": data[8],
        "code_lines": data[9],
        "purpose": data[10],
        "industry": data[11],
        "main_function": data[12],
        "func": data[13],
    }

async def save_cookies(page):
    state = await page.context.storage_state()
    COOKIE_FILE.write_text(json.dumps(state))
    print("✅ Cookie saved.")

async def login_or_load_cookies(pw):
    browser = await pw.chromium.launch(headless=False)
    if COOKIE_FILE.exists():
        context = await browser.new_context(storage_state=str(COOKIE_FILE))
    else:
        context = await browser.new_context()
        page = await context.new_page()
        print("➡️ 请手动登录网站…登录完按回车")
        await page.goto("https://register.ccopyright.com.cn/r11.html#/application")
        input()
        await save_cookies(page)
    page = await context.new_page()
    await page.goto("https://register.ccopyright.com.cn/r11.html#/application")
    return page

# -------------------------------------------

async def step1(page):
    print("➡️ Step1: 选择“我是申请人”")
    await page.click("text=我是申请人")

async def step2(page, info):
    print("➡️ Step2: 原始取得 + 填写软件信息")
    await page.click("text=原始取得")
    await page.fill('input[placeholder="请输入软件全称"]', info["fullname"])
    await page.fill('input[placeholder*="简称"]', info["shortname"])
    await page.fill('input[placeholder="请输入版本号"]', info["version"])
    await page.click('button:has-text("下一步")')
    await page.wait_for_load_state("networkidle")

async def step3(page):
    print("➡️ Step3: 软件分类 + 开发方式 + 发表状态")
    # 点击分类下拉框
    await page.click('div.box.large:has-text("请选择软件分类")')
    # await page.click('div.box.large:has-text("应用软件")')
    # await page.wait_for_load_state("networkidle")
    await page.wait_for_selector('.hd-option')  # 等选项展示

    # 点击 “应用软件”
    await page.click('.hd-option:has-text("应用软件")')

    
    await page.click('text=原创')
    await page.click('text=单独开发')
    
    # 点击日期输入框
    await page.click('input[placeholder="请选择日期"]')

    # 等日期弹窗出现
    await page.wait_for_selector('.hd-link')

    # 点击“今天”按钮
    await page.click('a.hd-link.chooseNow.day.chooseNowNew:has-text("今天")')
    # await page.click('text=未发表')
    await page.click('button:has-text("下一步")')
    await page.wait_for_load_state("networkidle")
    
async def step4(page, info):
    print("➡️ Step4: 填写软件说明")
    await page.wait_for_selector("textarea", timeout=5000)
    textareas = await page.locator("textarea").all()
    await textareas[0].fill(info["hardware_dev"])
    await textareas[1].fill(info["hardware_run"])
    await textareas[2].fill(info["os_dev"])
    await textareas[3].fill(info["dev_tools"])
    await textareas[4].fill(info["runtime_platform"])
    await textareas[5].fill(info["support_software"])

    # 编程语言 HTML + JS
    await page.click('span:has-text("HTML")')
    await page.click('span:has-text("JavaScript")')

    await page.locator('h3:has-text("源程序量") + div input').fill(info["code_lines"])

    await textareas[7].fill(info["purpose"])
    await textareas[8].fill(info["industry"])
    await textareas[9].fill(info["main_function"])

    # 游戏软件 checkbox
    await page.click('span:has-text("游戏软件")')
    await textareas[10].fill(info["func"])

    print("➡️ 上传文件...")
    # 上传程序鉴别材料（第一个上传框）
    await page.locator('div.upLoadBox:has-text("源程序前连续的30页") input[type="file"]').set_input_files("upload_docs/code.pdf")
    # 等待上传成功（隐藏错误提示）
    await page.wait_for_load_state("networkidle")    

    # 上传文档鉴别材料（第二个上传框）
    await page.locator('div.upLoadBox:has-text("提交任何一种文档的前连续的30页") input[type="file"]').set_input_files("upload_docs/doc.pdf")
    # 等待上传成功
    await page.wait_for_load_state("networkidle")


    await page.click('button:has-text("下一步")')
    await page.wait_for_load_state("networkidle")
    print("✅ Step4 完成")

async def step5(page):
    await page.click('span:has-text("电子证书")')
    # await page.click('button:has-text("下一步")')
    # await page.wait_for_load_state("networkidle")
    print("✅ Step5 完成")


# -------------------------------------------

async def main():
    async with async_playwright() as pw:
        page = await login_or_load_cookies(pw)
        page.set_default_timeout(0)              # 所有等待操作不超时
        info = load_info()

        await step1(page)
        await step2(page, info)
        await step3(page)
        await step4(page, info)
        await step5(page)
        print("🎉 已完成前 5 步，等待你确认下一步提交")
        print("🎉 浏览器仍然打开，按 Ctrl+C 退出")
        await asyncio.Event().wait()   # 阻塞，浏览器保持打开

if __name__ == "__main__":
    asyncio.run(main())
