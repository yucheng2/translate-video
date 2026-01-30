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
        self.max_translation_chars = self.config.get('max_translation_chars', 4000)
    
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
            
            batches = self._group_subtitles(subtitles)
            
            for batch in tqdm(batches, desc='翻译字幕批次', unit='批次'):
                batch_texts = [sub['text'] for sub in batch]
                combined_text = '|||'.join(batch_texts)
                
                translated_combined = self._translate_text(combined_text, target_language)
                
                translated_texts = self._split_translated_text(translated_combined, len(batch))
                
                for sub, translated_text in zip(batch, translated_texts):
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
    
    def _group_subtitles(self, subtitles):
        batches = []
        current_batch = []
        current_chars = 0
        
        for sub in subtitles:
            text = sub['text']
            text_chars = len(text)
            
            if current_chars + text_chars > self.max_translation_chars and current_batch:
                batches.append(current_batch)
                current_batch = []
                current_chars = 0
            
            current_batch.append(sub)
            current_chars += text_chars
        
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    def _split_translated_text(self, translated_text, expected_count):
        parts = translated_text.split('|||')
        
        if len(parts) == expected_count:
            return [part.strip() for part in parts]
        
        if len(parts) < expected_count:
            result = [part.strip() for part in parts]
            while len(result) < expected_count:
                result.append('')
            return result
        
        result = []
        for i in range(expected_count):
            if i < len(parts):
                result.append(parts[i].strip())
            else:
                result.append('')
        
        return result
    
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
                        {"role": "system", "content": f"You are a professional translator. Your task is to translate the ENTIRE following text to {target_language} accurately. IMPORTANT RULES: 1. The input contains multiple subtitle segments separated by |||. 2. You MUST translate EVERY segment, WITHOUT OMITTING ANY CONTENT. 3. You MUST separate the translated segments with |||. 4. You MUST keep the same number of segments as the input. 5. Do NOT add any extra text or explanations. 6. Translate the text completely and accurately."},
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
                translated_content = result['choices'][0]['message']['content'].strip()
                # 检查翻译结果是否为空或与原文相同
                if not translated_content or translated_content == text:
                    self.logger.warning(f'Translation may have failed, returning original text: {text[:50]}...')
                else:
                    self.logger.info(f'Translation successful, first 100 chars: {translated_content[:100]}...')
                return translated_content
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
    
    def batch_translate(self, subtitle_dir=None, target_language='en', overwrite=False):
        if subtitle_dir is None:
            subtitle_dir = self.config.subtitle_output_dir
        
        subtitle_files = list(Path(subtitle_dir).glob('*.srt'))
        
        translated_paths = []
        for subtitle_file in tqdm(subtitle_files, desc='批量翻译字幕', unit='文件'):
            if overwrite or f'_{target_language}.' not in str(subtitle_file):
                try:
                    translated_path = self.translate_subtitle(str(subtitle_file), target_language)
                    translated_paths.append(translated_path)
                except Exception as e:
                    self.logger.error(f'处理字幕 {subtitle_file} 失败: {str(e)}')
        
        return translated_paths
