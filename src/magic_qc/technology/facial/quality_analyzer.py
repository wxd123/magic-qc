# technology/facial/quality_analyzer.py
"""
图像质量分析模块 - 技术域

提供图像质量的原子计算能力。
"""

import cv2
import numpy as np
from typing import Dict


class QualityAnalyzer:
    """图像质量分析器 - 原子计算能力"""
    
    @staticmethod
    def calculate_clarity(gray: np.ndarray) -> float:
        """计算清晰度（拉普拉斯方差法）"""
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())
    
    @staticmethod
    def calculate_contrast(gray: np.ndarray) -> float:
        """计算对比度（标准差法）"""
        return float(np.std(gray))
    
    @staticmethod
    def calculate_edge_density(gray: np.ndarray) -> float:
        """计算边缘密度"""
        edges = cv2.Canny(gray, 50, 150)
        return float(np.sum(edges > 0) / edges.size)
    
    @staticmethod
    def estimate_noise(gray: np.ndarray, block_size: int = 32) -> float:
        """估计噪声水平"""
        h, w = gray.shape
        noise_levels = []
        
        for i in range(0, h, block_size):
            for j in range(0, w, block_size):
                block = gray[i:min(i+block_size, h), j:min(j+block_size, w)]
                if block.size > 0:
                    noise_levels.append(np.std(block))
        
        return float(np.mean(noise_levels)) if noise_levels else 0.0
    
    @staticmethod
    def calculate_all_metrics(img: np.ndarray) -> Dict[str, float]:
        """计算所有质量指标"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        return {
            'clarity': QualityAnalyzer.calculate_clarity(gray),
            'contrast': QualityAnalyzer.calculate_contrast(gray),
            'edge_density': QualityAnalyzer.calculate_edge_density(gray),
            'noise_level': QualityAnalyzer.estimate_noise(gray)
        }