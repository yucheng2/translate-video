from src.modules.subtitle_translator import SubtitleTranslator
from src.utils.config import Config
import os

# 指定字幕文件路径
subtitle_path = '/Users/yuchengfan/Documents/test/script/translate-video/output/subtitles/input.srt'

# 初始化配置和翻译器
config = Config()
translator = SubtitleTranslator(config)

try:
    # 翻译字幕
    translated_path = translator.translate_subtitle(subtitle_path, 'en')
    print(f'翻译成功: {translated_path}')
    
    # 读取翻译结果
    with open(translated_path, 'r', encoding='utf-8') as f:
        print('翻译结果:')
        # print(f.read())
except Exception as e:
    print(f'翻译失败: {e}')
    import traceback
    traceback.print_exc()
