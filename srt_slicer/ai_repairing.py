from tools.srt_slicer.srt_utils import parse_srt_with_lib, generate_srt_with_lib, merge_subtitles_with_lib, count_words_multilang

enable_anthropic = False

try:
    import httpx
    from anthropic import Anthropic

    enable_anthropic = True
except:
    pass

example_prompt = [
    {
        "role": "user",
        "content": """你是一个字幕修复AI，能帮我修正我提供的字幕识别结果，这里面有一些ASR错误，你将修正他们，常见的比如错误的人名、错误的她/他/它、错误的识别、缺字/吞字、把英文识别成中文的同音字。
        我将给你可能含有一些错误的字幕，以<index={$index}><text={$text}>的格式提供，你需要修正他们。返回的格式也是一样的，以<index={$index}><text={$text}>的格式返回。
        请注意，你是一个字幕修复AI，不是一个翻译AI，你只需要修正错误，不需要翻译，更不需要去补全对话，最重要的是你不能返回除了格式以外的任何内容。
        你要做的只是修正错误，在原有读音的基础上，没有错的不用硬修正。
        现在我们开始第一个例子
        <index=23><text=先生宠溺地摸摸他的头，听着他慢慢的说自己发明的巫术点石成冰。>
        """,
    },
    {
        "role": "assistant",
        "content": """
        <index=23><text=先生宠溺地摸摸她的头，听着他慢慢的说自己发明的巫术点石成兵。>""",
    },
    {
        "role": "user",
        "content": """<index=4><text=一群人右肩母俩一起丢到了屋外。>
        <index=5><text=温柔的对着身后地上的兔娘说唉唉，我来晚了，现在我不会让任何人碰到你一下。>
        <index=6><text=出发前兔观念紧紧地被搂在怀中。>
        <index=7><text=好久不见啊我终于来看你啦宝宝。>
        """,
    },
    {
        "role": "assistant",
        "content": """<index=4><text=一群人又将母俩一起丢到了屋外。>
        <index=5><text=温柔的对着身后地上的兔姑娘说，唉唉，我来晚了，现在我不会让任何人碰到你一下。>
        <index=6><text=出发前兔姑娘紧紧地被搂在怀中。>
        <index=7><text=好久不见啊我终于来看你啦宝宝。>
        """,
    },
]


def format_to_srt(content, subtitles):
    result = []
    for line in content.split("\n"):
        index = line.split("<index=")[1].split(">")[0]
        text = line.split("<text=")[1].split(">")[0]
        for subtitle in subtitles:
            if subtitle.index == int(index):
                subtitle.content = text
                break
    return subtitles
        
        

def srt_to_format(subtitles):
    result = []
    for subtitle in subtitles:
        result.append(f"<index={subtitle.index}><text={subtitle.content}>")
    return "\n".join(result)

max_messages = 10
def make_prompt(previous_subtitles, previous_repaired_subtitles, now_subtitles):
    prompt = []
    prompt.extend(example_prompt)
    if len(previous_subtitles) > 0:
        count = min(len(previous_subtitles),max_messages)
        for i in range(len(previous_subtitles) - count, len(previous_subtitles)):
            prompt.append({"role": "user", "content": srt_to_format(previous_subtitles[i])})
            prompt.append(
                {"role": "assistant", "content": srt_to_format(previous_repaired_subtitles[i])}
            )
    prompt.append({"role": "user", "content": srt_to_format(now_subtitles)})
    return prompt


client = Anthropic(
    api_key="",
    http_client=httpx.Client(proxies="http://127.0.0.1:10809"),
)


def AI_repairing(subtitles):
    if not enable_anthropic:
        return subtitles
    previous_subtitles = []
    previous_repaired_subtitles = []
    for subtitle in subtitles:
        prompt = make_prompt(previous_subtitles, previous_repaired_subtitles, [subtitle])
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=prompt)
        
        print(message.content)
        repaired_subtitle = format_to_srt(message.content[0].text, [subtitle])[0]
        if repaired_subtitle.content != subtitle.content:
            previous_subtitles.append(subtitle)
            previous_repaired_subtitles.append(repaired_subtitle)
            subtitle.content = repaired_subtitle.content
        print(previous_subtitles)
    return subtitles
        
        


example_srt = """
1
00:00:05,733 --> 00:00:09,966
好久不见啊我终于来看你啦宝宝。

2
00:00:12,000 --> 00:00:15,066
今天是不是又没有乖乖睡觉。

3
00:00:16,200 --> 00:00:19,866
这么晚了还不睡，敲你的小脑袋哦。

4
00:00:22,066 --> 00:00:24,500
闭上你的小眼睛啦。

5
00:00:26,200 --> 00:00:29,766
今天给你讲一个故事。

6
00:00:31,966 --> 00:00:37,200
讲一个爱爱的故事，准备好了我要出发了。

7
00:00:42,166 --> 00:00:44,300
兔姑娘是一位巫师。

8
00:00:45,400 --> 00:00:47,700
学习乌书是有好有坏的。

9
00:00:49,300 --> 00:00:53,200
好就是能获得各种各样的能力。

10
00:00:54,100 --> 00:00:58,766
坏就是会将老师的坏毛病成倍的传染上。

11
00:01:01,933 --> 00:01:07,366
突破年的巫术老师天生就口吃就翻个倍。

12
00:01:08,400 --> 00:01:12,566
到吐破年身上就成了只能说叠字。

13
00:01:14,666 --> 00:01:25,133
他第一次见到秃先生时，秃先生在田地里轻轻松松拔出了一根，比自己大3倍的红萝卜。

14
00:01:30,700 --> 00:01:39,166
与秃姑娘正要擦肩而过的时候，秃姑娘情不自禁兴奋的说了句帅帅。

15
00:01:41,933 --> 00:01:47,366
听到这一句，兔先生的脸唰的一下害羞得通红。

16
00:01:48,400 --> 00:01:50,766
比尖上的红萝卜还要红。

17
00:01:52,300 --> 00:01:58,066
兔不恋天周无邪围着兔先生欢呼雀跃，红红。

18
00:01:58,900 --> 00:02:04,933
哼，兔先生分不清他是在说萝卜还是自己。

19
00:02:08,700 --> 00:02:19,666
于是他轻轻放下肩上的萝卜，对姑娘对兔姑娘轻声问道你是谁呀，你在这里做什么呢。

20
00:02:20,766 --> 00:02:24,700
屠年没有回答他，就呆呆的看着他。

21
00:02:25,666 --> 00:02:34,733
因为自己是刚刚下的巫术课，又累又还没有吃东西，于是肚子就咕咕咕的叫了。

22
00:02:37,200 --> 00:02:41,733
托尼的脸也稍微红了傻笑的说道呃呃。

23
00:02:42,966 --> 00:02:52,666
他的样子是多么可爱，笑起来时，两双眼睫毛就像两只黑蝴蝶一样美丽。

24
00:02:53,533 --> 00:03:00,400
蝴蝶轻轻地扑着翅膀，像是害羞的马上就要飞走了一样。

25
00:03:02,700 --> 00:03:06,266
兔先生看中他，入了迷。

26
00:03:07,466 --> 00:03:16,333
夕阳西下，兔先生和兔娘在森林边缘的一个木桩上，并排坐在一起烤萝卜吃。

27
00:03:17,500 --> 00:03:25,133
明明见面那么久了，他们脸的脸上，依旧还是害羞时那样红彤彤的。

28
00:03:26,566 --> 00:03:27,966
当天晚上。

29
00:03:29,066 --> 00:03:34,733
兔先生在梦里牵着兔姑娘的手，像今天那样坐在一起。

30
00:03:35,700 --> 00:03:45,766
楚姑娘靠在自己的肩上，笑的眼睛又眯成了两只蝴蝶，纯真的说着爱爱。

31
00:03:47,733 --> 00:03:51,166
第二天兔先生魂不守舍。

32
00:03:52,000 --> 00:04:01,300
脑袋里全是兔姑娘笑起来时，眼睛里的蝴蝶，还有奇奇怪怪却可可爱爱的碟子。

"""


if __name__ == "__main__":
    subtitles = parse_srt_with_lib(example_srt)
    for subtitle in subtitles:
        print(f"index: {subtitle.index}, content: {subtitle.content}")
    subtitles = AI_repairing(subtitles)
    for subtitle in subtitles:
        print(f"index: {subtitle.index}, content: {subtitle.content}")