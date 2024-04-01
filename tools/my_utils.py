import os

global audio_file_ext_list
audio_file_ext_list = ["wav", "mp3", "flac", "m4a", "aac", "ogg", "wma", "ape", "aiff", "alac", "amr", "au", "awb", "dct", "dss", "dvf", "gsm", "iklax", "ivs", "m4p", "mmf", "msv", "mpc", "ogg", "oga", "opus", "ra", "rm", "raw", "sln", "tta", "vox", "wav", "wma", "wv", "webm", "8svx", "cda"]

def get_relative_path(path, base):
    return os.path.relpath(path, base)

def scan_ext(folder, ext_list):
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    ext_list = [ext.lower() for ext in ext_list]
    file_list = []
    for file in os.listdir(folder):
        if os.path.isdir(os.path.join(folder, file)):
            continue
        try:
            file_ext :str = file.rsplit('.', 1)[1]
        except IndexError:
            file_ext = ""
        if os.path.isfile(os.path.join(folder, file)) and file_ext.lower() in ext_list:
            file_list.append(get_relative_path(os.path.join(folder, file), folder))
    return file_list

def scan_folders(base_folder):
    if not os.path.exists(base_folder):
        os.makedirs(base_folder, exist_ok=True)
    folder_list = []
    for folder in os.listdir(base_folder):
        if os.path.isdir(os.path.join(base_folder, folder)):
            folder_list.append(get_relative_path(os.path.join(base_folder, folder), base_folder))
    return folder_list

def scan_audios(base_folder):
    if not os.path.exists(base_folder):
        os.makedirs(base_folder, exist_ok=True)
    audio_list = []
    audio_list.extend(scan_ext(base_folder, audio_file_ext_list))
    return audio_list

def scan_audios_and_folders(base_folder):
    if not os.path.exists(base_folder):
        os.makedirs(base_folder, exist_ok=True)
    audio_list = []
    audio_list.extend(scan_ext(base_folder, audio_file_ext_list))
    audio_list.extend(scan_folders(base_folder))
    return audio_list

def scan_ext_walk(folder, ext_list):
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    ext_list = [ext.lower() for ext in ext_list]
    file_list = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            try:
                file_ext :str = file.rsplit('.', 1)[1]
            except IndexError:
                file_ext = ""
            if file_ext.lower() in ext_list:
                file_list.append(get_relative_path(os.path.join(root, file), folder))
    return file_list

def scan_audios_walk(base_folder):
    if not os.path.exists(base_folder):
        os.makedirs(base_folder, exist_ok=True)
    audio_list = []
    audio_list.extend(scan_ext_walk(base_folder, audio_file_ext_list))
    return audio_list