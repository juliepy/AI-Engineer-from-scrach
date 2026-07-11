"""
自动混合精度（AMP）和梯度累积的包装器
用于在训练大模型时节省显存并提高训练效率
"""
import torch

class AmpGrad:
    """AMP + 梯度累积包装器
    
    该类封装了自动混合精度训练和梯度累积功能，可以在显存受限的情况下
    训练更大的模型。通过梯度累积，可以将多个小批次的梯度累积后再更新参数。
    
    什么是梯度？
        梯度（Gradient）是损失函数对模型参数的偏导数，表示参数变化对损失的影响
        方向和大小。在反向传播中，梯度从输出层向输入层传递，优化器使用梯度来
        更新参数，使损失函数值下降。
    
    什么是梯度累积？
        梯度累积（Gradient Accumulation）是将多个小批次的梯度累加后再更新参数。
        例如，如果 accum=4：
        - 批次1 → 计算梯度 → 累积（不更新参数）
        - 批次2 → 计算梯度 → 累积（不更新参数）
        - 批次3 → 计算梯度 → 累积（不更新参数）
        - 批次4 → 计算梯度 → 累积 → 更新参数（使用累积的梯度）
    
    梯度累积的作用：
        1. 节省显存：用小批次训练，通过累积模拟大批次效果
           例如：想用 batch_size=128，但显存只能支持 32
           解决方案：用 batch_size=32，accum=4，效果相当于 batch_size=128
        
        2. 提高训练稳定性：大批次通常训练更稳定，梯度噪声更小
           通过梯度累积可以模拟大批次的效果，获得更稳定的梯度
        
        3. 灵活调整有效批次大小：不改变单次显存占用，通过调整 accum 参数
           来控制有效批次大小
    
    使用方法:
        amp = AmpGrad(optimizer, accum=4, amp=True)
        amp.backward(loss)
        if amp.should_step(): 
            amp.step()
            amp.zero_grad()
    
    注意事项：
        - 损失会自动除以累积步数，确保多次累积后的总梯度是正确的平均值
        - 学习率通常不需要调整，因为梯度已经按累积步数平均了
    """
    def __init__(self, optimizer, accum: int = 1, amp: bool = True):
        """
        初始化 AMP 梯度累积包装器
        
        Args:
            optimizer: PyTorch 优化器对象
            accum: 梯度累积步数，默认为1（不累积）
            amp: 是否启用自动混合精度训练，默认为True
        """
        self.optim = optimizer  # 保存优化器引用
        self.accum = max(1, accum)  # 梯度累积步数，至少为1
        # 只有在 CUDA 可用时才启用 AMP
        self.amp = amp and torch.cuda.is_available()
        # 创建梯度缩放器，用于 AMP 训练时的梯度缩放
        self.scaler = torch.cuda.amp.GradScaler(enabled=self.amp)
        self._n = 0  # 内部计数器，记录已累积的梯度步数
    
    def backward(self, loss: torch.Tensor):
        """
        执行反向传播，支持梯度累积和 AMP
        
        Args:
            loss: 损失值张量
        
        梯度累积原理：
            假设我们想用 batch_size=128 训练，但显存只能支持 batch_size=32。
            我们可以设置 accum=4，每次处理 batch_size=32 的数据：
            
            1. 第一次调用：loss1/4 → backward() → 梯度1 累积到参数上
            2. 第二次调用：loss2/4 → backward() → 梯度2 累积到参数上
            3. 第三次调用：loss3/4 → backward() → 梯度3 累积到参数上
            4. 第四次调用：loss4/4 → backward() → 梯度4 累积到参数上
            5. 此时 should_step() 返回 True，调用 step() 更新参数
            
            累积后的总梯度 = (梯度1 + 梯度2 + 梯度3 + 梯度4) / 4
            这等价于用 batch_size=128 一次性计算的平均梯度
        """
        # 将损失除以累积步数，这样多次累积后的总梯度才是正确的平均值
        # 例如：accum=4 时，每次损失除以4，4次累积后总梯度 = (g1+g2+g3+g4)/4
        loss = loss / self.accum
        if self.amp:
            # 使用 AMP 的缩放反向传播
            self.scaler.scale(loss).backward()
        else:
            # 普通反向传播
            loss.backward()
        self._n += 1  # 增加累积计数器
    
    def should_step(self):
        """
        判断是否应该执行优化器更新
        
        Returns:
            bool: 如果累积步数达到设定值，返回 True，否则返回 False
        """
        return (self._n % self.accum) == 0
    
    def step(self):
        """
        执行优化器更新步骤
        如果启用了 AMP，会先缩放梯度，更新参数，然后更新缩放器
        """
        if self.amp:
            # AMP 模式：先缩放梯度再更新，然后更新缩放器
            self.scaler.step(self.optim)
            self.scaler.update()  # 更新缩放器的缩放因子
        else:
            # 普通模式：直接更新参数
            self.optim.step()
    
    def zero_grad(self):
        """
        清零梯度
        使用 set_to_none=True 可以节省内存，将梯度设置为 None 而不是 0
        """
        self.optim.zero_grad(set_to_none=True)


if __name__ == "__main__":
    """
    测试代码：验证 AmpGrad 类的功能
    """
    import torch.nn as nn
    
    print("=" * 60)
    print("AmpGrad 测试")
    print("=" * 60)
    
    # 设置随机种子以便复现
    torch.manual_seed(42)
    
    # 创建一个简单的模型用于测试
    model = nn.Sequential(
        nn.Linear(10, 5),
        nn.ReLU(),
        nn.Linear(5, 1)
    )
    
    # 测试1: 基本功能测试（无累积，accum=1）
    print("\n[测试1] 基本功能测试（无累积）")
    print("-" * 60)
    model1 = nn.Sequential(
        nn.Linear(10, 5),
        nn.ReLU(),
        nn.Linear(5, 1)
    )
    optimizer1 = torch.optim.SGD(model1.parameters(), lr=0.01)
    amp1 = AmpGrad(optimizer1, accum=1, amp=False)
    
    # 模拟一个批次
    x = torch.randn(4, 10)
    y = torch.randn(4, 1)
    output = model1(x)
    loss = nn.MSELoss()(output, y)
    
    amp1.backward(loss)
    print(f"✓ backward() 执行成功")
    print(f"✓ should_step() = {amp1.should_step()} (应该为 True)")
    
    if amp1.should_step():
        amp1.step()
        amp1.zero_grad()
        print(f"✓ step() 和 zero_grad() 执行成功")
    
    # 测试2: 梯度累积功能测试（accum=4）
    print("\n[测试2] 梯度累积功能测试（accum=4）")
    print("-" * 60)
    model2 = nn.Sequential(
        nn.Linear(10, 5),
        nn.ReLU(),
        nn.Linear(5, 1)
    )
    optimizer2 = torch.optim.SGD(model2.parameters(), lr=0.01)
    amp2 = AmpGrad(optimizer2, accum=4, amp=False)
    
    # 保存初始参数用于验证
    initial_params = [p.clone() for p in model2.parameters()]
    
    # 模拟4个小批次
    for i in range(4):
        x = torch.randn(2, 10)
        y = torch.randn(2, 1)
        output = model2(x)
        loss = nn.MSELoss()(output, y)
        
        amp2.backward(loss)
        should_step = amp2.should_step()
        print(f"  批次 {i+1}: backward() 完成, should_step() = {should_step}")
        
        if should_step:
            amp2.step()
            amp2.zero_grad()
            print(f"  ✓ 第 {i+1} 批次后执行了 step() 和 zero_grad()")
    
    # 验证参数已更新
    params_changed = any(not torch.equal(p1, p2) 
                        for p1, p2 in zip(initial_params, model2.parameters()))
    print(f"✓ 参数已更新: {params_changed}")
    
    # 测试3: 验证梯度累积的正确性
    print("\n[测试3] 验证梯度累积的正确性")
    print("-" * 60)
    print("  比较：梯度累积 vs 直接大批次")
    
    # 生成固定的测试数据（确保两种方法使用相同数据）
    torch.manual_seed(123)
    x_small_batches = [torch.randn(2, 10) for _ in range(4)]
    y_small_batches = [torch.randn(2, 1) for _ in range(4)]
    x_batch = torch.cat(x_small_batches, dim=0)  # 合并成大批次 (8, 10)
    y_batch = torch.cat(y_small_batches, dim=0)  # 合并成大批次 (8, 1)
    
    # 方法1: 使用梯度累积（4个小批次，每个batch_size=2）
    torch.manual_seed(123)  # 确保模型初始化相同
    model_accum = nn.Sequential(
        nn.Linear(10, 5),
        nn.ReLU(),
        nn.Linear(5, 1)
    )
    optimizer_accum = torch.optim.SGD(model_accum.parameters(), lr=0.01)
    amp_accum = AmpGrad(optimizer_accum, accum=4, amp=False)
    
    # 保存梯度用于比较
    gradients_accum = []
    
    # 4个小批次
    for i in range(4):
        x = x_small_batches[i]
        y = y_small_batches[i]
        output = model_accum(x)
        loss = nn.MSELoss()(output, y)
        amp_accum.backward(loss)
        
        if amp_accum.should_step():
            # 保存累积后的梯度
            gradients_accum = [p.grad.clone() for p in model_accum.parameters()]
            amp_accum.step()
            amp_accum.zero_grad()
    
    # 方法2: 直接使用大批次（batch_size=8，相当于4*2）
    torch.manual_seed(123)  # 确保模型初始化相同
    model_batch = nn.Sequential(
        nn.Linear(10, 5),
        nn.ReLU(),
        nn.Linear(5, 1)
    )
    optimizer_batch = torch.optim.SGD(model_batch.parameters(), lr=0.01)
    
    output_batch = model_batch(x_batch)
    loss_batch = nn.MSELoss()(output_batch, y_batch)
    loss_batch.backward()
    
    gradients_batch = [p.grad for p in model_batch.parameters()]
    
    # 比较梯度（应该非常接近）
    max_diff = 0
    for g_accum, g_batch in zip(gradients_accum, gradients_batch):
        diff = torch.abs(g_accum - g_batch).max().item()
        max_diff = max(max_diff, diff)
    
    print(f"  梯度最大差异: {max_diff:.6f}")
    if max_diff < 1e-5:
        print(f"  ✓ 梯度累积结果与大批次结果一致（差异 < 1e-5）")
    else:
        print(f"  ⚠ 梯度存在差异: {max_diff:.6f} (可能是数值精度问题)")
    
    # 测试4: should_step() 逻辑测试
    print("\n[测试4] should_step() 逻辑测试")
    print("-" * 60)
    model4 = nn.Sequential(nn.Linear(5, 1))
    optimizer4 = torch.optim.SGD(model4.parameters(), lr=0.01)
    amp4 = AmpGrad(optimizer4, accum=3, amp=False)
    
    for i in range(6):
        x = torch.randn(2, 5)
        y = torch.randn(2, 1)
        output = model4(x)
        loss = nn.MSELoss()(output, y)
        amp4.backward(loss)
        
        should_step = amp4.should_step()
        expected = (i + 1) % 3 == 0
        status = "✓" if should_step == expected else "✗"
        print(f"  步骤 {i+1}: should_step() = {should_step}, 期望 = {expected} {status}")
    
    # 测试5: AMP 功能测试（如果 CUDA 可用）
    print("\n[测试5] AMP 功能测试")
    print("-" * 60)
    if torch.cuda.is_available():
        print(f"  CUDA 可用，测试 AMP 功能")
        model5 = nn.Sequential(nn.Linear(10, 1)).cuda()
        optimizer5 = torch.optim.SGD(model5.parameters(), lr=0.01)
        amp5 = AmpGrad(optimizer5, accum=2, amp=True)
        
        x = torch.randn(4, 10).cuda()
        y = torch.randn(4, 1).cuda()
        output = model5(x)
        loss = nn.MSELoss()(output, y)
        
        amp5.backward(loss)
        print(f"  ✓ AMP backward() 执行成功")
        print(f"  ✓ AMP 已启用: {amp5.amp}")
        
        if amp5.should_step():
            amp5.step()
            amp5.zero_grad()
            print(f"  ✓ AMP step() 执行成功")
    else:
        print(f"  CUDA 不可用，跳过 AMP 测试")
        # 测试自动禁用 AMP 功能
        model5_cpu = nn.Sequential(nn.Linear(10, 1))
        optimizer5_cpu = torch.optim.SGD(model5_cpu.parameters(), lr=0.01)
        amp5_cpu = AmpGrad(optimizer5_cpu, accum=1, amp=True)
        print(f"  ✓ 自动禁用 AMP: {amp5_cpu.amp} (期望: False)")
    
    print("\n" + "=" * 60)
    print("所有测试完成！")
    print("=" * 60)