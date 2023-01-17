# -*- coding: utf-8 -*-

import os

import discord
from discord import client
from discord.ext import commands
from discord.utils import get

import random
import requests
import time
import pprint
import itertools
import ast
import json
from collections import Counter

from googletrans import Translator
translator = Translator()

from saucenao_api import SauceNao
sn = SauceNao("YOUR_SAUCENAO_API_KEY_HERE")

import openai
openai.api_key = "YOUR_OPENAI_API_KEY_HERE"

intents = discord.Intents(messages=True, guilds=True)
intents.message_content = True
cmd_prefix = ["！", "!"]
bot = commands.Bot(command_prefix=cmd_prefix, intents=intents)


def extract_video_id(url):
    # Examples:
    # - http://youtu.be/SA2iWivDJiE
    # - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    # - http://www.youtube.com/embed/SA2iWivDJiE
    # - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    query = urlparse(url)
    if query.hostname == 'youtu.be': return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch': return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/embed/': return query.path.split('/')[2]
        if query.path[:3] == '/v/': return query.path.split('/')[2]
    # fail?
    return None

import re
def filter_special_chars(input_str):
    new_str = re.sub(r'[()\"@;:<>`+=~|{}\[\]]®「」【】—', "", input_str)
    return new_str


@bot.event
async def on_ready():
    print('Logged in as', bot.user.name, "({})".format(bot.user.id))
    print(time.ctime())
    print('------')

@bot.command(pass_context=True, aliases=['翻譯', 'trans', 'tr'])
async def reply_to_trans(ctx, *user_define_tup): 
    user_input = " ".join(list(user_define_tup)).strip() # 去掉頭尾的空格
    if not ctx.message.reference:
        await ctx.reply(":ng: 你沒有引用訊息")
    else:
        if ctx.message.reference.message_id is None:
            await ctx.reply(":ng: 找不到該引用的訊息")
        else:
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if not message:
                await ctx.reply(":ng: 你沒有引用訊息")
            else:
                print("before] {}".format(message.content))
                dest = user_input if len(user_input) > 0 else "zh-TW"
                if "日" in user_input or "jp" in user_input.lower():
                    dest = "ja"
                if "韓" in user_input or "kr" in user_input.lower() or "ko" in user_input.lower():
                    dest = "ko"
                if "英" in user_input or "en" in user_input.lower():
                    dest = "en"
                print("lang] {}".format(dest))
                trnas_str = translator.translate(message.content, dest=dest).text
                await ctx.reply("{}".format(trnas_str))


@bot.command(pass_context=True, aliases=['detect', 'lang'])
async def detect_lang(ctx): 
    if not ctx.message.reference:
        await ctx.reply(":ng: 你沒有引用訊息")
    else:
        if ctx.message.reference.message_id is None:
            await ctx.reply(":ng: 找不到該引用的訊息")
        else:
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if not message:
                await ctx.reply(":ng: 你沒有引用訊息")
            else:
                print("before] {}".format(message.content))
                trnas_str = translator.detect(message.content)
                await ctx.reply(":ok: 應該是：{}".format(trnas_str.lang))



@bot.command(pass_context=True, aliases=['TLDR', 'tldr', '太長'])
async def print_tldr(ctx, *, user_sentence: str):  
    max_tokens = user_sentence.strip()
    print("before] max_tokens: >{}<".format(max_tokens))
    
    if max_tokens.isdigit():
        max_tokens = int(max_tokens)
    else:
        max_tokens = 60
    
    print("after] max_tokens: ", max_tokens)
    if not ctx.message.reference:
        await ctx.reply(":ng: 你沒有引用訊息")
    else:
        if ctx.message.reference.message_id is None:
            await ctx.reply(":ng: 找不到該引用的訊息")
        else:
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if not message:
                await ctx.reply(":ng: 你沒有引用訊息")
            else:
                if len(message.content) > 100:
                    print("type-message.content: >{}<".format(type(message.content)))
                    print("message.content: >{}<".format(message.content))
                    print("len-message.content: >{}<".format(len(message.content)))
                    response = openai.Completion.create(
                      model="text-davinci-003",
                      prompt= message.content.replace("> ", "") + ".\n\nTl;dr",
                      temperature=0.7,
                      max_tokens=max_tokens,
                      top_p=1.0,
                      frequency_penalty=0.0,
                      presence_penalty=1
                    )
                    await ctx.reply(response["choices"][0]["text"].replace("\n", ""))
                else:
                    await ctx.reply(":ng: 你瞎了嗎，才幾個字不會自己看嗎😠")



@bot.command(pass_context=True, aliases=['talk', 't'])
async def talk_to_ai(ctx, *, user_sentence: str):  
    print("before] user_sentence: >{}<".format(user_sentence))
    if len(user_sentence) == 0:
        await ctx.reply(":ng: 工威啊😠")

    if len(user_sentence) < 300:
        response = openai.Completion.create(
          model="text-davinci-003",
          prompt= user_sentence + ".\n\nTl;dr",
          temperature=0.9,
          max_tokens=500,
          top_p=1.0,
          frequency_penalty=0.0,
          presence_penalty=0.6
        )
        await ctx.reply(response["choices"][0]["text"].replace("\n", ""))
    else:
        await ctx.reply(":ng: 你話太多了😠")


@bot.command(pass_context=True, aliases=['yt'])
async def get_youtube_thumbnails(ctx, *user_define_tup):
    print("user>> {}".format("".join(list(user_define_tup)))) 
    target_url = "".join(list(user_define_tup)).strip() 
    print(">>>>> {}".format(target_url)) 

    if "://" not in target_url:
        await ctx.reply(":ng: 你給的不是有效的網址(-`ェ´-╬)")
        return
    
    if "yout" not in target_url:
        await ctx.reply(":ng: 你給的不是youtube的網址(-`ェ´-╬)")
        return
    
    if len(target_url.split("://")) > 2: # 有2個以上的url混在裡面
        await ctx.reply(":ng: 一次給一個網址好嗎！(-`ェ´-╬)")
        return

    print("start to search")
    video_id = extract_video_id(target_url)
    print("youtube_id is {}".format(video_id))
    
    if video_id == None:
        await ctx.reply(":ng: 找不到這個影片捏！(-`ェ´-╬)")
    else:
        if len(video_id.split()) > 0: 
            img_template = "https://img.youtube.com/vi/XXX/maxresdefault.jpg"
            print(img_template.replace("XXX", video_id))
            embed = discord.Embed(title="你要的圖是不是這個 ( • ̀ω•́ )✧")
            embed.set_image(url=img_template.replace("XXX", video_id))            
            await ctx.reply(embed=embed)
        else:
            await ctx.reply(":ng: 找不到影片。")


@bot.command(pass_context=True, aliases=['幫我找', 'search'])
async def saucenao_find(ctx, *user_define_tup):
    print("user>> {}".format("".join(list(user_define_tup)))) 
    target_url = "".join(list(user_define_tup)).strip() 
    print(">>>>> {}".format(target_url)) 

    if "://" not in target_url:
        await ctx.reply(":ng: 你給的不是有效的網址(-`ェ´-╬)")
        return
    
    if len(target_url.split("://")) > 2: # 有2個以上的url混在裡面
        await ctx.reply(":ng: 前輩，一次給一個網址好嗎！(-`ェ´-╬)")
        return

    print("start to search")
    rstr = sn.from_url(target_url)
    best_score = rstr[0].similarity
    print(best_score)
    
    if best_score > 60:
        print(best_score)
        if len(rstr) > 0:
            urls_merged_str = " ".join(rstr[0].urls)
            has_dan_gel = ("danbooru" in urls_merged_str) or ("gelbooru" in urls_merged_str)
            print("Has Danbooru/Gelbooru:", has_dan_gel)
            if len(rstr[0].urls) > 0 and (not has_dan_gel):
                await ctx.reply(":ok: 你要找的是不是這個：||{}||".format(rstr[0].urls[0]))
            else: # 如果預設欄位都沒有，改看raw data
                if len(rstr[0].raw) > 0 and len(rstr[0].raw['data']) > 0:
                    pprint.pprint(rstr[0].raw)
                    if has_dan_gel:
                        if 'source' in rstr[0].raw['data']:
                            await ctx.reply(":ok: 你要找的是不是這個：||{}||".format(rstr[0].raw['data']['source']))
                    else: # URL does not contains Danbooru/Gelbooru
                        if 'jp_name' in rstr[0].raw['data'] and rstr[0].raw['data']['jp_name'] != None:
                            await ctx.reply(":ok: 你要找的是不是這個：||{}||".format(rstr[0].raw['data']['jp_name']))
                        elif 'eng_name' in rstr[0].raw['data'] and rstr[0].raw['data']['eng_name'] != None:
                            await ctx.reply(":ok: 你要找的是不是這個：||{}||".format(rstr[0].raw['data']['eng_name']))
                        else:
                            pretty_str = pprint.pformat(rstr[0].raw)
                            await ctx.reply("資料怪怪的，全部給你：```{}```".format(pretty_str))
                else:
                    await ctx.send(":ng: ERROR *(json-format is wrong)*")
        else:
            await ctx.reply(":ng: Err: sim too low")
    else:
        await ctx.reply(":ng: Err: sim too low")


@bot.command(pass_context=True, aliases=['dice'])
async def roll_dice(ctx):
    await ctx.send("喀啦~ 喀啦~ 你的骰子滾著滾著，停在 __**{}**__ 點！:game_die: ".format(random.sample(list(range(1, 7)), 1)[0]))


bot.run('YOUR_DISCORD_BOT_API_KEY_HERE')