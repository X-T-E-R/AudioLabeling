import os
        
def merge_list_folders(first_list_file, second_list_file, provide_character, first_folder, second_folder):
    merged_lines = []
    character1 = ""
    filenames = set()
    with open(first_list_file, 'r', encoding="utf-8") as f:
        first_list = f.readlines()
        for line in first_list:
            filename, character1, language, content = line.split('|')
            filenames.add(filename)

            character = character1 if character in ["", None] else provide_character
            new_line = f"{filename}|{character}|{language}|{content}"
            merged_lines.append(new_line)
    with open(second_list_file, 'r', encoding="utf-8") as f:
        second_list = f.readlines()
        for line in second_list:
            filename, character1, language, content = line.split('|')
            orig_filename = filename
            num = 1
            while filename in filenames:
                filename = f"{filename.rsplit('.', 1)[0]}_{num}.{filename.rsplit('.', 1)[1]}"
                num += 1
            try:
                os.rename(os.path.join(second_folder, orig_filename), os.path.join(first_folder, filename))
            except Exception as e:
                raise e
            character = character1 if character in ["", None] else provide_character
            new_line = f"{filename}|{character}|{language}|{content}"
            merged_lines.append(new_line)
    os.remove(second_list_file)
    if not os.listdir(second_folder):
        os.rmdir(second_folder)
    with open(first_list_file, 'w', encoding="utf-8") as f:
        f.writelines(merged_lines)
    return "\n".join(merged_lines)
            
        
    