import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import Config
from src.utils.logger import Logger
from src.modules.audio_extractor import AudioExtractor
from src.modules.subtitle_extractor import SubtitleExtractor


class VideoProcessor:
    def __init__(self, config_path=None):
        self.config = Config(config_path)
        self.logger = Logger('VideoProcessor')
        
        self.audio_extractor = AudioExtractor(self.config)
        self.subtitle_extractor = SubtitleExtractor(self.config)
    
    def process_video(self, video_path, language=None):
        try:
            self.logger.info(f'开始处理视频：{video_path}')
            
            audio_path = self.audio_extractor.extract_audio(video_path)
            subtitle_path, result = self.subtitle_extractor.extract_subtitle(audio_path, language=language)
            
            self.logger.info(f'视频处理完成')
            return {
                'audio': audio_path,
                'subtitle': subtitle_path,
            }
        
        except Exception as e:
            self.logger.error(f'视频处理失败: {str(e)}')
            raise
    
    def process_batch(self, video_dir=None, language=None):
        if video_dir is None:
            video_dir = self.config.input_dir
        
        self.logger.info(f'开始批量处理视频：{video_dir}')
        
        audio_paths = self.audio_extractor.batch_extract(video_dir)
        subtitle_paths = self.subtitle_extractor.batch_extract(language=language)
        
        self.logger.info(f'批量处理完成')
        return {
            'audio_files': audio_paths,
            'subtitle_files': subtitle_paths,
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='视频处理工具：提取音频、生成字幕')
    parser.add_argument('--input', '-i', help='输入视频文件或目录')
    parser.add_argument('--language', '-l', help='音频语言（如：zh, en）')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--batch', '-b', action='store_true', help='批量处理模式')
    
    args = parser.parse_args()
    
    processor = VideoProcessor(args.config)
    
    if args.batch:
        result = processor.process_batch(args.input, args.language)
        print(f'批量处理完成！')
        print(f'音频文件: {len(result["audio_files"])} 个')
        print(f'字幕文件: {len(result["subtitle_files"])} 个')
    else:
        if args.input is None:
            print('请指定输入视频文件')
            return
        
        result = processor.process_video(args.input, args.language)
        print(f'处理完成！')
        print(f'音频: {result["audio"]}')
        print(f'字幕: {result["subtitle"]}')


if __name__ == '__main__':
    main()
