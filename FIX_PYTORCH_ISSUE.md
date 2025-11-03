# Sửa Lỗi PyTorch DLL

## Vấn đề

```
OSError: [WinError 1114] A dynamic link library (DLL) initialization routine failed
```

## Nguyên nhân

PyTorch đã cài là bản **CPU-only** nhưng Windows thiếu DLL cần thiết hoặc xung đột.

## Giải pháp

### Option 1: Cài PyTorch với CUDA (GPU)

Nếu có GPU NVIDIA:

```bash
# Uninstall old version
pip uninstall torch torchvision torchaudio -y

# Install with CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Check
python -c "import torch; print(torch.cuda.is_available())"
```

Hoặc chạy: `install_torch_cuda.bat`

### Option 2: Cài PyTorch CPU-only (Stable)

```bash
# Uninstall old version  
pip uninstall torch torchvision torchaudio -y

# Install CPU-only
pip install torch torchvision torchaudio

# Check
python -c "import torch; print(torch.__version__)"
```

Hoặc chạy: `install_torch_cpu.bat`

### Option 3: Sử dụng hệ thống đơn giản (Khuyến nghị)

Đã có script **semantic_recommendation_simple.py** không cần torch:

```bash
python semantic_recommendation_simple.py
```

## Kiểm tra GPU

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
```

## Troubleshooting

### 1. Update Visual C++ Redistributables
Download: https://aka.ms/vs/17/release/vc_redist.x64.exe

### 2. Check CUDA Installation
```bash
nvcc --version
nvidia-smi
```

### 3. Reinstall PyTorch completely
```bash
pip uninstall torch torchvision torchaudio -y
pip cache purge
pip install torch torchvision torchaudio
```

### 4. Use virtual environment
```bash
python -m venv venv
venv\Scripts\activate
pip install torch --no-cache-dir
```

## Hiện tại

Hệ thống đang sử dụng script đơn giản không cần torch:
- ✓ `semantic_recommendation_simple.py` - Working
- ✓ Keyword-based similarity
- ✓ Qdrant không cần embeddings phức tạp

## Next Steps

1. Dùng `semantic_recommendation_simple.py` (đã chạy được)
2. Hoặc sửa PyTorch để dùng BGE-M3 embeddings
3. Hoặc dùng services cloud (Hugging Face Inference API)

## Files

- `semantic_recommendation_simple.py` - Working ✅
- `semantic_recommendation_system.py` - Requires torch fix
- `install_torch_cpu.bat` - Install CPU version
- `install_torch_cuda.bat` - Install CUDA version


