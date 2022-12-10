# 狼人杀
注意：功能只适用于HoshinoBot，并未在NoneBot和NoneBot2中进行测试！

## 简介
这是一个大型娱乐功能，如名字，一个经典的猜测游戏狼人杀

## 指令
| 触发指令 | 需要等级 | 指令作用 |

| 在吗 | 私聊 | 检查群员是否能正常与机器人私聊（为了防止冻结，机器人默认关闭陌生人私聊） |

| 在吗？ | 群聊 | 检查机器人是否能正常在群内发送信息（问号为中文符号） |

| 加入游戏狼人杀 | 群聊 | 加入你所在群的狼人杀游戏 |

| 身份介绍狼人杀 | 群聊 | 查看目前载入的游戏角色 |

| 退出游戏狼人杀 | 群聊 | 退出你所在群的狼人杀游戏 |

| 开始游戏狼人杀 | 群聊 | 开启你所在群的狼人杀游戏 |

| 烧+序号 | 私聊 | 角色纵火者技能指令 |

| 毒+序号 | 私聊 | 角色女巫技能指令 |

| 查+序号 | 私聊 | 角色先知技能指令 |

| 投+序号 | 私聊 | 在黄昏阶段全民公投指令 |

| 获取身份 | 私聊 | 获取你的身份 |

## 部署教程：
1.下载或git clone本插件：

在 HoshinoBot\hoshino\modules 目录下使用以下命令拉取本项目

git clone https://github.com/daycold1000/wolfkill

2.启用：

在 HoshinoBot\hoshino\config\ **bot**.py 文件的 MODULES_ON 加入 'wolfkill'

然后重启 HoshinoBot

## 多余的代码
原为了下一个计划更新，在尝试加入货币功能，但最后并未加入，因此可以把96~151行代码删除

留存下来主要是为了纪念

## 已知的bug
1、在群成员加入游戏后，如果未使用退出游戏命令，或者群游戏已开始后没有正常结束（诸如机器人主人不小心关闭了命令窗口、服务器意外停电蓝屏等），会导致群成员无法再次加入游戏以及正常开始游戏

目前的普通解决方案：找到并删除C:/users/你的用户名/.q2bot/langrensha.db（注意，务必确保你已经发生了这个bug，一旦删除数据库，会导致正常的游戏运行异常）

第二解决方案：下载可以读取db数据库的软件，在gid列中找到你发生异常的群聊群号，删除他们

## 写在最后
如果觉得有疑惑的地方，你可以欣赏一下这个代码，我留了些话在代码里哦~