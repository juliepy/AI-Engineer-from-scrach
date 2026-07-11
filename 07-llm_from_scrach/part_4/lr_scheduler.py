"""
学习率调度器模块
===============

本模块实现了带线性预热（warmup）和余弦衰减（cosine decay）的学习率调度策略。
这种策略在训练大型语言模型（如 GPT、BERT）时非常常用。

学习率调度策略：
1. 线性预热阶段：从 0 线性增长到 base_lr，帮助模型稳定训练
2. 余弦衰减阶段：从 base_lr 按余弦函数平滑衰减到接近 0

优势：
- Warmup 可以避免训练初期，让模型更稳定地开始训练
- Cosine decay 提供平滑的学习率衰减，有助于模型收敛到更好的局部最优
"""

import math

class WarmupCosineLR:
    """带线性预热和余弦衰减的学习率调度器（按步数更新）。
    
    该调度器实现了两阶段学习率策略：
    1. 预热阶段（Warmup）：前 warmup_steps 步，学习率从 0 线性增长到 base_lr
    2. 衰减阶段（Cosine Decay）：后续步骤，学习率按余弦函数从 base_lr 衰减到接近 0
    
    学习率计算公式：
    - Warmup 阶段: lr = base_lr * (step / warmup_steps)
    - Cosine 阶段: lr = 0.5 * base_lr * (1 + cos(π * progress))
        其中 progress = (step - warmup_steps) / (total_steps - warmup_steps)
    
    示例：
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
        scheduler = WarmupCosineLR(optimizer, warmup_steps=1000, total_steps=10000, base_lr=1e-4)
        
        for step in range(10000):
            # 训练代码...
            scheduler.step()  # 更新学习率
    """
    
    def __init__(self, optimizer, warmup_steps: int, total_steps: int, base_lr: float):
        """初始化学习率调度器。
        
        Args:
            optimizer: PyTorch 优化器实例（如 Adam、SGD 等）
            warmup_steps: 预热步数，学习率从 0 线性增长到 base_lr 的步数
            total_steps: 总训练步数
            base_lr: 基础学习率，预热结束后的峰值学习率
        """
        self.optimizer = optimizer
        # 确保 warmup_steps 至少为 1，避免除零错误
        self.warmup_steps = max(1, warmup_steps)
        # 确保 total_steps 大于 warmup_steps，保证有衰减阶段
        self.total_steps = max(self.warmup_steps+1, total_steps)
        self.base_lr = base_lr
        self.step_num = 0  # 当前步数计数器
    
    def step(self):
        """更新学习率（每训练一步调用一次）。
        
        根据当前步数计算新的学习率：
        - 如果 step_num <= warmup_steps：线性预热阶段
        - 如果 step_num > warmup_steps：余弦衰减阶段
        
        Returns:
            当前的学习率值
        """
        self.step_num += 1
        
        if self.step_num <= self.warmup_steps:
            # 线性预热阶段：学习率从 0 线性增长到 base_lr
            # 公式：lr = base_lr * (step_num / warmup_steps)
            # 当 step_num = 0 时，lr = 0
            # 当 step_num = warmup_steps 时，lr = base_lr
            lr = self.base_lr * self.step_num / self.warmup_steps
        else:
            # 余弦衰减阶段：学习率从 base_lr 按余弦函数衰减
            # progress: 衰减阶段的进度，范围 [0, 1]
            #   0 表示衰减阶段开始（step_num = warmup_steps + 1）
            #   1 表示衰减阶段结束（step_num = total_steps）
            progress = (self.step_num - self.warmup_steps) / (self.total_steps - self.warmup_steps)
            # 余弦衰减公式：lr = 0.5 * base_lr * (1 + cos(π * progress))
            # 当 progress = 0 时，cos(0) = 1，lr = base_lr
            # 当 progress = 1 时，cos(π) = -1，lr ≈ 0
            lr = 0.5 * self.base_lr * (1.0 + math.cos(math.pi * progress))
        
        # 更新优化器中所有参数组的学习率
        for g in self.optimizer.param_groups:
            g['lr'] = lr
        
        return lr


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("学习率调度器测试")
    print("=" * 60)
    
    try:
        import torch
        import torch.nn as nn
        
        # 1. 创建简单的模型和优化器
        print("\n1. 创建测试模型和优化器...")
        model = nn.Linear(10, 1)  # 简单的线性层用于测试
        base_lr = 1e-3
        optimizer = torch.optim.Adam(model.parameters(), lr=base_lr)
        print(f"   基础学习率: {base_lr}")
        print(f"   优化器初始学习率: {optimizer.param_groups[0]['lr']}")
        
        # 2. 创建学习率调度器
        print("\n2. 创建学习率调度器...")
        warmup_steps = 100
        total_steps = 1000
        scheduler = WarmupCosineLR(optimizer, warmup_steps=warmup_steps, total_steps=total_steps, base_lr=base_lr)
        print(f"   预热步数: {warmup_steps}")
        print(f"   总步数: {total_steps}")
        print(f"   基础学习率: {base_lr}")
        
        # 3. 测试预热阶段
        print("\n3. 测试预热阶段（前几步）...")
        warmup_test_steps = [1, warmup_steps // 4, warmup_steps // 2, warmup_steps]
        for step in warmup_test_steps:
            # 重置调度器
            scheduler.step_num = 0
            scheduler.optimizer = torch.optim.Adam(model.parameters(), lr=base_lr)
            
            # 执行到指定步数
            for _ in range(step):
                lr = scheduler.step()
            
            expected_lr = base_lr * step / warmup_steps
            print(f"   步数 {step:3d}: 学习率 = {lr:.6f} (期望: {expected_lr:.6f})")
            print(f"      优化器学习率: {optimizer.param_groups[0]['lr']:.6f}")
            assert abs(lr - expected_lr) < 1e-6, f"预热阶段学习率计算错误: {lr} != {expected_lr}"
        
        # 4. 测试预热结束时的学习率
        print("\n4. 测试预热结束时的学习率...")
        scheduler.step_num = 0
        scheduler.optimizer = torch.optim.Adam(model.parameters(), lr=base_lr)
        for _ in range(warmup_steps):
            lr = scheduler.step()
        print(f"   步数 {warmup_steps}: 学习率 = {lr:.6f} (应该等于 base_lr: {base_lr})")
        assert abs(lr - base_lr) < 1e-6, f"预热结束时学习率应该等于 base_lr: {lr} != {base_lr}"
        print("   ✓ 预热结束时的学习率正确")
        
        # 5. 测试余弦衰减阶段
        print("\n5. 测试余弦衰减阶段...")
        scheduler.step_num = 0
        scheduler.optimizer = torch.optim.Adam(model.parameters(), lr=base_lr)
        
        # 测试几个关键点
        decay_test_steps = [
            warmup_steps + 1,  # 衰减阶段开始
            warmup_steps + (total_steps - warmup_steps) // 4,  # 1/4 处
            warmup_steps + (total_steps - warmup_steps) // 2,  # 1/2 处
            warmup_steps + 3 * (total_steps - warmup_steps) // 4,  # 3/4 处
            total_steps  # 结束
        ]
        
        for target_step in decay_test_steps:
            scheduler.step_num = 0
            scheduler.optimizer = torch.optim.Adam(model.parameters(), lr=base_lr)
            
            for _ in range(target_step):
                lr = scheduler.step()
            
            progress = (target_step - warmup_steps) / (total_steps - warmup_steps)
            expected_lr = 0.5 * base_lr * (1.0 + math.cos(math.pi * progress))
            print(f"   步数 {target_step:4d}: 学习率 = {lr:.6f} (期望: {expected_lr:.6f}, progress: {progress:.3f})")
            assert abs(lr - expected_lr) < 1e-5, f"余弦衰减阶段学习率计算错误: {lr} != {expected_lr}"
        
        # 6. 测试训练结束时的学习率
        print("\n6. 测试训练结束时的学习率...")
        scheduler.step_num = 0
        scheduler.optimizer = torch.optim.Adam(model.parameters(), lr=base_lr)
        for _ in range(total_steps):
            lr = scheduler.step()
        final_lr = lr
        print(f"   步数 {total_steps}: 最终学习率 = {final_lr:.6f}")
        print(f"   应该接近 0 (cos(π) = -1, lr = 0.5 * base_lr * (1 + (-1)) = 0)")
        assert final_lr < 1e-5, f"训练结束时学习率应该接近 0: {final_lr}"
        print("   ✓ 训练结束时的学习率正确")
        
        # 7. 记录完整的学习率曲线（采样）
        print("\n7. 记录学习率曲线（采样）...")
        scheduler.step_num = 0
        scheduler.optimizer = torch.optim.Adam(model.parameters(), lr=base_lr)
        
        lr_history = []
        sample_interval = max(1, total_steps // 20)  # 采样20个点
        
        for step in range(1, total_steps + 1):
            lr = scheduler.step()
            if step % sample_interval == 0 or step in [1, warmup_steps, warmup_steps + 1, total_steps]:
                lr_history.append((step, lr))
        
        print("   学习率曲线采样点:")
        for step, lr in lr_history[:10]:  # 只显示前10个点
            phase = "预热" if step <= warmup_steps else "衰减"
            print(f"     步数 {step:4d} ({phase:4s}): 学习率 = {lr:.6f}")
        if len(lr_history) > 10:
            print(f"     ... (共 {len(lr_history)} 个采样点)")
        
        # 8. 验证学习率单调性
        print("\n8. 验证学习率变化规律...")
        scheduler.step_num = 0
        scheduler.optimizer = torch.optim.Adam(model.parameters(), lr=base_lr)
        
        prev_lr = -1
        warmup_ok = True
        decay_ok = True
        
        for step in range(1, total_steps + 1):
            lr = scheduler.step()
            if step <= warmup_steps:
                # 预热阶段应该单调递增
                if lr < prev_lr:
                    warmup_ok = False
            else:
                # 衰减阶段应该单调递减
                if lr > prev_lr:
                    decay_ok = False
            prev_lr = lr
        
        print(f"   预热阶段单调递增: {'✓' if warmup_ok else '✗'}")
        print(f"   衰减阶段单调递减: {'✓' if decay_ok else '✗'}")
        
        # 9. 绘制学习率变化曲线
        print("\n9. 绘制学习率变化曲线...")
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            # 设置中文字体（如果系统支持）
            try:
                matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
                matplotlib.rcParams['axes.unicode_minus'] = False
            except:
                pass
            
            # 重新收集完整的学习率历史数据用于绘图
            scheduler.step_num = 0
            scheduler.optimizer = torch.optim.Adam(model.parameters(), lr=base_lr)
            
            steps = []
            lrs = []
            
            for step in range(1, total_steps + 1):
                lr = scheduler.step()
                steps.append(step)
                lrs.append(lr)
            
            # 创建图形
            plt.figure(figsize=(12, 6))
            
            # 绘制学习率曲线
            plt.plot(steps, lrs, 'b-', linewidth=2, label='学习率')
            
            # 标注预热阶段和衰减阶段的分界点
            plt.axvline(x=warmup_steps, color='r', linestyle='--', linewidth=1.5, alpha=0.7, label=f'预热结束 (步数 {warmup_steps})')
            
            # 标注关键点
            plt.plot([1], [lrs[0]], 'go', markersize=8, label='训练开始')
            plt.plot([warmup_steps], [lrs[warmup_steps-1]], 'ro', markersize=8, label=f'预热结束 (lr={lrs[warmup_steps-1]:.6f})')
            plt.plot([total_steps], [lrs[-1]], 'mo', markersize=8, label=f'训练结束 (lr={lrs[-1]:.6f})')
            
            # 设置图形属性
            plt.xlabel('训练步数 (Steps)', fontsize=12)
            plt.ylabel('学习率 (Learning Rate)', fontsize=12)
            plt.title(f'学习率调度曲线 (Warmup + Cosine Decay)\n预热步数: {warmup_steps}, 总步数: {total_steps}, 基础学习率: {base_lr}', fontsize=13)
            plt.grid(True, alpha=0.3)
            plt.legend(loc='best', fontsize=10)
            
            # 添加文本标注说明两个阶段
            plt.text(warmup_steps // 2, base_lr * 0.8, '预热阶段\n(线性增长)', 
                    ha='center', va='center', fontsize=11, 
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            plt.text(warmup_steps + (total_steps - warmup_steps) // 2, base_lr * 0.5, 
                    '衰减阶段\n(余弦衰减)', 
                    ha='center', va='center', fontsize=11,
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
            
            plt.tight_layout()
            
            # 保存图片
            import os
            output_dir = os.path.join(os.path.dirname(__file__), 'tmp')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, 'lr_schedule_curve.png')
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"   学习率曲线已保存到: {output_path}")
            
            # 显示图片（如果在支持 GUI 的环境中）
            try:
                plt.show()
            except:
                print("   注意: 无法显示图形窗口（可能在不支持 GUI 的环境中）")
            
            print("   ✓ 学习率曲线绘制完成")
            
        except ImportError:
            print("   警告: matplotlib 未安装，无法绘制学习率曲线")
            print("   请安装 matplotlib: pip install matplotlib")
        except Exception as e:
            print(f"   绘制曲线时出现错误: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("所有测试通过！")
        print("=" * 60)
        print("\n学习率调度器工作正常:")
        print(f"  - 预热阶段 ({warmup_steps} 步): 从 0 线性增长到 {base_lr}")
        print(f"  - 衰减阶段 ({total_steps - warmup_steps} 步): 从 {base_lr} 余弦衰减到接近 0")
        
    except ImportError as e:
        print(f"\n错误: {e}")
        print("请确保已安装 PyTorch: pip install torch")
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()