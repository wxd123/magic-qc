# `magic_qc`

## Table of Contents

- 🅼 [magic_qc](#magic_qc)
- 🅼 [magic_qc\.\_\_main\_\_](#magic_qc-__main__)
- 🅼 [magic_qc\.business](#magic_qc-business)
- 🅼 [magic_qc\.business\.facial](#magic_qc-business-facial)
- 🅼 [magic_qc\.business\.facial\.facial\_symmetry](#magic_qc-business-facial-facial_symmetry)
- 🅼 [magic_qc\.cli](#magic_qc-cli)
- 🅼 [magic_qc\.core](#magic_qc-core)
- 🅼 [magic_qc\.core\.engine](#magic_qc-core-engine)
- 🅼 [magic_qc\.interface](#magic_qc-interface)
- 🅼 [magic_qc\.interface\.cli](#magic_qc-interface-cli)
- 🅼 [magic_qc\.interface\.visualization](#magic_qc-interface-visualization)
- 🅼 [magic_qc\.management](#magic_qc-management)
- 🅼 [magic_qc\.management\.rules](#magic_qc-management-rules)
- 🅼 [magic_qc\.management\.rules\.facial\_symmetry\_rules](#magic_qc-management-rules-facial_symmetry_rules)
- 🅼 [magic_qc\.technology](#magic_qc-technology)
- 🅼 [magic_qc\.technology\.facial](#magic_qc-technology-facial)
- 🅼 [magic_qc\.technology\.facial\.feature\_detector](#magic_qc-technology-facial-feature_detector)
- 🅼 [magic_qc\.technology\.facial\.image\_processor](#magic_qc-technology-facial-image_processor)
- 🅼 [magic_qc\.technology\.facial\.symmetry](#magic_qc-technology-facial-symmetry)
- 🅼 [magic_qc\.utils](#magic_qc-utils)

<a name="magic_qc"></a>
## 🅼 magic_qc

Top-level package for magic_qc\.
<a name="magic_qc-__main__"></a>
## 🅼 magic_qc\.\_\_main\_\_
<a name="magic_qc-business"></a>
## 🅼 magic_qc\.business
<a name="magic_qc-business-facial"></a>
## 🅼 magic_qc\.business\.facial
<a name="magic_qc-business-facial-facial_symmetry"></a>
## 🅼 magic_qc\.business\.facial\.facial\_symmetry

面部对称性质检业务模块

本模块提供面部对称性分析的业务逻辑，协调技术层和管理层完成：
- 单张图片的对称性分析
- 批量图片的对称性分析
- 结果汇总与导出

典型用法:
    from magic_qc\.business\.facial\_symmetry import FacialSymmetryChecker
    
    checker = FacialSymmetryChecker\(\)
    
    \# 单张分析
    result = checker\.analyze\("path/to/image\.jpg"\)
    print\(f"对称性分数: \{result\['overall\_symmetry'\]\}"\)
    
    \# 批量分析
    results = checker\.batch\_analyze\("path/to/images/", output\_csv="results\.csv"\)

- **Classes:**
  - 🅲 [FacialSymmetryChecker](#magic_qc-business-facial-facial_symmetry-FacialSymmetryChecker)

### Classes

<a name="magic_qc-business-facial-facial_symmetry-FacialSymmetryChecker"></a>
### 🅲 magic_qc\.business\.facial\.facial\_symmetry\.FacialSymmetryChecker

```python
class FacialSymmetryChecker:
```

面部对称性质检业务类

负责协调技术层（图像处理、特征检测、对称性计算）和管理层（规则判断），
完成完整的面部对称性分析流程。

工作流程:
    1\. 加载图片并转换为灰度图
    2\. 计算整体对称性分数
    3\. 检测人脸和眼睛特征
    4\. 计算眼睛对称性分数
    5\. 分析对称性分布标准差
    6\. 综合评估真实性分数
    7\. 返回结构化的分析结果

**Attributes:**

- **tech_sym** (`SymmetryCalculator`): 对称性计算器（技术层）
- **tech_detector** (`FeatureDetector`): 特征检测器（技术层）
- **rules** (`FacialSymmetryRules`): 面部对称性规则库（管理层）

**Functions:**

<a name="magic_qc-business-facial-facial_symmetry-FacialSymmetryChecker-__init__"></a>
#### 🅵 magic_qc\.business\.facial\.facial\_symmetry\.FacialSymmetryChecker\.\_\_init\_\_

```python
def __init__(self):
```

初始化面部对称性质检器

创建技术层和管理层的实例，用于后续分析。
<a name="magic_qc-business-facial-facial_symmetry-FacialSymmetryChecker-analyze"></a>
#### 🅵 magic_qc\.business\.facial\.facial\_symmetry\.FacialSymmetryChecker\.analyze

```python
def analyze(self, image_path: str) -> Dict[str, Any]:
```

分析单张图片的面部对称性

这是核心分析方法，协调各层完成完整的分析流程。

Args:
    image\_path \(str\): 图片文件路径，支持 jpg、png、bmp 等格式

Returns:
    Dict\[str, Any\]: 分析结果字典，包含以下字段:
        - filename \(str\): 文件名
        - overall\_symmetry \(float\): 整体对称性分数，0-1之间，越高越对称
        - symmetry\_level \(str\): 对称性等级，'high' / 'medium' / 'low'
        - authenticity\_score \(float\): 真实性分数，0-100
        - authenticity\_level \(str\): 真实性等级，'真实' / '可能AI生成'
        - is\_realistic \(bool\): 是否为真实图片（分数 \>= 60）
        - recommendation \(str\): 改进建议
        - details \(dict\): 详细指标，包含:
            - eye\_symmetry \(float\): 眼睛对称性分数
            - left\_right\_ratio \(float\): 左右亮度比例
            - distribution\_std \(float\): 对称性分布标准差

Raises:
    不直接抛出异常，而是返回包含 "error" 字段的字典

Examples:
    \>\>\> checker = FacialSymmetryChecker\(\)
    \>\>\> result = checker\.analyze\("portrait\.jpg"\)
    \>\>\> if "error" not in result:
    \.\.\.     print\(f"对称性: \{result\['overall\_symmetry'\]\}"\)
    \.\.\.     print\(f"建议: \{result\['recommendation'\]\}"\)
    \.\.\. else:
    \.\.\.     print\(f"错误: \{result\['error'\]\}"\)
<a name="magic_qc-business-facial-facial_symmetry-FacialSymmetryChecker-batch_analyze"></a>
#### 🅵 magic_qc\.business\.facial\.facial\_symmetry\.FacialSymmetryChecker\.batch\_analyze

```python
def batch_analyze(self, image_dir: str, output_csv: Optional[str] = None, extensions: List[str] = None) -> List[Dict[str, Any]]:
```

批量分析目录下的所有图片

遍历指定目录，对所有符合扩展名的图片进行分析，
可选择性地将结果保存到 CSV 文件。

**Parameters:**

- **image_dir** (`str`): 图片目录路径
- **output_csv** (`Optional[str]`): 输出CSV文件路径。
如果提供，会将分析结果保存为CSV格式。
- **extensions** (`List[str]`): 图片扩展名列表，默认支持
\['\*\.png', '\*\.jpg', '\*\.jpeg', '\*\.bmp'\]

**Returns:**

- `List[Dict[str, Any]]`: 分析结果列表，每个元素与 analyze\(\) 返回结构一致。
如果目录不存在或无图片，返回空列表。
<a name="magic_qc-cli"></a>
## 🅼 magic_qc\.cli

magic_qc 命令行接口模块

本模块提供 magic_qc 工具的命令行入口，基于 Typer 框架实现。
用户通过命令行与工具交互，支持单张图片分析和批量分析两种模式。

典型用法:
    \# 单张图片分析
    python -m magic_qc\.cli analyze path/to/image\.jpg
    
    \# 单张图片分析并保存结果
    python -m magic_qc\.cli analyze path/to/image\.jpg -o result\.json
    
    \# 详细模式输出
    python -m magic_qc\.cli analyze path/to/image\.jpg -v
    
    \# 批量分析目录
    python -m magic_qc\.cli batch path/to/images/ -o report\.csv
    
    \# 查看版本
    python -m magic_qc\.cli version

- **Functions:**
  - 🅵 [analyze](#magic_qc-cli-analyze)
  - 🅵 [batch](#magic_qc-cli-batch)
  - 🅵 [version](#magic_qc-cli-version)
  - 🅵 [main](#magic_qc-cli-main)

### Functions

<a name="magic_qc-cli-analyze"></a>
### 🅵 magic_qc\.cli\.analyze

```python
def analyze(image_path: str = typer.Argument(..., help='图片文件路径'), output: Optional[str] = typer.Option(None, '--output', '-o', help='输出结果文件'), verbose: bool = typer.Option(False, '--verbose', '-v', help='显示详细信息')):
```

分析单张图片的面部对称性

对指定图片进行面部对称性分析，输出对称性分数、真实性评分等指标。

**Parameters:**

- **image_path**: 图片文件路径（支持 jpg、png、bmp 等格式）
- **output**: 可选，JSON 格式的结果输出文件路径
- **verbose**: 是否显示详细信息（包括 eye\_symmetry, left\_right\_ratio 等）

**Returns:**

- `None`: 结果直接打印到控制台，可选保存到文件

**Raises:**

- **typer.Exit**: 当文件不存在、初始化失败或分析失败时退出
<a name="magic_qc-cli-batch"></a>
### 🅵 magic_qc\.cli\.batch

```python
def batch(dir_path: str = typer.Argument(..., help='图片目录路径'), output: Optional[str] = typer.Option(None, '--output', '-o', help='输出CSV文件')):
```

批量分析目录下的所有图片

遍历指定目录，对所有图片进行面部对称性分析，输出统计摘要。
可选择将结果保存为 CSV 文件。

**Parameters:**

- **dir_path**: 图片目录路径
- **output**: 可选，CSV 格式的结果输出文件路径

**Returns:**

- `None`: 结果直接打印到控制台，可选保存到 CSV

**Raises:**

- **typer.Exit**: 当目录不存在时退出
<a name="magic_qc-cli-version"></a>
### 🅵 magic_qc\.cli\.version

```python
def version():
```

显示版本信息

输出 magic_qc 工具的当前版本号和功能说明。
<a name="magic_qc-cli-main"></a>
### 🅵 magic_qc\.cli\.main

```python
def main():
```

主入口函数

供外部程序调用，启动 Typer 命令行应用。
<a name="magic_qc-core"></a>
## 🅼 magic_qc\.core
<a name="magic_qc-core-engine"></a>
## 🅼 magic_qc\.core\.engine
<a name="magic_qc-interface"></a>
## 🅼 magic_qc\.interface
<a name="magic_qc-interface-cli"></a>
## 🅼 magic_qc\.interface\.cli

命令行接口模块 - 接口层

本模块提供 magic_qc 的命令行入口（基于 argparse 的轻量级版本）。
职责：接收命令行参数，调用业务层，输出结果。

与 cli\.py 的关系：
    - interface/cli\.py: 基于 argparse 的简单命令行实现
    - cli\.py: 基于 typer \+ rich 的功能更完整的命令行实现

典型用法:
    \# 单张图片分析
    python -m magic_qc\.interface\.cli path/to/image\.jpg
    
    \# 分析并保存结果
    python -m magic_qc\.interface\.cli path/to/image\.jpg -o result\.json
    
    \# 查看帮助
    python -m magic_qc\.interface\.cli -h

- **Functions:**
  - 🅵 [parse\_arguments](#magic_qc-interface-cli-parse_arguments)
  - 🅵 [print\_result](#magic_qc-interface-cli-print_result)
  - 🅵 [save\_result](#magic_qc-interface-cli-save_result)
  - 🅵 [main](#magic_qc-interface-cli-main)

### Functions

<a name="magic_qc-interface-cli-parse_arguments"></a>
### 🅵 magic_qc\.interface\.cli\.parse\_arguments

```python
def parse_arguments() -> argparse.Namespace:
```

解析命令行参数

**Returns:**

- `argparse.Namespace`: 解析后的参数对象，包含以下属性:
- image \(str\): 图像文件路径
- output \(Optional\[str\]\): 输出结果文件路径
<a name="magic_qc-interface-cli-print_result"></a>
### 🅵 magic_qc\.interface\.cli\.print\_result

```python
def print_result(result: Dict[str, Any]) -> None:
```

打印分析结果到控制台

**Parameters:**

- **result** (`Dict[str, Any]`): analyze\(\) 方法返回的结果字典
<a name="magic_qc-interface-cli-save_result"></a>
### 🅵 magic_qc\.interface\.cli\.save\_result

```python
def save_result(result: Dict[str, Any], output_path: str) -> None:
```

保存分析结果到 JSON 文件

**Parameters:**

- **result** (`Dict[str, Any]`): analyze\(\) 方法返回的结果字典
- **output_path** (`str`): 输出文件路径
<a name="magic_qc-interface-cli-main"></a>
### 🅵 magic_qc\.interface\.cli\.main

```python
def main() -> None:
```

命令行入口函数

完成以下流程:
    1\. 解析命令行参数
    2\. 验证输入文件存在性
    3\. 调用业务层进行对称性分析
    4\. 输出结果（控制台或文件）

**Returns:**

- None

**Raises:**

- **SystemExit**: 当文件不存在时退出（exit code 1）
<a name="magic_qc-interface-visualization"></a>
## 🅼 magic_qc\.interface\.visualization
<a name="magic_qc-management"></a>
## 🅼 magic_qc\.management
<a name="magic_qc-management-rules"></a>
## 🅼 magic_qc\.management\.rules
<a name="magic_qc-management-rules-facial_symmetry_rules"></a>
## 🅼 magic_qc\.management\.rules\.facial\_symmetry\_rules

面部对称性规则库 - 管理域

本模块提供面部对称性分析的规则定义和判断逻辑。

职责：
- 存储对称性阈值和真人面部数据范围
- 提供对称性等级判定
- 计算真实性分数
- 生成分析建议

典型用法:
    from magic_qc\.management\.rules\.facial\_symmetry\_rules import FacialSymmetryRules
    
    rules = FacialSymmetryRules\(\)
    
    \# 获取对称性等级
    level = rules\.get\_symmetry\_level\(0\.85\)
    
    \# 计算真实性分数
    score = rules\.get\_authenticity\_score\(
        overall=0\.82, eye\_sym=0\.91, 
        distribution\_std=0\.09, lr\_ratio=0\.89
    \)

- **Classes:**
  - 🅲 [SymmetryThresholds](#magic_qc-management-rules-facial_symmetry_rules-SymmetryThresholds)
  - 🅲 [RealFaceData](#magic_qc-management-rules-facial_symmetry_rules-RealFaceData)
  - 🅲 [FacialSymmetryRules](#magic_qc-management-rules-facial_symmetry_rules-FacialSymmetryRules)

### Classes

<a name="magic_qc-management-rules-facial_symmetry_rules-SymmetryThresholds"></a>
### 🅲 magic_qc\.management\.rules\.facial\_symmetry\_rules\.SymmetryThresholds

```python
class SymmetryThresholds:
```

对称性阈值定义

定义不同对称性等级的分数边界。
数值基于大量真实人脸数据的统计分析得出。

**Attributes:**

- **perfect** (`float`): 过度对称阈值，\>95% 通常为AI生成
- **excellent** (`float`): 优秀对称阈值，90-95% 非常对称
- **good** (`float`): 良好对称阈值，85-90% 较为对称
- **normal** (`float`): 正常不对称阈值，75-85% 真实人脸常见范围
- **low** (`float`): 明显不对称阈值，60-75% 存在明显不对称
<a name="magic_qc-management-rules-facial_symmetry_rules-RealFaceData"></a>
### 🅲 magic_qc\.management\.rules\.facial\_symmetry\_rules\.RealFaceData

```python
class RealFaceData:
```

真人面部数据范围

存储真实人脸各部位对称性的正常范围。
超出这些范围可能表明图像为AI生成或经过过度美化。

**Attributes:**

- **eyes** (`Tuple[float, float]`): 眼睛对称性正常范围 \(min, max\)
- **eyebrows** (`Tuple[float, float]`): 眉毛对称性正常范围
- **nose** (`Tuple[float, float]`): 鼻子对称性正常范围
- **mouth** (`Tuple[float, float]`): 嘴巴对称性正常范围
- **contour** (`Tuple[float, float]`): 面部轮廓对称性正常范围
<a name="magic_qc-management-rules-facial_symmetry_rules-FacialSymmetryRules"></a>
### 🅲 magic_qc\.management\.rules\.facial\_symmetry\_rules\.FacialSymmetryRules

```python
class FacialSymmetryRules:
```

面部对称性规则库

提供基于规则的对称性分析和真实性判断。
所有判断逻辑集中在此类中，便于维护和调整阈值。

规则设计原则:
    1\. 真实人脸存在自然的不对称性
    2\. 过度对称通常表明AI生成或过度美化
    3\. 各部位对称性应在特定范围内才真实

**Attributes:**

- **thresholds** (`SymmetryThresholds`): 对称性阈值配置
- **real_face** (`RealFaceData`): 真人面部数据范围配置

**Functions:**

<a name="magic_qc-management-rules-facial_symmetry_rules-FacialSymmetryRules-__init__"></a>
#### 🅵 magic_qc\.management\.rules\.facial\_symmetry\_rules\.FacialSymmetryRules\.\_\_init\_\_

```python
def __init__(self):
```

初始化规则库

创建对称性阈值和真人数据范围的实例。
<a name="magic_qc-management-rules-facial_symmetry_rules-FacialSymmetryRules-get_symmetry_level"></a>
#### 🅵 magic_qc\.management\.rules\.facial\_symmetry\_rules\.FacialSymmetryRules\.get\_symmetry\_level

```python
def get_symmetry_level(self, score: float) -> str:
```

根据对称性分数返回等级描述

分数越高表示越对称，但过度对称反而可能不真实。

**Parameters:**

- **score** (`float`): 对称性分数，取值范围 0-1

**Returns:**

- `str`: 对称性等级描述，可能的值:
- "过度对称（可能不真实）": score \>= 0\.95
- "优秀对称": score \>= 0\.90
- "良好对称": score \>= 0\.85
- "正常不对称（真实）": score \>= 0\.75
- "明显不对称": score \>= 0\.60
- "严重不对称": score \< 0\.60
<a name="magic_qc-management-rules-facial_symmetry_rules-FacialSymmetryRules-is_eye_symmetry_realistic"></a>
#### 🅵 magic_qc\.management\.rules\.facial\_symmetry\_rules\.FacialSymmetryRules\.is\_eye\_symmetry\_realistic

```python
def is_eye_symmetry_realistic(self, score: float) -> bool:
```

判断眼睛对称性是否在真实人脸范围内

真实人脸的左右眼存在轻微不对称，完全对称反而异常。

**Parameters:**

- **score** (`float`): 眼睛对称性分数，取值范围 0-1

**Returns:**

- `bool`: True 表示在真实范围内，False 表示超出真实范围
<a name="magic_qc-management-rules-facial_symmetry_rules-FacialSymmetryRules-get_authenticity_score"></a>
#### 🅵 magic_qc\.management\.rules\.facial\_symmetry\_rules\.FacialSymmetryRules\.get\_authenticity\_score

```python
def get_authenticity_score(self, overall: float, eye_sym: float, distribution_std: float, lr_ratio: float) -> float:
```

计算真实性分数

综合多个维度评估图片是真实人脸还是AI生成。
分数越高越可能是真实人脸。

评分权重:
    - 整体对称性: 30分（适中为佳，过高过低都扣分）
    - 眼睛对称性: 25分（在真实范围内满分）
    - 对称性分布: 25分（标准差大说明自然，满分）
    - 亮度平衡: 20分（适中为佳）

**Parameters:**

- **overall** (`float`): 整体对称性分数，取值范围 0-1
- **eye_sym** (`float`): 眼睛对称性分数，取值范围 0-1
- **distribution_std** (`float`): 对称性分布标准差，越大越自然
- **lr_ratio** (`float`): 左右亮度比例，0\.85-0\.95 为理想范围

**Returns:**

- `float`: 真实性分数，取值范围 0-100，分数越高越真实
<a name="magic_qc-management-rules-facial_symmetry_rules-FacialSymmetryRules-get_recommendation"></a>
#### 🅵 magic_qc\.management\.rules\.facial\_symmetry\_rules\.FacialSymmetryRules\.get\_recommendation

```python
def get_recommendation(self, authenticity_score: float, is_realistic: bool) -> str:
```

根据真实性分数返回使用建议

提供针对不同真实性等级的实用建议，
帮助用户判断该图片是否适合作为建模参考。

**Parameters:**

- **authenticity_score** (`float`): 真实性分数，0-100
- **is_realistic** (`bool`): 是否为真实图片（分数 \>= 60）

**Returns:**

- `str`: 使用建议，根据分数等级返回不同建议:
- \>=85: 高度推荐作为建模参考
- \>=70: 推荐作为建模参考
- \>=60: 可用作参考，但需注意
- \>=50: 可能AI生成，使用需调整
- \<50: 不建议作为主要参考
<a name="magic_qc-technology"></a>
## 🅼 magic_qc\.technology
<a name="magic_qc-technology-facial"></a>
## 🅼 magic_qc\.technology\.facial
<a name="magic_qc-technology-facial-feature_detector"></a>
## 🅼 magic_qc\.technology\.facial\.feature\_detector

人脸特征检测模块 - 技术域

本模块提供基于 OpenCV 的人脸和眼睛特征检测功能。
只负责底层检测，不包含任何业务判断逻辑。

典型用法:
    from magic_qc\.technology\.facial\.feature\_detector import FeatureDetector
    
    detector = FeatureDetector\(\)
    
    \# 检测人脸
    faces = detector\.detect\_faces\(gray\_image\)
    if len\(faces\) \> 0:
        x, y, w, h = faces\[0\]
        face\_roi = gray\_image\[y:y\+h, x:x\+w\]
        
        \# 在人脸区域内检测眼睛
        eyes = detector\.detect\_eyes\(face\_roi\)
        print\(f"检测到 \{len\(eyes\)\} 只眼睛"\)

- **Classes:**
  - 🅲 [FeatureDetector](#magic_qc-technology-facial-feature_detector-FeatureDetector)

### Classes

<a name="magic_qc-technology-facial-feature_detector-FeatureDetector"></a>
### 🅲 magic_qc\.technology\.facial\.feature\_detector\.FeatureDetector

```python
class FeatureDetector:
```

人脸特征检测器

基于 OpenCV 的 Haar Cascade 分类器进行人脸和眼睛检测。
只提供原子检测能力，不包含任何判断逻辑。

设计原则:
    - 单一职责: 只做检测，不做判断
    - 技术隔离: 上层业务不直接依赖 OpenCV
    - 可替换: 未来可替换为深度学习模型，不影响上层

**Attributes:**

- **face_cascade** (`cv2.CascadeClassifier`): 人脸检测分类器
- **eye_cascade** (`cv2.CascadeClassifier`): 眼睛检测分类器

**Functions:**

<a name="magic_qc-technology-facial-feature_detector-FeatureDetector-__init__"></a>
#### 🅵 magic_qc\.technology\.facial\.feature\_detector\.FeatureDetector\.\_\_init\_\_

```python
def __init__(self):
```

初始化特征检测器

加载 OpenCV 预训练的 Haar Cascade 模型文件。

**Raises:**

- **RuntimeError**: 如果级联分类器文件加载失败
<a name="magic_qc-technology-facial-feature_detector-FeatureDetector-detect_faces"></a>
#### 🅵 magic_qc\.technology\.facial\.feature\_detector\.FeatureDetector\.detect\_faces

```python
def detect_faces(self, gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
```

检测图像中的人脸位置

使用 Haar Cascade 方法检测图像中的所有正面人脸。

**Parameters:**

- **gray** (`np.ndarray`): 灰度图像，形状为 \(H, W\)，数据类型 uint8
建议先使用 cv2\.cvtColor\(\) 将彩色图像转换为灰度图。

**Returns:**

- `List[Tuple[int, int, int, int]]`: 人脸位置列表，每个元素为 \(x, y, w, h\)
- x \(int\): 人脸矩形左上角 x 坐标
- y \(int\): 人脸矩形左上角 y 坐标
- w \(int\): 人脸矩形宽度
- h \(int\): 人脸矩形高度

如果没有检测到人脸，返回空列表 \[\]。
<a name="magic_qc-technology-facial-feature_detector-FeatureDetector-detect_eyes"></a>
#### 🅵 magic_qc\.technology\.facial\.feature\_detector\.FeatureDetector\.detect\_eyes

```python
def detect_eyes(self, face_roi: np.ndarray) -> List[Tuple[int, int, int, int]]:
```

检测人脸区域内的眼睛位置

在人脸区域（ROI）内检测眼睛。通常在 detect\_faces\(\) 获取人脸区域后调用。

**Parameters:**

- **face_roi** (`np.ndarray`): 人脸区域的灰度图像，形状为 \(h, w\)，数据类型 uint8
通常由完整图像裁剪得到: face\_roi = gray\[y:y\+h, x:x\+w\]

**Returns:**

- `List[Tuple[int, int, int, int]]`: 眼睛位置列表，每个元素为 \(x, y, w, h\)
- x \(int\): 眼睛矩形左上角 x 坐标（相对于 face\_roi）
- y \(int\): 眼睛矩形左上角 y 坐标（相对于 face\_roi）
- w \(int\): 眼睛矩形宽度
- h \(int\): 眼睛矩形高度

如果没有检测到眼睛，返回空列表 \[\]。

注意: 坐标是相对于 face\_roi 的，如需在原始图像中定位，
需要加上人脸区域的偏移量 \(face\_x, face\_y\)。
<a name="magic_qc-technology-facial-image_processor"></a>
## 🅼 magic_qc\.technology\.facial\.image\_processor
<a name="magic_qc-technology-facial-symmetry"></a>
## 🅼 magic_qc\.technology\.facial\.symmetry

面部对称性计算模块 - 技术域

本模块提供面部对称性分析的底层计算能力。
只提供原子化的数学计算函数，不包含业务判断逻辑。

典型用法:
    from magic_qc\.technology\.facial\.symmetry import SymmetryCalculator
    
    \# 计算图像对称性
    left, right\_mirrored = SymmetryCalculator\.split\_mirror\(gray\_image\)
    symmetry\_score = SymmetryCalculator\.compute\_diff\(left, right\_mirrored\)
    
    \# 计算亮度平衡
    lr\_ratio = SymmetryCalculator\.compute\_intensity\_ratio\(left, right\_mirrored\)

- **Classes:**
  - 🅲 [SymmetryCalculator](#magic_qc-technology-facial-symmetry-SymmetryCalculator)

### Classes

<a name="magic_qc-technology-facial-symmetry-SymmetryCalculator"></a>
### 🅲 magic_qc\.technology\.facial\.symmetry\.SymmetryCalculator

```python
class SymmetryCalculator:
```

对称性计算器

提供面部对称性分析所需的原子计算能力。
所有方法均为静态方法，无状态，可随时调用。

设计原则:
    - 原子化: 每个方法只做一件事
    - 无状态: 不保存任何状态，线程安全
    - 纯计算: 不包含任何业务判断逻辑
    - 可组合: 上层可以自由组合这些原子能力

**Functions:**

<a name="magic_qc-technology-facial-symmetry-SymmetryCalculator-split_mirror"></a>
#### 🅵 magic_qc\.technology\.facial\.symmetry\.SymmetryCalculator\.split\_mirror

```python
def split_mirror(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
```

将图像分割为左右两半，并将右半部分镜像

这是对称性分析的基础步骤。将图像从中间垂直分割，
然后将右半部分水平翻转，使其与左半部分方向一致。

**Parameters:**

- **image** (`np.ndarray`): 输入图像，可以是灰度图 \(H, W\) 或彩色图 \(H, W, C\)

**Returns:**

- `Tuple[np.ndarray, np.ndarray]`: \(左半图像, 镜像后的右半图像\)
- left: 左半部分图像
- right\_mirrored: 右半部分镜像后的图像

两部分尺寸相同，宽度为原图的一半。
<a name="magic_qc-technology-facial-symmetry-SymmetryCalculator-compute_diff"></a>
#### 🅵 magic_qc\.technology\.facial\.symmetry\.SymmetryCalculator\.compute\_diff

```python
def compute_diff(img1: np.ndarray, img2: np.ndarray) -> float:
```

计算两张图像的差异度

通过计算像素差异的平均值来评估两张图像的相似程度。
数值越高表示越相似，1\.0 表示完全相同。

**Parameters:**

- **img1** (`np.ndarray`): 第一张图像
- **img2** (`np.ndarray`): 第二张图像

**Returns:**

- `float`: 相似度分数，取值范围 0-1
- 1\.0: 两图完全相同
- 0\.0: 两图完全不同
- 实际人脸左右半的典型值: 0\.70-0\.95
<a name="magic_qc-technology-facial-symmetry-SymmetryCalculator-compute_intensity_ratio"></a>
#### 🅵 magic_qc\.technology\.facial\.symmetry\.SymmetryCalculator\.compute\_intensity\_ratio

```python
def compute_intensity_ratio(img1: np.ndarray, img2: np.ndarray) -> float:
```

计算两张图像的亮度比例

评估左右半脸的亮度平衡程度。
真实人脸通常左右亮度相近，比例接近 1\.0。

**Parameters:**

- **img1** (`np.ndarray`): 第一张图像（通常为左半脸）
- **img2** (`np.ndarray`): 第二张图像（通常为右半脸）

**Returns:**

- `float`: 亮度比例，取值范围 0-1
- 1\.0: 亮度完全相同
- 0\.9-1\.0: 亮度非常平衡
- 0\.8-0\.9: 轻微亮度差异
- \<0\.8: 明显亮度差异

真实人脸的典型值: 0\.85-0\.95
<a name="magic_qc-technology-facial-symmetry-SymmetryCalculator-compute_histogram_similarity"></a>
#### 🅵 magic_qc\.technology\.facial\.symmetry\.SymmetryCalculator\.compute\_histogram\_similarity

```python
def compute_histogram_similarity(img1: np.ndarray, img2: np.ndarray) -> float:
```

计算两张图像的直方图相似度

通过比较图像的直方图分布来评估相似性。
直方图反映了图像的亮度分布特征，不受空间位置影响。

**Parameters:**

- **img1** (`np.ndarray`): 第一张图像（支持灰度或彩色）
- **img2** (`np.ndarray`): 第二张图像（支持灰度或彩色）

**Returns:**

- `float`: 直方图相似度，取值范围 -1 到 1
- 1\.0: 直方图完全相同
- 0\.0: 完全不相关
- -1\.0: 完全负相关

实际使用中，返回值会被限制在 \[0, 1\] 范围内。
真实人脸左右半的典型值: 0\.85-0\.98
<a name="magic_qc-utils"></a>
## 🅼 magic_qc\.utils

- **Functions:**
  - 🅵 [do\_something\_useful](#magic_qc-utils-do_something_useful)

### Functions

<a name="magic_qc-utils-do_something_useful"></a>
### 🅵 magic_qc\.utils\.do\_something\_useful

```python
def do_something_useful() -> None:
```
