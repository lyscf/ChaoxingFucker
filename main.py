import asyncio
import re
import requests
from bs4 import BeautifulSoup






import subchap_process

async def process_chapters(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    chapters = soup.find_all('div', class_='0 p20 btdwh btdwh1 fix')
    tasks = []  # 用于存储所有子章节处理任务

    for chapter in chapters:
        chapter_title = chapter.find('div', class_='chapterText').text.strip()
        print(f"章节名称: {chapter_title}") # 添加章节输出

        subsections = chapter.find('ul').find_all('li')
        for subsection in subsections:
            subsection_index = subsection.find('div', class_='chapter_index').text.strip()
            subsection_title = subsection.find('div', class_='chapterText').text.strip()
            section_link = subsection.find('a', class_='wh wh1').get('href') # 使用get()方法，避免KeyError
            if section_link is None: # 检查链接是否存在
                print(f"小节 {subsection_title} 没有链接")
                continue

            print(f'小节名称: {subsection_title}')
            pattern = r"courseId=(\d+)&knowledgeId=(\d+)"
            match = re.search(pattern, section_link)

            if match:
                course_id = match.group(1)
                knowledge_id = match.group(2)
                print(f"courseId: {course_id}, knowledgeId: {knowledge_id}")
                # 创建异步任务，并添加到tasks列表中
                tasks.append(subchap_process.process_sub_chapter(course_id, knowledge_id))
            else:
                print(f"小节 {subsection_title} 的链接没有匹配到courseId和knowledgeId") # 改进错误信息，显示哪个小节出错
                print(f"链接是: {section_link}") # 打印出错误的链接，方便调试

    if tasks:  # 只有当tasks不为空时才执行
      await asyncio.gather(*tasks) # 并发执行所有子章节处理任务
    else:
        print("[x]没有需要处理的章节。")
        print("[+]尝试使用越权漏洞提取内容")
        await subchap_process.get_data_from_html(html_content)

async def main():
    url = "https://mooc1.chaoxing.com/mooc-ans/course/这里是你的课程ID.html"

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie':'自己写',
        'Pragma': 'no-cache',
        'Referer': 'https://i.chaoxing.com/base?t=173408114514',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"'
    }

    res = requests.get(url, headers=headers)  # 获取网页内容
    if res.status_code == 200: # 检查请求是否成功
        html_content = res.text
        await process_chapters(html_content)
    else:
        print(f"请求失败，状态码：{res.status_code}")

if __name__ == "__main__":
    asyncio.run(main())
