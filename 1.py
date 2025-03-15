import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode('utf-8')

def save_base64_to_file(base64_string, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(base64_string)

# 示例用法
image_path = "photomode_11072024_204709.png"  # 替换为你的图片路径
base64_string = image_to_base64(image_path)
print(base64_string)

# 将Base64编码字符串存储到目标.txt文件中
output_file_path = "./token/NapCat.txt"  # 替换为你的目标文件路径
save_base64_to_file(base64_string, output_file_path)