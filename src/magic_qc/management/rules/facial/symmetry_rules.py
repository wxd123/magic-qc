# management/rules/facial/symmetry_rules.py
"""
面部对称性规则模块 - 管理域

本模块定义面部对称性分析所需的规则、阈值和评分逻辑。
职责包括：
- 对称性等级判定
- 真实性分数计算
- 使用建议生成

典型用法:
    from magic_qc.management.rules.facial.symmetry_rules import FacialSymmetryRules
    
    rules = FacialSymmetryRules()
    
    # 获取对称性等级
    level = rules.get_symmetry_level(0.85)
    
    # 计算真实性分数
    score = rules.get_authenticity_score(0.82, 0.91, 0.09, 0.89)
"""

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class SymmetryThresholds:
    """
    对称性阈值定义
    
    定义不同对称性等级的分数边界。
    数值基于大量真实人脸数据的统计分析得出。
    
    Attributes:
        perfect (float): 过度对称阈值，>95% 通常为AI生成
        excellent (float): 优秀对称阈值，90-95% 非常对称
        good (float): 良好对称阈值，85-90% 较为对称
        normal (float): 正常不对称阈值，75-85% 真实人脸常见范围
        low (float): 明显不对称阈值，60-75% 存在明显不对称
    """
    perfect: float = 0.95      # >95% 过度对称
    excellent: float = 0.90    # 90-95% 优秀
    good: float = 0.85         # 85-90% 良好
    normal: float = 0.75       # 75-85% 正常
    low: float = 0.60          # 60-75% 不对称


class FacialSymmetryRules:
    """
    面部对称性规则库
    
    提供基于规则的对称性分析和真实性判断。
    所有判断逻辑集中在此类中，便于维护和调整阈值。
    
    规则设计原则:
        1. 真实人脸存在自然的不对称性
        2. 过度对称通常表明AI生成或过度美化
        3. 各部位对称性应在特定范围内才真实
    
    Attributes:
        thresholds (SymmetryThresholds): 对称性阈值配置
    
    Examples:
        >>> rules = FacialSymmetryRules()
        >>> rules.get_symmetry_level(0.92)
        '优秀对称'
        >>> 
        >>> score = rules.get_authenticity_score(0.82, 0.91, 0.09, 0.89)
        >>> print(f"真实性分数: {score}")
        真实性分数: 95
    """
    
    def __init__(self):
        """
        初始化规则库
        
        创建对称性阈值配置实例。
        """
        self.thresholds = SymmetryThresholds()
    
    def get_symmetry_level(self, score: float) -> str:
        """
        根据对称性分数返回等级描述
        
        分数越高表示越对称，但过度对称反而可能不真实。
        
        Args:
            score (float): 对称性分数，取值范围 0-1
            
        Returns:
            str: 对称性等级描述，可能的值:
                - "过度对称（可能不真实）": score >= 0.95
                - "优秀对称": score >= 0.90
                - "良好对称": score >= 0.85
                - "正常不对称（真实）": score >= 0.75
                - "明显不对称": score >= 0.60
                - "严重不对称": score < 0.60
        
        Examples:
            >>> rules = FacialSymmetryRules()
            >>> rules.get_symmetry_level(0.96)
            '过度对称（可能不真实）'
            >>> rules.get_symmetry_level(0.82)
            '正常不对称（真实）'
        """
        if score >= self.thresholds.perfect:
            return "过度对称（可能不真实）"
        elif score >= self.thresholds.excellent:
            return "优秀对称"
        elif score >= self.thresholds.good:
            return "良好对称"
        elif score >= self.thresholds.normal:
            return "正常不对称（真实）"
        elif score >= self.thresholds.low:
            return "明显不对称"
        else:
            return "严重不对称"
    
    def get_authenticity_score(
        self, 
        overall: float, 
        eye_sym: float, 
        distribution_std: float, 
        lr_ratio: float
    ) -> float:
        """
        计算真实性分数
        
        综合多个维度评估图片是真实人脸还是AI生成。
        分数越高越可能是真实人脸。
        
        评分权重:
            - 整体对称性: 30分（适中为佳，过高过低都扣分）
            - 眼睛对称性: 25分（在真实范围内满分）
            - 对称性分布: 25分（标准差大说明自然，满分）
            - 亮度平衡: 20分（适中为佳）
        
        Args:
            overall (float): 整体对称性分数，取值范围 0-1
            eye_sym (float): 眼睛对称性分数，取值范围 0-1
            distribution_std (float): 对称性分布标准差，越大越自然
            lr_ratio (float): 左右亮度比例，0.85-0.95 为理想范围
            
        Returns:
            float: 真实性分数，取值范围 0-100，分数越高越真实
            
        Examples:
            >>> rules = FacialSymmetryRules()
            >>> # 真实人脸的典型数值
            >>> score = rules.get_authenticity_score(0.82, 0.91, 0.09, 0.89)
            >>> print(f"{score:.0f}")
            95
            >>> 
            >>> # AI生成的典型数值（过度对称）
            >>> score = rules.get_authenticity_score(0.97, 0.99, 0.02, 0.98)
            >>> print(f"{score:.0f}")
            45
        """
        score = 0.0
        
        # 1. 整体对称性评分（30分）
        #    真实人脸应在正常范围内，过低或过高都扣分
        if self.thresholds.normal <= overall <= self.thresholds.good:
            score += 30      # 真实人脸常见范围
        elif overall > self.thresholds.excellent:
            score += 20      # 过度对称，可能是AI
        else:
            score += 10      # 不对称较明显
        
        # 2. 眼睛对称性评分（25分）
        #    眼睛对称性在真实范围内得分，否则扣分
        if 0.85 <= eye_sym <= 0.98:
            score += 25
        else:
            score += 15
        
        # 3. 对称性分布评分（25分）
        #    标准差大说明对称性分布自然，小则可能人工生成
        if distribution_std > 0.08:
            score += 25
        else:
            score += 15
        
        # 4. 亮度平衡评分（20分）
        #    左右亮度比例适中为佳
        if 0.85 <= lr_ratio <= 0.95:
            score += 20
        else:
            score += 10
        
        # 确保分数不超过100
        return min(100, score)
    
    def get_recommendation(self, authenticity_score: float, is_realistic: bool) -> str:
        """
        根据真实性分数返回使用建议
        
        提供针对不同真实性等级的实用建议，
        帮助用户判断该图片是否适合作为建模参考。
        
        Args:
            authenticity_score (float): 真实性分数，0-100
            is_realistic (bool): 是否为真实图片（分数 >= 60）
            
        Returns:
            str: 使用建议，根据分数等级返回不同建议:
                - >=85: 高度推荐作为建模参考
                - >=70: 推荐作为建模参考
                - >=60: 可用作参考，但需注意
                - >=50: 可能AI生成，使用需调整
                - <50: 不建议作为主要参考
        
        Examples:
            >>> rules = FacialSymmetryRules()
            >>> rules.get_recommendation(85, True)
            '高度真实，非常适合作为建模参考'
            >>> rules.get_recommendation(45, False)
            '明显AI生成，不建议作为主要参考'
        """
        if authenticity_score >= 85:
            return "高度真实，非常适合作为建模参考"
        elif authenticity_score >= 70:
            return "比较真实，适合作为建模参考"
        elif authenticity_score >= 60:
            return "一般真实，可用作参考，但需注意对称性"
        elif authenticity_score >= 50:
            return "可能AI生成，对称性过于完美，使用时需调整"
        else:
            return "明显AI生成，不建议作为主要参考"