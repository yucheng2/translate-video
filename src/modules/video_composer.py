from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from pathlib import Path
import os
from ..utils.logger import Logger


class VideoComposer:
    def __init__(self, config):
        self.config = config
        self.logger = Logger('VideoComposer')
    
    def _parse_srt(self, srt_path):
        subtitles = []
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        blocks = content.strip().split('\n\n')
        for block in blocks:
            lines = block.split('\n')
            if len(lines) >= 3:
                time_line = lines[1]
                text = '\n'.join(lines[2:])
                
                start_str, end_str = time_line.split(' --> ')
                start_time = self._parse_time(start_str)
                end_time = self._parse_time(end_str)
                
                subtitles.append({
                    'start': start_time,
                    'end': end_time,
                    'text': text
                })
        
        return subtitles
    
    def _parse_time(self, time_str):
        time_str = time_str.strip()
        if ',' in time_str:
            time_part, ms_part = time_str.split(',')
            ms = int(ms_part)
        else:
            time_part = time_str
            ms = 0
        
        parts = time_part.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds + ms / 1000
        elif len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds + ms / 1000
        else:
            return float(time_str)
    
    def add_subtitles(self, video_path, subtitle_path, output_path=None):
        try:
            self.logger.info(f'开始添加字幕: {video_path}')
            
            video = VideoFileClip(video_path)
            subtitles = self._parse_srt(subtitle_path)
            
            subtitle_clips = []
            for sub in subtitles:
                txt_clip = TextClip(
                    sub['text'],
                    fontsize=self.config.get('subtitle_font_size', 24),
                    color=self.config.get('subtitle_font_color', 'white'),
                    font='Arial'
                )
                txt_clip = txt_clip.set_position('center').set_start(sub['start']).set_end(sub['end'])
                subtitle_clips.append(txt_clip)
            
            final_video = CompositeVideoClip([video] + subtitle_clips)
            
            if output_path is None:
                video_name = Path(video_path).stem
                output_path = self.config.video_output_dir / f'{video_name}_with_subtitles.{self.config.get("video_format")}'
            
            final_video.write_videofile(
                str(output_path),
                codec=self.config.get('video_codec', 'libx264'),
                audio_codec=self.config.get('audio_codec', 'aac')
            )
            
            video.close()
            final_video.close()
            
            self.logger.info(f'视频合成完成: {output_path}')
            return str(output_path)
        
        except Exception as e:
            self.logger.error(f'视频合成失败: {str(e)}')
            raise
    
    def batch_compose(self, video_dir=None, subtitle_dir=None):
        if video_dir is None:
            video_dir = self.config.input_dir
        if subtitle_dir is None:
            subtitle_dir = self.config.subtitle_output_dir
        
        video_files = list(Path(video_dir).glob('*.mp4')) + list(Path(video_dir).glob('*.avi')) + list(Path(video_dir).glob('*.mov'))
        
        output_paths = []
        for video_file in video_files:
            video_name = video_file.stem
            subtitle_file = Path(subtitle_dir) / f'{video_name}.{self.config.get("subtitle_format")}'
            
            if subtitle_file.exists():
                try:
                    output_path = self.add_subtitles(str(video_file), str(subtitle_file))
                    output_paths.append(output_path)
                except Exception as e:
                    self.logger.error(f'处理视频 {video_file} 失败: {str(e)}')
            else:
                self.logger.warning(f'未找到字幕文件: {subtitle_file}')
        
        return output_paths
