# technology/facial/symmetry.py
"""
面部对称性计算模块 - 技术域

本模块提供面部对称性分析的底层计算能力。
只提供原子化的数学计算函数，不包含业务判断逻辑。

典型用法:
    from magic_qc.technology.facial.symmetry import SymmetryCalculator
    
    # 计算图像对称性
    left, right_mirrored = SymmetryCalculator.split_mirror(gray_image)
    symmetry_score = SymmetryCalculator.compute_diff(left, right_mirrored)
    
    # 计算亮度平衡
    lr_ratio = SymmetryCalculator.compute_intensity_ratio(left, right_mirrored)
"""

import cv2
import numpy as np
from typing import Tuple


class SymmetryCalculator:
    """
    对称性计算器
    
    提供面部对称性分析所需的原子计算能力。
    所有方法均为静态方法，无状态，可随时调用。
    
    设计原则:
        - 原子化: 每个方法只做一件事
        - 无状态: 不保存任何状态，线程安全
        - 纯计算: 不包含任何业务判断逻辑
        - 可组合: 上层可以自由组合这些原子能力
    
    Examples:
        >>> # 完整的面部对称性分析流程
        >>> calculator = SymmetryCalculator()
        >>> left, right = calculator.split_mirror(gray_image)
        >>> symmetry = calculator.compute_diff(left, right)
        >>> ratio = calculator.compute_intensity_ratio(left, right)
        >>> print(f"对称性: {symmetry:.3f}, 亮度比: {ratio:.3f}")
    """
    
    @staticmethod
    def split_mirror(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        将图像分割为左右两半，并将右半部分镜像
        
        这是对称性分析的基础步骤。将图像从中间垂直分割，
        然后将右半部分水平翻转，使其与左半部分方向一致。
        
        Args:
            image (np.ndarray): 输入图像，可以是灰度图 (H, W) 或彩色图 (H, W, C)
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: (左半图像, 镜像后的右半图像)
                - left: 左半部分图像
                - right_mirrored: 右半部分镜像后的图像
                
                两部分尺寸相同，宽度为原图的一半。
        
        Notes:
            - 如果原图宽度为奇数，会自动舍弃最右侧一列以保证对称分割
            - 支持任意维度的图像（灰度或彩色）
        
        Examples:
            >>> calculator = SymmetryCalculator()
            >>> gray = cv2.imread("face.jpg", cv2.IMREAD_GRAYSCALE)
            >>> left, right = calculator.split_mirror(gray)
            >>> print(f"左半尺寸: {left.shape}, 右半尺寸: {right.shape}")
            >>> # 左半和右半镜像后可以直接比较
            >>> diff = calculator.compute_diff(left, right)
        """
        height, width = image.shape[:2]
        
        # 处理奇数宽度：舍弃最后一列，保证对称分割
        if width % 2 == 1:
            image = image[:, :-1]  # 去掉最右侧一列
            width -= 1
        
        mid = width // 2
        left = image[:, :mid]                    # 左半部分
        right = image[:, mid:]                   # 右半部分
        right_mirrored = cv2.flip(right, 1)      # 水平翻转右半部分
        
        return left, right_mirrored
    
    @staticmethod
    def compute_diff(img1: np.ndarray, img2: np.ndarray) -> float:
        """
        计算两张图像的差异度
        
        通过计算像素差异的平均值来评估两张图像的相似程度。
        数值越高表示越相似，1.0 表示完全相同。
        
        Args:
            img1 (np.ndarray): 第一张图像
            img2 (np.ndarray): 第二张图像
        
        Returns:
            float: 相似度分数，取值范围 0-1
                - 1.0: 两图完全相同
                - 0.0: 两图完全不同
                - 实际人脸左右半的典型值: 0.70-0.95
        
        Notes:
            - 如果两张图像尺寸不同，会自动缩放到较小尺寸
            - 支持 uint8 和 float 类型的图像
            - uint8 图像会自动归一化到 0-1 范围
        
        Examples:
            >>> calculator = SymmetryCalculator()
            >>> left, right = calculator.split_mirror(gray_image)
            >>> similarity = calculator.compute_diff(left, right)
            >>> print(f"对称性: {similarity:.3f}")
            >>> if similarity > 0.9:
            ...     print("非常对称")
            ... elif similarity > 0.75:
            ...     print("正常不对称")
            ... else:
            ...     print("明显不对称")
        """
        h = min(img1.shape[0], img2.shape[0])
        w = min(img1.shape[1], img2.shape[1])
        
        # 尺寸不一致时，缩放到较小尺寸
        if img1.shape != (h, w):
            img1 = cv2.resize(img1, (w, h))
        if img2.shape != (h, w):
            img2 = cv2.resize(img2, (w, h))
        
        # 计算像素差异
        diff = cv2.absdiff(img1, img2)
        mean_diff = np.mean(diff)
        
        # 归一化：uint8 类型 (0-255) 转换为 0-1 范围
        if img1.dtype == np.uint8:
            mean_diff = mean_diff / 255.0
        
        # 转换为相似度（1 - 差异）
        return 1.0 - mean_diff
    
    @staticmethod
    def compute_intensity_ratio(img1: np.ndarray, img2: np.ndarray) -> float:
        """
        计算两张图像的亮度比例
        
        评估左右半脸的亮度平衡程度。
        真实人脸通常左右亮度相近，比例接近 1.0。
        
        Args:
            img1 (np.ndarray): 第一张图像（通常为左半脸）
            img2 (np.ndarray): 第二张图像（通常为右半脸）
        
        Returns:
            float: 亮度比例，取值范围 0-1
                - 1.0: 亮度完全相同
                - 0.9-1.0: 亮度非常平衡
                - 0.8-0.9: 轻微亮度差异
                - <0.8: 明显亮度差异
                
                真实人脸的典型值: 0.85-0.95
        
        Notes:
            - 返回值为 min(mean1, mean2) / max(mean1, mean2)
            - 确保返回值 ≤ 1.0
            - 如果两张图像平均亮度都为 0，返回 1.0
        
        Examples:
            >>> calculator = SymmetryCalculator()
            >>> left, right = calculator.split_mirror(gray_image)
            >>> ratio = calculator.compute_intensity_ratio(left, right)
            >>> if ratio > 0.9:
            ...     print("亮度平衡良好")
            ... else:
            ...     print("左右亮度差异较大")
        """
        mean1 = np.mean(img1)
        mean2 = np.mean(img2)
        
        # 避免除以零
        if max(mean1, mean2) == 0:
            return 1.0
        
        # 返回较小的均值除以较大的均值，保证返回值 ≤ 1.0
        return min(mean1, mean2) / max(mean1, mean2)
    
    @staticmethod
    def compute_histogram_similarity(img1: np.ndarray, img2: np.ndarray) -> float:
        """
        计算两张图像的直方图相似度
        
        通过比较图像的直方图分布来评估相似性。
        直方图反映了图像的亮度分布特征，不受空间位置影响。
        
        Args:
            img1 (np.ndarray): 第一张图像（支持灰度或彩色）
            img2 (np.ndarray): 第二张图像（支持灰度或彩色）
        
        Returns:
            float: 直方图相似度，取值范围 -1 到 1
                - 1.0: 直方图完全相同
                - 0.0: 完全不相关
                - -1.0: 完全负相关
                
                实际使用中，返回值会被限制在 [0, 1] 范围内。
                真实人脸左右半的典型值: 0.85-0.98
        
        Notes:
            - 彩色图像会自动转换为灰度图
            - 使用相关性方法 (HISTCMP_CORREL) 进行比较
            - 返回值会通过 max(0.0, similarity) 确保非负
        
        Examples:
            >>> calculator = SymmetryCalculator()
            >>> left, right = calculator.split_mirror(gray_image)
            >>> hist_sim = calculator.compute_histogram_similarity(left, right)
            >>> print(f"直方图相似度: {hist_sim:.3f}")
            >>> if hist_sim > 0.9:
            ...     print("左右脸亮度分布非常相似")
        """
        # 彩色图转换为灰度图
        if len(img1.shape) == 3:
            img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        if len(img2.shape) == 3:
            img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        # 计算直方图（256 个 bins，范围 0-255）
        hist1 = cv2.calcHist([img1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([img2], [0], None, [256], [0, 256])
        
        # 计算直方图相关性
        similarity = cv2.compareHist(
            hist1.astype(np.float32),
            hist2.astype(np.float32),
            cv2.HISTCMP_CORREL
        )
        
        # 确保返回值非负
        return max(0.0, similarity)