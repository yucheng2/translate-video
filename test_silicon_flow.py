from src.modules.subtitle_translator import SubtitleTranslator
from src.utils.config import Config
import tempfile
import os

# 创建测试字幕内容
test_subtitle = '''1
00:00:00,000 --> 00:00:05,000
你好，世界！

2
00:00:05,000 --> 00:00:10,000
这是一个测试字幕。'''

# 硅基流动API密钥
SILICON_FLOW_API_KEY = 'sk-pzcisdgyxzlpjwaylyyvcnrvxwwdbjoyoixcppmbtxydqalx'

# 初始化配置和翻译器
config = Config()
translator = SubtitleTranslator(config, SILICON_FLOW_API_KEY)

# 创建临时字幕文件
with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8') as f:
    f.write(test_subtitle)
    temp_path = f.name

try:
    # 翻译字幕
    translated_path = translator.translate_subtitle(temp_path, 'en')
    print(f'翻译成功: {translated_path}')
    
    # 读取翻译结果
    with open(translated_path, 'r', encoding='utf-8') as f:
        print('翻译结果:')
        print(f.read())
finally:
    # 清理临时文件
    os.unlink(temp_path)
