import whisper
from pathlib import Path
from ..utils.logger import Logger


class SubtitleExtractor:
    def __init__(self, config):
        self.config = config
        self.logger = Logger('SubtitleExtractor')
        self.model = None
    
    def load_model(self, model_name=None):
        if model_name is None:
            model_name = self.config.get('whisper_model', 'base')
        
        self.logger.info(f'加载 Whisper 模型: {model_name}')
        self.model = whisper.load_model(model_name)
    
    def extract_subtitle(self, audio_path, output_path=None, language=None):
        try:
            self.logger.info(f'开始提取字幕: {audio_path}')
            
            if self.model is None:
                self.load_model()
            
            result = self.model.transcribe(audio_path, language=language)
            
            if output_path is None:
                audio_name = Path(audio_path).stem
                output_path = self.config.subtitle_output_dir / f'{audio_name}.{self.config.get("subtitle_format")}'
            
            self._save_srt(result['segments'], str(output_path))
            
            self.logger.info(f'字幕提取完成: {output_path}')
            return str(output_path), result
        
        except Exception as e:
            self.logger.error(f'字幕提取失败: {str(e)}')
            raise
    
    def _save_srt(self, segments, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                start_time = self._format_timestamp(segment['start'])
                end_time = self._format_timestamp(segment['end'])
                text = segment['text'].strip()
                
                f.write(f'{i}\n')
                f.write(f'{start_time} --> {end_time}\n')
                f.write(f'{text}\n\n')
    
    def _format_timestamp(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f'{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}'
    
    def batch_extract(self, audio_dir=None, language=None):
        if audio_dir is None:
            audio_dir = self.config.audio_output_dir
        
        audio_files = list(Path(audio_dir).glob('*.wav')) + list(Path(audio_dir).glob('*.mp3'))
        
        subtitle_paths = []
        for audio_file in audio_files:
            try:
                subtitle_path, result = self.extract_subtitle(str(audio_file), language=language)
                subtitle_paths.append(subtitle_path)
            except Exception as e:
                self.logger.error(f'处理音频 {audio_file} 失败: {str(e)}')
        
        return subtitle_paths
