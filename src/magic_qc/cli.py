"""
magic_qc 命令行接口 - 主入口

本模块是 magic_qc 工具的主命令行入口，负责注册所有子命令组。
"""

import typer
from rich.console import Console

from magic_qc.interface import facial_cli
from magic_qc.interface import config_cli


# 创建主应用
app = typer.Typer(help="magic_qc - 统一质控工具", no_args_is_help=True)
console = Console()


# 注册子命令组
app.add_typer(facial_cli.app, name="facial", help="人脸质控命令")
app.add_typer(config_cli.app, name="config", help="质量标准配置管理")


@app.command(name="version")
def version():
    """显示版本信息"""
    console.print("[bold cyan]magic_qc v1.0.0[/bold cyan]")
    console.print("统一质控工具 - 人脸图像质量与对称性分析")


def main():
    """主入口"""
    app()


if __name__ == "__main__":
    main()