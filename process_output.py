import re
import uuid
import os
from matplotlib import pyplot as plt
from matplotlib.text import Text as LaText
from matplotlib.transforms import Affine2D
from matplotlib import rcParams
import shutil

from sympy import symbols, preview
from sympy.abc import x
from ncatbot.core.element import (
    MessageChain,  # 消息链，用于组合多个消息元素
    Text,          # 文本消息
    Reply,         # 回复消息
    At,            # @某人
    AtAll,         # @全体成员
    Dice,          # 骰子
    Face,          # QQ表情
    Image,         # 图片
    Json,          # JSON消息
    Music,         # 音乐分享 (网易云, QQ 音乐等)
    CustomMusic,   # 自定义音乐分享
    Record,        # 语音
    Rps,           # 猜拳
    Video,         # 视频
    File,          # 文件
)
def remove_empty_lines(text):
    lines = text.split('\n')
    non_empty_lines = [line for line in lines if line.strip() != '']
    return '\n'.join(non_empty_lines)
# 设置matplotlib使用LaTeX渲染
rcParams['text.usetex'] = True

class ResponseProcess():

    def __init__(self):
        self.codelist = []
        self.latexlist = []
        self.language_dict = {
            'python': 'py',
            'javascript': 'js',
            'java': 'java',
            'html': 'html',
            'c++': 'cpp'
        }
        self.counter = 1  # 初始化计数器
        rcParams['text.usetex'] = True
        
        self.cleanup_directory('codes')
        self.cleanup_directory('images')

    def cleanup_directory(self, directory):
        """删除并重新创建指定的目录"""
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)

    def latex_to_image(self, latex_code, output_path, footer_text=""):
        """将LaTeX代码渲染为图片，并在底部添加特定字符"""
    

        try:
            
            '''plt.figure() 
            plt.text(0.5, 0.7, f'${latex_code}$', fontsize=20, ha='center', va='center')
            #plt.text(0.5, 0.1, footer_text, fontsize=10, ha='center', va='center')  # 在底部添加文本
            plt.axis('off')
            plt.tight_layout(pad=0)
            plt.savefig(output_path, bbox_inches='tight', pad_inches=0.1)
            plt.close()'''

            '''plt.rcParams.update({
                "text.usetex": True,          # 启用LaTeX渲染
                "font.family": "serif",       # 使用衬线字体（LaTeX默认）
                "font.serif": ["Computer Modern Roman"],  # LaTeX默认字体
                "font.size": 14,              # 控制公式字体大小
                "axes.linewidth": 1,          # 坐标轴线宽
            })
            plt.rcParams['text.latex.preamble'] = 
            # 创建画布，调整figsize控制整体尺寸
            fig = plt.figure(figsize=(0.2,0.1))  # 宽度4英寸，高度2英寸
            ax = fig.add_axes([0, 0, 1, 1])   # 占满整个画布
            ax.axis("off")                    # 隐藏坐标轴

            # 输入LaTeX公式

            # 渲染公式到画布中央
            ax.text(0.5, 0.5, f'${latex_code}$', 
                    ha='center', va='center', 
                    color='black')

            # 保存为PNG，调整dpi和bbox裁剪空白
            plt.savefig(output_path, 
                    dpi=300,               # 分辨率（按需调整）
                    bbox_inches='tight',   # 自动裁剪空白
                    pad_inches=0.1) 


            
            plt.close()'''

            preview(f'${latex_code}$', output='png', viewer='file', filename=output_path, euler=True, dvioptions=['-D', '300'])


        except Exception as e:
            print(f"LaTeX渲染失败: {e}")
            return False
        return True

    def latex_replacement(self, match):
        """处理LaTeX代码块的替换逻辑"""
        latex_code = match.group(1).strip().strip('$')
        filename = f'{self.counter}.png'
        output_path = os.path.join('images', filename)
        
        if self.latex_to_image(latex_code, output_path, footer_text=filename):
            self.latexlist.append(filename)  # 将计数器值存储到 latexlist 中
            self.counter += 1  # 递增计数器
            return '[LaTex公式(3sdh图片3sdf)LaTex]'
        else:
            return f'[LaTeX渲染失败]({latex_code})'

    def replace_block(self, match):
        """处理单个代码块的替换逻辑"""
        code_block = match.group(1)
        
        # 提取语言标识和代码内容
        lang_match = re.match(r'```([^\n]*)', code_block)
        if lang_match:
            lang = lang_match.group(1).strip().lower()
            code_start = lang_match.end()
            code = code_block[code_start:-3].strip()  # 去除结尾的```
        else:
            lang = ''
            code = code_block[3:-3].strip()  # 去除开头和结尾的```

        ext = self.language_dict.get(lang, 'txt')
        filename = f'{self.counter}.{ext}'
        with open(os.path.join('codes', filename), 'w', encoding='utf-8') as f:
            f.write(code)
        self.codelist.append(filename)  # 将计数器值存储到 codelist 中
        self.counter += 1  # 递增计数器
        return f'[代码文件({filename})]'

    def process_text(self, input_text):
        """主处理函数"""
        # 创建保存目录
        
        self.cleanup_directory('codes')
        self.cleanup_directory('images')

        output_list = []
        os.makedirs('codes', exist_ok=True)
        os.makedirs('images', exist_ok=True)
        
        # 正则表达式匹配代码块
        code_block_pattern = r'(```[\s\S]*?```)'
        
        # 执行替换处理
        processed_text = re.sub(code_block_pattern, self.replace_block, input_text, flags=re.DOTALL)
        

        latex_block_pattern1 = r'\\\[([\s\S]*?)\\]'

        latex_block_pattern2 = r'\\\(([\s\S]*?)\\\)'

        latex_block_pattern3 = r'$([\s\S]*?)$'

        processed_text = re.sub(latex_block_pattern1, self.latex_replacement, processed_text, flags=re.DOTALL)

        processed_text = re.sub(latex_block_pattern2, self.latex_replacement, processed_text, flags=re.DOTALL)
        #processed_text = re.sub(latex_block_pattern3, self.latex_replacement, processed_text, flags=re.DOTALL)
        
        

        filelist = []

        processed_text = remove_empty_lines(processed_text)

        if self.latexlist:
            output_list = []
            processed_text_list = processed_text.split('[LaTex公式(3sdh图片3sdf)LaTex]')

            for i in range(len(self.latexlist)):
                output_list.append(processed_text_list[i])
                element = os.path.join('D:/NapCat.32793.Shell/ncbot', "images",self.latexlist[i])
                output_list.append(element)
            
            output_list.append(processed_text_list[-1])

        else:
            output_list = [processed_text]


        for element in self.codelist:
            element = f'D:/NapCat.32793.Shell/ncbot/codes/{element}'
            filelist.append(element)
        self.latexlist = []
        self.codelist = []
        
        
        
        return output_list, filelist



if __name__ == "__main__":
    # 示例输入文本
    input_text = r"""一元二次方程的一般形式为：


"""
    test = ResponseProcess()
    processed_text = test.process_text(input_text)
    print("处理后的文本:\n", processed_text)