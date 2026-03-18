# 视频处理系统

一个简单的视频处理工具，可以从视频中提取音频并使用 Whisper AI 自动生成字幕。

## 功能特性

- 从视频中提取音频
- 使用 Whisper AI 自动生成字幕
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
│   └── subtitles/          # 输出字幕目录
├── src/
│   ├── modules/
│   │   ├── audio_extractor.py      # 音频提取模块
│   │   └── subtitle_extractor.py  # 字幕提取模块
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

### 单个视频处理

```bash
python main.py --input ./input/video.mp4 --language zh
```

### 批量处理

```bash
python main.py --batch --input /path/to/video/directory --language zh
```

### 参数说明

- `--input, -i`: 输入视频文件或目录
- `--language, -l`: 音频语言（如：zh, en）
- `--config, -c`: 配置文件路径
- `--batch, -b`: 批量处理模式

## 配置说明

在 `config/config.json` 中可以配置：

- 输入输出目录
- 音频格式（默认：wav）
- 字幕格式（默认：srt）
- Whisper 模型（默认：base）

## 依赖说明

- `moviepy`: 视频处理
- `openai-whisper`: 语音识别
- `torch`: 深度学习框架

## 注意事项

1. 首次运行会下载 Whisper 模型，需要网络连接
2. 处理大视频文件可能需要较长时间


## 下载bilibili视频

https://www.hellotik.app/zh/bilibili


## 问题

1. warnings.warn("FP16 is not supported on CPU; using FP32 instead")

无影响


