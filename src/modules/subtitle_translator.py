import requests
from pathlib import Path
from tqdm import tqdm
from ..utils.logger import Logger


class SubtitleTranslator:
    def __init__(self, config, api_key=None):
        self.config = config
        self.logger = Logger('SubtitleTranslator')
        self.api_key = api_key or self.config.get('siliconflow_api_key')
        self.api_base = "https://api.siliconflow.cn/v1"
        self.model_name = "Pro/Qwen/Qwen2.5-7B-Instruct"
    
    def _parse_srt(self, srt_path):
        subtitles = []
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        blocks = content.strip().split('\n\n')
        for block in blocks:
            lines = block.split('\n')
            if len(lines) >= 3:
                index = lines[0]
                time_line = lines[1]
                text = '\n'.join(lines[2:])
                
                subtitles.append({
                    'index': index,
                    'time': time_line,
                    'text': text
                })
        
        return subtitles
    
    def translate_subtitle(self, subtitle_path, target_language='en', output_path=None):
        try:
            self.logger.info(f'开始翻译字幕: {subtitle_path}')
            
            subtitles = self._parse_srt(subtitle_path)
            
            for sub in tqdm(subtitles, desc='翻译字幕', unit='条'):
                translated_text = self._translate_text(sub['text'], target_language)
                sub['translated_text'] = translated_text
            
            if output_path is None:
                subtitle_name = Path(subtitle_path).stem
                output_path = self.config.subtitle_output_dir / f'{subtitle_name}_{target_language}.{self.config.get("subtitle_format")}'
            
            self._save_translated_srt(subtitles, str(output_path))
            
            self.logger.info(f'字幕翻译完成: {output_path}')
            return str(output_path)
        
        except Exception as e:
            self.logger.error(f'字幕翻译失败: {str(e)}')
            raise
    
    def _translate_text(self, text, target_language):
        try:
            if self.api_key:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": f"You are a professional translator. Translate the following text to {target_language} accurately."},
                        {"role": "user", "content": text}
                    ],
                    "temperature": 0.3
                }
                
                response = requests.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                # 模拟翻译（实际项目中应该使用真实的翻译API）
                self.logger.warning('No API key provided, using mock translation')
                return f"[Translated to {target_language}]: {text}"
        except Exception as e:
            self.logger.error(f'Translation error: {str(e)}')
            return text
    
    def _save_translated_srt(self, subtitles, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            for sub in subtitles:
                f.write(f'{sub["index"]}\n')
                f.write(f'{sub["time"]}\n')
                f.write(f'{sub.get("translated_text", sub["text"])}\n\n')
    
    def batch_translate(self, subtitle_dir=None, target_language='en'):
        if subtitle_dir is None:
            subtitle_dir = self.config.subtitle_output_dir
        
        subtitle_files = list(Path(subtitle_dir).glob('*.srt'))
        
        translated_paths = []
        for subtitle_file in tqdm(subtitle_files, desc='批量翻译字幕', unit='文件'):
            if f'_{target_language}.' not in str(subtitle_file):
                try:
                    translated_path = self.translate_subtitle(str(subtitle_file), target_language)
                    translated_paths.append(translated_path)
                except Exception as e:
                    self.logger.error(f'处理字幕 {subtitle_file} 失败: {str(e)}')
        
        return translated_paths
