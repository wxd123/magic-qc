#!/usr/bin/env python3
"""
质量阈值自动优化工具 - 分析图片并记录到JSON配置
"""

import sys
import json
import numpy as np
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from magic_qc.technology.facial.quality_analyzer import QualityAnalyzer
from magic_qc.management.config_manager import QualityConfigManager


class QualityOptimizer:
    """质量阈值优化器"""
    
    def __init__(self, config_manager: QualityConfigManager):
        self.config_manager = config_manager
        self.analyzer = QualityAnalyzer()
        self.metrics_list = []
    
    def analyze_directory(self, image_dir: str) -> bool:
        """分析目录下的所有图片"""
        image_paths = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            image_paths.extend(Path(image_dir).glob(ext))
            image_paths.extend(Path(image_dir).glob(ext.upper()))
        
        if not image_paths:
            print(f"❌ 未找到图片: {image_dir}")
            return False
        
        print(f"📁 分析 {len(image_paths)} 张图片...")
        
        for img_path in image_paths:
            import cv2
            img = cv2.imread(str(img_path))
            if img is not None:
                metrics = self.analyzer.calculate_all_metrics(img)
                metrics['filename'] = img_path.name
                self.metrics_list.append(metrics)
        
        print(f"✅ 成功分析 {len(self.metrics_list)} 张图片")
        return True
    
    def get_statistics(self) -> dict:
        """计算统计数据"""
        stats = {}
        for key in ['clarity', 'contrast', 'noise_level', 'edge_density']:
            values = [m[key] for m in self.metrics_list]
            stats[key] = {
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'mean': float(np.mean(values)),
                'median': float(np.median(values)),
                'std': float(np.std(values)),
                'percentile_25': float(np.percentile(values, 25)),
                'percentile_50': float(np.percentile(values, 50)),
                'percentile_75': float(np.percentile(values, 75)),
                'percentile_90': float(np.percentile(values, 90))
            }
        return stats
    
    def suggest_thresholds(self, target_pass_rate: float = 0.35) -> dict:
        """基于数据分布建议阈值"""
        stats = self.get_statistics()
        current_thresholds = self.config_manager.get_thresholds()
        
        suggested = {}
        
        # 清晰度（值越大越好）
        suggested['clarity'] = {
            'excellent': max(current_thresholds['clarity']['excellent'], stats['clarity']['percentile_75']),
            'good': max(current_thresholds['clarity']['good'], stats['clarity']['percentile_50']),
            'pass': max(current_thresholds['clarity']['pass'], stats['clarity']['percentile_25']),
            'unit': current_thresholds['clarity']['unit'],
            'description': current_thresholds['clarity']['description']
        }
        
        # 对比度（值越大越好）
        suggested['contrast'] = {
            'excellent': max(current_thresholds['contrast']['excellent'], stats['contrast']['percentile_75']),
            'good': max(current_thresholds['contrast']['good'], stats['contrast']['percentile_50']),
            'pass': max(current_thresholds['contrast']['pass'], stats['contrast']['percentile_25']),
            'unit': current_thresholds['contrast']['unit'],
            'description': current_thresholds['contrast']['description']
        }
        
        # 边缘密度（值越大越好）
        suggested['edge_density'] = {
            'excellent': max(current_thresholds['edge_density']['excellent'], stats['edge_density']['percentile_75']),
            'good': max(current_thresholds['edge_density']['good'], stats['edge_density']['percentile_50']),
            'pass': max(current_thresholds['edge_density']['pass'], stats['edge_density']['percentile_25']),
            'unit': current_thresholds['edge_density']['unit'],
            'description': current_thresholds['edge_density']['description']
        }
        
        # 噪声（值越小越好）
        suggested['noise_level'] = {
            'excellent': min(current_thresholds['noise_level']['excellent'], stats['noise_level']['percentile_25']),
            'good': min(current_thresholds['noise_level']['good'], stats['noise_level']['percentile_50']),
            'pass': min(current_thresholds['noise_level']['pass'], stats['noise_level']['percentile_75']),
            'unit': current_thresholds['noise_level']['unit'],
            'description': current_thresholds['noise_level']['description'],
            'lower_is_better': True
        }
        
        return suggested
    
    def evaluate_thresholds(self, thresholds: dict) -> dict:
        """评估阈值效果"""
        from magic_qc.management.rules.facial.quality_rules import FaceQualityRules
        import tempfile
        
        # 临时保存配置进行评估
        temp_config = self.config_manager.config.copy()
        temp_config['thresholds'] = thresholds
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(temp_config, f)
            temp_path = f.name
        
        # 创建临时规则实例
        temp_rules = FaceQualityRules(temp_path)
        
        scores = []
        for metrics in self.metrics_list:
            score = temp_rules.calculate_quality_score(metrics)
            scores.append(score)
        
        pass_score = self.config_manager.get_scoring_config()['pass_score']
        pass_count = sum(1 for s in scores if s >= pass_score)
        
        return {
            'total': len(scores),
            'passed': pass_count,
            'pass_rate': pass_count / len(scores),
            'avg_score': float(np.mean(scores)),
            'median_score': float(np.median(scores))
        }
    
    def run_optimization(self, image_dir: str, target_pass_rate: float = 0.35, apply_changes: bool = False):
        """运行完整优化流程"""
        print("\n" + "="*70)
        print("🎯 质量阈值自动优化")
        print("="*70)
        
        # 1. 分析图片
        if not self.analyze_directory(image_dir):
            return
        
        # 2. 计算统计数据
        stats = self.get_statistics()
        
        # 3. 建议新阈值
        suggested = self.suggest_thresholds(target_pass_rate)
        
        # 4. 评估当前配置
        current_thresholds = self.config_manager.get_thresholds()
        current_eval = self.evaluate_thresholds(current_thresholds)
        
        # 5. 评估建议配置
        suggested_eval = self.evaluate_thresholds(suggested)
        
        # 6. 显示结果
        print("\n📊 当前数据统计:")
        for key, stat in stats.items():
            print(f"  {key}: 中位数={stat['median']:.2f}, 25分位={stat['percentile_25']:.2f}, 75分位={stat['percentile_75']:.2f}")
        
        print("\n📈 效果对比:")
        print(f"  当前配置 - 合格率: {current_eval['pass_rate']*100:.1f}%, 平均分: {current_eval['avg_score']:.1f}")
        print(f"  建议配置 - 合格率: {suggested_eval['pass_rate']*100:.1f}%, 平均分: {suggested_eval['avg_score']:.1f}")
        print(f"  目标合格率: {target_pass_rate*100:.0f}%")
        
        print("\n💡 建议的阈值配置:")
        for key, th in suggested.items():
            print(f"  {key}: excellent={th['excellent']}, good={th['good']}, pass={th['pass']}")
        
        # 7. 保存分析记录
        analysis_record = {
            "image_dir": image_dir,
            "total_images": len(self.metrics_list),
            "target_pass_rate": target_pass_rate,
            "statistics": stats,
            "current_thresholds": current_thresholds,
            "suggested_thresholds": suggested,
            "evaluation": {
                "current": current_eval,
                "suggested": suggested_eval
            }
        }
        
        self.config_manager.add_analysis_record(analysis_record)
        print(f"\n💾 分析记录已保存到配置文件")
        
        # 8. 可选：应用更改
        if apply_changes:
            self.config_manager.update_thresholds(suggested)
            print("✅ 已应用新的阈值配置")
        
        print(f"\n📄 配置文件位置: {self.config_manager.config_path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='质量阈值自动优化工具')
    parser.add_argument('image_dir', help='图片目录路径')
    parser.add_argument('--target-rate', type=float, default=0.35, help='目标合格率 (0-1), 默认0.35')
    parser.add_argument('--apply', action='store_true', help='是否应用建议的阈值')
    parser.add_argument('--config', help='配置文件路径（可选）')
    
    args = parser.parse_args()
    
    config_manager = QualityConfigManager(args.config)
    optimizer = QualityOptimizer(config_manager)
    
    optimizer.run_optimization(
        image_dir=args.image_dir,
        target_pass_rate=args.target_rate,
        apply_changes=args.apply
    )


if __name__ == "__main__":
    main()