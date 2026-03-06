#!/bin/bash

# 获取今天的日期，格式为 YYYY-MM-DD
TODAY=$(date +%Y-%m-%d)

# 定义视频目录
VIDEO_DIR="$HOME/work/temp/video/tiktok/$TODAY"
# VIDEO_DIR="$HOME/work/temp/video/tiktok/$TODAY"

# 固定文本内容
DESC="关注主播，带你玩更多好玩的小游戏
#抖音小游戏 #开来和我一起玩吧 # #解压小游戏 #这个游戏很好玩"

# 遍历该目录下所有 .mp4 文件
for VIDEO in "$VIDEO_DIR"/*.mp4; do
  # 获取视频文件名（不带路径）
  BASENAME=$(basename "$VIDEO" .mp4)

  # 生成对应的 .txt 文件
  echo "$DESC" > "$VIDEO_DIR/$BASENAME.txt"

  # 执行上传命令
  python cli_main.py douyin ycp upload "$VIDEO" -pt 0
done
