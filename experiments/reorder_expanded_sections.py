"""Restore logical section order after inserting editable thesis expansions."""

from docx import Document


DOCX = "documents/pcb_thesis_deeppcb_revised.docx"


def paragraph_map(doc):
    return {p.text: p for p in doc.paragraphs}


def move_after(paragraphs, block_texts, target_text):
    by_text = paragraph_map(paragraphs)
    block = [by_text[text]._p for text in block_texts]
    target = by_text[target_text]._p
    for element in block:
        element.getparent().remove(element)
    cursor = target
    for element in block:
        cursor.addnext(element)
        cursor = element


def main():
    doc = Document(DOCX)
    # Put the general 1.1 background before the two newly added subsections.
    move_after(
        doc,
        [
            "1.1.1 PCB 表面检测的生产流程",
            "典型的 PCB 表面检测流程包括板面清洁、光学成像、图像校正、缺陷定位、人工复核和结果追溯。相机采集的图像需要先完成畸变校正和亮度归一化，使同一线路在不同位置具有相近的外观。检测模型输出的类别、位置和置信度随后被写入质量记录，并与板号、批次号和工位号关联。由此可见，模型的评价不能只看单一精度数字，还要关注推理延迟、输出稳定性、误报后的复核工作量以及结果能否被保存和复查。",
            "1.1.2 研究问题的界定",
            "本文解决的是已裁剪、已标注的 PCB 图像中的目标检测问题，输入为 DeepPCB 的待检图，输出为六类缺陷的矩形框和类别。研究不把模板差分、缺陷分割、真实产线相机标定和自动剔除机构混入主要结论。模板图可以作为后续扩展输入，但一旦使用模板信息，就必须建立同样使用模板的基线。通过限定问题边界，可以使结构改进带来的变化与输入信息变化区分开。",
        ],
        "传统模板比对需要稳定配准，复杂光照、成像噪声和板面差异会影响阈值设定；学习式目标检测能够从标注数据中提取缺陷特征，但小目标容易在下采样中丢失。DeepPCB 提供成对、已配准的图像与六类缺陷标注，为结构改进和受控比较提供了可用基础[1]。其样本含人工增补的缺陷，数据集结果与真实生产场景之间仍需额外验证。",
    )
    # Keep the numbered 1.2 subsections in numerical order.
    move_after(
        doc,
        [
            "1.2.4 不同检测路线的比较",
            "模板比对方法利用正常模板和待测板之间的差异，具有直观、易解释的优点，但对配准误差、光照变化和线路位置偏移较为敏感。传统图像处理方法可以通过边缘、阈值和形态学运算定位规则异常，参数设置通常需要针对板型调整。两阶段检测器先产生候选区域再分类，定位能力较强但推理链路较长。一阶段检测器把候选生成和分类回归放在同一网络中，便于在边缘设备上保持较低延迟。本文选择 YOLO11 作为统一基线，重点讨论它在小缺陷场景下的尺度表达问题。",
            "不同研究使用的数据集、类别定义和 IoU 阈值差异很大。例如，同样称为针孔或漏孔的类别，可能对应不同的标注规则；同样的 mAP 数字也可能来自 0.5 或 0.5:0.95 的不同阈值范围。因此，本文不把其他项目 README 中的指标直接当作对照结果，而是只借鉴其数据转换和工程实现思路。所有能写入论文结论的数字都来自本研究固定清单和保存的评估日志。",
        ],
        "DeepPCB 的待检图和模板图为已配准图像对，标注覆盖断路、短路、鼠咬、毛刺、杂铜及针孔[1]。部分既有 PCB 研究使用的类别集合、图像大小和评价协议不同，直接横向比较其报告数值并不可靠。YOLO11 的官方实现以 C3k2、C2PSA 等模块构成主干与颈部，原始检测输出主要为 P3、P4、P5 三个尺度[10]。本研究拟在固定版本和数据协议下检验 P2 与高分辨率融合的独立贡献，并记录精度与延迟之间的取舍。",
    )
    doc.save(DOCX)


if __name__ == "__main__":
    main()
