# business/facial/quality_checker.py

"""
人脸图像质量分析业务模块
"""

import cv2
from pathlib import Path
from typing import Dict, Any, List, Optional

from magic_qc.core.base_checker import BaseChecker
from magic_qc.technology.facial.quality_analyzer import QualityAnalyzer
from magic_qc.management.rules.facial.quality_rules import FaceQualityRules


class FaceQualityChecker(BaseChecker):
    """人脸图像质量分析业务类"""
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__(name="FaceQualityChecker", version="1.0.0")
        self.analyzer = QualityAnalyzer()
        self.rules = FaceQualityRules(config_path)
    
    def check(self, image_path: str) -> Dict[str, Any]:
        """分析单张图片的质量"""
        img = cv2.imread(image_path)
        if img is None:
            return {
                "passed": False,
                "score": 0,
                "error": "无法读取图片",
                "filename": Path(image_path).name,
                "clarity": 0,
                "contrast": 0,
                "edge_density": 0,
                "noise_level": 0
            }
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 计算所有质量指标
        metrics = self.analyzer.calculate_all_metrics(img)
        
        # 提取各指标值
        clarity = metrics.get("clarity", 0)
        contrast = metrics.get("contrast", 0)
        edge_density = metrics.get("edge_density", 0)
        noise_level = metrics.get("noise_level", 0)
        
        # 应用规则获取质量等级和评分
        quality_level = self.rules.get_quality_level(metrics)
        quality_score = self.rules.calculate_quality_score(metrics)
        recommendation = self.rules.get_recommendation(quality_level, quality_score)
        
        # 直接从 rules 获取通过阈值
        scoring_config = self.rules.get_scoring_config()
        pass_threshold = scoring_config.get('pass_threshold', 60)
        passed = quality_score >= pass_threshold
        
        # 从 rules 获取状态文本
        status, _ = self.rules.get_status_and_color(quality_score)
        
        return {
            "passed": passed,
            "score": round(quality_score, 1),
            "filename": Path(image_path).name,
            "quality_level": quality_level,
            "status": status,
            "recommendation": recommendation,
            # 独立指标字段
            "clarity": round(clarity, 2),
            "contrast": round(contrast, 2),
            "edge_density": round(edge_density, 4),
            "noise_level": round(noise_level, 2),
            "metrics": {
                "clarity": round(clarity, 2),
                "contrast": round(contrast, 2),
                "edge_density": round(edge_density, 4),
                "noise_level": round(noise_level, 4)
            }
        }
    
    def get_supported_formats(self) -> List[str]:
        return ['.jpg', '.png', '.jpeg', '.bmp']