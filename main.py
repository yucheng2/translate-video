import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import Config
from src.utils.logger import Logger
from src.modules.audio_extractor import AudioExtractor
from src.modules.subtitle_extractor import SubtitleExtractor
from src.modules.subtitle_translator import SubtitleTranslator
# from src.modules.video_composer import VideoComposer


class VideoProcessor:
    def __init__(self, config_path=None, openai_api_key=None):
        self.config = Config(config_path)
        self.logger = Logger('VideoProcessor')
        
        self.audio_extractor = AudioExtractor(self.config)
        self.subtitle_extractor = SubtitleExtractor(self.config)
        self.subtitle_translator = SubtitleTranslator(self.config, openai_api_key)
        # self.video_composer = VideoComposer(self.config)
    
    def process_video(self, video_path, language=None, translate_to='en'):
        try:
            self.logger.info(f'开始处理视频: {video_path}')
            
            audio_path = self.audio_extractor.extract_audio(video_path)
            subtitle_path, result = self.subtitle_extractor.extract_subtitle(audio_path, language=language)
            # output_path = self.video_composer.add_subtitles(video_path, subtitle_path)
            
            translated_subtitle_path = self.subtitle_translator.translate_subtitle(subtitle_path, translate_to)
            # translated_video_path = self.video_composer.add_subtitles(video_path, translated_subtitle_path)
            
            self.logger.info(f'视频处理完成')
            return {
                'audio': audio_path,
                'subtitle': subtitle_path,
                # 'video': output_path,
                'translated_subtitle': translated_subtitle_path,
                # 'translated_video': translated_video_path
            }
        
        except Exception as e:
            self.logger.error(f'视频处理失败: {str(e)}')
            raise
    
    def process_batch(self, video_dir=None, language=None, translate_to='en'):
        if video_dir is None:
            video_dir = self.config.input_dir
        
        self.logger.info(f'开始批量处理视频: {video_dir}')
        
        audio_paths = self.audio_extractor.batch_extract(video_dir)
        subtitle_paths = self.subtitle_extractor.batch_extract(language=language)
        translated_subtitle_paths = self.subtitle_translator.batch_translate(target_language=translate_to)
        
        # output_paths = self.video_composer.batch_compose()
        
        # self.logger.info(f'批量处理完成，共处理 {len(output_paths)} 个视频')
        self.logger.info(f'批量处理完成')
        return {
            'audio_files': audio_paths,
            'subtitle_files': subtitle_paths,
            'translated_subtitle_files': translated_subtitle_paths,
            # 'video_files': output_paths
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='视频处理工具：提取音频、生成字幕、合成视频')
    parser.add_argument('--input', '-i', help='输入视频文件或目录')
    parser.add_argument('--language', '-l', help='音频语言（如：zh, en）')
    parser.add_argument('--translate-to', '-t', default='en', help='目标翻译语言（如：en, zh）')
    parser.add_argument('--openai-api-key', help='OpenAI API 密钥（用于字幕翻译）')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--batch', '-b', action='store_true', help='批量处理模式')
    
    args = parser.parse_args()
    
    processor = VideoProcessor(args.config, args.openai_api_key)
    
    if args.batch:
        result = processor.process_batch(args.input, args.language, args.translate_to)
        print(f'批量处理完成！')
        print(f'音频文件: {len(result["audio_files"])} 个')
        print(f'字幕文件: {len(result["subtitle_files"])} 个')
        print(f'翻译字幕文件: {len(result["translated_subtitle_files"])} 个')
        print(f'输出视频: {len(result["video_files"])} 个')
    else:
        if args.input is None:
            print('请指定输入视频文件')
            return
        
        result = processor.process_video(args.input, args.language, args.translate_to)
        print(f'处理完成！')
        print(f'音频: {result["audio"]}')
        print(f'字幕: {result["subtitle"]}')
        print(f'翻译字幕: {result["translated_subtitle"]}')
        # print(f'输出视频: {result["video"]}')
        # print(f'翻译字幕视频: {result["translated_video"]}')


if __name__ == '__main__':
    main()
