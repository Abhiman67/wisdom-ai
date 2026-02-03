WSL + CUDA + bitsandbytes quick guide (Windows)

Why: bitsandbytes (bnb) 4-bit is the easiest way to load large models on limited VRAM.
On native Windows, bnb often fails due to missing CUDA/Linux dependencies. Running inside WSL2 (Ubuntu) with proper NVIDIA drivers is the recommended path.

High-level steps (short):
1. Install WSL2 and Ubuntu from Microsoft Store.
   In an admin PowerShell:
     wsl --install -d ubuntu-22.04
   Reboot if prompted, then open the Ubuntu terminal.

2. Install NVIDIA drivers for WSL / CUDA on Windows host
   - Install the latest NVIDIA driver that supports WSL: https://developer.nvidia.com/cuda/wsl
   - Follow the "CUDA on WSL" driver installation steps on the NVIDIA site.

3. Inside Ubuntu (WSL) install CUDA toolkit and dependencies
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y build-essential git wget python3-venv python3-pip
   # Follow NVIDIA/CUDA toolkit install steps for Ubuntu on WSL (shortcuts can break). See: https://docs.nvidia.com/cuda/wsl-user-guide/index.html

4. Create venv and install required Python packages
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   # Install a matching PyTorch + CUDA wheel from https://pytorch.org/get-started/locally/
   # Example for CUDA 11.8 (change to your CUDA version):
   pip install torch --index-url https://download.pytorch.org/whl/cu118
   pip install -r /mnt/c/Users/shash/Downloads/bhagavad_gita_finetune/requirements.txt

5. bitsandbytes build notes
   - In many cases, `pip install bitsandbytes` will succeed in WSL once CUDA/toolchain are available.
   - If you run into compile problems, install libcuda-dev packages per bnb docs or use conda where wheels exist.

6. Verify GPU inside WSL
   # inside WSL
   python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"

7. Run training
   cd /mnt/c/Users/shash/Downloads/bhagavad_gita_finetune
   source .venv/bin/activate
   accelerate launch train_lora.py --data /mnt/c/Users/shash/Downloads/Bhagwad_Gita.jsonl --output_dir ./lora-output

If you want, I can produce a full step-by-step WSL script and the exact PyTorch wheel command based on the CUDA version you end up with.
