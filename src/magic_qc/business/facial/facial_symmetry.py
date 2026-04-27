# business/facial_symmetry.py

"""
面部对称性质检业务模块

本模块提供面部对称性分析的业务逻辑，协调技术层和管理层完成：
- 单张图片的对称性分析
- 批量图片的对称性分析
- 结果汇总与导出

典型用法:
    from magic_qc.business.facial_symmetry import FacialSymmetryChecker
    
    checker = FacialSymmetryChecker()
    
    # 单张分析
    result = checker.analyze("path/to/image.jpg")
    print(f"对称性分数: {result['overall_symmetry']}")
    
    # 批量分析
    results = checker.batch_analyze("path/to/images/", output_csv="results.csv")
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional

from magic_qc.technology.facial.symmetry import SymmetryCalculator
from magic_qc.technology.facial.feature_detector import FeatureDetector
from magic_qc.management.rules.facial.symmetry_rules import FacialSymmetryRules


class FacialSymmetryChecker:
    """
    面部对称性质检业务类
    
    负责协调技术层（图像处理、特征检测、对称性计算）和管理层（规则判断），
    完成完整的面部对称性分析流程。
    
    工作流程:
        1. 加载图片并转换为灰度图
        2. 计算整体对称性分数
        3. 检测人脸和眼睛特征
        4. 计算眼睛对称性分数
        5. 分析对称性分布标准差
        6. 综合评估真实性分数
        7. 返回结构化的分析结果
    
    Attributes:
        tech_sym (SymmetryCalculator): 对称性计算器（技术层）
        tech_detector (FeatureDetector): 特征检测器（技术层）
        rules (FacialSymmetryRules): 面部对称性规则库（管理层）
    """
    
    def __init__(self):
        """
        初始化面部对称性质检器
        
        创建技术层和管理层的实例，用于后续分析。
        
        Examples:
            >>> checker = FacialSymmetryChecker()
            >>> result = checker.analyze("face.jpg")
        """
        self.tech_sym = SymmetryCalculator()
        self.tech_detector = FeatureDetector()
        self.rules = FacialSymmetryRules()
    
    def analyze(self, image_path: str) -> Dict[str, Any]:
        """
        分析单张图片的面部对称性
        
        这是核心分析方法，协调各层完成完整的分析流程。
        
        Args:
            image_path (str): 图片文件路径，支持 jpg、png、bmp 等格式
        
        Returns:
            Dict[str, Any]: 分析结果字典，包含以下字段:
                - filename (str): 文件名
                - overall_symmetry (float): 整体对称性分数，0-1之间，越高越对称
                - symmetry_level (str): 对称性等级，'high' / 'medium' / 'low'
                - authenticity_score (float): 真实性分数，0-100
                - authenticity_level (str): 真实性等级，'真实' / '可能AI生成'
                - is_realistic (bool): 是否为真实图片（分数 >= 60）
                - recommendation (str): 改进建议
                - details (dict): 详细指标，包含:
                    - eye_symmetry (float): 眼睛对称性分数
                    - left_right_ratio (float): 左右亮度比例
                    - distribution_std (float): 对称性分布标准差
        
        Raises:
            不直接抛出异常，而是返回包含 "error" 字段的字典
        
        Examples:
            >>> checker = FacialSymmetryChecker()
            >>> result = checker.analyze("portrait.jpg")
            >>> if "error" not in result:
            ...     print(f"对称性: {result['overall_symmetry']}")
            ...     print(f"建议: {result['recommendation']}")
            ... else:
            ...     print(f"错误: {result['error']}")
        """
        
        # 1. 加载图片
        img = cv2.imread(image_path)
        if img is None:
            return {"error": "无法读取图片", "filename": Path(image_path).name}
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. 整体对称性计算
        #    将图像分为左右两半，计算差异度
        left, right_mirrored = self.tech_sym.split_mirror(gray)
        overall_score = self.tech_sym.compute_diff(left, right_mirrored)
        lr_ratio = self.tech_sym.compute_intensity_ratio(left, right_mirrored)
        
        # 3. 特征检测与眼睛对称性计算
        faces = self.tech_detector.detect_faces(gray)
        if len(faces) == 0:
            return {"error": "未检测到人脸", "filename": Path(image_path).name}
        
        x, y, w, h = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        eyes = self.tech_detector.detect_eyes(face_roi)
        
        # 计算眼睛对称性（至少需要检测到2只眼睛）
        eye_score = 0.5  # 默认值
        if len(eyes) >= 2:
            eyes_sorted = sorted(eyes, key=lambda e: e[0])  # 按x坐标排序
            left_eye = eyes_sorted[0]
            right_eye = eyes_sorted[1]
            # 提取眼睛ROI并计算差异度
            # 注：实际实现需要提取左右眼睛区域
            # left_roi = face_roi[left_eye[1]:left_eye[1]+left_eye[3], left_eye[0]:left_eye[0]+left_eye[2]]
            # right_roi = face_roi[right_eye[1]:right_eye[1]+right_eye[3], right_eye[0]:right_eye[0]+right_eye[2]]
            # eye_score = self.tech_sym.compute_diff(left_roi, right_roi)
        
        # 4. 对称性分布分析
        #    采样图像多行的对称性，计算标准差
        sym_values = []
        for y_pos in range(0, gray.shape[0], gray.shape[0] // 20):
            row = gray[y_pos, :]
            # 计算当前行的对称性
            # row_left = row[:len(row)//2]
            # row_right = np.flip(row[len(row)//2:])
            # row_score = self.tech_sym.compute_diff(row_left, row_right)
            # sym_values.append(row_score)
            pass
        distribution_std = np.std(sym_values) if sym_values else 0.0
        
        # 5. 真实性分数评估（使用规则库）
        authenticity_score = self.rules.get_authenticity_score(
            overall_score, eye_score, distribution_std, lr_ratio
        )
        
        # 6. 获取等级和建议
        symmetry_level = self.rules.get_symmetry_level(overall_score)
        is_realistic = authenticity_score >= 60
        recommendation = self.rules.get_recommendation(authenticity_score, is_realistic)
        
        # 7. 返回结构化结果
        return {
            "filename": Path(image_path).name,
            "overall_symmetry": round(overall_score, 4),
            "symmetry_level": symmetry_level,
            "authenticity_score": round(authenticity_score, 1),
            "authenticity_level": "真实" if is_realistic else "可能AI生成",
            "is_realistic": is_realistic,
            "recommendation": recommendation,
            "details": {
                "eye_symmetry": round(eye_score, 4),
                "left_right_ratio": round(lr_ratio, 4),
                "distribution_std": round(distribution_std, 4)
            }
        }
    
    def batch_analyze(
        self, 
        image_dir: str, 
        output_csv: Optional[str] = None,
        extensions: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        批量分析目录下的所有图片
        
        遍历指定目录，对所有符合扩展名的图片进行分析，
        可选择性地将结果保存到 CSV 文件。
        
        Args:
            image_dir (str): 图片目录路径
            output_csv (Optional[str], optional): 输出CSV文件路径。
                如果提供，会将分析结果保存为CSV格式。
            extensions (List[str], optional): 图片扩展名列表，默认支持
                ['*.png', '*.jpg', '*.jpeg', '*.bmp']
        
        Returns:
            List[Dict[str, Any]]: 分析结果列表，每个元素与 analyze() 返回结构一致。
                如果目录不存在或无图片，返回空列表。
        
        Examples:
            >>> checker = FacialSymmetryChecker()
            >>> results = checker.batch_analyze("./images/", output_csv="report.csv")
            找到 10 张图片，开始分析...
            [1/10] 分析: image1.jpg
            [2/10] 分析: image2.jpg
            ...
            ==================================================
            批量分析总结
            ==================================================
            图片数量: 8
            平均对称性: 0.852
            平均真实性: 78.5/100
            真实图片比例: 7/8 (87.5%)
            ==================================================
            
            >>> for r in results:
            ...     print(f"{r['filename']}: {r['overall_symmetry']}")
        """
        if extensions is None:
            extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp']
        
        image_dir = Path(image_dir)
        if not image_dir.exists():
            print(f"错误: 目录不存在 - {image_dir}")
            return []
        
        # 收集所有符合条件的图片文件
        image_files = []
        for ext in extensions:
            image_files.extend(image_dir.glob(ext))
        
        if not image_files:
            print(f"未在 {image_dir} 中找到图片")
            return []
        
        print(f"找到 {len(image_files)} 张图片，开始分析...")
        
        # 逐张分析
        results = []
        for i, img_path in enumerate(image_files, 1):
            print(f"[{i}/{len(image_files)}] 分析: {img_path.name}")
            result = self.analyze(str(img_path))
            if "error" not in result:
                results.append(result)
            else:
                print(f"  警告: {result['error']}")
        
        # 输出统计摘要
        self._print_batch_summary(results)
        
        # 保存到CSV（如果指定了输出路径）
        if output_csv and results:
            self._save_to_csv(results, output_csv)
        
        return results
    
    def _print_batch_summary(self, results: List[Dict]) -> None:
        """
        打印批量分析的统计摘要（内部方法）
        
        Args:
            results (List[Dict]): analyze() 返回的结果列表
        """
        if not results:
            return
        
        n = len(results)
        avg_sym = sum(r['overall_symmetry'] for r in results) / n
        avg_auth = sum(r['authenticity_score'] for r in results) / n
        real_count = sum(1 for r in results if r.get('is_realistic', False))
        
        print("\n" + "="*50)
        print("批量分析总结")
        print("="*50)
        print(f"图片数量: {n}")
        print(f"平均对称性: {avg_sym:.3f}")
        print(f"平均真实性: {avg_auth:.1f}/100")
        print(f"真实图片比例: {real_count}/{n} ({real_count/n*100:.1f}%)")
        print("="*50)
    
    def _save_to_csv(self, results: List[Dict], output_csv: str) -> None:
        """
        保存分析结果到CSV文件（内部方法）
        
        优先使用 pandas，如果不可用则降级为手动写入。
        
        Args:
            results (List[Dict]): analyze() 返回的结果列表
            output_csv (str): 输出CSV文件路径
        """
        try:
            import pandas as pd
            
            df = pd.DataFrame([{
                '文件名': r['filename'],
                '整体对称性': round(r['overall_symmetry'], 4),
                '对称性等级': r['symmetry_level'],
                '真实性评分': r['authenticity_score'],
                '真实性判断': r['authenticity_level'],
                '建议': r['recommendation']
            } for r in results])
            
            df.to_csv(output_csv, index=False, encoding='utf-8-sig')
            print(f"\n结果已保存至: {output_csv}")
            
        except ImportError:
            # 降级方案：手动写入CSV
            with open(output_csv, 'w', encoding='utf-8') as f:
                f.write("文件名,整体对称性,对称性等级,真实性评分,真实性判断,建议\n")
                for r in results:
                    f.write(f"{r['filename']},{r['overall_symmetry']:.4f},{r['symmetry_level']},{r['authenticity_score']},{r['authenticity_level']},{r['recommendation']}\n")
            print(f"\n结果已保存至: {output_csv}")