"""
配置管理命令行接口 - 质量标准配置管理

本模块提供质量标准的配置管理命令，包括：
- 查看当前配置
- 更新阈值
- 查看分析历史
- 导入/导出配置
"""

import datetime

import typer
import json
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table


from src.magic_qc.management.config.config_manager import ConfigManager


app = typer.Typer(help="质量标准配置管理", no_args_is_help=True)
console = Console()

@app.command(name="init")
def init_config(
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="配置文件路径"),
    force: bool = typer.Option(False, "--force", "-f", help="强制覆盖现有配置"),
):
    """初始化配置文件（从模板创建）"""
    
    # 确定配置文件路径
    if config_path is None:
        project_root = Path(__file__).parent.parent.parent.parent
        config_path = project_root / "config" / "quality_standards.json"
    else:
        config_path = Path(config_path)
    
    # 检查是否已存在
    if config_path.exists() and not force:
        console.print(f"[yellow]⚠️ 配置文件已存在: {config_path}[/yellow]")
        console.print("使用 --force 强制覆盖")
        return
    
    # 模板配置
    template = {
        "version": "2.0.0",
        "name": "人脸图像质量标准",
        "description": "完全可配置的质量标准",
        "last_updated": datetime.now().isoformat(),
        "thresholds": {
            "clarity": {"excellent": 150, "good": 80, "pass": 50, "unit": "拉普拉斯方差", "description": "清晰度越高越好", "higher_is_better": True},
            "contrast": {"excellent": 60, "good": 45, "pass": 30, "unit": "标准差", "description": "对比度越高越好", "higher_is_better": True},
            "edge_density": {"excellent": 0.10, "good": 0.06, "pass": 0.03, "unit": "边缘像素比例", "description": "边缘密度越高越好", "higher_is_better": True},
            "noise_level": {"excellent": 5, "good": 10, "pass": 20, "unit": "噪声估计值", "description": "噪声越低越好", "higher_is_better": False}
        },
        "scoring": {
            "weights": {"clarity": 0.40, "contrast": 0.25, "edge_density": 0.15, "noise_level": 0.20},
            "score_mapping": {"excellent": 100, "good": 75, "pass": 50, "fail": 25},
            "pass_threshold": 60,
            "good_threshold": 70,
            "excellent_threshold": 85
        },
        "quality_levels": {
            "excellent": {"min_score": 85, "label": "优秀", "recommendation": "质量优秀，可直接使用", "color": "green"},
            "good": {"min_score": 70, "label": "良好", "recommendation": "质量良好，建议使用", "color": "blue"},
            "pass": {"min_score": 60, "label": "合格", "recommendation": "质量合格，可使用", "color": "yellow"},
            "fail": {"min_score": 0, "label": "不合格", "recommendation": "质量较差，不建议使用", "color": "red"}
        },
        "analysis_history": []
    }
    
    # 确保目录存在
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 写入配置
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    
    console.print(f"[green]✅ 配置文件已创建: {config_path}[/green]")

@app.command(name="show")
def show_config(
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="配置文件路径"),
):
    """显示当前质量标准配置"""
    cm = ConfigManager(config_path)
    
    # 验证配置
    if not cm.validate_config():
        console.print("[red]❌ 配置文件验证失败[/red]")
        raise typer.Exit(code=1)
    
    # 显示版本信息
    console.print("\n[bold cyan]📋 质量标准配置[/bold cyan]")
    console.print(f"版本: {cm.config['version']}")
    console.print(f"最后更新: {cm.config['last_updated']}")
    console.print(f"分析记录数: {len(cm.config.get('analysis_history', []))}")
    
    # 显示阈值配置表
    table = Table(title="阈值配置", show_header=True, header_style="bold magenta")
    table.add_column("指标", style="cyan")
    table.add_column("优秀 (≥)", justify="right")
    table.add_column("良好 (≥)", justify="right")
    table.add_column("合格 (≥)", justify="right")
    table.add_column("单位", style="dim")
    
    for metric, thresholds in cm.config['thresholds'].items():
        table.add_row(
            metric,
            str(thresholds.get('excellent', 'N/A')),
            str(thresholds.get('good', 'N/A')),
            str(thresholds.get('pass', 'N/A')),
            thresholds.get('unit', '')
        )
    
    console.print(table)
    
    # 显示评分配置
    console.print("\n[bold]评分配置:[/bold]")
    weights = cm.config['scoring']['weights']
    console.print(f"  权重: clarity={weights['clarity']}, contrast={weights['contrast']}, "
                  f"edge_density={weights['edge_density']}, noise_level={weights['noise_level']}")
    console.print(f"  通过分数: {cm.config['scoring']['pass_threshold']}")
    console.print(f"  良好分数: {cm.config['scoring']['good_threshold']}")
    console.print(f"  优秀分数: {cm.config['scoring']['excellent_threshold']}")
    
    # 显示质量等级
    console.print("\n[bold]质量等级定义:[/bold]")
    for level, config in cm.config['quality_levels'].items():
        console.print(f"  {config['label']}: {config['recommendation']}")


@app.command(name="update")
def update_thresholds(
    metric: str = typer.Argument(..., help="指标名称 (clarity/contrast/edge_density/noise_level)"),
    excellent: float = typer.Option(..., "--excellent", "-e", help="优秀阈值"),
    good: float = typer.Option(..., "--good", "-g", help="良好阈值"),
    pass_value: float = typer.Option(..., "--pass", "-p", help="合格阈值"),
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="配置文件路径"),
    yes: bool = typer.Option(False, "--yes", "-y", help="确认更新"),
):
    """更新单个指标的阈值配置"""
    
    # 验证指标名称
    valid_metrics = ['clarity', 'contrast', 'edge_density', 'noise_level']
    if metric not in valid_metrics:
        console.print(f"[red]❌ 无效指标: {metric}，可选: {', '.join(valid_metrics)}[/red]")
        raise typer.Exit(code=1)
    
    # 验证阈值逻辑
    if not (excellent >= good >= pass_value):
        console.print("[red]❌ 阈值逻辑错误: 应满足 优秀 ≥ 良好 ≥ 合格[/red]")
        raise typer.Exit(code=1)
    
    cm = ConfigManager(config_path)
    old_thresholds = cm.config['thresholds'][metric].copy()
    
    # 显示变更
    console.print(f"\n[bold yellow]将要更新 {metric} 阈值:[/bold yellow]")
    console.print(f"  优秀: {old_thresholds['excellent']} → {excellent}")
    console.print(f"  良好: {old_thresholds['good']} → {good}")
    console.print(f"  合格: {old_thresholds['pass']} → {pass_value}")
    
    if not yes:
        confirm = typer.confirm("\n确认更新?")
        if not confirm:
            console.print("[yellow]已取消[/yellow]")
            return
    
    # 执行更新
    cm.config['thresholds'][metric]['excellent'] = excellent
    cm.config['thresholds'][metric]['good'] = good
    cm.config['thresholds'][metric]['pass'] = pass_value
    cm.config['last_updated'] = '2026-04-07T10:00:00'  # TODO: 使用实际datetime
    cm._save_config(cm.config)
    
    console.print("[green]✅ 阈值已更新[/green]")


@app.command(name="update-batch")
def update_thresholds_batch(
    json_file: str = typer.Argument(..., help="包含阈值配置的JSON文件"),
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="配置文件路径"),
    yes: bool = typer.Option(False, "--yes", "-y", help="确认更新"),
):
    """从JSON文件批量更新阈值配置"""
    
    try:
        with open(json_file, 'r') as f:
            new_thresholds = json.load(f)
    except Exception as e:
        console.print(f"[red]❌ 读取文件失败: {e}[/red]")
        raise typer.Exit(code=1)
    
    cm = ConfigManager(config_path)
    
    console.print("[bold yellow]将要更新以下阈值:[/bold yellow]")
    for metric, thresholds in new_thresholds.items():
        if metric in cm.config['thresholds']:
            old = cm.config['thresholds'][metric]
            console.print(f"\n  {metric}:")
            console.print(f"    优秀: {old['excellent']} → {thresholds.get('excellent', old['excellent'])}")
            console.print(f"    良好: {old['good']} → {thresholds.get('good', old['good'])}")
            console.print(f"    合格: {old['pass']} → {thresholds.get('pass', old['pass'])}")
    
    if not yes:
        confirm = typer.confirm("\n确认更新?")
        if not confirm:
            console.print("[yellow]已取消[/yellow]")
            return
    
    # 执行批量更新
    for metric, thresholds in new_thresholds.items():
        if metric in cm.config['thresholds']:
            if 'excellent' in thresholds:
                cm.config['thresholds'][metric]['excellent'] = thresholds['excellent']
            if 'good' in thresholds:
                cm.config['thresholds'][metric]['good'] = thresholds['good']
            if 'pass' in thresholds:
                cm.config['thresholds'][metric]['pass'] = thresholds['pass']
    
    cm.config['last_updated'] = '2026-04-07T10:00:00'
    cm._save_config(cm.config)
    
    console.print("[green]✅ 批量更新完成[/green]")


@app.command(name="history")
def show_history(
    limit: int = typer.Option(10, "--limit", "-l", help="显示记录数"),
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="配置文件路径"),
):
    """显示分析历史记录"""
    cm = ConfigManager(config_path)
    history = cm.get_analysis_history(limit)
    
    if not history:
        console.print("[yellow]暂无分析历史记录[/yellow]")
        return
    
    table = Table(title=f"最近 {len(history)} 条分析记录", show_header=True, header_style="bold magenta")
    table.add_column("时间", style="cyan")
    table.add_column("图片数", justify="right")
    table.add_column("当前合格率", justify="right")
    table.add_column("建议合格率", justify="right")
    table.add_column("目录", style="dim")
    
    for record in history:
        eval_data = record.get('evaluation', {})
        current_rate = eval_data.get('current', {}).get('pass_rate', 0) * 100
        suggested_rate = eval_data.get('suggested', {}).get('pass_rate', 0) * 100
        
        table.add_row(
            record.get('timestamp', 'N/A')[:19],
            str(record.get('total_images', 0)),
            f"{current_rate:.1f}%",
            f"{suggested_rate:.1f}%",
            record.get('image_dir', 'N/A')[:50]
        )
    
    console.print(table)


@app.command(name="export")
def export_config(
    output: str = typer.Option(..., "--output", "-o", help="输出文件路径"),
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="配置文件路径"),
):
    """导出配置到文件"""
    cm = ConfigManager(config_path)
    cm.export_config(output)
    console.print(f"[green]✅ 配置已导出到 {output}[/green]")


@app.command(name="import")
def import_config(
    input_file: str = typer.Argument(..., help="要导入的配置文件"),
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="配置文件路径"),
    merge: bool = typer.Option(False, "--merge", "-m", help="合并而非覆盖"),
):
    """从文件导入配置"""
    
    try:
        with open(input_file, 'r') as f:
            new_config = json.load(f)
    except Exception as e:
        console.print(f"[red]❌ 读取文件失败: {e}[/red]")
        raise typer.Exit(code=1)
    
    cm = ConfigManager(config_path)
    
    if merge:
        # 合并模式：只更新阈值和评分，保留历史
        if 'thresholds' in new_config:
            cm.config['thresholds'] = new_config['thresholds']
        if 'scoring' in new_config:
            cm.config['scoring'] = new_config['scoring']
        if 'quality_levels' in new_config:
            cm.config['quality_levels'] = new_config['quality_levels']
        console.print("[yellow]📝 合并模式：已更新阈值、评分和质量等级配置[/yellow]")
    else:
        # 覆盖模式：保留历史记录
        old_history = cm.config.get('analysis_history', [])
        cm.config = new_config
        cm.config['analysis_history'] = old_history
        console.print("[yellow]📝 覆盖模式：已替换配置（保留历史记录）[/yellow]")
    
    cm.config['last_updated'] = '2026-04-07T10:00:00'
    cm._save_config(cm.config)
    
    console.print("[green]✅ 配置已导入[/green]")


@app.command(name="reset")
def reset_config(
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="配置文件路径"),
    yes: bool = typer.Option(False, "--yes", "-y", help="确认重置"),
):
    """重置为默认配置"""
    
    if not yes:
        confirm = typer.confirm("[red]⚠️ 这将重置所有配置，确认吗？[/red]")
        if not confirm:
            console.print("[yellow]已取消[/yellow]")
            return
    
    cm = ConfigManager(config_path)
    cm.config = cm._create_default_config()
    cm._save_config(cm.config)
    
    console.print("[green]✅ 已重置为默认配置[/green]")


def main():
    """配置管理CLI入口"""
    app()


if __name__ == "__main__":
    main()