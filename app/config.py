from typing import Dict, Any

class AppConfig:
    DEFAULTS: Dict[str, Any] = {
        'SAVE_DIR': 'predictions',
        'MAX_FILE_SIZE': 10_000_000,  # 10MB
        'ALLOWED_MIME_TYPES': ['image/png', 'image/jpeg'],
        'CACHE_TIMEOUT': 3600,
        'NUM_CLUSTERS': 3
    }
    
    @classmethod
    def get(cls, key: str) -> Any:
        return cls.DEFAULTS.get(key)