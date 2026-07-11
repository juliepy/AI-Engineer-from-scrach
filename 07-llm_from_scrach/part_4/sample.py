"""
文本生成脚本

从保存的检查点加载模型并生成文本。支持：
- 从检查点加载模型配置和权重
- 自动加载关联的分词器（如果存在）
- 兼容旧版检查点（无配置时自动推断）
- 支持 CPU 和 GPU 运行
"""
from __future__ import annotations
import argparse, torch
from pathlib import Path

# 加载 Part 3 的模型定义
import sys
from pathlib import Path as _P
sys.path.append(str(_P(__file__).resolve().parents[1]/'part_3'))
from model_modern import GPTModern  # noqa: E402

from tokenizer_bpe import BPETokenizer


def main():
    """
    主函数：从检查点加载模型并生成文本
    
    流程：
    1. 解析命令行参数
    2. 加载检查点文件
    3. 加载分词器（如果存在）
    4. 构建或推断模型配置
    5. 构建并加载模型
    6. 编码提示词并生成文本
    7. 解码并输出生成的文本
    """
    # 解析命令行参数
    p = argparse.ArgumentParser(description='从检查点加载模型并生成文本')
    p.add_argument('--ckpt', type=str, required=True, help='检查点文件路径')
    p.add_argument('--prompt', type=str, default='', help='输入提示词（默认为空）')
    p.add_argument('--tokens', type=int, default=100, help='要生成的最大 token 数（默认 100）')
    p.add_argument('--cpu', action='store_true', help='强制使用 CPU（即使有 GPU 可用）')
    args = p.parse_args()

    # 确定运行设备（优先使用 GPU，除非指定 --cpu）
    device = torch.device('cuda' if torch.cuda.is_available() and not args.cpu else 'cpu')

    # 加载检查点（先在 CPU 上加载，稍后再移动到目标设备）
    ckpt = torch.load(args.ckpt, map_location='cpu')
    sd = ckpt['model']  # 模型状态字典
    cfg = ckpt.get('config') or {}  # 模型配置（如果存在）

    # 加载分词器（如果存在）
    # 检查点目录中可能包含 tokenizer_dir.txt 文件，其中保存了分词器目录路径
    tok = None
    tok_dir_file = Path(args.ckpt).with_name('tokenizer_dir.txt')
    if tok_dir_file.exists():
        tok_dir = tok_dir_file.read_text().strip()  # 文件包含分词器目录路径
        tok = BPETokenizer()
        tok.load(tok_dir)  # 实例方法，传入目录路径
        vocab_from_tok = tok.vocab_size  # 从分词器获取词汇表大小
    else:
        vocab_from_tok = None  # 没有分词器时使用字节级编码


    # ---- 构建配置（优先使用保存的配置；否则从权重推断） ----
    if not cfg:
        # 旧版检查点没有配置：从权重推断基本参数
        # tok_emb.weight 的形状为 [V, C]，其中 V 是词汇表大小，C 是嵌入维度（n_embd）
        V, C = sd['tok_emb.weight'].shape
        
        # pos_emb.weight 的形状为 [block_size, C]（如果存在位置编码）
        # 如果不存在位置编码，默认使用 256
        block_size = sd['pos_emb.weight'].shape[0] if 'pos_emb.weight' in sd else 256
        
        # 统计 Transformer 块的数量
        # 通过匹配状态字典中的键名 "blocks.{数字}." 来找出所有层
        import re
        layer_ids = {int(m.group(1)) for k in sd.keys() if (m := re.match(r"blocks\.(\d+)\.", k))}
        n_layer = max(layer_ids) + 1 if layer_ids else 1
        
        # 选择一个能整除 C 的 n_head（头数不影响权重形状，所以需要推断）
        # 优先尝试 8、4、2，最后是 1
        n_head = 8 if C % 8 == 0 else 4 if C % 4 == 0 else 2 if C % 2 == 0 else 1
        
        # 构建配置字典（使用合理的默认值）
        cfg = dict(
            vocab_size=vocab_from_tok or V,  # 优先使用分词器的词汇表大小
            block_size=block_size,
            n_layer=n_layer,
            n_head=n_head,
            n_embd=C,
            dropout=0.0,
            use_rmsnorm=True,  # 假设使用 RMSNorm
            use_swiglu=True,   # 假设使用 SwiGLU
            rope=True,        # 假设使用 RoPE 位置编码
            max_pos=4096,      # 最大位置
            sliding_window=None,  # 滑动窗口注意力
            attention_sink=0,     # 注意力 sink
        )

    # ---- 构建并加载模型 ----
    model = GPTModern(**cfg).to(device).eval()  # 创建模型并移动到目标设备，设置为评估模式
    model.load_state_dict(ckpt['model'])  # 加载保存的模型权重
    model.to(device).eval()  # 确保模型在正确的设备上且处于评估模式

    # 将提示词编码为 token ID
    if tok:
        # 使用 BPE 分词器编码
        ids = tok.encode(args.prompt)
        if len(ids) == 0: 
            ids = [10]  # 如果编码结果为空，使用换行符（ASCII 10）
    else:
        # 没有分词器时，使用字节级编码
        # 空提示词使用换行符，否则将 UTF-8 编码的字节转换为列表
        ids = [10] if args.prompt == '' else list(args.prompt.encode('utf-8'))
    
    # 将 ID 列表转换为张量，添加批次维度
    idx = torch.tensor([ids], dtype=torch.long, device=device)

    # 生成文本（禁用梯度计算以节省内存和加速）
    with torch.no_grad():
        out = model.generate(idx, max_new_tokens=args.tokens)
    
    # 将生成的 token ID 转换为列表
    out_ids = out[0].tolist()
    
    # 解码并输出生成的文本
    if tok:
        # 使用 BPE 分词器解码
        print(tok.decode(out_ids))
    else:
        # 使用字节级解码（忽略解码错误）
        print(bytes(out_ids).decode('utf-8', errors='ignore'))

if __name__ == '__main__':
    # 脚本入口：直接运行此文件时执行主函数
    main()