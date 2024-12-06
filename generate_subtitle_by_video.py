import json
import subprocess
import stt
import datetime
import llm
import os
import sys
import re

cur_dir = os.path.dirname(os.path.abspath(__file__))
mp3_file_path = cur_dir + "/output/{}.mp3"
chi_srt_file_path = cur_dir + "/temp/{}_chi.srt"
chi_ass_file_path = cur_dir + "/output/{}_chi.ass"
eng_srt_file_path = cur_dir + "/temp/{}_eng.srt"
eng_ass_file_path = cur_dir + "/output/{}_eng.ass"
combine_srt_file_path = cur_dir + "/temp/{}_combine.srt"
combine_ass_file_path = cur_dir + "/output/{}_combine.ass"
output_ass_file_path = cur_dir + "/output/{}_output_ass.mp4"
output_file_path = cur_dir + "/output/{}_output.mp4"


def init():
    current_file_path = __file__
    # 获取目录
    current_directory = os.path.dirname(os.path.abspath(current_file_path))
    directory_data = f"{current_directory}/data"
    directory_output = f"{current_directory}/output"
    directory_temp = f"{current_directory}/temp"

    # 检查文件夹是否存在
    if not os.path.exists(directory_data):
        # 如果不存在，创建文件夹
        os.makedirs(directory_data)
    # 检查文件夹是否存在
    if not os.path.exists(directory_output):
        # 如果不存在，创建文件夹
        os.makedirs(directory_output)
    # 检查文件夹是否存在
    if not os.path.exists(directory_temp):
        # 如果不存在，创建文件夹
        os.makedirs(directory_temp)


def replace_in_file(file_path, search_text, replace_text):
    # 读取文件内容
    with open(file_path, "r", encoding="utf-8") as file:
        file_contents = file.read()

    # 替换内容
    new_contents = file_contents.replace(search_text, replace_text)

    # 写回文件
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(new_contents)


def exec_system_cmd(command):
    # 使用subprocess.Popen执行命令
    print(command)
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    # 等待命令执行完成
    stdout, stderr = process.communicate()

    # 检查是否有错误输出
    if process.returncode != 0:
        print("命令执行出错：", stderr)
        return ""
    else:
        return stdout.rstrip()


def ffmpeg_2_mp3(file, output):
    # 定义要执行的命令

    command = f"ffmpeg  -nostdin -loglevel quiet -y  -i {file} -vn -acodec libmp3lame -ab 320k {output}"
    # 执行命令
    res = exec_system_cmd(command)
    if res != "":
        print("转换成功！")
    return ""


def combine_srt_video(
    mp4_path, chi_srt_path, eng_srt_path, combine_ass_path, output_path
):
    # 定义要执行的命令
    command = f"ffmpeg -nostdin  -loglevel quiet -y -i {mp4_path} -i {chi_srt_path} -i {eng_srt_path} -i {combine_ass_path} -map 0:v -map 0:a -map 1 -map 2 -map 3 -c:v copy -c:a copy -c:s mov_text -metadata:s:s:0 language=chi -metadata:s:s:1 language=eng -metadata:s:s:2 language=mul {output_path}"
    res = exec_system_cmd(command)
    if res != "":
        return res
    return res


def combine_video(mp4_path, srt_path, output_path):
    # 定义要执行的命令
    command = f'ffmpeg -nostdin  -loglevel quiet -y -i {mp4_path} -vf "scale=1280:720,subtitles={srt_path}" -c:a copy {output_path}'
    res = exec_system_cmd(command)
    if res != "":
        return res
    return res


def trans_to_ass(srt, ass):
    # 定义要执行的命令
    command = f"""
    ffmpeg -nostdin  -loglevel quiet -y -i {srt} -vf "subtitles={srt}:force_style='FontSize=10,PrimaryColour=&Hffffff,Outline=1,Shadow=1'" {ass}
    """
    res = exec_system_cmd(command)
    # 替换字幕颜色
    replace_in_file(ass, "&Hffffff", "&H05daff")
    # 多语言字幕替换换行符合
    replace_in_file(ass, "\\N", " \\N ")
    # 字体字号替换
    replace_in_file(ass, "Arial,16", "Arial,12")
    return res


def format_stt_res(res_obj):
    if "segments" not in res_obj:
        return ""
    ret = []
    count = 1
    for seg in res_obj["segments"]:
        temp = {
            "num": str(count),
            "duration": f"{seconds_to_hms_milliseconds(seg['start'])} --> {seconds_to_hms_milliseconds(seg['end'])}",
            "text": seg["text"],
        }
        ret.append(temp)
        count += 1
    return ret


# trans_subtitle LLM tools
def trans_subtitle(subtitle):
    final = []
    data = []
    chunk_data = []
    str_len = 0
    for item in subtitle:
        temp = {
            "num": item["num"],
            "duration": item["duration"],
            "text": item["text"],
        }
        data.append(temp)
        str_len += len(item["text"])
        if str_len > 500:
            chunk_data.append(data)
            data = []
            str_len = 0
    if len(data) > 0:
        chunk_data.append(data)

    for temp_data in chunk_data:
        content = ""
        count = 1
        for temp_item in temp_data:
            content += str(count) + ". " + temp_item["text"] + "\n"
            count += 1
        input = f"""
        目标：请将下面原文内容逐行翻译为中文，要求逐行输出翻译后的文本，且要求序号与原文一样，可以适当的切分长句，不要输出任何其他内容。
        原文：{content}
        举例：
        原文：1. Apple
        2. Banana
        输出：1. 苹果
        2. 香蕉
        """
        llm_res = llm.LlmClient().chat_single(input)
        llm_array = llm_res.split("\n")
        for index, line in enumerate(llm_array):
            result = re.sub(r"\d+\S", "", line)
            temp_data[index]["text"] = result
            final.append(temp_data[index])
    return final


def save_srt(ret, srt_path):
    with open(srt_path, mode="w", encoding="utf-8") as file:
        for item in ret:
            # 示例数据
            lines = [item["num"], item["duration"], item["text"], ""]
            # 逐行写入文本文件
            for line in lines:
                file.write(line + "\n")  # 每行后添加换行符
    print("文本文件已成功写入！")


def read_from_file(srt_path):
    # 使用 with 语句打开文件
    res = []
    with open(srt_path, "r") as file:
        # 逐行读取文件
        count = 1
        temp = {}
        for line in file:
            content = line.strip()
            if count == 1:
                temp["num"] = content
            if count == 2:
                temp["duration"] = content
            if count == 3:
                temp["text"] = content
            if count == 4:
                res.append(temp)
                count = 0
                temp = {}
            count += 1
    return res


def save_combine_srt(chi, ori, srt_path):
    with open(srt_path, mode="w", encoding="utf-8") as file:
        trans_obj = {}
        for item in chi:
            trans_obj[item["num"]] = item["text"]
        for index, item in enumerate(ori):
            if item["num"] in trans_obj:
                trans_text = trans_obj[item["num"]]
            else:
                trans_text = ""
            # 示例数据
            lines = [
                item["num"],
                item["duration"],
                trans_text,
                item["text"],
                "",
            ]
            # 逐行写入文本文件
            for line in lines:
                file.write(line + "\n")  # 每行后添加换行符
    print("文本文件已成功写入！")


def seconds_to_hms_milliseconds(seconds):
    # 转换为 timedelta 对象
    td = datetime.timedelta(seconds=seconds)

    # 获取小时、分钟和秒
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # 获取毫秒
    milliseconds = int(td.microseconds / 1000)

    # 格式化为字符串
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


if len(sys.argv) < 2:
    print("please use python generate_subtitle_by_video.py xxx.mp4")
    exit(-1)
file_path = sys.argv[1]
# 获取文件名
filename = os.path.basename(file_path)
# 去掉扩展名
filename_without_extension = os.path.splitext(filename)[0]

file_name = filename_without_extension
mp4 = os.path.abspath(file_path)
mp3 = mp3_file_path.format(file_name)
chi_srt = chi_srt_file_path.format(file_name)
chi_ass = chi_ass_file_path.format(file_name)
eng_srt = eng_srt_file_path.format(file_name)
eng_ass = eng_ass_file_path.format(file_name)
combine_srt = combine_srt_file_path.format(file_name)
combine_ass = combine_ass_file_path.format(file_name)
output_ass = output_ass_file_path.format(file_name)
output = output_file_path.format(file_name)


print("step0: 初始化文件夹")
init()
print("step1: 将mp4 转化为 mp3")
# 将mp4 转化为 mp3
ffmpeg_2_mp3(mp4, mp3)
print("step2 将mp3 转化为文本")
# 将mp3 转化为文本
ori_text = stt.TransVoice().audio_to_text(mp3)
print("step3 将文本转化为字幕文件")
# 将文本转化为字幕文件
subtitle = format_stt_res(ori_text)
# 将原始语言字幕保存
save_srt(subtitle, eng_srt)
# subtitle = read_from_file(eng_srt)
# 将字幕文件完成翻译
print("step4 将字幕文件完成翻译")
# trans_res = trans_subtitle(subtitle)
print("step5 将字幕保存")
# 将中文字幕保存
# save_srt(trans_res, chi_srt)
trans_res = read_from_file(chi_srt)
# 将中英混合字幕保存
save_combine_srt(trans_res, subtitle, combine_srt)
# 将srt字幕转化为ass格式，支持自定义字幕格式
trans_to_ass(chi_srt, chi_ass)
trans_to_ass(eng_srt, eng_ass)
trans_to_ass(combine_srt, combine_ass)
print("step6 将字幕合成到视频")
# 将视频合成
combine_srt_video(mp4, chi_ass, eng_ass, combine_ass, output_ass)
combine_video(mp4, combine_ass, output)
print("all_done")
exit(0)
