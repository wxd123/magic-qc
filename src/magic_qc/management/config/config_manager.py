# management/config/configManager.py
from .facial.config import FacialQualityConfig
from .config_writer import ConfigWriter


class ConfigManager:
    """配置管理器 - 统一入口"""
    
    _instance = None
    _facial_config = None
    _facial_writer = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_facial_config(cls) -> FacialQualityConfig:
        """获取面部配置（只读）"""
        if cls._facial_config is None:
            cls._facial_config = FacialQualityConfig()
        return cls._facial_config
    
    @classmethod
    def get_facial_writer(cls) -> ConfigWriter:
        """获取面部配置写入器（可写）"""
        if cls._facial_writer is None:
            cls._facial_writer = ConfigWriter("facial")
        return cls._facial_writer