import json
import os
from pathlib import Path


class Config:
    def __init__(self, config_path=None):
        if config_path is None:
            self.base_dir = Path(os.path.dirname(__file__)).parent.parent
            config_path = self.base_dir / 'config' / 'config.json'
        else:
            self.base_dir = Path(os.path.dirname(__file__)).parent.parent
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self._setup_directories()
    
    def _setup_directories(self):
        self.input_dir = self.base_dir / self.config['input_dir']
        self.output_dir = self.base_dir / self.config['output_dir']
        self.audio_output_dir = self.base_dir / self.config['audio_output_dir']
        self.subtitle_output_dir = self.base_dir / self.config['subtitle_output_dir']
        self.video_output_dir = self.base_dir / self.config['video_output_dir']
        
        for dir_path in [self.input_dir, self.output_dir, self.audio_output_dir, 
                         self.subtitle_output_dir, self.video_output_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get(self, key, default=None):
        return self.config.get(key, default)
