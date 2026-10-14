# DeepPCB YOLO11 训练与测试代码

这个目录包含 DeepPCB 数据准备、YOLO11n 基线训练、P2 小目标检测分支训练和官方测试集评估代码。`train_deeppcb.py` 在训练结束后会自动加载最佳权重，在官方 `test` 划分上测试，并保存 `test_metrics.json`。

## 1. 安装环境

建议使用 Python 3.10–3.12 的虚拟环境。CPU 或 NVIDIA GPU 都可以运行；GPU 运行时请按照本机 CUDA 版本安装 PyTorch。

```bash
pip install -r requirements-deeppcb.txt
```

## 2. 准备 DeepPCB

先下载官方仓库，并确认 `PCBData` 下有 `trainval.txt`、`test.txt` 及对应图片和标注：

```bash
git clone https://github.com/tangsanli5201/DeepPCB.git
```

把官方 1000 组 `trainval` 按固定种子划分为 800 组训练和 200 组验证，同时把 500 组官方测试集转换为 YOLO 格式：

```bash
python prepare_deeppcb.py \
  --source /path/to/DeepPCB/PCBData \
  --out /path/to/DeepPCB_yolo \
  --seed 2026 \
  --val-count 200
```

脚本会把官方类别编号转换为 YOLO 的 0–5 编号，并保留官方测试清单。默认使用符号链接，Linux/macOS 需要确保输出目录和原始数据目录同时保留；若在 Windows 上运行，请先把脚本中的 `symlink_to` 改为文件复制，或在管理员权限下启用开发者模式。

## 3. 训练并测试 YOLO11n 基线

`--device cpu` 是默认值。NVIDIA GPU 可写成 `--device 0`；多卡可按 Ultralytics 格式填写。

```bash
python train_deeppcb.py \
  --data /path/to/DeepPCB_yolo \
  --model baseline \
  --epochs 10 \
  --imgsz 320 \
  --batch 16 \
  --workers 2 \
  --seed 2026 \
  --device cpu \
  --project runs/deeppcb
```

结果会写入 `runs/deeppcb/baseline_e10_s2026/`，包括最佳权重、训练曲线和 `test_metrics.json`。

## 4. 训练并测试 P2 版本

P2 配置在 `yolo11n-p2.yaml`。它在 YOLO11n 的 P3/P4/P5 之外增加步长为 4 的高分辨率检测分支：

```bash
python train_deeppcb.py \
  --data /path/to/DeepPCB_yolo \
  --model p2 \
  --epochs 10 \
  --imgsz 320 \
  --batch 16 \
  --workers 2 \
  --seed 2026 \
  --device cpu \
  --project runs/deeppcb
```

P2 模型会加载 `yolo11n.pt` 中能够匹配的权重，新增加的检测路径随机初始化。两个配置必须使用相同的数据划分、训练轮次、输入尺寸和随机种子，才适合做消融比较。

## 5. 当前预备实测

`RESULTS.md` 记录了本次 10 epoch、320 输入、CPU 的可复核结果。基线 mAP@0.5 为 25.5285%，P2 为 20.4037%；这是用于核对训练和测试链路的预备实验，不代表充分收敛的最终论文结果。正式实验应增加训练轮次、输入尺寸和随机种子。

`update_thesis_results.py` 是把已经确认的结果写入论文表格的辅助脚本；运行前请备份 Word 文件，并确认结果来自同一数据协议。
