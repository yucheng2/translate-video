# 视频处理系统

一个完整的视频处理工具，可以将视频分割成音频，提取字幕，并制作成带字幕的视频。

## 功能特性

- 从视频中提取音频
- 使用 Whisper AI 自动生成字幕
- 将字幕合成到视频中
- 支持批量处理
- 完整的日志记录

## 项目结构

```
translate-video/
├── config/
│   └── config.json          # 配置文件
├── input/                   # 输入视频目录
├── output/
│   ├── audio/              # 输出音频目录
│   ├── subtitles/          # 输出字幕目录
│   └── videos/             # 输出视频目录
├── src/
│   ├── modules/
│   │   ├── audio_extractor.py      # 音频提取模块
│   │   ├── subtitle_extractor.py  # 字幕提取模块
│   │   └── video_composer.py      # 视频合成模块
│   └── utils/
│       ├── config.py              # 配置管理
│       └── logger.py              # 日志管理
├── main.py                  # 主程序入口
└── requirements.txt         # 依赖包
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 单个视频处理（带翻译）

```bash
python main.py --input /path/to/video.mp4 --language zh --translate-to en
```

### 批量处理（带翻译）

```bash
python main.py --batch --input /path/to/video/directory --language zh --translate-to en
```

### 使用 OpenAI API 进行翻译

```bash
python main.py --input /path/to/video.mp4 --language zh --translate-to en --openai-api-key YOUR_API_KEY
```

### 参数说明

- `--input, -i`: 输入视频文件或目录
- `--language, -l`: 音频语言（如：zh, en）
- `--translate-to, -t`: 目标翻译语言（默认：en）
- `--openai-api-key`: OpenAI API 密钥（用于字幕翻译）
- `--config, -c`: 配置文件路径
- `--batch, -b`: 批量处理模式

## 配置说明

在 `config/config.json` 中可以配置：

- 输入输出目录
- 音频格式（默认：wav）
- 字幕格式（默认：srt）
- 视频格式（默认：mp4）
- Whisper 模型（默认：base）
- 字幕样式（字体大小、颜色、位置）

## 依赖说明

- `moviepy`: 视频处理
- `openai-whisper`: 语音识别
- `torch`: 深度学习框架
- `pydub`: 音频处理
- `numpy`: 数值计算
- `Pillow`: 图像处理

## 注意事项

1. 首次运行会下载 Whisper 模型，需要网络连接
2. 需要安装 ImageMagick 用于字幕渲染
3. 处理大视频文件可能需要较长时间
