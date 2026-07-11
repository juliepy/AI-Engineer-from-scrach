"""
读取并显示 text_ids.pt 文件的内容
==================================

这个脚本用于读取 PyTorch 保存的 text_ids.pt 文件，并显示其内容。
可以显示：
1. 张量的基本信息（形状、数据类型等）
2. Token IDs 的数值
3. 如果提供了 tokenizer，还可以解码为文本
"""

import torch
from pathlib import Path
import sys

def read_text_ids(pt_file: str, tokenizer_path: str = None, max_display: int = 50):
    """
    读取 text_ids.pt 文件并显示内容
    
    Args:
        pt_file: text_ids.pt 文件路径
        tokenizer_path: tokenizer 目录路径（可选），如果提供则可以解码为文本
        max_display: 最多显示的 token 数量
    """
    pt_path = Path(pt_file)
    
    if not pt_path.exists():
        print(f"错误: 文件不存在: {pt_file}")
        return
    
    print("=" * 60)
    print("读取 text_ids.pt 文件")
    print("=" * 60)
    
    # 加载张量
    print(f"\n1. 加载文件: {pt_file}")
    try:
        ids = torch.load(pt_file, map_location='cpu')
        print("   ✓ 文件加载成功")
    except Exception as e:
        print(f"   ✗ 加载失败: {e}")
        return
    
    # 显示张量基本信息
    print(f"\n2. 张量基本信息:")
    print(f"   类型: {type(ids)}")
    if isinstance(ids, torch.Tensor):
        print(f"   形状: {ids.shape}")
        print(f"   数据类型: {ids.dtype}")
        print(f"   设备: {ids.device}")
        print(f"   总元素数: {ids.numel()}")
        print(f"   最小值: {ids.min().item()}")
        print(f"   最大值: {ids.max().item()}")
        print(f"   平均值: {ids.float().mean().item():.2f}")
    
    # 转换为列表以便显示
    if isinstance(ids, torch.Tensor):
        ids_list = ids.tolist()
    else:
        ids_list = list(ids) if hasattr(ids, '__iter__') else [ids]
    
    # 显示前几个 token IDs
    print(f"\n3. Token IDs (前 {min(max_display, len(ids_list))} 个):")
    display_count = min(max_display, len(ids_list))
    print(f"   {ids_list[:display_count]}")
    
    if len(ids_list) > max_display:
        print(f"   ... (总共 {len(ids_list)} 个 tokens)")
    
    # 尝试使用 tokenizer 解码
    if tokenizer_path:
        tokenizer_dir = Path(tokenizer_path)
        if tokenizer_dir.exists() and (tokenizer_dir / "tokenizer.json").exists():
            print(f"\n4. 使用 tokenizer 解码 (tokenizer: {tokenizer_path})")
            try:
                # 动态导入 tokenizer
                sys.path.insert(0, str(Path(__file__).parent))
                from tokenizer_bpe import BPETokenizer
                
                tokenizer = BPETokenizer()
                tokenizer.load(tokenizer_dir)
                print("   ✓ Tokenizer 加载成功")
                
                # 解码前几个 tokens
                sample_ids = ids_list[:max_display]
                decoded_text = tokenizer.decode(sample_ids)
                print(f"\n   前 {len(sample_ids)} 个 tokens 解码为文本:")
                print(f"   {repr(decoded_text)}")
                
                # 如果文本较长，也显示原始文本
                if len(decoded_text) < 200:
                    print(f"\n   文本内容:")
                    print(f"   {decoded_text}")
                
            except Exception as e:
                print(f"   ✗ Tokenizer 加载或解码失败: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"\n4. Tokenizer 路径不存在或无效: {tokenizer_path}")
    else:
        print(f"\n4. 未提供 tokenizer 路径，跳过文本解码")
        print("   提示: 可以使用 --tokenizer 参数指定 tokenizer 目录路径")
    
    # 保存为可读格式（可选）
    print(f"\n5. 保存为文本格式...")
    output_txt = pt_path.parent / "text_ids.txt"
    try:
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write(f"# Token IDs from {pt_file}\n")
            f.write(f"# Total tokens: {len(ids_list)}\n")
            f.write(f"# Shape: {ids.shape if isinstance(ids, torch.Tensor) else 'N/A'}\n")
            f.write(f"# Data type: {ids.dtype if isinstance(ids, torch.Tensor) else type(ids)}\n")
            f.write(f"\n# Token IDs (one per line):\n")
            for i, token_id in enumerate(ids_list):
                f.write(f"{token_id}\n")
        print(f"   ✓ 已保存为文本格式: {output_txt}")
    except Exception as e:
        print(f"   ✗ 保存失败: {e}")
    
    print("\n" + "=" * 60)
    print("读取完成")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="读取并显示 text_ids.pt 文件的内容")
    parser.add_argument("pt_file", type=str, nargs="?", 
                       default="tmp/text_ids.pt",
                       help="text_ids.pt 文件路径 (默认: tmp/text_ids.pt)")
    parser.add_argument("--tokenizer", "-t", type=str, default=None,
                       help="tokenizer 目录路径（可选），用于解码 token IDs 为文本")
    parser.add_argument("--max-display", "-m", type=int, default=50,
                       help="最多显示的 token 数量 (默认: 50)")
    
    args = parser.parse_args()
    
    # 如果没有提供 tokenizer，尝试自动查找
    if args.tokenizer is None:
        pt_path = Path(args.pt_file)
        # 尝试在同目录下查找 test_tokenizer
        possible_tokenizer = pt_path.parent / "test_tokenizer"
        if possible_tokenizer.exists() and (possible_tokenizer / "tokenizer.json").exists():
            args.tokenizer = str(possible_tokenizer)
            print(f"自动检测到 tokenizer: {args.tokenizer}")
    
    read_text_ids(args.pt_file, args.tokenizer, args.max_display)


