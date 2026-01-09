# GMC 项目使用说明（基于 main.py 一键生成 3D 可视化）

本项目提供“一行命令生成交互式 3D 曲面图”的脚本 main.py。它整合了采样、权重计算（支持有/无 STD）、相关系数计算（PLCC/SRCC/KRCC）与曲面拟合，并输出可交互的 HTML 图。

## 目录结构与关键模块
- 数据采样: [sampling.py](file:///d:/AppGallery/python代码/GMC/sampling.py)
- 权重（无 STD，LDS 平滑；有 STD，高斯平滑）: [dataset_balance.py](file:///d:/AppGallery/python代码/GMC/dataset_balance.py)
- 相关系数计算: [GMC.py](file:///d:/AppGallery/python代码/GMC/GMC.py)
- 曲面拟合与绘图: [multi_surface.py](file:///d:/AppGallery/python代码/GMC/multi_surface.py)
- STD 估计（无 STD 自动估计）: [std_deviation.py](file:///d:/AppGallery/python代码/GMC/std_deviation.py)
- 主脚本（命令行入口）: [main.py](file:///d:/AppGallery/python代码/GMC/main.py)

## 环境依赖
- Python 3.8+
- 必需依赖: numpy, pandas, scipy, statsmodels, plotly
- 读取 XLSX 需: openpyxl

安装示例:
```bash
pip install numpy pandas scipy statsmodels plotly openpyxl
```

## 输入数据格式
- 支持 CSV 或 XLSX 文件
- 至少包含 MOS 列（默认列名 mos；也可指定 Ground Truth Labels）
- 预测结果列（一个或多个），例如 Results Scores for CC 或自定义名称
- STD 数据（可选）：可在同一表内作为列 std，或通过文本文件提供（每行一个数）

最小 CSV 示例（无 STD）:
```csv
mos,pred_a,pred_b
1.2,0.35,0.42
2.1,0.55,0.60
...
```

带 STD 的 CSV 示例:
```csv
mos,std,pred
1.2,0.08,0.35
2.1,0.10,0.55
...
```

STD 文本文件示例（每行一个值）:
```
0.0831
0.0975
...
```

## 快速开始
最简用法（自动检测列，未提供 STD 时将自动估计 STD）:
```bash
python main.py --pred-file ./data/SPAQ/qualiclip.csv
```

指定预测列与 MOS 列:
```bash
python main.py --pred-file ./data/SPAQ/qualiclip.csv \
  --pred-cols "Results Scores for CC" \
  --mos-col "Ground Truth Labels"
```

提供 STD 文件:
```bash
python main.py --pred-file ./data/SPAQ/qualiclip.csv \
  --std-file ./results/SPAQ/mos_std.txt
```

提供 STD 列:
```bash
python main.py --pred-file ./data/LIVE.csv --std-col std
```

指定采样数与输出:
```bash
python main.py --pred-file ./data/SPAQ/qualiclip.csv \
  --samples 200 --output results/3d/spaq_srcc.html
```

## 命令行参数详解
- --pred-file 路径：输入数据（CSV/XLSX），必填
- --pred-cols 文本：预测列名，逗号分隔；不填则自动检测数值列（排除 MOS/STD）
- --mos-col 文本：MOS 列名，默认 mos（兼容 Ground Truth Labels）
- --std-col 文本：STD 列名（可选）
- --std-file 路径：STD 文本文件（每行一个数，可选）
- --weights-file 路径：权重文件（每行一个数，优先使用；否则自动计算）
- --samples 数值：拉丁超立方采样点数量，默认 100
- --method 文本：相关系数类型 PLCC/SRCC/KRCC，默认 SRCC
- --std-scale 数值：传入相关系数计算中的 std 缩放倍数，默认 1.0
- --weight-plus 数值：权重缩放倍数，默认 10.0
- --ks 数值：LDS 核窗口大小，默认 5
- --sigma 数值：LDS 高斯核 sigma，默认 2.0
- --bw-method 文本：核回归带宽选择，默认 cv_ls
- --grid-res 数值：曲面网格分辨率，默认 100
- --output 路径：输出 HTML 路径，默认 results/3d/plot.html

## 处理流程
1. 读取数据表（CSV/XLSX）并自动识别 MOS/STD/预测列 [main.py](file:///d:/AppGallery/python代码/GMC/main.py#L99-L107)
2. STD 处理:
   - 若提供 --std-file：读取文本为 STD
   - 若提供 --std-col：使用表内 STD 列
   - 否则：自动调用 [estimate_std_from_mos](file:///d:/AppGallery/python代码/GMC/std_deviation.py#L7-L24) 估计 STD
3. 权重计算:
   - 若提供 --weights-file：直接读取
   - 否则：若 STD 有效，使用高斯平滑权重 [cal_mos_weights_gaussian](file:///d:/AppGallery/python代码/GMC/高斯分布平滑.py#L13-L33)
   - 无 STD 情况：使用 LDS 平滑权重 [cal_mos_weights](file:///d:/AppGallery/python代码/GMC/dataset_balance.py#L13-L35)
4. 采样生成 (Q, Qd):
   - 拉丁超立方采样 [LHS](file:///d:/AppGallery/python代码/GMC/sampling.py#L4-L26)
5. 相关系数计算:
   - 对每个预测列，遍历采样点调用 [GCC](file:///d:/AppGallery/python代码/GMC/GMC.py#L5-L96) 计算对应方法的分值 [main.py](file:///d:/AppGallery/python代码/GMC/main.py#L55-L66)
6. 曲面拟合与输出:
   - 使用核回归拟合 3D 曲面并生成交互式 HTML [multi_surface.py](file:///d:/AppGallery/python代码/GMC/multi_surface.py#L7-L47) 与 [main.py](file:///d:/AppGallery/python代码/GMC/main.py#L69-L78)

## 输出结果
- 交互式 3D HTML 图（可在浏览器中旋转/缩放/查看图例）
- 控制台输出每个预测列的平均高度（评估指标均值），例如:
```
qualiclip SRCC avg_height = 0.4231
Saved: results/3d/plot.html
```

## 常见问题与排查
- 列名不匹配
  - 使用 --mos-col/--pred-cols/--std-col 指定准确列名
- STD 缺失
  - 不提供 STD 时会自动估计；若需外部 STD，使用 --std-file
- XLSX 读取失败
  - 安装 openpyxl 或改用 CSV
- 权重来源
  - 优先使用 --weights-file；否则自动按 STD 情况选择高斯/频次平滑
- Windows 路径
  - 建议使用双引号包裹路径，避免反斜杠转义问题

## 进阶用法
- 调整 STD 估计强度
  - 修改 [estimate_std_from_mos](file:///d:/AppGallery/python代码/GMC/std_deviation.py#L7-L24) 的 phi 参数（数值越大 std 越小）
- 自定义核回归带宽
  - 使用 --bw-method 选择带宽方法（如 cv_ls、aic）
- 修改可视化配色/布局
  - 参考 [plot_surfaces](file:///d:/AppGallery/python代码/GMC/main.py#L69-L78) 与 [multi_surface.py](file:///d:/AppGallery/python代码/GMC/multi_surface.py#L49-L178)

## 重要提示
- 请确保相关函数导入与调用一致：
  - 相关系数函数为 GCC，导入应为 `from GMC import GCC`，调用 `GCC(...)`
  - 高斯权重函数位于 高斯分布平滑.py，导入应为 `from 高斯分布平滑 import cal_mos_weights_gaussian`
  - 若导入不一致，运行将报错；可参考此说明修正

## 许可证
- 本项目文件仅用于研究与教学用途；如需商用请自行评估风险与责任。