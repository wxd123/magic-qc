"""
质控检查器基类 - 核心框架

所有业务场景的检查器都应继承此类，统一接口。

典型用法:
    from magic_qc.core.base_checker import BaseChecker
    
    class MyChecker(BaseChecker):
        def __init__(self):
            super().__init__(name="MyChecker", version="1.0.0")
        
        def check(self, input_path: str) -> Dict[str, Any]:
            # 实现检查逻辑
            return {"passed": True, "score": 100}
        
        def get_supported_formats(self) -> List[str]:
            return ['.jpg', '.png']
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path


class BaseChecker(ABC):
    """
    质控检查器抽象基类
    
    定义统一的检查接口，所有业务场景必须实现。
    
    Attributes:
        name (str): 检查器名称
        version (str): 版本号
    """
    
    def __init__(self, name: str = "BaseChecker", version: str = "1.0.0"):
        """
        初始化检查器
        
        Args:
            name: 检查器名称
            version: 版本号
        """
        self.name = name
        self.version = version
        self._results = []
    
    @abstractmethod
    def check(self, input_path: str) -> Dict[str, Any]:
        """
        执行质控检查
        
        Args:
            input_path: 输入文件路径
        
        Returns:
            检查结果字典，必须包含:
                - passed (bool): 是否通过质控
                - score (float): 综合评分 (0-100)
                - details (dict): 详细结果（可选）
                - error (str): 错误信息（可选）
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        返回支持的输入文件格式列表
        
        Returns:
            格式列表，如 ['.jpg', '.png', '.jpeg', '.bmp']
        """
        pass
    
    def batch_check(self, input_dir: str) -> List[Dict[str, Any]]:
        """
        批量检查目录下的所有文件
        
        Args:
            input_dir: 输入目录路径
        
        Returns:
            检查结果列表
        """
        results = []
        input_path = Path(input_dir)
        
        if not input_path.exists():
            return [{"error": f"目录不存在: {input_dir}", "passed": False, "score": 0}]
        
        if not input_path.is_dir():
            return [{"error": f"路径不是目录: {input_dir}", "passed": False, "score": 0}]
        
        supported = self.get_supported_formats()
        
        for file_path in input_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported:
                try:
                    result = self.check(str(file_path))
                    results.append(result)
                except Exception as e:
                    results.append({
                        "error": str(e),
                        "passed": False,
                        "score": 0,
                        "filename": file_path.name
                    })
        
        return results
    
    def get_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取批量检查的统计摘要
        
        Args:
            results: 检查结果列表
        
        Returns:
            统计摘要字典，包含:
                - total: 总数
                - passed: 通过数
                - failed: 失败数
                - avg_score: 平均分
        """
        if not results:
            return {"total": 0, "passed": 0, "failed": 0, "avg_score": 0.0}
        
        total = len(results)
        passed = sum(1 for r in results if r.get("passed", False))
        failed = total - passed
        scores = [r.get("score", 0) for r in results if r.get("score", 0) > 0]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "avg_score": round(avg_score, 1)
        }


class CompositeChecker(BaseChecker):
    """
    组合检查器
    
    将多个检查器组合成一个完整的质控流程。
    
    Attributes:
        checkers (List[BaseChecker]): 子检查器列表
    
    Examples:
        >>> checker1 = SymmetryChecker()
        >>> checker2 = QualityChecker()
        >>> composite = CompositeChecker([checker1, checker2])
        >>> result = composite.check("face.jpg")
    """
    
    def __init__(self, checkers: List[BaseChecker], name: str = "CompositeChecker"):
        """
        初始化组合检查器
        
        Args:
            checkers: 子检查器列表
            name: 组合检查器名称
        """
        super().__init__(name=name)
        self.checkers = checkers
    
    def check(self, input_path: str) -> Dict[str, Any]:
        """
        依次执行所有子检查器
        
        Args:
            input_path: 输入文件路径
        
        Returns:
            组合结果字典，包含:
                - passed: 是否全部通过
                - score: 平均分
                - details: 各子检查器结果列表
        """
        results = []
        overall_passed = True
        overall_score = 0.0
        
        for checker in self.checkers:
            try:
                result = checker.check(input_path)
                results.append({
                    "checker": checker.name,
                    "result": result
                })
                
                if not result.get("passed", False):
                    overall_passed = False
                overall_score += result.get("score", 0)
            except Exception as e:
                results.append({
                    "checker": checker.name,
                    "result": {
                        "passed": False,
                        "score": 0,
                        "error": str(e)
                    }
                })
                overall_passed = False
        
        overall_score = overall_score / len(self.checkers) if self.checkers else 0
        
        return {
            "passed": overall_passed,
            "score": round(overall_score, 1),
            "details": results
        }
    
    def get_supported_formats(self) -> List[str]:
        """
        获取所有子检查器支持的格式的并集
        
        Returns:
            支持的格式列表
        """
        formats = set()
        for checker in self.checkers:
            formats.update(checker.get_supported_formats())
        return list(formats)