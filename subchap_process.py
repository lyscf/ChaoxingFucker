import json
import aiohttp
import asyncio
import re
from bs4 import BeautifulSoup


async def process_unknown_file(filehash):
    """Fetches information about a file with the given hash.

    Args:
        filehash (str): The hash of the file.

    Returns:
        dict: A dictionary containing information about the file,
              or None if the request fails.
    """
    url = f"https://mooc1.chaoxing.com/ananas/status/{filehash}"
    headers = {
        "Accept": "*/*",
        "Referer": "https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2024-1128-1842",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                text = await response.text()
                if ".pdf" in text:
                    print("[+]Processing doc file...")
                    await process_doc_file(filehash)
                elif "duration" in text:
                    print("[+]Processing video file...")
                    await process_video_file(filehash)
                else:
                    print(await response.json())  # 同样需要使用 await 获取 response.json() 的值
    except aiohttp.ClientError as e:
        print(f"Error fetching file status: {e}")
        return None


async def download_file(url, session, filename):
    """Downloads a file from the given URL and saves it with the specified filename.

    Args:
        url (str): The URL of the file to download.
        session (aiohttp.ClientSession): The aiohttp session object.
        filename (str): The name of the file to save.
    """
    print(f"[+] Downloading {filename}")

    async with session.get(url) as response:
        response.raise_for_status()
        with open(filename, "wb") as file:
            while True:
                chunk = await response.content.read(1024)
                if not chunk:
                    break
                file.write(chunk)
    print(f"[+] Downloaded {filename}")


async def process_video_file(filehash):
    """Fetches information and potentially downloads a video file.

    Args:
        filehash (str): The hash of the video file.
    """
    url = f"https://mooc1.chaoxing.com/ananas/status/{filehash}"
    headers = {
        "Accept": "*/*",
        "Referer": "https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2024-1128-1842",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
    except aiohttp.ClientError as e:
        print(f"Error fetching video file status: {e}")
        return

    if data["status"] == "pending" or data["status"] == "waiting":
        print("[!] Video file is waiting for format conversion")
    else:
        print(f"[+] Duration: {data['duration']}")
        print(f"[+] Filename: {data['filename']}")
        print(f"[+] Download URL: {data['http']}")

        print(f"[+] Screenshot: {data['screenshot']}")
        try:
            print(f"[+] MP3: {data['mp3']}")
        except KeyError:
            print("[x] MP3 file not found")

        # Download video logic can be added here, checking data["http"] and calling download_file


async def process_doc_file(filehash):
    """Fetches information and potentially downloads a document file.

    Args:
        filehash (str): The hash of the document file.
    """
    url = f"https://mooc1.chaoxing.com/ananas/status/{filehash}"
    headers = {
        "Accept": "*/*",
        "Referer": "https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2024-1128-1842",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
    except aiohttp.ClientError as e:
        print(f"Error fetching document file status: {e}")
        return

    print(f"[+] Filename: {data['filename']}")
    print(f"[+] Download URL: {data['download']}")

    print(f"[+] PDF: {data['pdf']}")
    async with aiohttp.ClientSession() as session:
        await download_file(data["pdf"], session, data["filename"])
    # Download document logic can be added here, checking data["download"] and calling download_file


async def fetch_html(url, headers):
    """Fetches HTML content from the given URL.

    Args:
        url (str): The URL to fetch.
        headers (dict): The request headers.

    Returns:
        str: The fetched HTML content, or None if the request fails.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as e:
            print(f"Error fetching HTML: {e}")
            return None


async def process_sub_chapter(course_id, chapter_id):
    """Processes a sub-chapter to extract video and document information.

    Args:
        course_id (str): The ID of the course.
        chapter_id (str): The ID of the chapter.
    """
    base_url = f"https://mooc1.chaoxing.com/mooc-ans/nodedetailcontroller/visitnodedetail?courseId={course_id}&knowledgeId={chapter_id}"
    print(f"[+] 爬取URL: {base_url}")

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="133", "Google Chrome";v="133", "Not?A_Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
    }

    html_content = await fetch_html(base_url, headers)
    if not html_content:
        print("[!] Failed to fetch HTML")
        return

    soup = BeautifulSoup(html_content, "html.parser")

    # 提取ktoken
    ktoken_match = re.search(r'"ktoken":"(.*?)"', str(soup))
    if not ktoken_match:
        print("[!] ktoken not found!")
        return
    ktoken = ktoken_match.group(1)
    print(f"[+] Find ktoken: {ktoken}")

    async def process_iframes(iframes, process_func, objectid_regex=r'"objectid":"(.*?)"'):
        tasks = []
        for iframe in iframes:
            data_attr = iframe.get("data")
            if data_attr:
                match = re.search(objectid_regex, data_attr)
                if match:
                    objectid = match.group(1)
                    print(f"[+] Find objectid: {objectid}")
                    tasks.append(process_func(objectid))
        if tasks:
            await asyncio.gather(*tasks)

    # 处理视频
    print("[+] Search for video file")
    video_iframes = soup.find_all("iframe", attrs={"class": "ans-module ans-insertvideo-retract ans-attach-online"})
    await process_iframes(video_iframes, process_video_file)

    # 处理章节考试
    print("[+] Search for chapter exam")
    exam_iframes = soup.find_all("iframe", attrs={"class": "ans-module ans-work-module"})
    for iframe in exam_iframes:
        data_attr = iframe.get("data")
        if data_attr:
            try:
                data_json = json.loads(data_attr.replace('\\"', '"'))  # Properly handle escaped quotes
                workid = data_json["_jobid"].strip("work-")
                title = data_json.get("title")
                print(f"[+] Find workid: {workid} title: {title}")
                url = f"https://mooc1.chaoxing.com/mooc-ans/api/selectWorkQuestion?workId={workid}&ut=null&classId=0&courseId={course_id}&utenc=null&ktoken={ktoken}&fromType=portal&classIdForPortal=0&chapterId={chapter_id}"
                print(f"[+] Exam API URL: {url}")
                # 在此处添加异步请求以解析题目信息
            except json.JSONDecodeError as e:
                print(f"[!] Error decoding JSON: {e}, data: {data_attr}")

    # 处理文档
    print("[+] Search for document")
    doc_iframes = soup.find_all("iframe", attrs={"class": "ans-module ans-insertdoc-module ans-attach-online"})
    doc_iframes.extend(soup.find_all("iframe", attrs={"class": "ans-module ans-attach-online ans-insertdoc-module"}))
    doc_iframes.extend(soup.find_all("iframe", attrs={"class": "ans-module ans-insertdoc-retract ans-attach-online"}))
    await process_iframes(doc_iframes, process_doc_file)


async def get_data_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    data = []
    tasks = []

    li_tags = soup.find_all('li')

    for li in li_tags:
        data_attr = li.get('data')
        if data_attr:
            matches = re.findall(r'_([0-9a-f]{32})_', data_attr)
            for match in matches:
                print("[+] 匹配到ID", match)
                data.append(match)
                tasks.append(process_unknown_file(match))

    if tasks:
        results = await asyncio.gather(*tasks)
    else:
        print("没有需要处理的文档。")

