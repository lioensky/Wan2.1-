import os
import requests
import time
from dotenv import load_dotenv

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
        print(f"视频已成功下载为 {filename}")
        return filename
    else:
        print(f"下载视频失败: {response.status_code}")
        return None

def main():
    # 加载配置文件
    load_dotenv("config.env")
    api_key = os.getenv("API_Key")

    # 从post.txt读取requestId
    try:
        with open("post.txt", "r") as f:
            request_id = f.read().strip()
    except FileNotFoundError:
        print("找不到post.txt文件，请先运行wan2.1.py生成视频")
        return
    except Exception as e:
        print(f"读取post.txt时出错: {str(e)}")
        return

    if not request_id:
        print("post.txt文件为空，请先运行wan2.1.py生成视频")
        return

    print(f"正在查询视频生成状态，请求ID: {request_id}")

    # 轮询视频生成状态
    while True:
        try:
            status_response = check_video_status(api_key, request_id)
            status = status_response.get("status")
            print(f"当前状态: {status}")

            if status == "Succeed":
                video_url = status_response.get("results", {}).get("videos", [{}])[0].get("url")
                print(f"视频生成成功！正在下载...")
                downloaded_file = download_video(video_url, request_id)
                if downloaded_file:
                    print(f"视频已保存为: {downloaded_file}")
                break
            elif status == "Failed":
                reason = status_response.get("reason", "未知错误")
                print(f"视频生成失败: {reason}")
                break
            elif status in ["InQueue", "InProgress"]:
                print("等待视频生成完成...")
                time.sleep(5)  # 每5秒检查一次状态
            else:
                print("未知状态，停止查询...")
                break
        except Exception as e:
            print(f"查询状态时出错: {str(e)}")
            break

if __name__ == "__main__":
    main()