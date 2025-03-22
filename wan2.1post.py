import os
import base64
import requests
import time
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# 支持的分辨率和宽高比
SUPPORTED_RESOLUTIONS = {
    "16:9": (1280, 720),
    "9:16": (720, 1280),
    "1:1": (960, 960),
    "4:3": (1024, 768),
    "3:4": (768, 1024)
}

def get_closest_aspect_ratio(width, height):
    """计算最接近的支持宽高比"""
    aspect_ratio = width / height
    ratios = {
        "16:9": 16/9,
        "9:16": 9/16,
        "1:1": 1,
        "4:3": 4/3,
        "3:4": 3/4
    }
    
    # 找到最接近的宽高比
    closest_ratio = min(ratios.items(), key=lambda x: abs(x[1] - aspect_ratio))
    return closest_ratio[0]

def resize_and_crop_image(image_path, target_resolution):
    """调整图片大小并裁切到目标分辨率"""
    img = Image.open(image_path)
    original_width, original_height = img.size
    target_width, target_height = target_resolution

    # 先按比例缩放，使短边匹配目标分辨率
    if original_width / original_height > target_width / target_height:
        # 宽图，按高度缩放
        new_height = target_height
        new_width = int(original_width * (new_height / original_height))
    else:
        # 高图，按宽度缩放
        new_width = target_width
        new_height = int(original_height * (new_width / original_width))

    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # 裁切到目标分辨率（居中裁切）
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height
    img = img.crop((left, top, right, bottom))

    return img

def image_to_webp_base64(img):
    """将图片转换为 webp 格式并编码为 base64"""
    buffer = BytesIO()
    img.save(buffer, format="WEBP")
    img_bytes = buffer.getvalue()
    base64_encoded = base64.b64encode(img_bytes).decode('utf-8')
    return f"data:image/webp;base64,{base64_encoded}"

def submit_video_request(api_key, image_base64, prompt, negative_prompt, model):
    """提交视频生成请求"""
    url = "https://api.siliconflow.cn/v1/video/submit"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "image": image_base64,
        "seed": 123
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("requestId")
    else:
        raise Exception(f"Failed to submit video request: {response.text}")

def check_video_status(api_key, request_id):
    """检查视频生成状态"""
    url = "https://api.siliconflow.cn/v1/video/status"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {"requestId": request_id}

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def download_video(url, request_id):
    """下载视频并保存到本地"""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        filename = f"{request_id}.mp4"
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Video downloaded successfully as {filename}")
        return filename
    else:
        print(f"Failed to download video: {response.status_code}")
        return None

def main():
    # 加载配置文件
    load_dotenv("config.env")
    api_key = os.getenv("API_Key")
    prompt = os.getenv("prompt")
    negative_prompt = os.getenv("negative_prompt")
    model = os.getenv("ModelName")

    # 查找并读取本地图片文件（支持任何格式）
    image_file = None
    for file in os.listdir("."):
        if file.lower().startswith("image."):
            image_file = file
            break
    
    if not image_file:
        raise FileNotFoundError("No image file found in project folder. Please ensure there is an image file starting with 'image.'")
    
    image_path = image_file
    print(f"Using image file: {image_file}")
    
    # 检查文件是否可以被PIL打开
    try:
        with Image.open(image_path) as test_img:
            pass
    except Exception as e:
        raise ValueError(f"The image file '{image_file}' cannot be processed: {str(e)}")

    # 获取图片原始尺寸并确定目标分辨率
    with Image.open(image_path) as img:
        width, height = img.size
    target_ratio = get_closest_aspect_ratio(width, height)
    target_resolution = SUPPORTED_RESOLUTIONS[target_ratio]

    # 处理图片
    processed_img = resize_and_crop_image(image_path, target_resolution)
    image_base64 = image_to_webp_base64(processed_img)

    # 提交视频生成请求
    print("Submitting video generation request...")
    request_id = submit_video_request(api_key, image_base64, prompt, negative_prompt, model)
    print(f"Request submitted. Request ID: {request_id}")
    
    # 将requestId保存到post.txt文件中
    with open("post.txt", "w") as f:
        f.write(request_id)
    print("Request ID saved to post.txt")

    # 记录生成历史
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    history_entry = f"[{timestamp}] RequestID: {request_id} | Prompt: {prompt}\n"
    with open("PostHistory.txt", "a", encoding="utf-8") as f:
        f.write(history_entry)
    print("Generation history recorded")

    # 轮询视频生成状态
    while True:
        status_response = check_video_status(api_key, request_id)
        status = status_response.get("status")
        print(f"Current status: {status}")

        if status == "Succeed":
            video_url = status_response.get("results", {}).get("videos", [{}])[0].get("url")
            print(f"Video generated successfully! URL: {video_url}")
            downloaded_file = download_video(video_url, request_id)
            if downloaded_file:
                print(f"Video saved as: {downloaded_file}")
            break
        elif status == "Failed":
            reason = status_response.get("reason", "Unknown error")
            print(f"Video generation failed: {reason}")
            break
        elif status in ["InQueue", "InProgress"]:
            print("Waiting for video generation to complete...")
            time.sleep(5)  # 每5秒检查一次状态
        else:
            print("Unknown status, stopping...")
            break

if __name__ == "__main__":
    main()