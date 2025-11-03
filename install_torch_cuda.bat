@echo off
echo Installing PyTorch with CUDA 12.1 support...
echo.
echo Uninstalling CPU-only version...
pip uninstall torch -y

echo.
echo Installing PyTorch with CUDA 12.1...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo.
echo Checking installation...
python -c "import torch; print('CUDA version:', torch.version.cuda); print('CUDA available:', torch.cuda.is_available())"

pause


