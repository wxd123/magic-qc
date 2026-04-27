# management/config/configLoader.py
import json
from pathlib import Path
from typing import Dict, Any
from platformdirs import user_config_dir


class ConfigLoader:
    """底层配置加载器"""
    
    def __init__(self, module_name: str, config_filename: str = "config.json"):
        """
        初始化配置加载器
        
        Args:
            module_name: 模块名称（如 'facial'）
            config_filename: 配置文件名（默认为 config.json）
        """
        self.module_name = module_name
        self.config_filename = config_filename
    
    def get_project_config_path(self) -> Path:
        """获取模块默认配置路径（与代码同目录）"""
        current_file = Path(__file__).resolve()
        # loader.py 在 management/config/ 下
        # 配置文件在 management/config/{module_name}/{config_filename}
        return current_file.parent / self.module_name / self.config_filename
    
    def get_user_config_path(self) -> Path:
        """获取用户配置路径"""
        return Path(user_config_dir("magic_qc", "magic_qc")) / self.module_name / self.config_filename
    
    def load(self, path: Path) -> Dict[str, Any]:
        """加载配置文件"""
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_merged(self) -> Dict[str, Any]:
        """加载合并后的配置（用户配置覆盖模块配置）"""
        # 加载模块默认配置
        module_path = self.get_project_config_path()
        module_config = self.load(module_path)
        
        # 加载用户配置并合并
        user_path = self.get_user_config_path()
        if user_path.exists():
            user_config = self.load(user_path)
            return self._deep_merge(module_config, user_config)
        
        return module_config
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """深度合并"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def save(self, path: Path, config: Dict[str, Any]):
        """保存配置文件"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def exists(self, path: Path) -> bool:
        """检查配置文件是否存在"""
        return path.exists()