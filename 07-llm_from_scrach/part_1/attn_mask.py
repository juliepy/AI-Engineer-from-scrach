import torch

def causal_mask(T: int, device=None):
    """Returns a bool mask where True means *masked* (disallowed).
    Shape: (1, 1, T, T) suitable for broadcasting with (B, heads, T, T).
    """
    m = torch.triu(torch.ones((T, T), dtype=torch.bool, device=device), diagonal=1)
    return m.view(1, 1, T, T)


if __name__ == "__main__":
    print("=== Testing causal_mask function ===\n")
    
    # Test 1: Basic functionality with small size
    T = 5
    mask = causal_mask(T)
    print(f"Test 1: Create causal mask with T={T}")
    print(f"Shape: {mask.shape}")
    print(f"Expected shape: (1, 1, {T}, {T})")
    print(f"Mask:\n{mask.squeeze()}\n")
    
   