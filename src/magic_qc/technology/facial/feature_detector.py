# technology/facial/feature_detector.py
"""
人脸特征检测模块 - 技术域

本模块提供基于 OpenCV 的人脸和眼睛特征检测功能。
只负责底层检测，不包含任何业务判断逻辑。

典型用法:
    from magic_qc.technology.facial.feature_detector import FeatureDetector
    
    detector = FeatureDetector()
    
    # 检测人脸
    faces = detector.detect_faces(gray_image)
    if len(faces) > 0:
        x, y, w, h = faces[0]
        face_roi = gray_image[y:y+h, x:x+w]
        
        # 在人脸区域内检测眼睛
        eyes = detector.detect_eyes(face_roi)
        print(f"检测到 {len(eyes)} 只眼睛")
"""

import cv2
from typing import List, Tuple
import numpy as np


class FeatureDetector:
    """
    人脸特征检测器
    
    基于 OpenCV 的 Haar Cascade 分类器进行人脸和眼睛检测。
    只提供原子检测能力，不包含任何判断逻辑。
    
    设计原则:
        - 单一职责: 只做检测，不做判断
        - 技术隔离: 上层业务不直接依赖 OpenCV
        - 可替换: 未来可替换为深度学习模型，不影响上层
    
    Attributes:
        face_cascade (cv2.CascadeClassifier): 人脸检测分类器
        eye_cascade (cv2.CascadeClassifier): 眼睛检测分类器
    
    Examples:
        >>> detector = FeatureDetector()
        >>> gray = cv2.imread("face.jpg", cv2.IMREAD_GRAYSCALE)
        >>> faces = detector.detect_faces(gray)
        >>> for (x, y, w, h) in faces:
        ...     print(f"人脸位置: x={x}, y={y}, w={w}, h={h}")
    """
    
    def __init__(self):
        """
        初始化特征检测器
        
        加载 OpenCV 预训练的 Haar Cascade 模型文件。
        
        Raises:
            RuntimeError: 如果级联分类器文件加载失败
            
        Examples:
            >>> detector = FeatureDetector()
        """
        # 加载人脸检测模型（OpenCV 内置的正面人脸检测器）
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # 加载眼睛检测模型（OpenCV 内置的眼睛检测器）
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
    
    def detect_faces(self, gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        检测图像中的人脸位置
        
        使用 Haar Cascade 方法检测图像中的所有正面人脸。
        
        Args:
            gray (np.ndarray): 灰度图像，形状为 (H, W)，数据类型 uint8
                建议先使用 cv2.cvtColor() 将彩色图像转换为灰度图。
        
        Returns:
            List[Tuple[int, int, int, int]]: 人脸位置列表，每个元素为 (x, y, w, h)
                - x (int): 人脸矩形左上角 x 坐标
                - y (int): 人脸矩形左上角 y 坐标
                - w (int): 人脸矩形宽度
                - h (int): 人脸矩形高度
                
                如果没有检测到人脸，返回空列表 []。
        
        Examples:
            >>> detector = FeatureDetector()
            >>> gray = cv2.imread("portrait.jpg", cv2.IMREAD_GRAYSCALE)
            >>> faces = detector.detect_faces(gray)
            >>> if faces:
            ...     x, y, w, h = faces[0]
            ...     print(f"检测到人脸: {w}x{h}")
            ... else:
            ...     print("未检测到人脸")
        """
        # detectMultiScale 参数说明:
        #   scaleFactor: 图像缩放比例，1.1 表示每次缩小 10%
        #   minNeighbors: 每个候选矩形至少需要的邻居数量，4 为适中值
        return self.face_cascade.detectMultiScale(gray, 1.1, 4)
    
    def detect_eyes(self, face_roi: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        检测人脸区域内的眼睛位置
        
        在人脸区域（ROI）内检测眼睛。通常在 detect_faces() 获取人脸区域后调用。
        
        Args:
            face_roi (np.ndarray): 人脸区域的灰度图像，形状为 (h, w)，数据类型 uint8
                通常由完整图像裁剪得到: face_roi = gray[y:y+h, x:x+w]
        
        Returns:
            List[Tuple[int, int, int, int]]: 眼睛位置列表，每个元素为 (x, y, w, h)
                - x (int): 眼睛矩形左上角 x 坐标（相对于 face_roi）
                - y (int): 眼睛矩形左上角 y 坐标（相对于 face_roi）
                - w (int): 眼睛矩形宽度
                - h (int): 眼睛矩形高度
                
                如果没有检测到眼睛，返回空列表 []。
                
                注意: 坐标是相对于 face_roi 的，如需在原始图像中定位，
                需要加上人脸区域的偏移量 (face_x, face_y)。
        
        Examples:
            >>> detector = FeatureDetector()
            >>> gray = cv2.imread("portrait.jpg", cv2.IMREAD_GRAYSCALE)
            >>> faces = detector.detect_faces(gray)
            >>> if faces:
            ...     x, y, w, h = faces[0]
            ...     face_roi = gray[y:y+h, x:x+w]
            ...     eyes = detector.detect_eyes(face_roi)
            ...     print(f"检测到 {len(eyes)} 只眼睛")
            ...     for ex, ey, ew, eh in eyes:
            ...         # 转换到原始图像坐标
            ...         orig_x = x + ex
            ...         orig_y = y + ey
            ...         print(f"眼睛位置: ({orig_x}, {orig_y})")
        """
        # detectMultiScale 参数说明:
        #   scaleFactor: 图像缩放比例，1.05 适合眼睛这种较小特征
        #   minNeighbors: 3 是眼睛检测的常用值，平衡准确率和召回率
        return self.eye_cascade.detectMultiScale(face_roi, 1.05, 3)