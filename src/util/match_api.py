import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.sporttery.cn/"
}

def fetch_api(url):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    try:
        resp.raise_for_status()
    except Exception as e:
        print(f"请求失败，状态码: {resp.status_code}, url: {url}")
        return None
    try:
        return resp.json()
    except Exception as e:
        print(f"JSON 解析失败，url: {url}, 返回内容: {resp.text[:200]}")
        return None
