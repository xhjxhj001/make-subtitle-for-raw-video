#!/bin/bash

# 获取当前脚本的绝对路径
SCRIPT_DIR="$(dirname "$(realpath "$0")")"

cd $SCRIPT_DIR

# 要检查的文件路径
FILE="$SCRIPT_DIR/.env"

# 检查文件是否存在
if [ ! -e "$FILE" ]; then
    echo "env 文件不存在: $FILE"
    exit
fi
pip install -r requirements.txt