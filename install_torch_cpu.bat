@echo off
echo Installing PyTorch (CPU-only version for compatibility)...
echo.
echo Uninstalling old version...
pip uninstall torch -y

echo.
echo Installing CPU-only PyTorch...
pip install torch torchvision torchaudio

echo.
echo Checking installation...
python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"

pause


