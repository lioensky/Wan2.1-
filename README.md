# Wan2.1 视频生成工具

这是一个基于硅基流动接口的图生视频生成工具，可以将静态图片转换为动态视频。该工具通过调用API接口，支持多种分辨率的视频生成，并提供了便捷的使用方式。

## 功能特点

- 支持多种图片格式输入
- 自动调整图片格式，尺寸和裁剪
- 支持多种视频分辨率（16:9、9:16、1:1、4:3、3:4）
- 自动选择最接近的宽高比
- 支持自定义提示词
- 提供生成历史记录
- 支持异步视频生成和状态查询

## 广告内容
https://cloud.siliconflow.cn/i/HxM1olJu
点击邀请链接获得共享额度支持作者。

## 环境要求

- Python 3.6+
- 安装requirements.txt中列出的依赖包
- 有效的API密钥

## 安装步骤

1. 克隆或下载项目到本地
2. 安装依赖包：
   ```
   pip install -r requirements.txt
   ```
3. 配置config.env文件，包含以下内容：
   ```
   API_Key=你的API密钥
   prompt=生成视频的提示词
   negative_prompt=负面提示词
   ModelName=使用的模型名称
   ```

## 使用说明

1. 准备图片文件：
   - 将要处理的图片文件重命名为image.xxx（支持常见图片格式）
   - 将图片放在项目根目录下

2. 运行程序：
   - 方式一：直接运行StartWan.bat批处理文件
   - 方式二：分别运行以下Python脚本
     ```
     python wan2.1post.py  # 提交视频生成请求
     python wan2.1get.py   # 查询视频生成状态
     ```

3. 查看结果：
   - 生成的视频将以requestId命名保存在项目目录下
   - 生成历史记录保存在PostHistory.txt文件中
   - 当前请求ID保存在post.txt文件中

## 文件说明

- `wan2.1post.py`: 负责提交视频生成请求，处理图片并上传
- `wan2.1get.py`: 负责查询视频生成状态和下载生成的视频
- `StartWan.bat`: 批处理脚本，用于一键运行程序
- `config.env`: 配置文件，存储API密钥和生成参数
- `requirements.txt`: 项目依赖包列表
- `post.txt`: 存储当前请求ID
- `PostHistory.txt`: 记录生成历史

## 注意事项

1. 确保config.env文件配置正确
2. 图片文件必须以image开头
3. 保持网络连接稳定
4. 视频生成可能需要一定时间，请耐心等待
