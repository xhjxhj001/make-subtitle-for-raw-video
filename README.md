# make-subtitle-for-raw-video

# 为原生视频生成多语言字幕

# 简介
通过 ffmpeg、whisper、llm 工具，将视频中的语音提取后，转化为多语言字幕，合成到视频中

## 环境配置
安装ffmpeg
`brew install ffmpeg`

## 一、快速使用
1. 将根目录下 .env.template 复制一份到 .env
`cp .env.template .env`
2. 配置 .env 文件中的 SK 信息
3. 执行根目录下的 init.sh
`sh init.sh`
4. 执行 `python generate_subtitle_by_video.py xxx.mp4`

## 二、目录介绍
output 是最终输出的视频文件目录，一共有2个
- xxxx_output.mp3 是提取的音频文件
- xxxx_output.mp4 是硬编码多语言视频文件
- xxxx_output_ass.mp4 是软编码，可以自己通过播放器选择挂载哪种语音的视频文件
- xxxx.ass 是字幕文件，可以外挂到视频中
temp 是中间过程的文件目录
- xxxx.srt 是srt字幕文件