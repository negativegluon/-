from ncatbot.core import BotClient
from ncatbot.core.message import GroupMessage, PrivateMessage
from ncatbot.utils.config import config
from ncatbot.utils.logger import get_log
import time
import ollama
from ollama import chat
from ollama import ChatResponse

from process_output import ResponseProcess
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
import re
from ollama import Client
_log = get_log()

config.set_bot_uin("")  # 设置 bot qq 号 (必填)
config.set_ws_uri("")  # 设置 napcat websocket server 地址
config.set_token("") # 设置 token (napcat 服务器的 token)

bot = BotClient()

import csv

import requests

import random

def unload_model(model_name):
    url = ""
    payload = {"model": model_name}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"Model '{model_name}' has been successfully unloaded from GPU memory.")
    else:
        print(f"Failed to unload model '{model_name}'. Status code: {response.status_code}")

client = Client(
    host='',
    
)
message_tmp = ''

with open('systemprompt1.txt', 'r', encoding='utf-8') as file:
    systemprompt = file.read().strip()

with open('prompt-maths.txt', 'r', encoding='utf-8') as file:
    math_prompt = file.read().strip()
justifyer1 = '你是一个群聊的参与者。请根据你见过的messages中user的对话与上文的有关你自己的信息，判断他们最新的聊天内容是否适合你加入讨论或与你有关。如果是，回复1。如果不是，回复0.请仅在你的回答中提供数字0或1.'
justifyer2 = '对于你看到的文本，你需要判断其是否涉及数学推理、代码设计与写作或谜语。如果是，回复1。如果不是，回复0。请仅在你的回答中提供数字0或1.'

justifyer = systemprompt

class Anti_DDos():
    def __init__(self):
        self.last_time = time.time()
        self.msgtmp = ''
        self.function1_running = False
    
    def check_timer(self):
        timenow = time.time()
        timebreak = timenow - self.last_time
        self.last_time = timenow
        if timebreak < 2:
            return 0
        else:
            return int(timebreak)
    
    def update_timer(self):
        self.last_time = time.time()

timer = Anti_DDos()

responseprocessor = ResponseProcess()

class Ollamabot():
    def __init__(self):

        self.messagehistory = []
        self.pendingwords = ''
        self.math_history = []
    async def reply_message(self, msg):
        pattern = r'\[.*?CQ:at.*?\]'
        words = msg.raw_message
        skip_reply = 0
        if "[CQ:at" in words:
            if "3832692983" in words:
                skip_reply=1
            else:
                return 1
        words = re.sub(pattern, '', words, flags=re.DOTALL)
        
        if '[CQ:image' in words:
            return 1
        if not words:
            return 1


        self.messagehistory.append({"role": "user", "content": words})
        self.math_history.append({"role": "user", "content": words})

        if_use_qwq = ''
        reply5 = client.chat(model='qwen2.5:14b-13k', messages = ([{"role": "system", "content": justifyer2}] + [{"role": "user", "content": words}]), stream = True)
        for chunk in reply5:
            if_use_qwq += chunk["message"]["content"]
        if '1' in if_use_qwq:
            skip_reply = 1



        if skip_reply == 1:
            if_reply = '1'
        else:
            if '[CQ:image' in words:
                return 1
            if not words:
                return 1
            
            
            

            if_reply3 = client.chat(model='qwen2.5:14b-13k', messages = ([{"role": "system", "content": justifyer},{"role": "user", "content": justifyer1}] + self.messagehistory), stream = True)
            if_reply = ''
            for chunk in if_reply3:
                    if_reply += chunk["message"]["content"]
            #if_reply = '1'
            print(if_reply)
            
            pass
        if not ('0' in if_reply):
            #if len(words) < 7:
                #response = client.chat(model='llama-16k', messages=([{"role": "system", "content": systemprompt}] + self.messagehistory), stream=True) 
            if len(words) < 5:
                response = client.chat(model='qwen2.5:14b-13k', messages=([{"role": "system", "content": systemprompt}] + self.messagehistory ), stream=True)
            else:
                if '0' in if_use_qwq:
                    
                    response = client.chat(model='qwen2.5:14b-13k', messages=([{"role": "system", "content": systemprompt}] + self.messagehistory), stream=True)
                else:
                    await msg.reply(text='唔…这是个有趣的问题…让我想想…呃…你能出来帮忙看看这道题吗…')
                    print('need qwq')
                    
                    if len(words) < 1000:

                        response = client.chat(model='qwen2.5:14b-13k', messages=([{"role": "system", "content": math_prompt}] + self.math_history ), stream=True)
                    else:
                        response = client.chat(model='qwq:32b-100k', messages=([{"role": "system", "content": math_prompt}] + self.math_history ), stream=True)
                    

            reply = ""
            for chunk in response:
                reply += chunk["message"]["content"]
            reply = re.sub(r'<think>.*?</think>', '', reply, flags=re.DOTALL)    
            
            # 将模型回复加入历史
            if '0' in if_use_qwq:
                
                self.math_history.pop()
                self.messagehistory.append({"role": "assistant", "content": reply})

            else:
                self.messagehistory.pop()
                
                self.math_history.append({"role": "assistant", "content": reply})
                await msg.reply(text='嗯…问题想出来了…我也该走了')
            
            self.trim_message_history()
            self.trim_message_history_math()

            textlist,files = responseprocessor.process_text(reply)
            #message = MessageChain(textlist)
            #await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)
            for b in range(len(textlist)):
                
                all_message_list = []

                if b % 2 == 0:
                    
                    rawtext = textlist[b]
                    rawtext = rawtext.replace('.', '').replace('-', '')

                    rawlines = rawtext.split('\n')
                    non_empty_lines = [line for line in rawlines if line.strip() != '']
                    
                    rawtext = ''.join(non_empty_lines)

                    if rawtext.strip():
                        tmp_message = MessageChain([Text(rawtext)])
                    else:
                        continue
                else:
                    tmp_message = MessageChain([Image(textlist[b])])
                
                if tmp_message:
                    await msg.reply(rtf=tmp_message)
            
            
            for a in files:
                tmp_message = MessageChain([File(a)])
                await msg.reply(rtf=tmp_message)
        else:
            return 114514

    def trim_message_history(self):
        total_length = sum(len(item["content"]) for item in self.messagehistory)
        while total_length > 8500:
            print(f'cleaning chat history at {total_length}')
            for i, item in enumerate(self.messagehistory):
                if item["role"] == "assistant":
                    del self.messagehistory[i]
                    break
            else:
                self.messagehistory.pop(0)
            total_length = sum(len(item["content"]) for item in self.messagehistory)
        print(f'cleaned chat history to {total_length}')

    def trim_message_history_math(self):
        total_length = sum(len(item["content"]) for item in self.math_history)
        while total_length > 10000:
            print(f'cleaning chat history at {total_length}')
            for i, item in enumerate(self.math_history):
                if item["role"] == "assistant":
                    del self.math_history[i]
                    break
            else:
                self.math_history.pop(0)
            total_length = sum(len(item["content"]) for item in self.math_history)
        print(f'cleaned chat history to {total_length}')

    async def clean_message(self, msg):
        self.messagehistory = []
        self.math_history = []
        await msg.reply(text='睦酱，已经死了……')
        
            

bot_instance = Ollamabot() 



@bot.group_event()
async def on_group_message(msg: GroupMessage):
    _log.info(msg)
    

    
    if msg.raw_message == '[CQ:at,qq=3832692983] 这个，不需要了。':
        a = 'D:/NapCat.32793.Shell/ncbot/break.png'
        tmp_message = MessageChain([Image(a)])
        await msg.reply(rtf=tmp_message)
        await bot_instance.clean_message(msg)
    elif "[CQ:at,qq=3832692983] 添加功能：" in msg.raw_message:
        
        data = [
    ["id", "content"],
    [1, msg.user_id],
    [2, msg.raw_message]
]
        with open('messages.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(data)
    elif (24 == random.randint(1, 30)):
        await bot._api.post_group_file(group_id=msg.group_id, image="un.png")
    elif msg.raw_message:
        await bot_instance.reply_message(msg)


@bot.private_event()
async def on_private_message(msg: PrivateMessage):
    _log.info(msg)
    if msg.raw_message == '这个，不需要了。':
        a = 'D:/NapCat.32793.Shell/ncbot/break.png'
        tmp_message = MessageChain([Image(a)])
        await msg.reply(rtf=tmp_message)
        await bot_instance.clean_message(msg)
    elif "[CQ:at,qq=3832692983] 添加功能：" in msg.raw_message:
        
        data = [
    ["id", "content"],
    [1, msg.user_id],
    [2, msg.raw_message]
]
        with open('messages.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(data)
    elif (24 == random.randint(1, 30)):
        await msg.reply(image="un.png")
    elif msg.raw_message:
        await bot_instance.reply_message(msg)


if __name__ == "__main__":

    bot.run()