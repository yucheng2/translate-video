from moviepy import VideoFileClip
import os
from pathlib import Path
from ..utils.logger import Logger


class AudioExtractor:
    def __init__(self, config):
        self.config = config
        self.logger = Logger('AudioExtractor')
    
    def extract_audio(self, video_path, output_path=None):
        try:
            self.logger.info(f'开始提取音频: {video_path}')
            
            video = VideoFileClip(video_path)
            
            if output_path is None:
                video_name = Path(video_path).stem
                output_path = self.config.audio_output_dir / f'{video_name}.{self.config.get("audio_format")}'
            
            video.audio.write_audiofile(str(output_path))
            video.close()
            
            self.logger.info(f'音频提取完成: {output_path}')
            return str(output_path)
        
        except Exception as e:
            self.logger.error(f'音频提取失败: {str(e)}')
            raise
    
    def batch_extract(self, video_dir=None):
        if video_dir is None:
            video_dir = self.config.input_dir
        
        video_files = list(Path(video_dir).glob('*.mp4')) + list(Path(video_dir).glob('*.avi')) + list(Path(video_dir).glob('*.mov'))
        
        audio_paths = []
        for video_file in video_files:
            try:
                audio_path = self.extract_audio(str(video_file))
                audio_paths.append(audio_path)
            except Exception as e:
                self.logger.error(f'处理视频 {video_file} 失败: {str(e)}')
        
        return audio_paths
