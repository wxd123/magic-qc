# business/facial/symmetry_checker.py

"""
面部对称性分析业务模块
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

from magic_qc.core.base_checker import BaseChecker
from magic_qc.technology.facial.symmetry import SymmetryCalculator
from magic_qc.technology.facial.feature_detector import FeatureDetector
from magic_qc.management.rules.facial.symmetry_rules import FacialSymmetryRules
from magic_qc.business.facial.eye.eye_checker import EyeChecker  # 新增导入


class SymmetryChecker(BaseChecker):
    """面部对称性分析业务类"""
    
    def __init__(self):
        super().__init__(name="SymmetryChecker", version="1.0.0")
        self.calculator = SymmetryCalculator()
        self.detector = FeatureDetector()
        self.rules = FacialSymmetryRules()
        self.eye_checker = EyeChecker()  # 新增
    
    def check(self, image_path: str) -> Dict[str, Any]:
        """分析单张图片的面部对称性"""
        img = cv2.imread(image_path)
        if img is None:
            return {
                "passed": False,
                "score": 0,
                "error": "无法读取图片",
                "filename": Path(image_path).name
            }
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 整体对称性计算
        left, right_mirrored = self.calculator.split_mirror(gray)
        overall_score = self.calculator.compute_diff(left, right_mirrored)
        lr_ratio = self.calculator.compute_intensity_ratio(left, right_mirrored)
        
        # 人脸检测
        faces = self.detector.detect_faces(gray)
        if len(faces) == 0:
            return {
                "passed": False,
                "score": 0,
                "error": "未检测到人脸",
                "filename": Path(image_path).name
            }
        
        # 获取第一张人脸区域
        x, y, w, h = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        
        # 使用 EyeChecker 评估眼睛
        eye_result = self.eye_checker.check(face_roi)
        
        # 动态计算真实性评分（基于多个因素）
        authenticity_score = self._calculate_authenticity_score(
            overall_score=overall_score,
            eye_symmetry=eye_result['eye_symmetry'],
            lr_ratio=lr_ratio,
            eyes_detected=eye_result['eyes_detected']
        )
        
        # 判断是否真实
        is_realistic = authenticity_score >= 60
        
        # 规则判断
        symmetry_level = self.rules.get_symmetry_level(overall_score)
        recommendation = self.rules.get_recommendation(authenticity_score, is_realistic)
        
        # 综合评分（使用真实性分数）
        score = authenticity_score
        
        return {
            "passed": is_realistic,
            "score": round(score, 1),
            "filename": Path(image_path).name,
            "overall_symmetry": round(overall_score, 4),
            "symmetry_level": symmetry_level,
            "authenticity_score": round(authenticity_score, 1),
            "is_realistic": is_realistic,
            "recommendation": recommendation,
            "details": {
                "left_right_ratio": round(lr_ratio, 4),
                "eye_symmetry": eye_result['eye_symmetry'],
                "eyes_detected": eye_result['eyes_detected'],
                "face_detected": True
            }
        }
    
    def _calculate_authenticity_score(self, overall_score: float, eye_symmetry: float,
                                   lr_ratio: float, eyes_detected: int) -> float:
        """
        真实性评分 - 基于真实人脸区间
        
        真实人脸特征区间：
        - 整体对称性：0.80 - 0.88（最佳区间）
        - 眼睛对称性：0.82 - 0.90（最佳区间）
        - 亮度平衡：0.85 - 0.95（最佳区间）
        """
        score = 0.0
        
        # 1. 整体对称性评分 (40分)
        # 最佳区间 [0.80, 0.88]，区间内满分，区间外线性衰减
        optimal_low = 0.80
        optimal_high = 0.88
        overall_score = self._score_in_range(overall_score, optimal_low, optimal_high, 40)
        score += overall_score
        
        # 2. 眼睛对称性评分 (30分)
        # 最佳区间 [0.82, 0.90]
        eye_score = self._score_in_range(eye_symmetry, 0.82, 0.90, 30)
        score += eye_score
        
        # 3. 亮度平衡评分 (20分)
        # 最佳区间 [0.85, 0.95]
        lr_score = self._score_in_range(lr_ratio, 0.85, 0.95, 20)
        score += lr_score
        
        # 4. 眼睛检测评分 (10分)
        if eyes_detected >= 2:
            score += 10
        elif eyes_detected == 1:
            score += 5
        
        return min(100, max(0, score))

    def _score_in_range(self, value: float, low: float, high: float, max_score: float) -> float:
        """
        区间评分函数
        
        区间内：满分
        区间外：线性衰减，超出边界越多分数越低
        """
        if low <= value <= high:
            return max_score
        
        # 计算偏离距离
        if value < low:
            deviation = low - value
            max_deviation = low  # 从 low 降到 0 的距离
        else:
            deviation = value - high
            max_deviation = 1 - high  # 从 high 升到 1 的距离
        
        # 线性衰减，最低0分
        if deviation >= max_deviation:
            return 0
        
        return max_score * (1 - deviation / max_deviation)
    
    def get_supported_formats(self) -> List[str]:
        return ['.jpg', '.png', '.jpeg', '.bmp']