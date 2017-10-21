#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import channel
import telethon.tl.types as tty
import telethon.tl.functions as tfu
from telethon import TelegramClient


def parser(entity, message, message_id):
    client.send_read_acknowledge(entity, None, message_id)
    client(tfu.messages.SetTypingRequest(entity, tty.SendMessageTypingAction()))

    param = message.split(' ')
    if param[0].startswith('t.me/') or param[0].startswith('https://t.me/'):
        invite = param[0]
        invite_name = invite[invite.rfind('/') + 1:]
        invite_public = invite.find('joinchat') == -1

        try:
            if invite_public:
                entity_join = client.get_input_entity(invite_name)
                if isinstance(entity_join, tty.InputPeerChannel):
                    client(tfu.channels.JoinChannelRequest(entity_join))
                else:
                    res = '=_='
            else:
                client(tfu.messages.ImportChatInviteRequest(invite_name))
        except:
            res = '好像找不到这个群组/频道\n' \
                  '如果你确定没发错，我觉得你应该是把我给 ban 了=.=\n' \
                  '要不然就是我已经在群组/频道里了\n' \
                  '如果你认为这是一个 bug，建议 /about\n'
        else:
            res = '已加入\n' \
                  '我现在我需要验证你\n' \
                  '你需要把我设为管理员后将开始工作\n' \
                  '设置管理员可以只拥有一种权限（例如 Add users）\n'\
                  'PS：不用担心，当验证完成后你可以随时取消管理员权限'
    elif param[0] == '/about':
        # 关于
        res = '建议、bug、女装（不存在）、代码发送：/report xx（你的消息）\n' \
              'PS：注意，report 将收集你的身份信息（如 username、user_id）'
    elif param[0] == '/report':
        # 报告
        try:
            assert (param[1])
            entity_master = client.get_input_entity(108895024)
            client(tfu.messages.ForwardMessagesRequest(
                   entity, [message_id], entity_master))
        except:
            res = '/report xx（你的消息）'
        else:
            res = '已发送报告'
    elif param[0] == '/enable':
        channel.add(entity.user_id, entity.user_id)
        res = '现在开始，如果你的消息被转发，我将通知你'
    elif param[0] == '/disable':
        channel.delete(entity.user_id)
        res = '已关闭转发通知'
    else:
        # 帮助
        res = 'Hi，我会通知你的消息被转发\n' \
              '但你需要添加我到你的频道才会开始服务~\n' \
              '另外给你命令列表：\n' \
              '/enable 开启个人消息转发通知\n'\
              '/disable 关闭个人消息转发通知\n' \
              '/about 关于&报告bug\n' \
              '关于一些紧急情况通知 Channel：https://t.me/TGForwarderNotice\n'\
              'PS：如果需要添加我，发送 t.me/xx 的邀请链接就可以'
    client.send_message(entity, res, message_id)


def callback(update):

    if isinstance(update, tty.UpdateShortMessage) and not update.out:
        parser(client.get_input_entity(update.user_id),
               update.message,
               update.id)
    elif isinstance(update, tty.UpdateNewMessage) and not update.message.out:
        parser(client.get_input_entity(update.message.from_id),
               update.message.message,
               update.message.id)
    elif isinstance(update, tty.UpdateNewChannelMessage):
        if (update.message.fwd_from and
            update.message.fwd_from.channel_id != update.message.to_id.channel_id):

            if update.message.fwd_from.channel_id:
                fwdinfo = channel.get(update.message.fwd_from.channel_id)
            else:
                fwdinfo = channel.get(update.message.fwd_from.from_id)
            if fwdinfo:
                message_id = update.message.id
                entity = client.get_input_entity(update.message.to_id)
                entity_fwd = client.get_input_entity(int(fwdinfo[0][1]))
                cinfo = client(tfu.channels.GetChannelsRequest([entity]))
                if cinfo.chats[0].username:
                    cusername = cinfo.chats[0].username
                    clink = 'https://t.me/%s/%d' % (
                        cusername, update.message.id)
                else:
                    clink = '不可描述（private）'


                if update.message.media:
                    res = '已被转发：%s' % (clink)
                    client(tfu.messages.ForwardMessagesRequest(
                           entity, [message_id], entity_fwd))
                else:
                    res = '「%s」\n\n已被转发：\n%s' % (
                          update.message.message, clink)
                client.send_message(entity_fwd, res, link_preview=False)

    elif isinstance(update, tty.UpdateChannel):
        entity = client.get_input_entity(tty.PeerChannel(update.channel_id))
        if channel.get(entity.channel_id, count=True):
            try:
                client(tfu.channels.GetChannelsRequest([entity]))
            except:
                channel.delete(entity.channel_id)
        else:
            try:
                admins = client(tfu.channels.GetParticipantsRequest(
                                entity, tty.ChannelParticipantsAdmins(), 0, 1))
                assert(admins.users[0].is_self)
                entity_creator = client.get_input_entity(admins.users[1])
            except:
                return
            else:
                channel.add(entity.channel_id, entity_creator.user_id)
                client.send_message(entity_creator,
                                    '绑定成功！你可以将机器人从管理员中移除了')


with open('config.json', 'r', encoding='UTF-8') as f:
    configs = json.load(f)

client = TelegramClient(configs['telegram']['some_name'],
                        configs['telegram']['api_id'],
                        configs['telegram']['api_hash'],
                        update_workers=10)
if not client.connect():
    print('连接服务器失败')
    exit()
if not client.is_user_authorized():
    client.send_code_request(configs['telegram']['phone_number'])
    code = input('输入 code: ')
    client.sign_in(configs['telegram']['phone_number'], code)
client.add_update_handler(callback)

command = ''
while command != '/stop':
    command = input('command: ')
