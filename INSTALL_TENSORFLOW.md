# Fix TensorFlow DLL Error

## Lỗi hiện tại
```
ImportError: DLL load failed while importing _pywrap_tensorflow_internal
```

## Giải pháp nhanh - Uninstall TensorFlow

```bash
pip uninstall tensorflow tf-keras -y
```

TensorFlow không cần thiết cho sentence-transformers cơ bản.

## Nếu vẫn cần TensorFlow

### Option 1: Install CPU-only TensorFlow
```bash
pip uninstall tensorflow tf-keras -y
pip install tensorflow-cpu
```

### Option 2: Install TensorFlow with GPU
```bash
pip uninstall tensorflow tf-keras -y
pip install tensorflow[and-cuda]
```

## Kiểm tra
```python
import tensorflow as tf
print(tf.__version__)
```

## Workaround - Disable TensorFlow Import

Thêm vào đầu file:

```python
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TF warnings
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Disable TensorFlow import in transformers
os.environ['TRANSFORMERS_NO_TENSORFLOW'] = '1'
```


