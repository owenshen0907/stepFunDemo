#!/usr/bin/env python3
import configparser
import json
import os
import datetime
import sys
import base64

import requests

def read_config():
    config = configparser.ConfigParser()
    config.read('../config.ini')
    # 读取 API 配置；测试环境将 step_api_prod 换成 step_api_test 即可
    api_key = config.get('genmini', 'key')
    api_url = config.get('genmini', 'url')
    return api_key, api_url

# 从配置文件读取
API_KEY, BASE_URL = read_config()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def edit_image(api_key, model, prompt, image_path, base_url):
    """
    Edit image using the Step Fun API

    Args:
        api_key: API key for authentication
        model: Model to use for image editing
        prompt: Text prompt for image editing
        image_path: Path to the input image file
        base_url: Base URL for the API
    """
    if not image_path or not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        return None

    url = f"{base_url}/v1/images/edits"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        with open(image_path, 'rb') as image_file:
            files = {
                'image': (os.path.basename(image_path), image_file, 'image/jpeg')
            }

            data = {
                'prompt': prompt,
                'model': model,
                'n': '1',
                # 'size': '1024x1024'
            }

            response = requests.post(url, headers=headers, files=files, data=data, timeout=60)

        if response.status_code == 200:
            result = response.json()
            return result

        print(f"Error: {response.status_code}")
        print(f"Response text: {response.text}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def main():
    """Main function to test image editing."""

    api_key = API_KEY
    model = "gemini-2.5-flash-image-preview"
    prompt = """
场景：在办公室的桌面上，一台电脑显示器正在打开3D建模软件，屏幕中展示正在制作的人物手办3D模型，建模对象严格基于参考照片中的人物，面部特征、发型、服饰与姿态都与参考照片保持一致，细节还原度极高。  
在显示器前的桌面上，摆放着完成的1/7比例人物手办，带透明支架，PVC材质，光泽感强烈，细致涂装，整体写实但带手办质感，最大程度还原参考照片人物的外貌与服装。  
手办旁边放着一个商品包装盒，包装正面印有大幅人物图像和插画，这些图像和插画都基于参考照片人物设计，保证外貌特征与参考人物完全一致，同时带有日系手办盒的鲜艳配色和插画风格。  
桌面细节：有键盘、鼠标、耳机线材，整体是写实工作室环境。  
光线：明亮的室内摄影风格，高分辨率，突出真实感。  
整体效果：完整展示“参考照片人物 → 3D建模 → 实体手办 → 包装插画”的全过程，手办与包装都最大程度还原参考照片中的人物细节。
"""
    image_path = "../img/人物1.jpeg"
    base_url = BASE_URL

    if not os.path.exists(image_path):
        print(f"请先准备一个测试图片文件: {image_path}")
        print("或修改 image_path 变量指向现有的图片文件")
        return

    result = edit_image(
        api_key=api_key,
        model=model,
        prompt=prompt,
        image_path=image_path,
        base_url=base_url
    )

    if result and "data" in result:
        # 打印接口返回的其他信息
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # 解析图片
        image_base64 = result["data"][0]["b64_json"]
        image_bytes = base64.b64decode(image_base64)

        # 生成带时间戳的文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"edit_result_{timestamp}.png"

        with open(output_path, "wb") as img_file:
            img_file.write(image_bytes)

        print(f"Edited image saved to {output_path}")


if __name__ == "__main__":
    main()