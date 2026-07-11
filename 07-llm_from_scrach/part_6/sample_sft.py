"""
SFT模型文本生成脚本

该脚本用于加载训练好的监督微调（SFT）模型，并根据给定的提示（prompt）生成文本回复。
主要功能包括：
- 加载训练好的模型检查点
- 格式化提示文本
- 使用模型生成文本
- 解码并输出生成的文本
"""
from __future__ import annotations
import argparse, torch

# 复用 Part 3 中的 GPTModern 模型
import sys
from pathlib import Path as _P
# 将 part_3 目录添加到系统路径，以便导入模型
sys.path.append(str(_P(__file__).resolve().parents[1]/'part_3'))
from model_modern import GPTModern  # noqa: E402

# 导入SFT相关的数据批处理和格式化模块
from collator_sft import SFTCollator  # SFT数据批处理器（用于编码/解码）
from formatters import format_prompt_only  # 格式化提示文本


def main():
    """
    主生成函数
    
    执行文本生成流程：
    1. 解析命令行参数
    2. 加载模型检查点
    3. 格式化并编码提示文本
    4. 使用模型生成文本
    5. 解码并输出生成的文本
    """
    # ========== 解析命令行参数 ==========
    p = argparse.ArgumentParser()
    p.add_argument('--ckpt', type=str, required=True, help='模型检查点路径（必需）')
    p.add_argument('--prompt', type=str, required=True, help='输入提示文本（必需）')
    p.add_argument('--block_size', type=int, default=256, help='序列最大长度（上下文窗口）')
    p.add_argument('--n_layer', type=int, default=4, help='Transformer层数')
    p.add_argument('--n_head', type=int, default=4, help='注意力头数')
    p.add_argument('--n_embd', type=int, default=256, help='嵌入维度')
    p.add_argument('--tokens', type=int, default=80, help='生成的最大新token数量')
    p.add_argument('--temperature', type=float, default=0.2, help='采样温度（控制随机性，越低越确定）')
    p.add_argument('--cpu', action='store_true', help='强制使用CPU（即使有GPU）')
    p.add_argument('--bpe_dir', type=str, default='../part_4/runs/part4-demo/tokenizer',
                   help='BPE分词器目录路径')
    args = p.parse_args()

    # 确定运行设备（优先使用GPU）
    device = torch.device('cuda' if torch.cuda.is_available() and not args.cpu else 'cpu')

    # ========== 加载模型检查点 ==========
    ckpt = torch.load(args.ckpt, map_location=device)
    cfg = ckpt.get('config', {})

    # ========== 初始化数据批处理器和模型 ==========
    # 使用检查点中的block_size（如果存在），否则使用默认值
    col = SFTCollator(block_size=cfg.get('block_size', 256), bpe_dir=args.bpe_dir)
    # 创建GPT模型，使用现代架构特性（RMSNorm, SwiGLU, RoPE）
    model = GPTModern(vocab_size=col.vocab_size, block_size=args.block_size,
                      n_layer=args.n_layer, n_head=args.n_head, n_embd=args.n_embd,
                      use_rmsnorm=True, use_swiglu=True, rope=True).to(device)
    # 加载训练好的模型权重
    model.load_state_dict(ckpt['model'])
    model.eval()  # 设置为评估模式（禁用dropout等）

    # ========== 格式化并编码提示文本 ==========
    # 格式化提示文本（添加必要的格式标记）
    prompt_text = format_prompt_only(args.prompt).replace('</s>','')  # 移除结束标记
    # 将文本编码为token ID序列
    ids = col.encode(prompt_text)
    # 转换为张量并移动到指定设备
    idx = torch.tensor([ids], dtype=torch.long, device=device)

    # ========== 生成文本 ==========
    with torch.no_grad():  # 禁用梯度计算以节省内存和加速
        # 使用模型生成文本
        # top_k=3 表示只从概率最高的3个token中选择（nucleus sampling的简化版本）
        out = model.generate(idx, max_new_tokens=args.tokens, 
                             temperature=args.temperature, top_k=3)

    # ========== 解码并输出生成的文本 ==========
    # 将生成的token ID转换为列表
    out_ids = out[0].tolist()
    orig_len = idx.size(1)  # 原始提示的长度
    
    # 解码：优先使用BPE分词器（如果可用），否则回退到字节解码
    if hasattr(col, "tok") and hasattr(col.tok, "decode"):
        # 使用BPE分词器解码完整文本（包括提示和生成部分）
        # 解码完整文本或仅生成的后缀；后缀通常更清晰
        generated = col.tok.decode(out_ids)
        print(generated)
    else:
        # 回退到字节解码：只解码生成的部分（跳过原始提示）
        generated = bytes(out_ids[orig_len:]).decode("utf-8", errors="ignore")
        print(generated)


if __name__ == '__main__':
    main()