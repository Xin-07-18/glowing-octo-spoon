# DeepPCB YOLO11 实测记录

本目录的脚本使用官方 DeepPCB 仓库的 `PCBData/trainval.txt`（1000 组）和 `PCBData/test.txt`（500 组）。`prepare_deeppcb.py` 以随机种子 2026 把 trainval 划为 800 组训练和 200 组验证，再将标注转换为六类 YOLO 格式；官方 500 组测试集保持独立。

本次运行环境为 CPU（AMD EPYC 9V74，5 个可用执行线程）、Python 3.12、PyTorch 2.14.1+cpu、Ultralytics 8.4.177，输入 320×320，batch 16，随机种子 2026。每个模型训练 10 epoch；基线使用官方 `yolo11n.pt`，P2 使用本目录的 `yolo11n-p2.yaml` 并转移可匹配的基线参数。P2 是实验性结构适配，不是 Ultralytics 官方 YOLO11-P2 配置。

| 模型 | mAP@0.5 | mAP@0.5:0.95 | Precision | Recall | 参数量 | GFLOPs | 预处理+推理+后处理（ms/图） |
|---|---:|---:|---:|---:|---:|---:|---:|
| YOLO11n 基线 | 25.5285% | 11.5029% | 23.7361% | 36.5759% | 2.58M | 6.4 | 17.5 |
| YOLO11n-P2 | 20.4037% | 9.5723% | 20.7381% | 36.5162% | 2.66M | 10.3 | 25.7 |

按六类 AP@0.5（open、short、mousebite、spur、copper、pin-hole）分别为：

- YOLO11n：16.3068%、9.4052%、13.3152%、9.4095%、70.6151%、34.1191%。
- YOLO11n-P2：16.1784%、6.6183%、15.2723%、8.5665%、36.4477%、39.3392%。

这是一次用于验证训练和测试链路的预备实测，不是充分收敛的最终论文实验：训练轮次只有 10、输入缩放为 320，且每个配置只有一个随机种子。Ultralytics 的单次测速显示基线约 17.5 ms/图、P2 约 25.7 ms/图；CPU 运行会有波动。P2 在该配置下 mAP@0.5 比基线低 5.1248 个百分点，因此当前结果不能支持“P2 提升性能”的结论。正式论文应使用更长训练、至少三个随机种子和 640 输入重新测定。

结果文件位于 `runs/deeppcb/baseline_e10_s2026/test_metrics.json` 和 `runs/deeppcb/p2_e10_s2026/test_metrics.json`。
