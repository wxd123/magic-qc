# interface/facial/display.py
"""
控制台输出模块 - 负责所有终端显示相关的函数
"""

from typing import Dict, Any, Tuple
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


# ============================================================
# 配置辅助函数
# ============================================================

_quality_rules = None

def _get_quality_config():
    """获取质量配置（懒加载）"""
    global _quality_rules
    try:
        from magic_qc.management.rules.facial.quality_rules import FaceQualityRules
        if _quality_rules is None:
            _quality_rules = FaceQualityRules()
        return _quality_rules
    except Exception:
        return None


def get_status_and_color(score: float) -> Tuple[str, str]:
    """从配置获取状态和颜色"""
    rules = _get_quality_config()
    if rules:
        try:
            return rules.get_status_and_color(score)
        except Exception:
            pass
    
    # 降级：使用默认值（状态文字统一为2个字符）
    if score >= 85:
        return "优秀", "green"
    elif score >= 80:
        return "良好", "cyan"
    elif score >= 60:
        return "合格", "yellow"
    else:
        return "差", "red"  # 改为2个字符，保持宽度一致


def get_icon_for_status(status: str) -> str:
    """根据状态获取图标"""
    icon_map = {
        "优秀": "✅",
        "良好": "👍",
        "合格": "⚠️",
        "不合格": "❌"
    }
    return icon_map.get(status, "📷")


# ============================================================
# 批量结果摘要显示
# ============================================================

def print_batch_summary(summary: Dict[str, Any], all_scores: list) -> None:
    """打印批量检测摘要"""
    console.print(f"\n[bold green]✅ 批量分析完成[/bold green]")
    console.print(f"   总图片数: {summary['total']}")
    console.print(f"   ✅ 通过: {summary['passed']}")
    console.print(f"   ❌ 不通过: {summary['failed']}")
    console.print(f"   📊 平均评分: {summary['avg_score']:.1f}/100")
    console.print(f"   📊 最高分: {max(all_scores):.1f}")
    console.print(f"   📊 最低分: {min(all_scores):.1f}")


def truncate_filename(filename: str, max_len: int = 30, keep_end: int = 10) -> str:
    """智能截断文件名，保留末尾指定长度"""
    if len(filename) <= max_len:
        return filename
    
    keep_start = max_len - 3 - keep_end
    if keep_start <= 0:
        return f"...{filename[-max_len+3:]}"
    
    return f"{filename[:keep_start]}...{filename[-keep_end:]}"



# interface/facial/display.py

def print_batch_results(display_results: list, descending: bool, verbose: bool = False) -> None:
    """打印批量检测结果列表"""
    console.print(f"\n[bold cyan]📋 详细结果（按评分{'降序' if descending else '升序'}）:[/bold cyan]")
    
    # 创建表格 - 三维建模专用
    table = Table(title="人脸三维建模质控检查结果", show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("文件名", style="white", max_width=50)
    table.add_column("对称性", justify="right", width=10)
    table.add_column("亮度比", justify="right", width=10)  # 新增
    table.add_column("清晰度", justify="right", width=10)
    table.add_column("对比度", justify="right", width=10)
    table.add_column("噪点", justify="right", width=10)
    table.add_column("综合评分", justify="right", width=10)
    table.add_column("建模适用性", width=10)
    
    for i, result in enumerate(display_results, 1):
        # 获取基础信息
        score = result.get('score', 0)
        filename = result.get('filename', 'N/A')
        if filename is None:
            filename = "N/A"
        display_name = truncate_filename(str(filename), max_len=50, keep_end=20)
        
        # 获取状态和颜色
        status, color = get_status_and_color(score)
        
        # 获取各指标
        overall_symmetry = result.get('overall_symmetry', 0)
        lr_ratio = result.get('lr_ratio', 1.0)  # 新增：获取亮度比
        clarity = result.get('clarity', 0)
        contrast = result.get('contrast', 0)
        noise_level = result.get('noise_level', 0)
        
        # 清晰度颜色
        clarity_color = "green" if clarity >= 120 else ("cyan" if clarity >= 80 else ("yellow" if clarity >= 50 else "red"))
        contrast_color = "green" if contrast >= 60 else ("cyan" if contrast >= 45 else ("yellow" if contrast >= 30 else "red"))
        noise_color = "green" if noise_level <= 8 else ("cyan" if noise_level <= 15 else ("yellow" if noise_level <= 25 else "red"))
        
        table.add_row(
            str(i),
            display_name,
            f"{overall_symmetry:.3f}",
            f"{lr_ratio:.3f}",  # 新增：只显示数值，无颜色
            f"[{clarity_color}]{clarity:.1f}[/{clarity_color}]",
            f"[{contrast_color}]{contrast:.1f}[/{contrast_color}]",
            f"[{noise_color}]{noise_level:.1f}[/{noise_color}]",
            f"[{color}]{score:.1f}[/{color}]",
            f"[{color}]{status}[/{color}]"
        )
    
    console.print(table)
    
    # verbose模式显示更详细的指标
    if verbose:
        console.print("\n[bold cyan]📊 详细指标（仅显示前3条）:[/bold cyan]")
        for i, result in enumerate(display_results[:3], 1):
            console.print(f"\n[bold]📷 {result.get('filename', 'N/A')}[/bold]")
            console.print(f"   对称性: {result.get('overall_symmetry', 0):.4f}")
            console.print(f"   亮度比: {result.get('lr_ratio', 1.0):.3f}")  # 新增
            console.print(f"   清晰度: {result.get('clarity', 0):.1f}")
            console.print(f"   对比度: {result.get('contrast', 0):.1f}")
            console.print(f"   噪点: {result.get('noise_level', 0):.2f}")
            console.print(f"   边缘密度: {result.get('edge_density', 0):.4f}")
            console.print(f"   质量评分: {result.get('quality_score', 0):.1f}")

            
def print_truncation_notice(total: int, displayed: int) -> None:
    """打印截断提示"""
    if displayed < total:
        console.print(f"\n[dim]... 还有 {total - displayed} 条结果未显示，使用 --top 调整显示数量[/dim]")


# ============================================================
# 单张结果显示
# ============================================================

def print_single_result(result: Dict[str, Any], verbose: bool = False) -> None:
    """打印单张图片检测结果"""
    score = result.get('score', 0)
    status, color = get_status_and_color(score)
    icon = get_icon_for_status(status)
    
    console.print(f"\n[bold green]✅ 人脸质控检查完成[/bold green]")
    console.print(f"   {icon} {status}")
    console.print(f"   📊 综合评分: [{color}]{score:.1f}[/{color}]/100")
    
    if verbose:
        print_verbose_details(result)


def print_single_brief(result: Dict[str, Any], indent: int = 0) -> None:
    """打印单张图片简要信息（用于批量模式）"""
    padding = " " * indent
    symmetry = result.get('symmetry', {})
    quality = result.get('quality', {})
    metrics = quality.get('metrics', {})
    
    console.print(f"{padding}对称性: {symmetry.get('overall_symmetry', 0):.3f}")
    console.print(f"{padding}质量: {quality.get('score', 0):.1f}")
    if metrics:
        console.print(f"{padding}清晰度: {metrics.get('clarity', 0):.1f} | 对比度: {metrics.get('contrast', 0):.1f}")
        console.print(f"{padding}边缘密度: {metrics.get('edge_density', 0):.4f} | 噪声: {metrics.get('noise_level', 0):.1f}")


# ============================================================
# 详细结果显示
# ============================================================

def print_verbose_details(result: Dict[str, Any]) -> None:
    """打印详细结果（包含所有指标）"""
    
    # 对称性分析详情
    if result.get("symmetry"):
        _print_symmetry_details(result["symmetry"])
    
    # 质量分析详情
    if result.get("quality"):
        _print_quality_details(result["quality"])


def _print_symmetry_details(symmetry_data: Dict[str, Any]) -> None:
    """打印对称性分析详情"""
    console.print("\n[bold cyan]📊 对称性分析详情:[/bold cyan]")
    console.print(f"   对称性分数: {symmetry_data.get('overall_symmetry', 0):.4f}")
    console.print(f"   对称性等级: {symmetry_data.get('symmetry_level', 'N/A')}")
    console.print(f"   真实性评分: {symmetry_data.get('authenticity_score', 0):.1f}/100")
    console.print(f"   是否真实人脸: {'✅ 是' if symmetry_data.get('is_realistic') else '⚠️ 否（可能AI生成）'}")
    console.print(f"   左右亮度比: {symmetry_data.get('details', {}).get('left_right_ratio', 0):.4f}")
    console.print(f"   建议: {symmetry_data.get('recommendation', 'N/A')}")


def _print_quality_details(quality_data: Dict[str, Any]) -> None:
    """打印质量分析详情（从配置文件读取指标配置）"""
    score = quality_data.get('score', 0)
    status, color = get_status_and_color(score)
    
    console.print("\n[bold cyan]📷 图像质量分析详情:[/bold cyan]")
    console.print(f"   综合质量评分: [{color}]{score:.1f}[/{color}]/100")
    console.print(f"   质量等级: {quality_data.get('quality_level', 'N/A')}")
    console.print(f"   状态: {status}")
    console.print(f"   建议: {quality_data.get('recommendation', 'N/A')}")
    
    # 详细指标
    metrics = quality_data.get('metrics', {})
    if metrics:
        console.print("\n[bold]📈 详细指标:[/bold]")
        _print_metrics_table(metrics)


def _print_metrics_table(metrics: Dict[str, float]) -> None:
    """打印指标表格（从配置读取）"""
    rules = _get_quality_config()
    metric_display = {}
    thresholds = {}
    
    if rules:
        metric_display = getattr(rules, 'get_metric_display_config', lambda: {})()
        thresholds = rules.thresholds
    
    for metric_name, value in metrics.items():
        display = metric_display.get(metric_name, {})
        label = display.get('label', metric_name)
        icon = display.get('icon', '📊')
        precision = display.get('precision', 2)
        
        # 判断状态
        status_icon, status_text = _get_metric_status(metric_name, value, thresholds)
        
        # 格式化数值
        if precision == 0:
            formatted_value = f"{int(value)}"
        else:
            formatted_value = f"{value:.{precision}f}"
        
        console.print(f"   {icon} {label}: {formatted_value} {status_icon} {status_text}".strip())


def _get_metric_status(metric_name: str, value: float, thresholds: Dict) -> Tuple[str, str]:
    """获取单个指标的状态和图标"""
    metric_thresholds = thresholds.get(metric_name, {})
    if not metric_thresholds:
        return "❓", "未知"
    
    higher_is_better = metric_thresholds.get('higher_is_better', True)
    
    if higher_is_better:
        if value >= metric_thresholds.get('excellent', float('inf')):
            return "✅", "优秀"
        elif value >= metric_thresholds.get('good', float('inf')):
            return "👍", "良好"
        elif value >= metric_thresholds.get('pass', float('inf')):
            return "⚠️", "合格"
        else:
            return "❌", "较差"
    else:
        if value <= metric_thresholds.get('excellent', float('-inf')):
            return "✅", "优秀"
        elif value <= metric_thresholds.get('good', float('-inf')):
            return "👍", "良好"
        elif value <= metric_thresholds.get('pass', float('-inf')):
            return "⚠️", "合格"
        else:
            return "❌", "较差"


# ============================================================
# 对称性分析显示
# ============================================================

def print_symmetry_result(result: Dict[str, Any]) -> None:
    """打印对称性分析结果"""
    console.print(f"\n[bold green]✅ 对称性分析完成[/bold green]")
    console.print(f"   对称性分数: {result.get('overall_symmetry', 0):.3f}")
    console.print(f"   对称性等级: {result.get('symmetry_level', 'N/A')}")
    console.print(f"   真实性评分: {result.get('authenticity_score', 0):.1f}/100")
    console.print(f"   {'✅ 真实人脸' if result.get('is_realistic') else '⚠️ 可能AI生成'}")


def print_symmetry_batch_summary(results: list) -> None:
    """打印对称性批量分析摘要"""
    scores = [r.get('overall_symmetry', 0) for r in results]
    console.print(f"\n[bold green]✅ 批量分析完成，共处理 {len(results)} 张图片[/bold green]")
    console.print(f"📊 平均对称性: {sum(scores)/len(scores):.3f}")
    console.print(f"📊 最高分: {max(scores):.3f}")
    console.print(f"📊 最低分: {min(scores):.3f}")


def print_symmetry_batch_results(display_results: list, descending: bool) -> None:
    """打印对称性批量结果"""
    console.print(f"\n[bold cyan]📋 详细结果（按对称性分数{'降序' if descending else '升序'}）:[/bold cyan]")
    
    for i, result in enumerate(display_results, 1):
        score = result.get('overall_symmetry', 0)
        filename = result.get('filename', 'N/A')
        
        if score >= 0.9:
            color, icon, level = "green", "✅", "优秀"
        elif score >= 0.8:
            color, icon, level = "cyan", "👍", "良好"
        elif score >= 0.7:
            color, icon, level = "yellow", "⚠️", "合格"
        else:
            color, icon, level = "red", "❌", "较差"
        
        console.print(f"  {i:3d}. [{color}]{score:.3f}[/{color}] {icon} {level} - {filename}")


# ============================================================
# 进度显示
# ============================================================

def create_progress() -> Progress:
    """创建进度条"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    )


def print_start_analysis(file_path: str) -> None:
    """打印开始分析提示"""
    console.print(f"[bold blue]🔍 正在分析: {file_path}[/bold blue]")


def print_start_batch(dir_path: str) -> None:
    """打印开始批量分析提示"""
    console.print(f"[bold blue]📁 批量分析目录: {dir_path}[/bold blue]")


def print_no_images() -> None:
    """打印未找到图片提示"""
    console.print("[yellow]⚠️ 未找到可分析的图片[/yellow]")


def print_error(message: str) -> None:
    """打印错误信息"""
    console.print(f"[red]❌ {message}[/red]")


def print_success(message: str) -> None:
    """打印成功信息"""
    console.print(f"[green]✅ {message}[/green]")


def print_warning(message: str) -> None:
    """打印警告信息"""
    console.print(f"[yellow]⚠️ {message}[/yellow]")