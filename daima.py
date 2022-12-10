import asyncio
import base64
from distutils.command.build import build
from email import message
import os
import random
from re import M, T, match
import re
import sqlite3
from datetime import datetime, timedelta
from io import SEEK_CUR, BytesIO
from tokenize import group
from winsound import PlaySound
from xmlrpc.client import TRANSPORT_ERROR
from PIL import Image
#如果你能欣赏一下这个石山代码的话，应该能看到我下面的留言~（这也许会解答一些你觉得很疑惑的地方，比如狼人杀没有狼人）

from httpx import AsyncByteStream
from hoshino import Service, priv
from hoshino.typing import CQEvent, CommandSession, CQHttpError
from hoshino.util import DailyNumberLimiter
import copy
import json
import math
import pytz
import nonebot
from nonebot import on_command, on_request
from hoshino import sucmd
from nonebot import get_bot
from hoshino.typing import NoticeSession

DB_PATH = os.path.expanduser('~/.q2bot/langrensha.db')
file_path = 'C:/Users/yun/.q2bot/langrensha.db'
            
# 创建DB数据
class dbnum:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._create_sysnum()
        
        

    def _connect(self):
        return sqlite3.connect(DB_PATH)

    def _create_sysnum(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS SYSNUM
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           NUM1            INT    NOT  NULL,
                           NUM2           INT    NOT NULL,
                           PRIMARY KEY(GID, UID, NUM1));''')
        except:
            raise Exception('创建表发生错误')
    def _set_sysnum(self, gid, uid, num1, num2):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO SYSNUM (GID, UID, NUM1, NUM2) VALUES (?, ?, ?, ?)",
                (gid, uid, num1, num2,),
            )
    def _get_sysnum(self, gid, uid, num1):
        try:
            r = self._connect().execute("SELECT NUM2 FROM SYSNUM WHERE GID=? AND UID=? AND NUM1=?", (gid, uid, num1)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找表发生错误')
    def _add_sysnum(self, gid, uid, num1, num2):
        num = self._get_sysnum(gid, uid, num1)
        if num == None:
            num = 0
        num += num2
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO SYSNUM (GID, UID, NUM1, NUM2) VALUES (?, ?, ?, ?)",
                (gid, uid, num1, num),
            )
    def _reduce_sysnum(self, gid, uid, num1, num2):
        num = self._get_sysnum(gid, uid, num1)
        num -= num2
        num = max(num,0)
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO SYSNUM (GID, UID, NUM1, NUM2) VALUES (?, ?, ?, ?)",
                (gid, uid, num1, num),
            )

#获取列表
    def _get_uid_list(self, gid):
        try:
            r = self._connect().execute("SELECT DISTINCT(UID) FROM SYSNUM WHERE GID=? ", (gid,)).fetchall()
            return [u[0] for u in r] if r else {}
        except:
            raise Exception('查找uid表发生错误')

DB_PATH2 = os.path.expanduser('~/.q2bot/chouka.db')

# 创建DB数据
class chouka:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH2), exist_ok=True)
        self._create_shitou()
        

    def _connect(self):
        return sqlite3.connect(DB_PATH2)

#母猪石数量
    def _create_shitou(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS SHITOU
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           SHITOU           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建表发生错误')
    def _set_shitou(self, gid, uid, shitou):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO SHITOU (GID, UID, SHITOU) VALUES (?, ?, ?)",
                (gid, uid, shitou,),
            )

    def _get_shitou(self, gid, uid):
        try:
            r = self._connect().execute("SELECT SHITOU FROM SHITOU WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找表发生错误')

    def _add_shitou(self, gid, uid, num):
        num1 = self._get_shitou(gid, uid)
        if num1 == None:
            num1 = 0
        num1 += num
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO SHITOU (GID, UID, SHITOU) VALUES (?, ?, ?)",
                (gid, uid, num1),
            )

    def _reduce_shitou(self, gid, uid, num):
        msg1 = self._get_shitou(gid, uid)
        msg1 -= num
        msg1 = max(msg1,0)
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO SHITOU (GID, UID, SHITOU) VALUES (?, ?, ?)",
                (gid, uid, msg1),
            )



sv = Service('wolfkick', enable_on_default=True)

@on_command('在吗')
async def zaima(session: CommandSession):
    bot = nonebot.get_bot()
    user = session.event.user_id
    await bot.send_private_msg(user_id=user, message='嗨！')  #为测试指令，目的于检查玩家是否可以私聊机器人（如果无法私聊请让他加好友）

@sv.on_command('在吗？')
async def haogan(session: CommandSession):
    bot = nonebot.get_bot()
    user = session.event.user_id
    gid = session.event.group_id

    await bot.send_group_msg(group_id=gid, message=f'嗨！') #at_sender没有用！！#为另一个测试指令，检查机器人是否可以在群里发送信息

@sv.on_fullmatch(['加入游戏狼人杀'])
async def start(bot,ev:CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    nm = dbnum()
    if nm._get_sysnum(gid,uid,2) !=0:
        await bot.finish(ev,'你已加入游戏',at_sender=True)
    if nm._get_sysnum(gid,0,1) ==1:
        await bot.finish(ev,'游戏已开始，请等待下一盘',at_sender=True)
    if nm._get_sysnum(0,uid,12) !=0:
        await bot.finish(ev,'你已经在其他群聊加入游戏，若需加入本群请先在另一边<退出游戏狼人杀>')
    nm._set_sysnum(gid,uid,2,1) #设置为加入游戏
    nm._add_sysnum(gid,0,3,1) #房间人数+1
    nm._set_sysnum(0,uid,12,gid) #绑定群聊
    ready_player_num = nm._get_sysnum(gid,0,3) #获取一下房间人数
    nm._set_sysnum(gid,uid,4,ready_player_num)  #存储玩家编号
    nm._set_sysnum(gid,ready_player_num,5,uid) #存储编号对应的玩家qq号
    await bot.send(ev,f'加入成功({ready_player_num}/5)',at_sender=True)
    while nm._get_sysnum(gid,uid,2) ==1 and nm._get_sysnum(gid,0,1) ==0: #循环检测玩家游戏状态是
        await asyncio.sleep(1)                                          #否为1以及群游戏开关是否为0
    if nm._get_sysnum(gid,uid,2) ==0: #玩家游戏状态为0，判断退出游戏
        nm._reduce_sysnum(gid,0,3,1)  #房间人数-1
        nm._set_sysnum(gid,uid,4,0)  #清除玩家编号
        nm._set_sysnum(gid,ready_player_num,5,0) #清除编号对应的玩家qq号
        nm._set_sysnum(0,uid,12,0) #解绑群聊
        while True: #后续加入玩家编号前移循环
            ready_player_num += 1
            player_uid = nm._get_sysnum(gid,ready_player_num,5) #获取uid
            if player_uid != 0: #非0判定
                ready_player_num_1 = ready_player_num - 1 #前移
                nm._set_sysnum(gid,player_uid,4,ready_player_num_1) #写入新玩家编号
                nm._set_sysnum(gid,ready_player_num_1,5,player_uid) #写入新的编号对应玩家QQ号
                nm._set_sysnum(gid,ready_player_num,5,0) #移动完后清除方便下一次写入
            else: #但获取到了0
                break #跳出循环
        ready_player_num = nm._get_sysnum(gid,0,3)
        await bot.finish(ev,f'退出成功({ready_player_num}/5)',at_sender=True)
    await asyncio.sleep(30)  #如果运行到这个代码说明游戏开了
    
        


@sv.on_fullmatch(['身份介绍狼人杀'])
async def jieshao(bot,ev):
    msg = '''狼人杀身份介绍：
    平民：没有任何能力，可在黄昏投票
    纵火者：夜晚角色，使用纵火烧死玩家，无法被女巫救，可在黄昏投票
    先知：夜晚角色，可以查询玩家身份，可在黄昏投票
    信仰者：黄昏角色，被处决后胜利，可在黄昏投票，
    女巫：夜晚角色，使用药水毒害玩家，可在黄昏投票'''
    await bot.send(ev,msg)

#当初在写这个插件的时候，没有群聊愿意来测试，觉得非常浪费时间...因此这个插件从写完到现在，没有做过任何的运行测试！！任何的！！！
#然后插件就这样一直被埋没了，直到10个月之后的2022年11月2日，机器人宣布停止服务，卷服跑路，这个插件都没有真正意义上的运行过
#要是你有幸看到这里我留下的注释，我会很开心！你愿意尝试来观赏这个代码❤
#很多东西其实都是很混乱的，我记忆代码除了备注外，还借助到了只有我自己能看得懂的list.json
#这个玩意放在同目录下了，要是你能看得懂的话...这个是记录数据库中每个个位数uid的真实作用
#狼人杀现在并没有狼人，只有一个纵火者，所以应该叫火人杀？（狼人和纵火者最大的区别是，狼人杀人后女巫可救，纵火者杀人后女巫不可救（其实省了一大堆代码））
#其他的角色是齐全的，甚至呢在里面加入了一个自创角色 信仰者
#
        
@sv.on_fullmatch(['退出游戏狼人杀'])
async def start(bot,ev:CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    nm = dbnum()
    if nm._get_sysnum(gid,0,1) ==1:
        await bot.finish(ev,'游戏已开始，无法退出')
    nm._set_sysnum(gid,uid,2,0)

@sv.on_command('开始游戏狼人杀')
async def start(session: CommandSession):
    bot = nonebot.get_bot()
    gid = session.event.group_id
    nm = dbnum()
    if nm._get_sysnum(gid,0,1) ==1:  #开始游戏后再发出开始游戏指令不会响应
        return 0
    if nm._get_sysnum(gid,0,3) <5:  
        await bot.send_group_msg(group_id=gid,message='人数不足，至少需要5人')
        return 0
    nm._set_sysnum(gid,0,1,1) #游戏开始
    player_num = nm._get_sysnum(gid,0,3) #获取房间人数
    #身份卡分配阶段
    sf_1 = random.randint(0,player_num) #设置身份为1的身份编号
    sf_2 = random.randint(0,player_num)
    while sf_1 == sf_2: #初始化身份为2的身份编号，并与身份为1的身份编号校验，一样则进入循环重分配
        sf_2 = random.randint(0,player_num)
    sf_3 = random.randint(0,8)
    while sf_1 == sf_3 or sf_2 == sf_3: #与身份1和身份2校验，若其中任何一个一样则重分配
        sf_3 = random.randint(0,8)
    sf_4 = random.randint(0,player_num)
    while sf_1 == sf_4 or sf_2 == sf_4 or sf_3 == sf_4:
        sf_4 = random.randint(0,player_num)
    #身份卡载入阶段
    uid_player_get1 = nm._get_sysnum(gid,sf_1,5)  #读取编号对应QQ
    uid_player_get2 = nm._get_sysnum(gid,sf_2,5)  
    uid_player_get3 = nm._get_sysnum(gid,sf_3,5)  
    uid_player_get4 = nm._get_sysnum(gid,sf_4,5)  
    nm._set_sysnum(gid,uid_player_get1,6,1)  #赋予身份
    nm._set_sysnum(gid,uid_player_get2,6,2)
    nm._set_sysnum(gid,uid_player_get3,6,3)
    nm._set_sysnum(gid,uid_player_get4,6,4)
    #记录身份QQ号，以方便胜负判定时检查以及后续运行
    fire_player = uid_player_get1
    wife_player = uid_player_get2
    know_player = uid_player_get3
    god_player = uid_player_get4    #虽然是多此一举，但是这个变量名好记多了hhh
    #阶段：30秒准备时间
    await bot.send_group_msg(group_id=gid,message='身份卡分配完成！请各位私聊输入<获取身份>来检视，30秒后天黑！')
    await asyncio.sleep(30)
    #阶段：正式游戏阶段
    nm._set_sysnum(gid,0,7,0)   #修改时间为晚上
    game_round = 1  #设置为第一回合
    while nm._get_sysnum(gid,0,1) ==1: #只要游戏处于运行状态，循环一直保持
        #阶段1：进行游戏胜负判定
        #结局1：纵火者失败（条件：纵火者死亡）
        if nm._get_sysnum(gid,fire_player,2) ==2:  #检测到纵火者游戏状态为2（死亡）
            uid_player_list = nm._get_uid_list(gid)  #获取玩家列表
            msg = '游戏结束：纵火者得到了制裁！'
            for a in range(len(uid_player_list)):   #循环生成玩家数据
                uid_list = int(uid_player_list[a])
                msg += f'\n[CQ:at,qq={uid_list}]  '
                #获取玩家身份
                player_sf = nm._get_sysnum(gid,uid_list,6)   
                if player_sf ==0:
                    msg += '平民 (胜利)'
                elif player_sf ==1:
                    msg += '纵火者 (失败)'
                elif player_sf ==2:
                    msg += '女巫 (胜利)'
                elif player_sf ==3:
                    msg += '先知 (胜利)'
                elif player_sf ==4:
                    msg += '信仰者 (失败)'
                else:                   #鬼知道会不会出问题
                    msg += '[获取身份时发生错误] (?)'
                #身份获取完成后复位他的身份
                nm._set_sysnum(gid,uid_list,6,0)
                msg += '  '
                #获取玩家状态
                player_zt = nm._get_sysnum(gid,uid_list,2)
                if player_zt ==1:
                    msg += '存活'
                elif player_zt ==2:
                    msg += '死亡'
                else:
                    msg += '[获取状态时发生错误]'
                #状态获取完成后复位他的状态
                nm._set_sysnum(gid,uid_list,2,0)
                #解绑群聊
                nm._set_sysnum(0,uid_list,12,0)
            #发送消息
            await bot.send_group_msg(group_id=gid,message=msg)
            player_num +=1
            for b in range(player_num):
                nm._set_sysnum(gid,b,5,0) #清除存档QQ号
            nm._set_sysnum(gid,0,7,0) #进度复位
            nm._set_sysnum(gid,0,1,0) #关闭游戏
            return 0
        #结局2：信仰者被票（条件：信仰者被黄昏公投处决）
        if nm._get_sysnum(gid,0,8) == god_player:  #获取到处决QQ号与信仰者QQ号一致触发
            uid_player_list = nm._get_uid_list(gid)  #获取玩家列表
            msg = '游戏结束：无知的无信仰者，毁灭吧！我将带着光明，拯救世界！'
            for a in range(len(uid_player_list)):   #循环生成玩家数据
                uid_list = int(uid_player_list[a])
                msg += f'\n[CQ:at,qq={uid_list}]  '
                #获取玩家身份
                player_sf = nm._get_sysnum(gid,uid_list,6)   
                if player_sf ==0:
                    msg += '平民 (失败)'
                    nm._set_sysnum(gid,uid_list,2,2)  #炸死了
                elif player_sf ==1:
                    msg += '纵火者 (失败)'
                    nm._set_sysnum(gid,uid_list,2,2)
                elif player_sf ==2:
                    msg += '女巫 (失败)'
                    nm._set_sysnum(gid,uid_list,2,2)
                elif player_sf ==3:
                    msg += '先知 (失败)'
                    nm._set_sysnum(gid,uid_list,2,2)
                elif player_sf ==4:
                    msg += '信仰者 (胜利)'
                else:                   #鬼知道会不会出问题
                    msg += '[获取身份时发生错误] (?)'
                    nm._set_sysnum(gid,uid_list,2,2)
                #身份获取完成后复位他的身份
                nm._set_sysnum(gid,uid_list,6,0)
                msg += '  '
                #获取玩家状态
                player_zt = nm._get_sysnum(gid,uid_list,2)
                if player_zt ==1:
                    msg += '存活'
                elif player_zt ==2:
                    msg += '死亡'
                else:
                    msg += '[获取状态时发生错误]'
                #状态获取完成后复位他的状态
                nm._set_sysnum(gid,uid_list,2,0)
                #解绑群聊
                nm._set_sysnum(0,uid_list,12,0)
            #发送消息
            await bot.send_group_msg(group_id=gid,message=msg)
            player_num +=1
            for b in range(player_num):
                nm._set_sysnum(gid,b,5,0) #清除存档QQ号
            nm._set_sysnum(gid,0,7,0) #进度复位
            nm._set_sysnum(gid,0,1,0) #关闭游戏
            return 0
        #结局3：纵火者存活 （条件：当房间游戏人数只剩下2人且纵火者身份玩家仍然存活）
        if nm._get_sysnum(gid,0,3) ==2 and nm._get_sysnum(gid,fire_player,2) ==1:
            uid_player_list = nm._get_uid_list(gid)  #获取玩家列表
            msg = '游戏结束：纵火者胜利！这一届村民不行啊~'
            for a in range(len(uid_player_list)):       #循环生成玩家数据
                uid_list = int(uid_player_list[a])
                msg += f'\n[CQ:at,qq={uid_list}]  '
                #获取玩家身份
                player_sf = nm._get_sysnum(gid,uid_list,6)   
                if player_sf ==0:
                    msg += '平民 (失败)'
                elif player_sf ==1:
                    msg += '纵火者 (胜利)'
                elif player_sf ==2:
                    msg += '女巫 (失败)'
                elif player_sf ==3:
                    msg += '先知 (失败)'
                elif player_sf ==4:
                    msg += '信仰者 (失败)'
                else:                   #鬼知道会不会出问题
                    msg += '[获取身份时发生错误] (?)'
                #身份获取完成后复位他的身份
                nm._set_sysnum(gid,uid_list,6,0)
                msg += '  '
                #获取玩家状态
                player_zt = nm._get_sysnum(gid,uid_list,2)
                if player_zt ==1:
                    msg += '存活'
                elif player_zt ==2:
                    msg += '死亡'
                else:
                    msg += '[获取状态时发生错误]'
                #状态获取完成后复位他的状态
                nm._set_sysnum(gid,uid_list,2,0)
                #解绑群聊
                nm._set_sysnum(0,uid_list,12,0)
            #发送消息
            await bot.send_group_msg(group_id=gid,message=msg)
            player_num +=1
            for b in range(player_num):
                nm._set_sysnum(gid,b,5,0) #清除存档QQ号
            nm._set_sysnum(gid,0,7,0) #进度复位
            nm._set_sysnum(gid,0,1,0) #关闭游戏
            return 0
        #结局4：平局（条件：游戏回合数达到10）
        if game_round >=10:
            uid_player_list = nm._get_uid_list(gid)  #获取玩家列表
            msg = '游戏结束：天道累了，强行关闭了游戏(游戏回合达到10)'
            for a in range(len(uid_player_list)):   #循环生成玩家数据
                uid_list = int(uid_player_list[a])
                msg += f'\n[CQ:at,qq={uid_list}]  '
                #获取玩家身份
                player_sf = nm._get_sysnum(gid,uid_list,6)   
                if player_sf ==0:
                    msg += '平民'
                elif player_sf ==1:
                    msg += '纵火者'
                elif player_sf ==2:
                    msg += '女巫'
                elif player_sf ==3:
                    msg += '先知'
                elif player_sf ==4:
                    msg += '信仰者'
                else:                   #鬼知道会不会出问题
                    msg += '[获取身份时发生错误]'
                #身份获取完成后复位他的身份
                nm._set_sysnum(gid,uid_list,6,0)
                msg += '  '
                #获取玩家状态
                player_zt = nm._get_sysnum(gid,uid_list,2)
                if player_zt ==1:
                    msg += '存活'
                elif player_zt ==2:
                    msg += '死亡'
                else:
                    msg += '[获取状态时发生错误]'
                #状态获取完成后复位他的状态
                nm._set_sysnum(gid,uid_list,2,0)
                #解绑群聊
                nm._set_sysnum(0,uid_list,12,0)
            #发送消息
            await bot.send_group_msg(group_id=gid,message=msg)
            player_num +=1
            for b in range(player_num):
                nm._set_sysnum(gid,b,5,0) #清除存档QQ号
            nm._set_sysnum(gid,0,7,0) #进度复位
            nm._set_sysnum(gid,0,1,0) #关闭游戏
            return 0
        #阶段2：晚上
        while nm._get_sysnum(gid,0,7) ==0:  #检测时间是否处于白天
            uid_player_list = nm._get_uid_list(gid)  #获取玩家列表
            msg = '夜晚降临，人们生活在恐惧之中，今晚居然长达<我也不知道>秒！（持有角色牌玩家可输入不存在的序号来放弃）'
            b = 0
            for a in range(len(uid_player_list)):       #获取玩家状态
                uid_list = int(uid_player_list[a])
                b +=1
                msg += f'\n{b}、[CQ:at,qq={uid_list}]  '
                player_zt = nm._get_sysnum(gid,uid_list,2)
                if player_zt ==1:
                    msg += '存活'
                elif player_zt ==2:
                    msg += '死亡'
                else:
                    msg += '[获取状态时发生错误]'
            await bot.send_group_msg(group_id=gid,message=msg)
            await bot.set_group_whole_ban(group_id=gid,enable=True) #开启全体禁言
            await asyncio.sleep(2)
            #纵火者操作
            nm._set_sysnum(gid,1,9,0)
            nm._set_sysnum(gid,1,10,0)
            await bot.send_private_msg(user_id=fire_player,message='烧谁<烧 [序号]>')
            user_time = 0
            while nm._get_sysnum(gid,1,9) ==0 and user_time <=19:
                await asyncio.sleep(1)
                user_time +=1
            if user_time ==20:
                await bot.send_private_msg(user_id=fire_player,message='操作超时')
            #女巫操作
            nm._set_sysnum(gid,2,9,0)
            nm._set_sysnum(gid,2,10,0)
            await bot.send_private_msg(user_id=wife_player,message='毒谁<毒 [序号]>')
            user_time = 0
            while nm._get_sysnum(gid,2,9) ==0 and user_time <=19:
                await asyncio.sleep(1)
                user_time +=1
            if user_time ==20:
                await bot.send_private_msg(user_id=wife_player,message='操作超时')
            #先知操作
            nm._set_sysnum(gid,3,9,0)
            nm._set_sysnum(gid,3,10,0)
            await bot.send_private_msg(user_id=know_player,message='查谁<查 [序号]>')
            user_time = 0
            while nm._get_sysnum(gid,3,9) ==0 and user_time <=19:
                await asyncio.sleep(1)
                user_time +=1
            if user_time ==20:
                await bot.send_private_msg(user_id=know_player,message='操作超时')
            #夜晚行动角色完成操作
            nm._set_sysnum(gid,0,7,1)   #设置游戏为白天
            break
        #阶段3：白天
        while nm._get_sysnum(gid,0,7) ==1:  #检测时间是否处于白天
            await bot.send_group_msg(group_id=gid,message='天亮了...')
            await asyncio.sleep(2)
            await bot.set_group_whole_ban(group_id=gid,enable=False)    #关闭全体禁言
            #运行夜晚角色的操作
            msg = '今日新闻：'
            kill_fire = nm._get_sysnum(gid,1,10) #获取纵火者操作编号
            if kill_fire !=0:   #如果获取到的不是0
                kill_player = nm._get_sysnum(gid,kill_fire,5) #获取qq号
                if nm._get_sysnum(gid,kill_player,2) ==1: #侦测需要击杀的玩家是否已经死亡
                    nm._set_sysnum(gid,kill_player,2,2) #设置被动作玩家死亡
                    nm._reduce_sysnum(gid,0,3,1) #房间人数-1
                    msg += f'\n震惊！昨日晚上[CQ:at,qq={kill_player}]家燃起了熊熊大火！'
                else: #如果死亡了
                    kill_fire =0    #你的玩家搁着鞭尸呢
            nm._set_sysnum(gid,1,9,1) #覆盖当前角色已经使用技能的操作（防止玩家使用角色指令后并未成功写入数据库中
            kill_wife = nm._get_sysnum(gid,2,10) #获取女巫操作编号
            if kill_wife !=0:
                kill_player = nm._get_sysnum(gid,kill_wife,5)
                if nm._get_sysnum(gid,kill_player,2) ==1: #侦测需要击杀的玩家是否已经死亡
                    nm._set_sysnum(gid,kill_player,2,2) #设置被动作玩家死亡
                    nm._reduce_sysnum(gid,0,3,1) #房间人数-1
                    msg += f'\n太可怕了！[CQ:at,qq={kill_player}]死了，有人在ta家中发现了药水痕迹！'
                else: #如果死亡了
                    kill_wife =0
            nm._set_sysnum(gid,2,9,1)
            nm._set_sysnum(gid,3,9,1)
            if kill_wife ==0 and kill_fire ==0: #两个都没动作
                msg += '\n昨日平安无事。'
            await bot.send_group_msg(group_id=gid,message=msg)
            await asyncio.sleep(2)
            #开始讨论
            await bot.send_group_msg(group_id=gid,message='开始自由讨论，时长<60>秒~')
            await asyncio.sleep(60)
            #结束讨论
            nm._set_sysnum(gid,0,7,2) 
            break
        #阶段4：黄昏
        while nm._get_sysnum(gid,0,7) ==2:  #检测时间是否处于黄昏
            #开始投票
            uid_player_list = nm._get_uid_list(gid)  #获取玩家列表
            msg = '黄昏将至，全民公投！请在<30>秒内私聊使用<投 [序号]>投票吧！（可以输入不存在的序号放弃投票）'
            b = 0
            for a in range(len(uid_player_list)):       #列出玩家状态
                uid_list = int(uid_player_list[a])
                b +=1
                msg += f'\n{b}、[CQ:at,qq={uid_list}]  '
                player_zt = nm._get_sysnum(gid,uid_list,2)
                if player_zt ==1:
                    msg += '存活'
                elif player_zt ==2:
                    msg += '死亡'
                else:
                    msg += '[获取状态时发生错误]'
            await bot.send_group_msg(group_id=gid,message=msg)
            await asyncio.sleep(30)
            #统计票数
            msg = '投票结束！'
            uid_player_list = nm._get_uid_list(gid)  #获取玩家列表
            kill_ps = 0  #初始化最高票数
            nm._set_sysnum(gid,0,8,0) #初始化处决玩家
            b = 0
            for a in range(len(uid_player_list)):  #循环获取玩家票数并判断最高
                uid_list = int(uid_player_list[a])
                player_bh = nm._get_sysnum(gid,uid_list,4)
                b +=1
                player_ps = nm._get_sysnum(gid,player_bh,11)
                if player_ps !=0:
                    msg += f'\n{b}、[CQ:at,qq={uid_list}]  '
                    msg += f'票数：{player_ps}'
                if player_ps > kill_ps:  #判定最高票数
                    kill_ps = player_ps
                    nm._set_sysnum(gid,0,8,uid_list)
                if player_ps == kill_ps: #判定相同票数
                    nm._set_sysnum(gid,0,8,0)
            await bot.send_group_msg(group_id=gid,message=msg)
            await asyncio.sleep(2)
            #开始处决
            kill_player = nm._get_sysnum(gid,0,8)   #获取需要处决的玩家QQ号
            if kill_player !=0:
                nm._set_sysnum(gid,kill_player,2,2) #设置玩家状态为死亡
                nm._reduce_sysnum(gid,0,3,1) #房间人数-1
                msg = f'[CQ:at,qq={kill_player}]被处决了！'
            else:
                msg = '你们没能达成一致，天道失望的离开了...'
            await bot.send_group_msg(group_id=gid,message=msg)
            #结束处决
            nm._set_sysnum(gid,0,7,0) #进入晚上
            game_round +=1  #+1个回合
            await asyncio.sleep(2)
            break

@on_command('烧')
async def zaima(session: CommandSession):
    bot = nonebot.get_bot()
    uid = session.event.user_id
    nm = dbnum()
    gid = nm._get_sysnum(0,uid,12)
    if nm._get_sysnum(gid,0,7) !=0: #不在天黑
        return 0
    if nm._get_sysnum(gid,1,9) ==1: #已操作
        return 0
    if nm._get_sysnum(gid,0,1) ==0: #如果游戏没开始就无视这个指令
        return 0
    if nm._get_sysnum(gid,uid,2) !=1: #玩家不是已加入游戏状态
        return 0    #你问我为什么不把这些条件使用 or 合并起来？这样分开来我好备注，不然糊在一起了
    id = session.current_arg_text.strip()
    if not id:
        await bot.send_private_msg(user_id=uid, message='在命令后加id')
    id = int(id)  
    kill_player = nm._get_sysnum(gid,id,5) #先获取一下被杀玩家qq
    if kill_player !=0:  #如果存在
        nm._set_sysnum(gid,1,9,1) #更变为已操作
        nm._set_sysnum(gid,1,10,id) #存储操作编号
        await bot.send_private_msg(user_id=uid, message='OK')
    else: #如果不存在
        nm._set_sysnum(gid,1,9,1)
        await bot.send_private_msg(user_id=uid, message='你放弃了')
        
@on_command('毒')
async def zaima(session: CommandSession):
    bot = nonebot.get_bot()
    uid = session.event.user_id
    nm = dbnum()
    gid = nm._get_sysnum(0,uid,12)
    if nm._get_sysnum(gid,0,7) !=0: #不在天黑
        return 0
    if nm._get_sysnum(gid,2,9) ==1: #已操作
        return 0
    if nm._get_sysnum(gid,0,1) ==0: #如果游戏没开始就无视这个指令
        return 0
    if nm._get_sysnum(gid,uid,2) !=1: #玩家不是已加入游戏状态
        return 0
    id = session.current_arg_text.strip()
    if not id:
        await bot.send_private_msg(user_id=uid, message='在命令后加id')
    id = int(id)  
    kill_player = nm._get_sysnum(gid,id,5) #先获取一下被杀玩家qq
    if kill_player !=0:  #如果存在
        nm._set_sysnum(gid,2,9,1) #更变为已操作
        nm._set_sysnum(gid,2,10,id) #存储操作编号
        await bot.send_private_msg(user_id=uid, message='OK')
    else: #如果不存在
        nm._set_sysnum(gid,2,9,1)
        await bot.send_private_msg(user_id=uid, message='你放弃了')

@on_command('查')
async def zaima(session: CommandSession):
    bot = nonebot.get_bot()
    uid = session.event.user_id
    nm = dbnum()
    gid = nm._get_sysnum(0,uid,12)
    if nm._get_sysnum(gid,0,7) !=0: #不在天黑
        return 0
    if nm._get_sysnum(gid,3,9) ==1: #已操作
        return 0
    if nm._get_sysnum(gid,0,1) ==0: #如果游戏没开始就无视这个指令
        return 0
    if nm._get_sysnum(gid,uid,2) !=1: #玩家不是已加入游戏状态
        return 0
    id = session.current_arg_text.strip()
    if not id:
        await bot.send_private_msg(user_id=uid, message='在命令后加id')
    id = int(id)  
    know_player = nm._get_sysnum(gid,id,5) #先获取一下被查玩家qq
    if know_player !=0:  #如果存在
        nm._set_sysnum(gid,3,9,1) #更变为已操作
        msg='他的身份是：'
        player_sf = nm._get_sysnum(gid,know_player,6)
        if player_sf ==0:
            msg += '平民'
        elif player_sf ==1:
            msg += '纵火者'
        elif player_sf ==2:
            msg += '女巫'
        elif player_sf ==3:
            msg += '先知'
        elif player_sf ==4:
            msg += '信仰者'
        else:                   #鬼知道会不会出问题
            msg += '[获取身份时发生错误]'
        await bot.send_private_msg(user_id=uid, message=msg)
    else: #如果不存在
        nm._set_sysnum(gid,3,9,1)
        await bot.send_private_msg(user_id=uid, message='你放弃了')

@on_command('投')
async def zaima(session: CommandSession):
    bot = nonebot.get_bot()
    uid = session.event.user_id
    nm = dbnum()
    gid = nm._get_sysnum(0,uid,12)
    if nm._get_sysnum(gid,0,7) !=2: #不在黄昏
        return 0
    if nm._get_sysnum(gid,uid,9) ==1: #已操作
        return 0
    if nm._get_sysnum(gid,0,1) ==0: #如果游戏没开始就无视这个指令
        return 0
    if nm._get_sysnum(gid,uid,2) !=1: #玩家不是已加入游戏状态
        return 0
    id = session.current_arg_text.strip()
    if not id:
        await bot.send_private_msg(user_id=uid, message='在命令后加id')
    id = int(id)  
    kill_player = nm._get_sysnum(gid,id,5) #先获取一下被投玩家qq
    if kill_player !=0:  #如果存在
        nm._set_sysnum(gid,uid,9,1) #更变为已操作
        nm._add_sysnum(gid,id,11,1) #存储操作编号
        await bot.send_private_msg(user_id=uid, message='OK')
        await asyncio.sleep(60)  #60秒后重置（应该进入天黑了）
        nm._set_sysnum(gid,uid,9,0)
        nm._reduce_sysnum(gid,id,11,1)
    else: #如果不存在
        nm._set_sysnum(gid,uid,9,1)
        await bot.send_private_msg(user_id=uid, message='你放弃了')
        await asyncio.sleep(60)  #60秒后重置（应该进入天黑了）
        nm._set_sysnum(gid,uid,9,0)


@on_command('获取身份')
async def zaima(session: CommandSession):
    bot = nonebot.get_bot()
    uid = session.event.user_id
    nm = dbnum()
    gid = nm._get_sysnum(0,uid,12)
    if nm._get_sysnum(gid,0,1) ==0: #如果游戏没开始就无视这个指令
        return 0
    if nm._get_sysnum(gid,uid,2) !=1: #玩家不是已加入游戏状态
        return 0
    msg=''
    player_sf = nm._get_sysnum(gid,uid,6)
    if player_sf ==0:
        msg += '平民'
    elif player_sf ==1:
        msg += '纵火者'
    elif player_sf ==2:
        msg += '女巫'
    elif player_sf ==3:
        msg += '先知'
    elif player_sf ==4:
        msg += '信仰者'
    else:                   #鬼知道会不会出问题
        msg += '[获取身份时发生错误]'
    await bot.send_private_msg(user_id=uid, message=msg)




    