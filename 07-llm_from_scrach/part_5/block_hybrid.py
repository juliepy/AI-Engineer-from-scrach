"""
混合前馈网络（Hybrid Feed-Forward Network）实现。

本模块实现了将密集前馈网络（Dense FFN）与专家混合（MoE）输出混合的混合架构。
通过可调节的混合系数 α，可以在稳定性（密集网络）和容量（MoE）之间进行权衡。
"""
from __future__ import annotations
import torch.nn as nn
from moe import MoE

class HybridFFN(nn.Module):
    """
    混合前馈网络（Hybrid Feed-Forward Network）。
    
    该网络将密集前馈网络（Dense FFN）和专家混合（MoE）的输出进行混合：
    y = α * Dense(x) + (1-α) * MoE(x)
    
    使用混合系数 α ∈ [0,1] 来在稳定性和容量之间进行权衡：
    - α 接近 1：更依赖密集网络，更稳定但容量有限
    - α 接近 0：更依赖 MoE，容量更大但可能不够稳定
    - α = 0.5：平衡两种架构的优势
    
    Args:
        dim: 输入和输出的特征维度
        alpha: 混合系数，控制密集网络和 MoE 的权重，范围 [0,1]，默认为 0.5
        mult: 隐藏层维度相对于输入维度的倍数，默认为 4
        swiglu: 是否在 MoE 中使用 SwiGLU 激活函数，默认为 True
        n_expert: MoE 中的专家数量，默认为 4
        k: 每个 token 路由到的专家数量，默认为 1（Switch Transformer 风格）
        dropout: Dropout 概率，默认为 0.0（不使用 dropout）
    """
    def __init__(self, dim: int, alpha: float = 0.5, mult: int = 4, swiglu: bool = True, n_expert: int = 4, k: int = 1, dropout: float = 0.0):
        """
        初始化混合前馈网络。
        
        Args:
            dim: 输入和输出的特征维度
            alpha: 混合系数，控制密集网络和 MoE 的权重，范围 [0,1]，默认为 0.5
            mult: 隐藏层维度相对于输入维度的倍数，默认为 4
            swiglu: 是否在 MoE 中使用 SwiGLU 激活函数，默认为 True
            n_expert: MoE 中的专家数量，默认为 4
            k: 每个 token 路由到的专家数量，默认为 1
            dropout: Dropout 概率，默认为 0.0
        """
        super().__init__()
        self.alpha = alpha  # 混合系数，用于平衡密集网络和 MoE 的输出
        inner = mult * dim  # 计算隐藏层维度
        
        # 构建密集前馈网络：Linear -> GELU -> Linear -> Dropout
        self.dense = nn.Sequential(
            nn.Linear(dim, inner),      # 第一个线性层：dim -> inner
            nn.GELU(),                  # GELU 激活函数
            nn.Linear(inner, dim),      # 第二个线性层：inner -> dim
            nn.Dropout(dropout)         # Dropout 层（如果 dropout > 0）
        )
        
        # 构建专家混合（MoE）网络
        self.moe = MoE(dim, n_expert=n_expert, k=k, mult=mult, swiglu=swiglu, dropout=dropout)
    
    def forward(self, x):
        """
        前向传播函数。
        
        处理流程：
        1. 通过密集前馈网络处理输入
        2. 通过 MoE 网络处理输入（同时获取辅助损失）
        3. 将两个输出按混合系数 α 进行加权求和
        
        Args:
            x: 输入张量，形状为 (B, T, C)
               B = batch size（批次大小）
               T = sequence length（序列长度）
               C = feature dimension（特征维度）
        
        Returns:
            y: 混合后的输出张量，形状为 (B, T, C)，与输入形状相同
            aux: 辅助损失（负载均衡损失），来自 MoE 层，用于鼓励专家被均匀使用
        """
        # 通过密集前馈网络处理输入
        y_dense = self.dense(x)
        
        # 通过 MoE 网络处理输入，同时获取辅助损失
        y_moe, aux = self.moe(x)
        
        # 将密集网络和 MoE 的输出按混合系数进行加权求和
        # y = α * y_dense + (1-α) * y_moe
        y = self.alpha * y_dense + (1.0 - self.alpha) * y_moe
        
        return y, aux