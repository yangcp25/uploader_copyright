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
        page = await context.new_page()
    else:
        context = await browser.new_context()
        page = await context.new_page()
        # 跳转到登录页 (如果此URL不是登录页，请替换为实际的统一登录URL)
        await page.goto("https://register.ccopyright.com.cn/r11.html#/application")
        
        print("➡️ 尝试自动填写账号密码...")
        # ⚠️ 注意：以下选择器('input[type="text"]')可能需要根据版权中心实际的页面 DOM 进行调整
        # 如果 placeholder 是 "请输入手机号" 等，可以换成 'input[placeholder="请输入手机号"]'
        try:
            # 填入账号
            await page.locator('input[type="text"]').first.fill("18983663382")
            # 填入密码
            await page.locator('input[type="password"]').first.fill("1994Okyang0225.")
            # 点击登录按钮
            await page.click('button:has-text("登录")') 
            
            await asyncio.sleep(2) # 等待可能出现的滑动验证码弹窗

            print("➡️ 尝试处理滑动验证码...")
            # 寻找滑块元素（常见的 class 名如 .slider, .nc_iconfont 等，需根据实际情况修改）
            # 这里假设滑块选择器为 '.slider-btn' (你需要 F12 看一下实际的 class)
            slider = await page.query_selector('.slider-btn') 
            if slider:
                box = await slider.bounding_box()
                # 把鼠标移动到滑块中心
                await page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
                await page.mouse.down()
                # 模拟人为滑动：往右滑动（假设需要滑 300 像素），分步滑动模拟真实轨迹
                await page.mouse.move(box['x'] + 300, box['y'] + box['height'] / 2, steps=15)
                await page.mouse.up()
                print("✅ 自动滑动完成，等待页面跳转...")
                await asyncio.sleep(3)
        except Exception as e:
            print(f"⚠️ 自动登录或滑动识别遇到问题: {e}")

        # 兜底：如果验证码校验失败或行为被拦截，留出手动处理的机会
        print("➡️ 请确认是否已成功登录。如果卡在验证码，请手动拉一下滑块。登录完成后按回车继续...")
        input() 
        await save_cookies(page)

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

    print("➡️ 上传文件 (代码.pdf)...")
    # 上传程序鉴别材料（第一个上传框）
    await page.locator('div.upLoadBox:has-text("源程序前连续的30页") input[type="file"]').set_input_files("upload_docs/代码.pdf")
    print("⏳ 代码文件较大，强制等待 60 秒以确保后端接收完毕...")
    await asyncio.sleep(60)

    print("➡️ 上传文件 (手册.pdf)...")
    # 上传文档鉴别材料（第二个上传框）
    await page.locator('div.upLoadBox:has-text("提交任何一种文档的前连续的30页") input[type="file"]').set_input_files("upload_docs/手册.pdf")
    print("⏳ 手册文件较大，强制等待 60*3 秒以确保后端接收完毕...")
    await asyncio.sleep(60*3)

    print("➡️ 无视可能卡住的上传转圈动画，直接强制点击下一步")
    await page.click('button:has-text("下一步")')
    
    # 给页面跳转预留一点加载时间
    await asyncio.sleep(10)
    print("✅ Step4 完成")
async def step5(page):
    print("➡️ Step5: 选择证书类型并提交")
    await page.click('span:has-text("电子证书")')
    
    print("➡️ 正在点击 保存并提交申请...")
    # 使用 text 定位，兼容它是 button、span 还是 div
    await page.click('text=保存并提交申请')
    
    # 提交后系统通常需要时间处理或进行页面跳转，强制等待几秒确保请求发出去
    await asyncio.sleep(3)
    
    print("✅ Step5 完成，申请已成功提交！")


async def step6(page):
    print("➡️ Step6: 提交后过渡 (立即上传 -> 跳过)")
    # 根据你的描述，点击“立即上传”
    await page.click('text=立即上传')
    await asyncio.sleep(2)
    
    # 点击“跳过”
    await page.click('text=跳过')
    await asyncio.sleep(3)
    print("✅ 过渡完成，进入列表页")

async def step7(context, page, info):
    print("➡️ Step7: 寻找对应软件，打印签章页并静默保存为PDF")
    software_name = info["fullname"]
    
    # 精准定位：找到包含该软件名称的 <li> 行
    row_locator = page.locator(f'li:has(p:text("{software_name}"))')
    
    # 监听新标签页的弹出
    async with context.expect_page() as new_page_info:
        await row_locator.locator('button:has-text("打印签章页")').click()
    
    new_page = await new_page_info.value
    await new_page.wait_for_load_state("networkidle")
    print("✅ 已打开打印预览新标签页")
    
    # ⚠️ 核心黑科技：绕过系统打印弹窗，直接用 CDP 协议将网页静默导出为 PDF
    # 即使在 headless=False (有头模式) 下也能完美工作
    print("⏳ 正在调用底层接口静默生成 PDF...")
    client = await new_page.context.new_cdp_session(new_page)
    # 调整配置：landscape=False(纵向), printBackground=True(保留背景色和图片)
    res = await client.send("Page.printToPDF", {"landscape": False, "printBackground": True})
    
    import base64
    pdf_bytes = base64.b64decode(res["data"])
    
    # 保存到你上一阶段需要的目录，自动覆盖同名文件！
    pdf_save_path = Path("template/sign_assets/用户中心.pdf")
    pdf_save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(pdf_save_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"✅ 签章页 PDF 已自动保存至: {pdf_save_path}")
    
    # 关掉这个新标签页，回到主页面
    await new_page.close()

async def step8(page, info):
    print("➡️ Step8: 返回用户中心，上传已签章文件并最终提交")
    
    # 点击“用户中心”
    await page.click('text=用户中心')
    await asyncio.sleep(3)
    
    software_name = info["fullname"]
    row_locator = page.locator(f'li:has(p:text("{software_name}"))')
    
    print("➡️ 正在上传合成完毕的签章页 PDF...")
    # 找到该行里面的 input[type="file"]
    file_input = row_locator.locator('input[type="file"]')
    
    # ⚠️ 这里填写你用上一个脚本自动生成的“已盖章PDF”的绝对或相对路径
    signed_pdf_path = "template/output/申请表_已签章.pdf"
    await file_input.set_input_files(signed_pdf_path)
    
    print("⏳ 上传中，强制等待 60 秒...")
    await asyncio.sleep(60)
    
    print("➡️ 尝试点击 确认提交...")
    # 注意：我根据你的描述猜测按钮文字是"确认提交"，如果原网页用的是别的词（比如"提交申请"），请修改这里
    await row_locator.locator('button:has-text("确认提交")').click()
    await asyncio.sleep(3)
    print("🎉 全流程完美结束！软著已彻底提交。")
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
        # 新增的后半段流水线
        await step6(page)
        await step7(context, page, info)  # 传入 context
        
        # --- ⚠️ 极度重要的说明 ⚠️ ---
        # 此时你的程序已经把待签名的 PDF 下载到了 template/sign_assets/用户中心.pdf
        # 在真实流水线中，你需要在这里停顿，去调用你的“阶段四：自动盖章” Python 脚本。
        # 如果你把它整合到了同一个项目里，可以直接在这里 await 那个盖章函数。
        print("⚠️ 请确保现在已生成了盖好章的 PDF (template/output/申请表_已签章.pdf)")
        
        await step8(page, info)

        print("🎉 浏览器仍然打开，按 Ctrl+C 退出")
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())