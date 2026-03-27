import whisper
import os
import hashlib
import io
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
        
        model_url = self.config.get('whisper_model_url', '')
        
        if model_url:
            self.logger.info(f'使用自定义模型下载链接: {model_url}')
            self.model = self._load_model_from_url(model_url, model_name)
        else:
            self.logger.info(f'加载 Whisper 模型: {model_name}')
            self.model = whisper.load_model(model_name)
    
    def _load_model_from_url(self, url, model_name):
        import torch
        from tqdm import tqdm
        import urllib.request
        from huggingface_hub import HfApi, hf_hub_download
        
        repo_id = self._extract_repo_id_from_url(url)
        
        download_root = os.path.join(os.path.expanduser("~"), ".cache", "whisper", repo_id.replace("/", "_"))
        os.makedirs(download_root, exist_ok=True)
        
        self.logger.info(f'从 HuggingFace 下载模型: {repo_id}')
        
        try:
            api = HfApi()
            files = api.list_repo_files(repo_id=repo_id)
            self.logger.info(f'模型文件列表: {files}')
            
            for file in files:
                if file.endswith(('.bin', '.safetensors', '.json', '.txt')):
                    try:
                        hf_hub_download(
                            repo_id=repo_id,
                            filename=file,
                            local_dir=download_root,
                            local_dir_use_symlinks=False
                        )
                        self.logger.info(f'下载完成: {file}')
                    except Exception as e:
                        self.logger.warning(f'下载 {file} 失败: {e}')
        except Exception as e:
            self.logger.warning(f'使用 HfApi 失败，尝试直接下载: {e}')
            filename = os.path.basename(url)
            if not filename:
                filename = f"{model_name}.bin"
            download_target = os.path.join(download_root, filename)
            
            with urllib.request.urlopen(url) as source, open(download_target, "wb") as output:
                with tqdm(
                    total=int(source.info().get("Content-Length")),
                    ncols=80,
                    unit="iB",
                    unit_scale=True,
                    unit_divisor=1024,
                ) as loop:
                    while True:
                        buffer = source.read(8192)
                        if not buffer:
                            break
                        output.write(buffer)
                        loop.update(len(buffer))
        
        self.logger.info(f'使用 transformers 加载模型: {download_root}')
        
        from transformers import WhisperForConditionalGeneration, WhisperProcessor
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        model = WhisperForConditionalGeneration.from_pretrained(
            download_root,
            local_files_only=True,
            torch_dtype="float32"
        )
        processor = WhisperProcessor.from_pretrained(
            download_root,
            local_files_only=True
        )
        
        class WhisperAdapter:
            def __init__(self, model, processor, device):
                self.model = model
                self.processor = processor
                self.device = device
            
            def transcribe(self, audio_path, language=None):
                import numpy as np
                import librosa
                
                audio, sr = librosa.load(audio_path, sr=16_000)
                
                if language:
                    forced_decoder_ids = self.model.config.forced_decoder_ids
                    if forced_decoder_ids:
                        forced_decoder_ids[0][1] = self.processor.tokenizer.lang_code_to_id[language]
                
                input_features = self.processor(audio, sampling_rate=16_000, return_tensors="pt").input_features
                input_features = input_features.to(self.device)
                
                predicted_ids = self.model.generate(input_features)
                transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
                
                segments = []
                duration = len(audio) / 16_000
                chunk_size = duration / max(1, len(transcription.split()))
                for i, text in enumerate(transcription.split('. ')):
                    segments.append({
                        'start': i * chunk_size,
                        'end': (i + 1) * chunk_size,
                        'text': text
                    })
                
                return {'segments': segments}
        
        adapter = WhisperAdapter(model, processor, device)
        return adapter
    
    def _extract_repo_id_from_url(self, url):
        if 'hf-mirror.com' in url or 'huggingface.co' in url:
            parts = url.split('/')
            for i, part in enumerate(parts):
                if part in ['openai', 'distilbert', 'facebook', 'google', 'microsoft', 'ba'] and i + 1 < len(parts):
                    model_name = parts[i + 1].replace('.bin', '').replace('.safetensors', '').replace('resolve', '').strip()
                    if model_name:
                        return f"{part}/{model_name}"
        return "openai/whisper-base"
    
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
