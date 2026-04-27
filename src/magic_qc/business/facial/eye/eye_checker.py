# business/facial/eye/eye_checker.py
"""
眼睛真实性评估模块 - 业务域

提供眼睛对称性分析、真实性评分等功能。
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Any
from pathlib import Path

from magic_qc.core.base_checker import BaseChecker
from magic_qc.technology.facial.feature_detector import FeatureDetector
from magic_qc.technology.facial.symmetry import SymmetryCalculator


class EyeChecker(BaseChecker):
    """
    眼睛真实性评估器
    
    负责眼睛的检测、对称性分析和真实性评分。
    
    Examples:
        >>> checker = EyeChecker()
        >>> result = checker.check(face_roi)
        >>> print(f"眼睛对称性: {result['eye_symmetry']}")
        >>> print(f"真实性评分: {result['authenticity_score']}")
    """
    
    def __init__(self):
        super().__init__(name="EyeChecker", version="1.0.0")
        self.detector = FeatureDetector()
        self.calculator = SymmetryCalculator()
    
    def check(self, face_roi: np.ndarray) -> Dict[str, Any]:
        """
        评估眼睛真实性
        
        Args:
            face_roi: 人脸区域灰度图像
        
        Returns:
            包含眼睛检测结果和对称性分数的字典
        """
        # 检测眼睛
        eyes = self.detector.detect_eyes(face_roi)
        
        # 计算眼睛对称性
        eye_symmetry = self._compute_eye_symmetry(eyes, face_roi)
        
        # 计算真实性评分
        authenticity_score = self._calculate_authenticity_score(
            eyes_count=len(eyes),
            eye_symmetry=eye_symmetry
        )
        
        return {
            "eyes_detected": len(eyes),
            "eye_symmetry": round(eye_symmetry, 4),
            "authenticity_score": round(authenticity_score, 1),
            "is_realistic": authenticity_score >= 60,
            "details": {
                "eye_positions": eyes,
                "face_roi_shape": face_roi.shape
            }
        }
    
    def _compute_eye_symmetry(self, eyes: List[Tuple[int, int, int, int]], 
                              face_roi: np.ndarray) -> float:
        """
        计算两只眼睛的对称性
        
        Args:
            eyes: 眼睛位置列表，每个元素为 (x, y, w, h)
            face_roi: 人脸区域灰度图像
        
        Returns:
            眼睛对称性分数 (0-1)
        """
        if len(eyes) < 2:
            return 0.85  # 默认值
        
        # 按 x 坐标排序（左眼到右眼）
        sorted_eyes = sorted(eyes, key=lambda e: e[0])
        left_eye = sorted_eyes[0]
        right_eye = sorted_eyes[1]
        
        # 提取左右眼区域
        lx, ly, lw, lh = left_eye
        rx, ry, rw, rh = right_eye
        
        # 边界检查
        h_img, w_img = face_roi.shape
        if lx + lw > w_img or ly + lh > h_img or rx + rw > w_img or ry + rh > h_img:
            return 0.85
        
        left_eye_roi = face_roi[ly:ly+lh, lx:lx+lw]
        right_eye_roi = face_roi[ry:ry+rh, rx:rx+rw]
        
        # 检查区域是否有效
        if left_eye_roi.size == 0 or right_eye_roi.size == 0:
            return 0.85
        
        # 调整尺寸一致
        h = min(left_eye_roi.shape[0], right_eye_roi.shape[0])
        w = min(left_eye_roi.shape[1], right_eye_roi.shape[1])
        
        if h == 0 or w == 0:
            return 0.85
        
        left_resized = cv2.resize(left_eye_roi, (w, h))
        right_resized = cv2.resize(right_eye_roi, (w, h))
        
        # 计算对称性
        return self.calculator.compute_diff(left_resized, right_resized)
    
    def _calculate_authenticity_score(self, eyes_count: int, eye_symmetry: float) -> float:
        """
        计算眼睛真实性评分
        
        Args:
            eyes_count: 检测到的眼睛数量
            eye_symmetry: 眼睛对称性分数
        
        Returns:
            真实性评分 (0-100)
        """
        score = 0.0
        
        # 1. 眼睛检测评分 (40分)
        if eyes_count >= 2:
            score += 40
        elif eyes_count == 1:
            score += 20
        else:
            score += 5
        
        # 2. 眼睛对称性评分 (60分)
        if eye_symmetry >= 0.85:
            score += 60
        elif eye_symmetry >= 0.75:
            score += 45
        elif eye_symmetry >= 0.65:
            score += 30
        else:
            score += 15
        
        return min(100, score)
    
    def get_supported_formats(self) -> List[str]:
        return ['.jpg', '.png', '.jpeg', '.bmp']