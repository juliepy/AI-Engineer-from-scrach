"""
GPT 模型文本生成脚本
从训练好的模型检查点加载模型并生成文本
支持自定义提示词和多种采样策略（温度、Top-K、Top-P）
"""
from __future__ import annotations
import argparse
import torch
from tokenizer import ByteTokenizer
from model_gpt import GPT


def main():
    """
    主函数
    解析命令行参数，加载模型检查点，生成文本并输出
    """
    # ========== 参数解析 ==========
    p = argparse.ArgumentParser(description='从训练好的 GPT 模型生成文本')
    
    # 必需参数
    p.add_argument('--ckpt', type=str, required=True, help='模型检查点文件路径（.pt 文件）')
    
    # 生成相关参数
    # 使用 nargs='*' 来接受多个单词，然后自动拼接（便于处理带空格的提示词）
    p.add_argument('--prompt', type=str, nargs='*', default=[], help='输入提示词（prompt），多个单词用空格分隔，默认为空字符串。在 Windows cmd 中请使用双引号：--prompt "Once upon a time"')
    p.add_argument('--tokens', type=int, default=200, help='要生成的 token 数量（默认 200）')
    p.add_argument('--temperature', type=float, default=1.0, help='温度参数，控制生成的随机性（>1 更随机，<1 更确定，默认 1.0）')
    p.add_argument('--top_k', type=int, default=50, help='Top-K 采样参数，只从概率最高的 k 个 token 中采样（默认 50）')
    p.add_argument('--top_p', type=float, default=None, help='Top-P（核采样）参数，从累积概率达到 p 的 token 中采样（可选）')
    
    # 设备相关参数
    p.add_argument('--cpu', action='store_true', help='强制使用 CPU（即使有 GPU）')
    
    args = p.parse_args()

    # ========== 设备设置 ==========
    device = torch.device('cuda' if torch.cuda.is_available() and not args.cpu else 'cpu')
    print(f"使用设备: {device}")

    # ========== 初始化分词器 ==========
    tok = ByteTokenizer()
    
    # ========== 处理提示词 ==========
    # 使用 nargs='*' 时，prompt 总是列表（即使使用双引号也会是单元素列表）
    # 将列表拼接成字符串（如果列表为空则为空字符串）
    prompt_text = ' '.join(args.prompt) if args.prompt else ''
    
    # 将提示词编码为 token ID 序列，并添加批次维度
    prompt_ids = tok.encode(prompt_text).unsqueeze(0).to(device)
    
    # 如果提示词为空，使用换行符（ASCII 10）作为起始 token
    if prompt_ids.numel() == 0:
        prompt_ids = torch.tensor([[10]], dtype=torch.long, device=device)

    # ========== 加载模型检查点 ==========
    print(f"加载模型检查点: {args.ckpt}")
    ckpt = torch.load(args.ckpt, map_location=device)
    config = ckpt.get('config', None)
    print(config)
    # config = None

    # 根据检查点中是否包含配置信息来创建模型
    if config is None:
        # 如果检查点中没有配置信息，使用默认配置
        print("警告: 检查点中未找到配置信息，使用默认配置")
        model = GPT(tok.vocab_size, block_size=256).to(device)
        model.load_state_dict(ckpt['model'])
    else:
        # 使用检查点中保存的配置信息创建模型
        model = GPT(**config).to(device)
        model.load_state_dict(ckpt['model'])
    
    print("模型加载完成")

    # ========== 生成文本 ==========
    print(f"开始生成文本（提示词: '{prompt_text}', 生成 {args.tokens} 个 token）...")
    with torch.no_grad():  # 禁用梯度计算以节省内存和加速
        out = model.generate(
            prompt_ids,
            max_new_tokens=args.tokens,
            temperature=args.temperature,
            top_k=args.top_k,
            top_p=args.top_p
        )
    
    # ========== 解码并输出 ==========
    # 将生成的 token ID 序列解码为文本并打印
    generated_text = tok.decode(out[0].cpu())
    print("\n" + "=" * 60)
    print("生成的文本:")
    print("=" * 60)
    print(generated_text)
    print("=" * 60)


if __name__ == '__main__':
    main()