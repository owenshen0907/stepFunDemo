#!/usr/bin/env python3
import os, json, base64, requests
import configparser
def read_config():
    config = configparser.ConfigParser()
    config.read('../config.ini')
    # 读取 API 配置；测试环境将 step_api_prod 换成 step_api_test 即可
    api_key = config.get('genmini', 'key')
    api_url = config.get('genmini', 'url')
    return api_key, api_url

# 从配置文件读取
API_KEY, BASE_URL = read_config()
def generate_image_openai_compatible(
    api_key: str,
    base_url: str,
    model: str,
    prompt: str,
    n: int = 1,
    size: str | None = None,            # e.g. "1024x1024"
    response_format: str = "b64_json",  # or "url"
    timeout: int = 120,
):
    url = f"{base_url}/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "response_format": response_format,
    }
    if size:
        payload["size"] = size

    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    if resp.status_code != 200:
        print("Error:", resp.status_code)
        print(resp.text)
        return None

    out = resp.json()
    for i, item in enumerate(out.get("data", []), 1):
        if "b64_json" in item:
            img_bytes = base64.b64decode(item["b64_json"])
            with open(f"gen_{i}.png", "wb") as f:
                f.write(img_bytes)
        elif "url" in item:
            print(f"[{i}] image url:", item["url"])
    return out

if __name__ == "__main__":
    API_KEY = API_KEY
    BASE_URL = BASE_URL
    MODEL = "gemini-2.5-flash-image-preview"
    PROMPT = "neon outline cute nano banana logo, white background, clean vector style"

    res = generate_image_openai_compatible(
        api_key=API_KEY,
        base_url=BASE_URL,
        model=MODEL,
        prompt=PROMPT,
        n=1,
        # size="1024x1024",  # 代理若不支持可忽略
        response_format="b64_json",
    )
    if res:
        with open("gen_result.json", "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        print("Saved: gen_result.json")