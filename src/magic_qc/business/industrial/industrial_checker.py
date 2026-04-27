# business/industrial/industrial_checker.py
from magic_qc.core.base_checker import BaseChecker
# from magic_qc.technology.measurement.dimension import DimensionMeasurer
# from magic_qc.technology.image.defect_detector import DefectDetector
# from magic_qc.management.rules.industrial_rules import IndustrialRules


class IndustrialChecker(BaseChecker):
    """
    工业产品质控检查器
    
    特定场景：产品尺寸、缺陷检测
    """
    
    def __init__(self, product_type: str, tolerance: float = 0.01):
        super().__init__()
        self.product_type = product_type
        self.tolerance = tolerance
        # self.dimension_measurer = DimensionMeasurer()
        # self.defect_detector = DefectDetector()
        # self.rules = IndustrialRules(product_type)
    
    def check(self, image_path: str) -> Dict[str, Any]:
        # 1. 技术层：测量和检测
        dimensions = self.dimension_measurer.measure(image_path)
        defects = self.defect_detector.detect(image_path)
        
        # 2. 管理层：规则判断
        passed = self.rules.evaluate(dimensions, defects, self.tolerance)
        score = self.rules.calculate_score(dimensions, defects)
        
        return {
            'passed': passed,
            'score': score,
            'dimensions': dimensions,
            'defects': defects,
            'checker': 'IndustrialChecker'
        }
    
    def get_supported_formats(self) -> List[str]:
        return ['.jpg', '.png', '.bmp']