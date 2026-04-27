# management/config/reader.py
"""
配置读取器 - 只读，不提供写入功能
"""

from typing import Dict, Any, Optional
from .config_loader import ConfigLoader


class ConfigReader:
    """配置读取器 - 只读"""
    
    def __init__(self, module_name: str, config_filename: str = "config.json"):
        """
        初始化配置读取器
        
        Args:
            module_name: 模块名称
            config_filename: 配置文件名
        """
        self._loader = ConfigLoader(module_name, config_filename)
        self._config = self._loader.load_merged()        
    
    def get(self, key: str, default: Any = None) -> Any:
        """横向获取配置项"""
        return self._config.get(key, default)
    
    def get_path(self, path: str, default: Any = None) -> Any:
        """纵向获取配置项（点分隔路径）"""
        keys = path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default
    
    def get_multi(self, *keys: str, default: Any = None) -> Dict[str, Any]:
        """批量获取多个配置项"""
        result = {}
        for key in keys:
            if '.' in key:
                result[key] = self.get_path(key, default)
            else:
                result[key] = self.get(key, default)
        return result
    
    def reload(self):
        """重新加载配置"""
        self._config = self._loader.load_merged()
    
    def get_config_source(self) -> Dict[str, str]:
        """获取配置来源信息"""
        return {
            "project_config": str(self._loader.get_project_config_path()),
            "user_config": str(self._loader.get_user_config_path()),
            "current_config": str(self._loader.get_current_config_path()),
            "using_user_config": self._loader.is_using_user_config()
        }