"""
人脸质控命令行接口 - 子命令组

本模块提供人脸质控相关的命令行接口，作为magic_qc工具的子命令组。
支持单张图片分析、批量目录分析、结果导出等功能。

命令结构:
    magic_qc facial [COMMAND] [OPTIONS] [ARGUMENTS]

可用命令:
    check   - 完整人脸质控检查（对称性+质量）
    symmetry - 仅面部对称性分析
    quality  - 仅图像质量分析
    batch    - 批量对称性分析

典型用法:
    # 批量分析目录下所有图片
    magic_qc facial batch /path/to/images/ -o results.csv
    
    # 单张图片完整检查
    magic_qc facial check portrait.jpg -v
    
    # 仅分析对称性
    magic_qc facial symmetry portrait.jpg
    
    # 批量分析并显示前10张最对称的图片
    magic_qc facial batch /path/to/images/ --top 10 --desc
"""

import typer
from pathlib import Path
from typing import Optional

from magic_qc.business.facial.face_checker import FaceChecker
from magic_qc.business.facial.symmetry_checker import SymmetryChecker
from magic_qc.business.facial.quality_checker import FaceQualityChecker
from magic_qc.interface.facial.display import (
    print_start_batch, print_start_analysis, print_batch_summary,
    print_batch_results, print_truncation_notice, print_single_result,
    print_symmetry_result, print_symmetry_batch_summary,
    print_symmetry_batch_results, print_no_images, print_error
)
from magic_qc.interface.facial.export import (
    save_batch_results, save_symmetry_batch_results, save_single_result
)


# 创建Typer应用，作为facial子命令组
app = typer.Typer(help="人脸质控命令", no_args_is_help=True)


def resolve_output_path(input_path: str, output_file: Optional[str], output_default: bool) -> Optional[Path]:
    """
    解析输出路径
    
    根据输入参数智能决定输出文件的保存位置。
    
    Args:
        input_path: 输入文件或目录路径
        output_file: 命令行指定的输出文件路径（-o/--output参数）
        output_default: 是否使用默认输出位置（-O/--output-default参数）
    
    Returns:
        Optional[Path]: 解析后的输出路径，如果不需要保存则返回None
        
    优先级:
        1. 如果指定了output_file，使用该路径
        2. 如果指定了output_default，根据input_path自动生成:
           - 输入为目录: 目录/face_report.csv
           - 输入为文件: 文件所在目录/文件名_report.csv
        3. 否则返回None（不保存）
    
    Examples:
        >>> resolve_output_path("/path/to/img.jpg", None, True)
        PosixPath("/path/to/img_report.csv")
        
        >>> resolve_output_path("/path/to/dir/", "out.csv", False)
        PosixPath("out.csv")
    """
    if output_default:
        path = Path(input_path)
        if path.is_dir():
            return path / "face_report.csv"
        else:
            return path.parent / f"{path.stem}_report.csv"
    elif output_file:
        return Path(output_file)
    return None


@app.command(name="check")
def check_face(
    input_path: str = typer.Argument(..., help="图片文件或目录路径"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="输出结果文件路径"),
    output_default: bool = typer.Option(False, "--output-default", "-O", help="在输入目录生成 face_report.csv"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示详细信息"),
    sort_by_score: bool = typer.Option(True, "--sort/--no-sort", help="按综合评分排序"),
    descending: bool = typer.Option(True, "--desc/--asc", help="降序排列"),
    top_n: Optional[int] = typer.Option(None, "--top", "-t", help="只显示前N条"),
):
    """
    完整人脸质控检查（对称性+质量）
    
    同时进行面部对称性分析和图像质量分析，输出综合评分和详细报告。
    
    Args:
        input_path: 图片文件路径或包含图片的目录路径
        output_file: 输出结果文件路径（支持CSV格式）
        output_default: 自动在输入目录生成face_report.csv
        verbose: 显示详细信息，包括各项指标的具体数值
        sort_by_score: 批量模式时是否按综合评分排序
        descending: 排序方向，True为降序（高分在前）
        top_n: 只显示前N条结果，适用于大批量分析
    
    Examples:
        # 单张图片检查
        magic_qc facial check portrait.jpg
        
        # 详细模式
        magic_qc facial check portrait.jpg -v
        
        # 批量检查目录
        magic_qc facial check /path/to/images/
        
        # 批量检查并保存结果
        magic_qc facial check /path/to/images/ -o results.csv
        
        # 自动生成报告并只显示前10张
        magic_qc facial check /path/to/images/ -O --top 10
    """
    checker = FaceChecker()
    path = Path(input_path)
    
    output_path = resolve_output_path(input_path, output_file, output_default)
    
    if path.is_dir():
        # 批量处理目录
        print_start_batch(input_path)
        results = checker.batch_check(input_path)
        
        if not results:
            print_no_images()
            return
        
        # 排序
        if sort_by_score:
            results.sort(key=lambda x: x.get('score', 0), reverse=descending)
        
        # 截取前N条
        display_results = results[:top_n] if top_n else results
        
        # 计算统计摘要
        all_scores = [r.get('score', 0) for r in results]
        summary = checker.get_summary(results)
        
        # 打印结果
        print_batch_summary(summary, all_scores)
        print_batch_results(display_results, descending, verbose)
        print_truncation_notice(len(results), len(display_results))
        
        # 保存结果
        if output_path:
            save_batch_results(results, str(output_path), sort_by_score, descending)
    else:
        # 单张图片处理
        print_start_analysis(input_path)
        result = checker.check(input_path)
        
        if "error" in result:
            print_error(result['error'])
            raise typer.Exit(code=1)
        
        print_single_result(result, verbose)
        
        if output_path:
            save_single_result(result, str(output_path))


@app.command(name="symmetry")
def check_symmetry(
    image_path: str = typer.Argument(..., help="图片文件路径"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出结果文件"),
):
    """
    仅面部对称性分析
    
    专注于分析面部的对称性，包括整体对称性、眼睛对称性、亮度平衡等指标，
    并评估图片的真实性（真实人脸 vs AI生成）。
    
    Args:
        image_path: 图片文件路径（支持jpg、png、bmp等格式）
        output: 输出结果文件路径，支持JSON格式
    
    Examples:
        # 基本对称性分析
        magic_qc facial symmetry portrait.jpg
        
        # 分析并保存结果
        magic_qc facial symmetry portrait.jpg -o symmetry_result.json
    
    输出指标:
        - overall_symmetry: 整体对称性分数(0-1)
        - symmetry_level: 对称性等级
        - authenticity_score: 真实性分数(0-100)
        - is_realistic: 是否为真实图片
        - recommendation: 改进建议
    """
    checker = SymmetryChecker()
    result = checker.check(image_path)
    
    if "error" in result:
        print_error(result['error'])
        raise typer.Exit(code=1)
    
    print_symmetry_result(result)
    
    if output:
        save_single_result(result, output)


@app.command(name="quality")
def check_quality(
    image_path: str = typer.Argument(..., help="图片文件路径"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出结果文件"),
):
    """
    仅图像质量分析
    
    分析图片的技术质量指标，包括清晰度、对比度、边缘密度、噪声水平等。
    
    Args:
        image_path: 图片文件路径
        output: 输出结果文件路径
    
    Examples:
        # 质量分析
        magic_qc facial quality blurry_image.jpg
        
        # 分析并保存
        magic_qc facial quality image.jpg -o quality_result.json
    
    输出指标:
        - clarity: 清晰度分数
        - contrast: 对比度分数
        - edge_density: 边缘密度
        - noise_level: 噪声水平
        - quality_score: 综合质量评分(0-100)
        - quality_level: 质量等级
        - recommendation: 改进建议
    """
    checker = FaceQualityChecker()
    result = checker.check(image_path)
    
    if "error" in result:
        print_error(result['error'])
        raise typer.Exit(code=1)
    
    score = result.get('score', 0)
    from magic_qc.interface.facial.display import get_status_and_color, get_icon_for_status
    status, color = get_status_and_color(score)
    icon = get_icon_for_status(status)
    
    from rich.console import Console
    console = Console()
    console.print(f"\n[bold green]✅ 质量分析完成[/bold green]")
    console.print(f"   {icon} {status}")
    console.print(f"   质量评分: [{color}]{score:.1f}[/{color}]/100")
    console.print(f"   质量等级: {result.get('quality_level', 'N/A')}")
    console.print(f"   建议: {result.get('recommendation', 'N/A')}")
    
    if output:
        save_single_result(result, output)


@app.command(name="batch")
def batch_symmetry(
    dir_path: str = typer.Argument(..., help="图片目录路径"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出CSV文件"),
    sort_by_score: bool = typer.Option(True, "--sort/--no-sort", help="按对称性分数排序"),
    descending: bool = typer.Option(True, "--desc/--asc", help="降序排列"),
    top_n: Optional[int] = typer.Option(None, "--top", "-t", help="只显示前N条"),
):
    """
    批量对称性分析
    
    遍历目录下所有图片，批量进行面部对称性分析，支持结果排序和导出。
    
    Args:
        dir_path: 包含图片文件的目录路径
        output: 输出CSV文件路径，便于在Excel中查看分析结果
        sort_by_score: 是否按对称性分数排序
        descending: 排序方向，True为降序（最对称的在前）
        top_n: 只显示前N条结果
    
    支持的图片格式:
        - .jpg, .jpeg, .png, .bmp（包括大写扩展名）
    
    Examples:
        # 批量分析当前目录
        magic_qc facial batch ./images/
        
        # 批量分析并保存CSV
        magic_qc facial batch ./images/ -o analysis_results.csv
        
        # 显示最不对称的10张图片
        magic_qc facial batch ./images/ --top 10 --asc
        
        # 完整示例：分析、排序、保存
        magic_qc facial batch /path/to/support/ -o support_symmetry.csv --top 20 --desc
    
    输出CSV包含字段:
        - filename: 文件名
        - overall_symmetry: 整体对称性分数
        - symmetry_level: 对称性等级
        - authenticity_score: 真实性分数
        - is_realistic: 是否真实
        - recommendation: 建议
    """
    print_start_batch(dir_path)
    
    if not Path(dir_path).is_dir():
        print_error(f"目录不存在: {dir_path}")
        raise typer.Exit(code=1)
    
    checker = SymmetryChecker()
    results = []
    
    # 遍历所有支持的图片格式（支持大小写扩展名）
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
        for p in Path(dir_path).glob(ext):
            result = checker.check(str(p))
            if "error" not in result:
                results.append(result)
        for p in Path(dir_path).glob(ext.upper()):
            result = checker.check(str(p))
            if "error" not in result:
                results.append(result)
    
    if not results:
        print_no_images()
        return
    
    # 排序
    if sort_by_score:
        results.sort(key=lambda x: x.get('overall_symmetry', 0), reverse=descending)
    
    # 截取前N条
    display_results = results[:top_n] if top_n else results
    
    # 打印结果
    print_symmetry_batch_summary(results)
    print_symmetry_batch_results(display_results, descending)
    
    # 保存结果
    if output:
        save_symmetry_batch_results(results, output, sort_by_score, descending)


def main():
    """
    CLI入口函数
    
    供外部调用的主入口，执行Typer应用。
    """
    app()


if __name__ == "__main__":
    main()