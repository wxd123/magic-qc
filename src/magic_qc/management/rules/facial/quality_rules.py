# management/rules/quality_rules.py
"""
人脸图像质量规则模块 - 完全基于JSON配置
"""

from typing import Dict, Optional, Any
from src.magic_qc.management.config.config_manager import ConfigManager


class FaceQualityRules:
    """人脸图像质量规则库 - 完全配置驱动"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化规则库
        
        Args:
            config_path: 配置文件路径，如果不指定则使用默认路径
        """
        # 使用新的配置架构
        if config_path:
            # 如果指定了路径，需要特殊处理
            from src.magic_qc.management.config.config_writer import ConfigWriter
            self._config = ConfigWriter("facial")
            self._config._loader._config_path = config_path
            self._config.reload()
        else:
            self._config = ConfigManager.get_facial_config()
        
        self._load_config()
    
    def _load_config(self):
        """从配置文件加载所有配置"""
        self.thresholds = self._config.get("thresholds", {})
        self.scoring = self._config.get("scoring", {})
        self.quality_levels = self._config.get("quality_levels", {})
        # 从配置中获取分数映射
        self.score_mapping = self.scoring.get('score_mapping', {})
    
    def reload_config(self):
        """重新加载配置（用于动态更新）"""
        self._config.reload()
        self._load_config()
    
    def _get_item_score(self, value: float, thresholds: Dict[str, float]) -> int:
        """
        计算单项指标的分数（值越大越好）
        
        Args:
            value: 指标实际值
            thresholds: 包含 excellent, good, pass 的字典
        
        Returns:
            分数 (0-100)
        """
        if value >= thresholds.get('excellent', float('inf')):
            return self.score_mapping.get('excellent', 100)
        elif value >= thresholds.get('good', float('inf')):
            return self.score_mapping.get('good', 75)
        elif value >= thresholds.get('pass', float('inf')):
            return self.score_mapping.get('pass', 50)
        else:
            return self.score_mapping.get('fail', 25)
    
    def _get_item_score_lower_better(self, value: float, thresholds: Dict[str, float]) -> int:
        """
        计算单项指标的分数（值越小越好）
        
        Args:
            value: 指标实际值
            thresholds: 包含 excellent, good, pass 的字典
        
        Returns:
            分数 (0-100)
        """
        if value <= thresholds.get('excellent', float('-inf')):
            return self.score_mapping.get('excellent', 100)
        elif value <= thresholds.get('good', float('-inf')):
            return self.score_mapping.get('good', 75)
        elif value <= thresholds.get('pass', float('-inf')):
            return self.score_mapping.get('pass', 50)
        else:
            return self.score_mapping.get('fail', 25)
    
    def get_quality_level(self, metrics: Dict[str, float]) -> str:
        """
        获取质量等级
        
        Args:
            metrics: 质量指标字典
        
        Returns:
            质量等级标签
        """
        scores = []
        
        for key, thresholds in self.thresholds.items():
            if key not in metrics:
                continue
            
            value = metrics[key]
            higher_is_better = thresholds.get('higher_is_better', True)
            
            if higher_is_better:
                score = self._get_item_score(value, thresholds)
            else:
                score = self._get_item_score_lower_better(value, thresholds)
            
            scores.append(score)
        
        if not scores:
            return self.quality_levels.get('fail', {}).get('label', '不合格')
        
        avg_score = sum(scores) / len(scores)
        
        # 根据平均分确定等级
        for level, config in self.quality_levels.items():
            if avg_score >= config.get('min_score', 0):
                return config.get('label', '未知')
        
        return self.quality_levels.get('fail', {}).get('label', '不合格')
    
    def calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """
        计算综合质量评分（加权评分）
        
        Args:
            metrics: 质量指标字典
        
        Returns:
            综合评分 (0-100)
        """
        weights = self.scoring.get('weights', {})
        if not weights:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for key, weight in weights.items():
            if key not in metrics:
                continue
            
            value = metrics[key]
            thresholds = self.thresholds.get(key, {})
            pass_threshold = thresholds.get('pass', 1)
            higher_is_better = thresholds.get('higher_is_better', True)
            
            if pass_threshold == 0:
                item_score = 0
            elif higher_is_better:
                # 值越大越好：score = min(100, value/pass_threshold * 100)
                item_score = min(100, (value / pass_threshold) * 100)
            else:
                # 值越小越好：score = max(0, 100 - (value/pass_threshold) * 100)
                item_score = max(0, 100 - (value / pass_threshold) * 100)
            
            total_score += item_score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return round(total_score / total_weight, 1)
    
    def get_recommendation(self, quality_level: str, quality_score: float) -> str:
        """
        根据质量等级返回建议
        
        Args:
            quality_level: 质量等级标签
            quality_score: 质量分数
        
        Returns:
            建议文本
        """
        # 首先根据分数查找对应的建议
        for level, config in self.quality_levels.items():
            if quality_score >= config.get('min_score', 0):
                return config.get('recommendation', '无建议')
        
        return self.quality_levels.get('fail', {}).get('recommendation', '质量较差，不建议使用')
    
    def get_color_for_score(self, quality_score: float) -> str:
        """
        根据分数返回对应的颜色（用于终端显示）
        
        Args:
            quality_score: 质量分数
        
        Returns:
            颜色名称
        """
        for level, config in self.quality_levels.items():
            if quality_score >= config.get('min_score', 0):
                return config.get('color', 'white')
        
        return self.quality_levels.get('fail', {}).get('color', 'red')
    
    def get_status_text(self, quality_score: float) -> str:
        """
        根据分数返回状态文本
        
        Args:
            quality_score: 质量分数
        
        Returns:
            状态文本（优秀/良好/合格/不合格）
        """
        for level, config in self.quality_levels.items():
            if quality_score >= config.get('min_score', 0):
                return config.get('label', '未知')
        
        return self.quality_levels.get('fail', {}).get('label', '不合格')
    
    def get_status_and_color(self, quality_score: float) -> tuple:
        """
        根据分数返回状态文本和颜色
        
        Args:
            quality_score: 质量分数
        
        Returns:
            (status_text, color) 元组
        """
        for level, config in self.quality_levels.items():
            if quality_score >= config.get('min_score', 0):
                return config.get('label', '未知'), config.get('color', 'white')
        
        fail_config = self.quality_levels.get('fail', {})
        return fail_config.get('label', '不合格'), fail_config.get('color', 'red')
    
    def get_scoring_config(self) -> Dict[str, Any]:
        """获取评分配置"""
        return self._config.get("scoring", {})
    
    def get_pass_threshold(self) -> float:
        """获取及格分数阈值"""
        return self.get_scoring_config().get('pass_threshold', 60)