## Audio Labeling

## 使用说明
本项目是为快速从音频文件/文件夹得到质量还可以的数据集，相当一部分人工智能有关代码基于funasr。

### 推荐使用方式
推荐在项目的数据预处理阶段使用本工具，以确保输入数据的质量和一致性。

### 建议流程

1. 前置音频处理
   1. 去人声&降噪&去混响之类（没做好）
   2. 生成srt文件
2. 切分并生成list文件
   1. 通过SRT文件切分音频并生成list文件
   2. 直接通过已经有打标文件的数据集生成list文件
3. 后置音频处理
   1. 响度标准化
   2. （可选）根据特定情感/多说话人分类
4. 对list文件操作
   1. （可选）合并多个list文件
   2. （可选）筛选掉不符合时长、文本要求等的数据

### 模块介绍

- **人声分离与降噪（没做好）** (`src.audio_enhancer`): 用于 1.分离人声 2.降噪、去混响（在实现），
- **生成srt** (`src.srt_generator`): 此模块旨在自动生成 SRT 字幕文件，基于funasr实现，需要torch与大约3G左右内存/显存，您当然也可以用剪映等软件。
- **从srt和音频切分** (`src.srt_slicer`): 这个模块可以从 SRT 字幕文件和对应的音频文件中自动切分出各段音频，便于后续处理。
- **合并list文件** (`src.list_merger`): 当有多个数据列表需要合并为一个统一的列表时，此模块能够简化合并过程。
- **响度标准化** (`src.audio_normalizer`): 用于将音频文件的响度标准化到一致的水平，确保数据输入的一致性。
- **情感识别** (`src.emotion_recognition`): 基于emotion2vec实现，用于把音频按9种情感分类。
- **多说话人分类** (`src.speaker_classifier`): 基于funasr/cam++/3d_speaker实现，可以分成不同的说话人，（未来还可以通过不同的维度分类，在做）。
- **list文件筛选器(没做好)** (`src.list_filter`): 当需要从大量数据中筛选特定项时，此模块能提供帮助，目前正在开发中。
- **从已有数据集生成list(没做好)** (`src.list_generator`): 可以基于现有的数据集自动生成列表，方便管理和使用，目前仍在完善中。

特别的，我们提供了一个模板示例，可以在此基础上自定义一些模块

- **模板示例** (`src.empty_template`): 提供了一个模板示例，方便用户根据自己的需求开发新的模块。

### 截图

#### 切分并生成list文件

![image-20240402032542345](./assets/image-20240402032542345.png)

#### 后置音频处理

![image-20240402032421491](./assets/image-20240402032421491.png)

### 对list文件操作

![image-20240402032803436](./assets/image-20240402032803436.png)

*文档仍在书写中

## 如何安装

### Colab
https://colab.research.google.com/github/X-T-E-R/AudioLabeling/blob/main/colab.ipynb
直接点击进入，然后逐步执行即可
### Docker
~~建议您使用Docker部署，也提供 ipynb 等文件用于在 colab 之类的地方使用；~~: 但是有关文件都没做好

~~但是，对于windows用户，更推荐的是直接本地用整合包启动~~：甚至整合包也没做好
### 手动安装
您还可以选择手动安装

创建虚拟环境（建议python=3.10，要求python>3.8）-> 安装torch的cuda版本（可选） -> 安装requirements.txt

有关指令

``` 
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install install -r requirements.txt
```

## 如何使用

### Webui 界面

```
python app.py
```

### ipynb

如果是colab，请使用

https://colab.research.google.com/github/X-T-E-R/AudioLabeling/blob/main/colab.ipynb

本地则请运行
```
local.ipynb
```




## Credits

感谢所有贡献者与依赖的项目！
*文档仍在书写中，可能有遗漏



1. [gradio](https://www.gradio.app/)
2. i18n modified from [GPT-soVITS](https://github.com/RVC-Boss/GPT-SoVITS)
3. [funasr](https://github.com/alibaba-damo-academy/FunASR)
4. [pyloudnorm](https://github.com/csteinmetz1/pyloudnorm)
5. [srt](https://github.com/cdown/srt)
6. [emotion2vec](https://github.com/ddlBoJack/emotion2vec)
7. [3D-Speaker](https://github.com/alibaba-damo-academy/3D-Speaker)
