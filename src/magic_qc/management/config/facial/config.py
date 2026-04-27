# management/config/facial/config.py
"""
面部质量配置 - 业务逻辑层（只读）
"""

from typing import Tuple
from ..config_reader import ConfigReader


class FacialQualityConfig:
    """面部质量配置类 - 只读"""
    
    CONFIG_FILENAME = "quality_standards_v2.json"  # 面部专用配置文件名
    
    def __init__(self):
        self._reader = ConfigReader("facial", self.CONFIG_FILENAME)
    
    # 代理到 reader
    def get(self, key: str, default=None):
        return self._reader.get(key, default)
    
    def get_path(self, path: str, default=None):
        return self._reader.get_path(path, default)
    
    def get_multi(self, *keys: str, default=None):
        return self._reader.get_multi(*keys, default=default)
    
    def reload(self):
        self._reader.reload()
    
    def get_config_source(self):
        return self._reader.get_config_source()
    
    # ============================================================
    # 业务便捷方法
    # ============================================================
    
    def get_symmetry_status_and_color(self, symmetry_score: float) -> Tuple[str, str, str]:
        """根据对称性分数返回状态、颜色和图标"""
        excellent = self.get_path("symmetry_thresholds.excellent", 0.9)
        good = self.get_path("symmetry_thresholds.good", 0.8)
        pass_val = self.get_path("symmetry_thresholds.pass", 0.7)
        
        if symmetry_score >= excellent:
            level = 'excellent'
        elif symmetry_score >= good:
            level = 'good'
        elif symmetry_score >= pass_val:
            level = 'pass'
        else:
            level = 'fail'
        
        return (
            self.get_path(f"symmetry_levels.{level}.label", "未知"),
            self.get_path(f"symmetry_levels.{level}.color", "white"),
            self.get_path(f"symmetry_levels.{level}.icon", "📷")
        )
    
    def get_status_and_color(self, quality_score: float) -> Tuple[str, str]:
        """根据质量分数返回状态和颜色"""
        levels = self.get("quality_levels", {})
        
        for level, config in sorted(levels.items(), key=lambda x: x[1].get('min_score', 0), reverse=True):
            if quality_score >= config.get('min_score', 0):
                return config.get('label', '未知'), config.get('color', 'white')
        
        return '不合格', 'red'