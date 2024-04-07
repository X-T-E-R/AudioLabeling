import srt


def parse_srt_with_lib(content):
    subtitles = list(srt.parse(content))
    return subtitles

def generate_srt_with_lib(subtitles):
    content = srt.compose(subtitles)
    return content

def merge_subtitles_with_lib(subtitles, short_interval, max_interval, max_text_length=30, add_period=True, merge_zero_interval=True):
    # 标点符号
    punctuations = ["。","!", "！", "？", "?", "；", ";",  "…", ".", "~"]
    punctuations_extanded = []
    punctuations_extanded.extend(punctuations)
    punctuations_extanded.extend([ "：", ":", "，", ",", "—","、"])
    
    # 直接合并间隔特别短的字幕
    if merge_zero_interval:
        eps = short_interval
        for i in range(len(subtitles) - 1, 0, -1):
            if subtitles[i-1].content[-1] in punctuations_extanded:
                continue
            if abs(subtitles[i].start.total_seconds() - subtitles[i-1].end.total_seconds()) < eps:
                subtitles[i - 1].end = subtitles[i].end
                subtitles[i - 1].content += subtitles[i].content
                subtitles.pop(i)
                
    merged_subtitles = []
    current_subtitle = None
    for subtitle in subtitles:
        if current_subtitle is None:
            current_subtitle = subtitle
        else:
            current_end = current_subtitle.end.total_seconds()
            next_start = subtitle.start.total_seconds()
            if current_subtitle.content[-1] not in punctuations and (next_start - current_end <= max_interval and count_words_multilang(current_subtitle.content + subtitle.content) < max_text_length):
                current_subtitle.end = subtitle.end
                comma = '，' if current_subtitle.content[-1] not in punctuations_extanded else ''
                current_subtitle.content += comma + subtitle.content
                
            else:
                if add_period and current_subtitle.content[-1] not in punctuations_extanded:
                    current_subtitle.content += '。'
                merged_subtitles.append(current_subtitle)
                current_subtitle = subtitle
    if current_subtitle is not None:
        merged_subtitles.append(current_subtitle)
    # 重新分配id，因为srt.compose需要id连续
    for i, subtitle in enumerate(merged_subtitles, start=1):
        subtitle.index = i
    return merged_subtitles


def count_words_multilang(text):
    # 初始化计数器
    word_count = 0
    in_word = False
    
    for char in text:
        if char.isspace():  # 如果当前字符是空格
            in_word = False
        elif char.isascii() and not in_word:  # 如果是ASCII字符（英文）并且不在单词内
            word_count += 1  # 新的英文单词
            in_word = True
        elif not char.isascii():  # 如果字符非英文
            word_count += 1  # 每个非英文字符单独计为一个字
    
    return word_count

import pydub, os



# TODO: Add auto detect language
def slice_audio_with_lib(
    audio_path,
    save_folder,
    format,
    subtitles,
    pre_preserve_time=0.1,
    post_preserve_time=0.05,
    pre_silence_time=0.1,
    post_silence_time=0.1,
    min_audio_duration=2.0,
    max_audio_duration=300.0,
    language="ZH",
    character="character",
):
    os.makedirs(save_folder, exist_ok=True)
    list_file = os.path.join(save_folder, "datamapping.list")
    try:
        audio = pydub.AudioSegment.from_file(audio_path)
        audio_duration = audio.duration_seconds
    except Exception as e:
        raise e
    with open(list_file, 'w', encoding="utf-8") as f:
        for i in range(len(subtitles)):
            subtitle = subtitles[i]
            start = max(subtitle.start.total_seconds() - pre_preserve_time, 0.0001)
            end = min(subtitle.end.total_seconds() + post_preserve_time, audio_duration - 0.0001)
            if end - start < min_audio_duration or end - start > max_audio_duration:
                # 如果音频片段过短或过长，跳过
                continue
            if i < len(subtitles) - 1:
                next_subtitle = subtitles[i + 1]
                end = min(end, 1.0/2*(subtitle.end.total_seconds()+next_subtitle.start.total_seconds()))
            if i > 0:
                prev_subtitle = subtitles[i - 1]
                start = max(start, 1.0/2*(prev_subtitle.end.total_seconds()+subtitle.start.total_seconds()))
            try:
                sliced_audio = audio[int(start * 1000):int(end * 1000)]
                file_name = f'{character}_{i + 1:03d}.{format}'
                save_path = os.path.join(save_folder, file_name)
                sliced_audio.export(save_path, format=format)
                f.write(f"./{file_name}|{character}|{language}|{subtitle.content}\n")
                print(f"Slice {file_name} from {start} to {end}")
            except Exception as e:
                raise e

def filter_subtitles(subtitles, min_length, filter_english = False, filter_words = ""):
    filtered_subtitles = []
    for subtitle in subtitles:
        if count_words_multilang(subtitle.content) >= min_length:
            flag = False
            if filter_english:
                for i in subtitle.content:
                    if i in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
                        flag = True
                        break
            if not flag and filter_words:
                filter_words.replace("\r", "\n")
                for word in filter_words.split("\n"):
                    if word in subtitle.content:
                        flag = True
                        break
            if not flag:
                filtered_subtitles.append(subtitle)
    return filtered_subtitles

def filter_srt(input_text, min_length, filter_english = False, filter_words = ""):
    subtitles = parse_srt_with_lib(input_text)
    filtered_subtitles = filter_subtitles(subtitles, min_length, filter_english, filter_words)
    return generate_srt_with_lib(filtered_subtitles)