#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试进度条功能
"""

import tempfile
from pathlib import Path
from src.modules.subtitle_translator import SubtitleTranslator

# 模拟配置类
class MockConfig:
    def __init__(self):
        self.subtitle_output_dir = Path('.')
    
    def get(self, key, default=None):
        if key == 'subtitle_format':
            return 'srt'
        return default

# 创建测试SRT文件
def create_test_srt():
    srt_content = """
1
00:00:01,000 --> 00:00:03,000
Hello, world!

2
00:00:04,000 --> 00:00:06,000
This is a test subtitle.

3
00:00:07,000 --> 00:00:09,000
Testing progress bar functionality.

4
00:00:10,000 --> 00:00:12,000
Another test subtitle line.

5
00:00:13,000 --> 00:00:15,000
Final test subtitle.
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8') as f:
        f.write(srt_content.strip())
        return f.name

if __name__ == '__main__':
    print("测试进度条功能...")
    
    # 创建模拟配置
    config = MockConfig()
    
    # 创建SubtitleTranslator实例
    translator = SubtitleTranslator(config)
    
    # 创建测试SRT文件
    test_srt = create_test_srt()
    print(f"创建测试SRT文件: {test_srt}")
    
    try:
        # 测试单个文件翻译（带进度条）
        print("\n测试单个文件翻译:")
        output_path = translator.translate_subtitle(test_srt, target_language='zh')
        print(f"翻译完成，输出文件: {output_path}")
        
        # 测试批量翻译（带进度条）
        print("\n测试批量翻译:")
        # 复制测试文件以模拟多个文件
        test_srt2 = str(Path(test_srt).parent / f"{Path(test_srt).stem}_2.srt")
        import shutil
        shutil.copy(test_srt, test_srt2)
        
        translated_paths = translator.batch_translate(subtitle_dir=str(Path(test_srt).parent), target_language='fr')
        print(f"批量翻译完成，输出文件数: {len(translated_paths)}")
        
    finally:
        # 清理测试文件
        import os
        if os.path.exists(test_srt):
            os.remove(test_srt)
        test_srt2 = str(Path(test_srt).parent / f"{Path(test_srt).stem}_2.srt")
        if os.path.exists(test_srt2):
            os.remove(test_srt2)
        # 清理生成的翻译文件
        for ext in ['zh.srt', 'fr.srt']:
            output_file = f"{Path(test_srt).stem}_{ext}"
            if os.path.exists(output_file):
                os.remove(output_file)
            output_file2 = f"{Path(test_srt).stem}_2_{ext}"
            if os.path.exists(output_file2):
                os.remove(output_file2)
    
    print("\n测试完成！")
