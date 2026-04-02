#!/bin/bash
set -e

echo "=== Voice-to-Line 安装脚本 ==="

# 安装系统依赖
echo "[1/2] 安装系统依赖..."
sudo apt-get update -qq
sudo apt-get install -y -qq xdotool

# 安装 Python 依赖
echo "[2/2] 安装 Python 依赖..."
pip install -r requirements.txt

echo ""
echo "=== 安装完成 ==="
echo "请编辑 config.yaml 填入你的阿里云 DashScope API Key"
echo "然后运行: python main.py"
