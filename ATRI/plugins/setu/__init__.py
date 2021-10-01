import re
import asyncio
from random import choice
from nonebot.adapters.cqhttp import Bot, MessageEvent, Message

from ATRI.utils.limit import FreqLimiter, DailyLimiter
from ATRI.utils.apscheduler import scheduler
from .data_source import Setu


_setu_flmt = FreqLimiter(120)
_setu_dlmt = DailyLimiter(5)


random_setu = Setu().on_command(
    "来张涩图", "来张随机涩图，冷却2分钟，每天限5张", aliases={"涩图来", "来点涩图", "来份涩图"}
)


@random_setu.handle()
async def _random_setu(bot: Bot, event: MessageEvent):
    user_id = event.get_user_id()
    if not _setu_flmt.check(user_id):
        await random_setu.finish()
    if not _setu_dlmt.check(user_id):
        await random_setu.finish()

    repo, setu = await Setu().random_setu()
    await bot.send(event, repo)

    msg_1 = dict()
    try:
        msg_1 = await bot.send(event, Message(setu))
    except Exception:
        await random_setu.finish("hso（发不出")

    event_id = msg_1["message_id"]
    _setu_flmt.start_cd(user_id)
    _setu_dlmt.increase(user_id)
    await asyncio.sleep(30)
    await bot.delete_msg(message_id=event_id)


tag_setu = Setu().on_regex(r"来[张点丶份](.*?)的[涩色🐍]图", "根据提供的tag查找涩图")


@tag_setu.handle()
async def _tag_setu(bot: Bot, event: MessageEvent):
    user_id = event.get_user_id()
    if not _setu_flmt.check(user_id):
        await random_setu.finish()
    if not _setu_dlmt.check(user_id):
        await random_setu.finish()

    msg = str(event.message).strip()
    pattern = r"来[张点丶份](.*?)的[涩色🐍]图"
    tag = re.findall(pattern, msg)[0]
    repo, setu = await Setu().tag_setu(tag)
    if not setu:
        await tag_setu.finish(repo)

    await bot.send(event, repo)

    msg_1 = dict()
    try:
        msg_1 = await bot.send(event, Message(setu))
    except Exception:
        await random_setu.finish("hso（发不出")

    event_id = msg_1["message_id"]
    _setu_flmt.start_cd(user_id)
    _setu_dlmt.increase(user_id)
    await asyncio.sleep(30)
    await bot.delete_msg(message_id=event_id)


@scheduler.scheduled_job("interval", hours=1, misfire_grace_time=60, args=[Bot])
async def _scheduler_setu(bot):
    try:
        group_list = await bot.get_group_list()
        lucky_group = choice(group_list)
        group_id = lucky_group["group_id"]
        setu = await Setu().scheduler()
        if not setu:
            return

        msg_0 = await bot.send_group_msg(group_id=int(group_id), message=Message(setu))
        message_id = msg_0["message_id"]
        await asyncio.sleep(60)
        await bot.delete_msg(message_id=message_id)

    except Exception:
        pass
