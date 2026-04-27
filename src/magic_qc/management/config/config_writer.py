# management/config/writer.py
"""
配置写入器 - 负责配置的修改和保存
"""

from typing import Dict, Any, Optional
from .config_loader import ConfigLoader
from .config_reader import ConfigReader


class ConfigWriter:
    """配置写入器 - 可读写"""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self._loader = ConfigLoader(module_name)
        self._config = self._loader.load_merged()
    
    # ============================================================
    # 读取方法（继承reader功能）
    # ============================================================
    
    def get(self, key: str, default: Any = None) -> Any:
        """横向获取配置项"""
        return self._config.get(key, default)
    
    def get_path(self, path: str, default: Any = None) -> Any:
        """纵向获取配置项"""
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
    
    # ============================================================
    # 写入方法
    # ============================================================
    
    def set(self, key: str, value: Any):
        """横向设置配置项"""
        self._config[key] = value
    
    def set_path(self, path: str, value: Any):
        """纵向设置嵌套配置项"""
        keys = path.split('.')
        target = self._config
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value
    
    def update(self, updates: Dict[str, Any]):
        """批量更新配置"""
        for key, value in updates.items():
            self.set(key, value)
    
    def update_path(self, updates: Dict[str, Any]):
        """批量更新嵌套配置"""
        for path, value in updates.items():
            self.set_path(path, value)
    
    # ============================================================
    # 保存方法
    # ============================================================
    
    def save(self):
        """保存配置到用户文件"""
        self._loader.save(self._config, to_user_config=True)
    
    def save_as_project(self):
        """保存配置到项目文件（需要权限）"""
        self._loader.save(self._config, to_user_config=False)
    
    # ============================================================
    # 配置管理
    # ============================================================
    
    def reload(self):
        """重新加载配置"""
        self._config = self._loader.load_merged()
    
    def switch_to_user_config(self):
        """切换到用户配置"""
        self._loader.switch_to_user_config()
        self.reload()
    
    def switch_to_project_config(self):
        """切换到项目配置"""
        self._loader.switch_to_project_config()
        self.reload()