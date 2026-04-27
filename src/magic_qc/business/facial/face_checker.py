# business/facial/face_checker.py

from typing import Dict, Any, List, Optional
from pathlib import Path
from magic_qc.core.base_checker import BaseChecker, CompositeChecker
from magic_qc.business.facial.symmetry_checker import SymmetryChecker
from magic_qc.business.facial.quality_checker import FaceQualityChecker
from src.magic_qc.management.config.config_manager import ConfigManager


class FaceChecker(BaseChecker):
    def __init__(self, config_path: Optional[str] = None):
        super().__init__(name="FaceChecker", version="1.0.0")
        self.symmetry_checker = SymmetryChecker()
        self.quality_checker = FaceQualityChecker(config_path)
        self.composite = CompositeChecker([self.symmetry_checker, self.quality_checker], name="FaceCompositeChecker")
        # 获取配置
        self.config = ConfigManager.get_facial_config()
    
    def _get_lr_score(self, lr_ratio: float) -> float:
        """从配置获取亮度比评分"""
        lr_config = self.config.get("lr_ratio", {})
        score_mapping = lr_config.get("score_mapping", {})
        
        # 获取各区间
        excellent_range = lr_config.get("excellent", [0.85, 0.95])
        good_range = lr_config.get("good", [0.75, 0.85])
        
        if excellent_range[0] <= lr_ratio <= excellent_range[1]:
            return score_mapping.get("excellent", 100)
        elif good_range[0] <= lr_ratio < good_range[1]:
            return score_mapping.get("good", 70)
        else:
            return score_mapping.get("poor", 40)
    
    def check(self, input_path: str) -> Dict[str, Any]:
        result = self.composite.check(input_path)
        symmetry_result = None
        quality_result = None
        for detail in result.get("details", []):
            if detail["checker"] == "SymmetryChecker":
                symmetry_result = detail["result"]
            elif detail["checker"] == "FaceQualityChecker":
                quality_result = detail["result"]
        
        # 获取对称性分数
        overall_symmetry = symmetry_result.get('overall_symmetry', 0) if symmetry_result else 0
        
        # 获取脸部亮度比
        lr_ratio = symmetry_result.get('details', {}).get('left_right_ratio', 1.0) if symmetry_result else 1.0
        
        # 获取质量评分
        quality_score = quality_result.get('score', 0) if quality_result else 0
        
        # 获取质量指标
        clarity = quality_result.get('clarity', 0) if quality_result else 0
        contrast = quality_result.get('contrast', 0) if quality_result else 0
        edge_density = quality_result.get('edge_density', 0) if quality_result else 0
        noise_level = quality_result.get('noise_level', 0) if quality_result else 0
        
        # 从配置获取亮度比评分和权重
        lr_score = self._get_lr_score(lr_ratio)
        lr_weight = self.config.get("lr_ratio", {}).get("weight", 0.10)
        quality_weight = 1 - lr_weight
        
        # 综合评分
        if overall_symmetry < 0.75:
            total_score = 0
            passed = False
            status = "对称性不足"
        else:
            total_score = quality_score * quality_weight + lr_score * lr_weight
            passed = total_score >= 70
            status = quality_result.get('status', '未知') if quality_result else '未知'
        
        return {
            "passed": passed,
            "score": round(total_score, 1),
            "filename": Path(input_path).name,
            "symmetry": symmetry_result,
            "quality": quality_result,
            "overall_symmetry": round(overall_symmetry, 4),
            "lr_ratio": round(lr_ratio, 3),
            "clarity": round(clarity, 2),
            "contrast": round(contrast, 2),
            "edge_density": round(edge_density, 4),
            "noise_level": round(noise_level, 2),
            "quality_score": round(quality_score, 1),
            "status": status
        }
    
    def get_supported_formats(self) -> List[str]:
        return ['.jpg', '.png', '.jpeg', '.bmp']