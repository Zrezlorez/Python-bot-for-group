#!/usr/bin/python3.8
# coding=utf-8
import copy
import codecs
import vk_api
import json
import megacrypt
from datetime import datetime
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import time

key = ''
vk_session = vk_api.VkApi(token = key)
vk = vk_session.get_api()

def pythonify(data):
    correctData = {}
    for key, value in data.items():
        if isinstance(value, list):
            value = [pythonify(item) if isinstance(item, dict) else item for item in value]
        elif isinstance(value, dict):
            value = pythonify(value)
        try:
            key = int(key)
        except Exception as ex:
            pass
        correctData[key] = value
    return correctData
def load(name):
    f = codecs.open(name + '.json', 'r', 'utf-8')
    data = json.load(f)
    return pythonify(data)
def save(data, name):
    with open(name +".json", 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class MyVkBotLongPoll(VkBotLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as e:
                print('VkLongPoll Error:', e)

class Bot:
    def __init__(self, data):
        self.data = data
        self.admins = self.data["settings"]["admins"]
        self.modules = ["photo", "video", "audio", "sticker", "audio_message", "profiles"]
        self.abc = [
                'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
                'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ',
                'abcdefghijklmnopqrstuvwxyz',
                'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                '.,/_-\=+]<?:;~[{^|`*&}%$#№@!>',
                '0123456789']
        self.news = self.data["news"]
        self.ver = self.data["settings"]["ver"]
    def switchAdmin(self, user_id):
        if user_id in self.admins:
            self.admins.remove(user_id)
        else:
            self.admins.append(user_id)
        self.data["settings"]["admins"] = self.admins
        save(self.data, "data")
        return self.data
    def crypt(self, msg):
        out = ""
        for i in msg:
            inAlphabet = 0
            for j in self.abc:
                if i in j:
                    out += j[len(j) - 1 - j.find(i)]
                    break
                else:
                    inAlphabet += 1
            if inAlphabet == len(self.abc):
                out += i
        return out
    def megacrypt(self, msg):
        return megacrypt.megaCrypt(msg)
    def megadecrypt(self, msg):
        return megacrypt.megaDecrypt(msg)
    def getNews(self, page):
        try:
            page = int(page) - 1
        except:
            page = 0
        list = self.news[::-1]
        if page >= len(list):
            return f"На странице {page + 1} еще нет новостей!"
        if page < 0:
            return f"Ты дурак? Номер страницы не может быть отрицательным!"
        out = ""
        for i in list[page]:
            out += i + "<br>"
        out += f"<br>Страница {page + 1} из {len(list)}"
        return out
    def getVer(self):
        return self.ver
    def getTop(self, conversation_id, size, module):
        list = []
        if conversation_id not in self.data["conversations"] or module not in self.data["conversations"][conversation_id]:
            return "В этом топе еще никого нет, ты можешь стать первым!"
        top = self.data["conversations"][conversation_id][module]
        for i in top:
            if module == "profiles":
                list.append([top[i]["lvl"], top[i]["exp"], top[i]["name"]])
            else:
                list.append([top[i]["count"], top[i]["name"]])
        list.sort()
        list = list[::-1]
        out = self.data["settings"]["types"][module]["head"] + "<br><br>"
        for i in range(min(size, len(list))):
            if module == "profiles":
                out += str(i+1) + '. ' + list[i][2] + " | Уровень " + str(list[i][0]) + " (" + str(list[i][1]) + "/" + str(data["settings"]["levels"][list[i][0]]) + ")" + "<br>"
            else:
                out += str(i+1) + '. ' + list[i][1] + " - " + str(list[i][0]) + "<br>"
        return out
    def getTopGlobal(self, size, module):
        list = []
        ids = []
        if len(self.data["conversations"]) == 0:
            return "В этом топе еще никого нет, ты можешь стать первым!"
        for i in self.data["conversations"]:
            if module not in self.data["conversations"][i]:
                continue
            if "disableTop" in self.data["conversations"][i] and self.data["conversations"][i]["disableTop"]:
                continue
            top = self.data["conversations"][i][module]
            for j in top:
                if module == "profiles":
                    list.append([top[j]["lvl"], top[j]["exp"], top[j]["name"], j])
                else:
                    list.append([top[j]["count"], top[j]["name"], j])
        if len(list) == 0:
            return "В этом топе еще никого нет, ты можешь стать первым!"
        list.sort()
        list = list[::-1]
        minus = 0
        out = self.data["settings"]["types"][module]["head"] + " (Глобальный)<br><br>"
        i = 0
        while i < min(size, len(list)):
            if list[i][-1] in ids:
                minus -= 1
            else:
                if module == "profiles":
                    out += str(i+minus+1) + '. ' + list[i][2] + " | Уровень " + str(list[i][0]) + " (" + str(list[i][1]) + "/" + str(data["settings"]["levels"][list[i][0]]) + ")" + "<br>"
                else:
                    out += str(i+minus+1) + '. ' + list[i][1] + " - " + str(list[i][0]) + "<br>"
                ids.append(list[i][-1])
            i += 1
        return out
    def getModule(self, name):
        if name == "image":
            return "photo"
        elif name == "voice":
            return "audio_message"
        elif name == "music":
            return "audio"
        elif name == "lvl":
            return "profiles"
        else:
            return name
    def getFormattedTime(self, secs):
        out = ""
        if secs >= 3600:
            out += f"{int(secs // 3600)}ч "
            secs %= 3600
        if secs >= 60:
            out += f"{int(secs // 60)}м "
            secs %= 60
        if secs != 0:
            out += f"{secs}с"
        if out[-1] == " ":
            out = out[:-1]
        return out
    def getFormattedLenght(self, lenght):
        out = ""
        if lenght >= 100000:
            out += f"{int(lenght // 100000)}км "
            lenght %= 100000
            if lenght >= 100:
                out += f"{int(lenght // 100)}м"
        elif lenght >= 100:
            out += f"{int(lenght // 100)}м "
            lenght %= 100
            if lenght != 0:
                out += f"{int(lenght)}см"
        else:
            out += f"{lenght}см"
        return out
    def isConvAdmin(self, conversation_id, user_id):
        members = vk.messages.getConversationMembers(peer_id = conversation_id)["items"]
        for i in members:
            if i["member_id"] == user_id and i["is_admin"]:
                return True
        return False
    def switchTop(self, conversation_id):
        if conversation_id not in self.data["conversations"]:
            self.data["conversations"][conversation_id] = {}
        if "disableTop" in self.data["conversations"][conversation_id] and self.data["conversations"][conversation_id]["disableTop"]:
            self.data["conversations"][conversation_id]["disableTop"] = False
        else:
            self.data["conversations"][conversation_id]["disableTop"] = True
        return self.data

class User:
    def __init__(self, user_id, conversation_id, data):
        self.data = data
        self.user_id = user_id
        self.profile = Profile(self, user_id, conversation_id, self.data)
        self.allowedTypes = ["photo", "video", "audio", "sticker", "audio_message"]
        self.types = {}
        for i in self.allowedTypes:
            self.types[i] = Stats(self, i, user_id, conversation_id, self.data)
        self.help = self.data["help"]
        self.commandHelp = self.data["commandHelp"]
    def isAdmin(self):
        return True if self.user_id in self.data["settings"]["admins"] else False
    def save(self):
        self.data = self.profile.save(self.data)
        for i in self.types:
            self.data = self.types[i].save(self.data)
        save(self.data, "data")
        return self.data
    def inConversation(self, conversation_id):
        list = []
        members = vk.messages.getConversationMembers(peer_id = conversation_id)
        for i in members['items']:
            list.append(i['member_id'])
        return True if user_id in list else False
    def getProfile(self):
        out = self.profile.getText() + "<br><br>"
        for i in self.types:
            out += self.types[i].getText() + "<br>"
        out += "<br>"
        return out
    def getHelp(self, command):
        out = ""
        if command in self.commandHelp:
            out += f"Помощь по команде !{command}:" + "<br>"
            for i in self.commandHelp[command]:
                out += i + "<br>"
        else:
            for i in self.help["default"]:
                out += i + "<br>"
            if self.isAdmin():
                out += "<br>"
                for i in self.help["admin"]:
                    out += i + "<br>"
        return out
    def kick(self, conversation_id):
        try:
            vk.messages.removeChatUser(
            chat_id = conversation_id - 2000000000,
            member_id = self.user_id
            )
        except:
            None
    def delete(self):
        for i in self.data["conversations"][conversation_id]:
            if self.user_id in self.data["conversations"][conversation_id][i]:
                del self.data["conversations"][conversation_id][i][self.user_id]

class Profile():
    def __init__(self, user, user_id, conversation_id, data):
        self.data = data
        self.user_id = user_id
        if conversation_id not in self.data["conversations"] or "profiles" not in self.data["conversations"][conversation_id] or self.user_id not in self.data["conversations"][conversation_id]["profiles"]:
            self.name = vk.users.get(user_ids = self.user_id)
            self.name = self.name[0]['first_name'] + ' ' + self.name[0]['last_name']
            self.exp = 0
            self.lvl = 0
            self.block = 0
        else:
            self.name = self.data["conversations"][conversation_id]["profiles"][user_id]["name"]
            self.exp = self.data["conversations"][conversation_id]["profiles"][user_id]["exp"]
            self.lvl = self.data["conversations"][conversation_id]["profiles"][user_id]["lvl"]
            if "block" in self.data["conversations"][conversation_id]["profiles"][user_id]:
                self.block = self.data["conversations"][conversation_id]["profiles"][user_id]["block"]
            else:
                self.block = 0
        self.edit = False
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.user = user
    def save(self, data):
        if self.edit:
            if self.conversation_id not in data["conversations"]:
                data["conversations"][self.conversation_id] = {}
            if "profiles" not in data["conversations"][self.conversation_id]:
                data["conversations"][self.conversation_id]["profiles"] = {}
            if self.user_id not in data["conversations"][self.conversation_id]["profiles"]:
                data["conversations"][self.conversation_id]["profiles"][self.user_id] = {}
            data["conversations"][self.conversation_id]["profiles"][self.user_id]["name"] = self.name
            data["conversations"][self.conversation_id]["profiles"][self.user_id]["exp"] = self.exp
            data["conversations"][self.conversation_id]["profiles"][self.user_id]["lvl"] = self.lvl
            data["conversations"][self.conversation_id]["profiles"][self.user_id]["block"] = self.block
            self.edit = False
        return data
    def giveExp(self, amount):
        self.edit = True
        self.exp = round(self.exp + amount)
        self.update()
    def setExp(self, amount):
        self.edit = True
        self.exp = round(amount)
        self.update()
    def giveLvl(self, amount):
        self.edit = True
        self.lvl = round(self.lvl + amount)
        self.exp = 0
        if self.lvl < 0:
            self.lvl = 0
        elif self.lvl > len(self.data["settings"]["levels"]) - 1:
            self.lvl = len(self.data["settings"]["levels"]) - 1
    def setLvl(self, amount):
        self.edit = True
        self.lvl = round(amount)
        self.exp = 0
        if self.lvl < 0:
            self.lvl = 0
        elif self.lvl > len(data["settings"]["levels"]) - 1:
            self.lvl = len(data["settings"]["levels"]) - 1
    def update(self):
        if self.exp >= data["settings"]["levels"][self.lvl] and self.lvl != len(data["settings"]["levels"]) - 1:
            self.lvl += 1
            self.exp -= data["settings"]["levels"][self.lvl]
        elif self.exp < 0:
            self.exp = 0
    def blockUser(self, durability):
        try:
            self.block = time.time() + int(durability)
            self.edit = True
        except:
            None
    def isBlocked(self):
        return False if time.time() > self.block else True
    def getText(self):
        text = self.name
        if self.user.isAdmin():
            text = "👑 " + text
        if self.isBlocked():
            text = "⛔ " + text
        text += "<br>"
        text += "Уровень: " + str(self.lvl) + " (" + str(self.exp) + "/" + str(self.data["settings"]["levels"][self.lvl]) + ")"
        return text

class Stats():
    def __init__(self, user, type, user_id, conversation_id, data):
        if conversation_id not in data["conversations"] or type not in data["conversations"][conversation_id] or user_id not in data["conversations"][conversation_id][type]:
            self.name = vk.users.get(user_ids = user_id)
            self.name = self.name[0]['first_name'] + ' ' + self.name[0]['last_name']
            self.count = 0
            self.rank = 0
        else:
            self.name = data["conversations"][conversation_id][type][user_id]["name"]
            self.count = data["conversations"][conversation_id][type][user_id]["count"]
            self.rank = data["conversations"][conversation_id][type][user_id]["rank"]
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.data = data
        self.icons = {"photo" : "🖼 ", "video": "🎦 ", "audio": "🎵 ", "sticker": "🤩 ", "audio_message": "🔊 "}
        self.edit = False
        self.type = type
    def getText(self):
        return f"{self.icons[self.type]} {self.getRankName(self.rank)} [{self.count}]"
    def giveStat(self, amount):
        self.edit = True
        self.count = round(self.count + amount)
        self.update()
    def setStat(self, amount):
        self.edit = True
        self.count = round(amount)
        self.update()
    def giveRank(self, amount):
        self.edit = True
        self.rank = round(self.rank + amount)
        if self.rank < 0:
            self.rank = 0
        elif self.rank > len(data["settings"]["types"][self.type]["ranks"]) - 1:
            self.rank = len(data["settings"]["types"][self.type]["ranks"]) - 1
        if self.rank == 0:
            self.count = 0
        else:
            self.count = data["settings"]["types"][self.type]["ranks"][self.rank - 1]["count"]
    def setRank(self, amount):
        self.edit = True
        self.rank = round(amount)
        if self.rank < 0:
            self.rank = 0
        elif self.rank > len(data["settings"]["types"][self.type]["ranks"]) - 1:
            self.rank = len(data["settings"]["types"][self.type]["ranks"]) - 1
        if self.rank == 0:
            self.count = 0
        else:
            self.count = data["settings"]["types"][self.type]["ranks"][self.rank - 1]["count"]
    def update(self):
        if self.count < 0:
            self.count = 0
        for i in range(len(data["settings"]["types"][self.type]["ranks"])):
            if data["settings"]["types"][self.type]["ranks"][i]["count"] > self.count:
                break
        self.rank = i
    def getRankName(self, rank):
        return self.data["settings"]["types"][self.type]["ranks"][self.rank]["name"]
    def save(self, data):
        if self.edit:
            if self.conversation_id not in data["conversations"]:
                data["conversations"][self.conversation_id] = {}
            if self.type not in data["conversations"][self.conversation_id]:
                data["conversations"][self.conversation_id][self.type] = {}
            if self.user_id not in data["conversations"][self.conversation_id][self.type]:
                data["conversations"][self.conversation_id][self.type][self.user_id] = {}
            data["conversations"][self.conversation_id][self.type][self.user_id]["name"] = self.name
            data["conversations"][self.conversation_id][self.type][self.user_id]["count"] = self.count
            data["conversations"][self.conversation_id][self.type][self.user_id]["rank"] = self.rank
            self.edit = False
        return data

class Logs():
    def __init__(self, logs):
        self.logs = logs
        self.enabled = self.logs["settings"]["enabled"]
    def switchLogs(self):
        self.enabled = not self.enabled
        if self.enabled:
            send(conversation_id, "Отладка включена")
        else:
            send(conversation_id, "Отладка выключена")
        self.logs["settings"]["enabled"] = self.enabled
        save(self.logs, "logs")
        return self.logs
    def save(self, msg):
        conversation_id = msg["peer_id"]
        user_id = msg["from_id"]
        if conversation_id not in self.logs["conversations"]:
            self.logs["conversations"][conversation_id] = {}
            self.logs["conversations"][conversation_id]["messages"] = []
            self.logs["conversations"][conversation_id]["admin"] = vk.messages.getConversationsById(peer_ids = conversation_id)["items"][0]["chat_settings"]["owner_id"]
            self.logs["conversations"][conversation_id]["names"] = [vk.messages.getConversationsById(peer_ids = conversation_id)["items"][0]["chat_settings"]["title"]]
        if 'action' in msg and msg["action"]["type"] == "chat_title_update":
            self.logs["conversations"][conversation_id]["names"].append(msg["action"]["text"])
        else:
            form = {}
            form["id"] = user_id
            if user_id < 0:
                form["name"] = "Сообщество"
            else:
                name = vk.users.get(user_ids = user_id)
                form["name"] = name[0]['first_name'] + ' ' + name[0]['last_name']
            form["message"] = msg["text"]
            form["time"] = datetime.now().strftime("%B %d, %Y | %H:%M:%S")
            if "reply_message" in msg:
                form["reply_message"] = {}
                form["reply_message"]["id"] = msg["reply_message"]["from_id"]
                if msg["reply_message"]["from_id"] < 0:
                    form["reply_message"]["name"] = "Сообщество"
                else:
                    name = vk.users.get(user_ids = user_id)
                    form["reply_message"]["name"] = name[0]['first_name'] + ' ' + name[0]['last_name']
                form["reply_message"]["message"] = msg["reply_message"]["text"]
            self.logs["conversations"][conversation_id]["messages"].append(form)
        save(self.logs, "logs")
        return self.logs

group_id = "205847122"
elite_id = 2000000003
stars_id = 2000000010
creator = 231052013

key = 'c53619db37f00a8b5dcf331bb8952cfedb607932b44a3d0b8b8c6f9b2f60bafa8c3c512b237a34e004323'
spam = '@all Произошол рейд... ' * 100
protoRaidKey = 'ajhdna87y3e3'
raidKey = protoRaidKey

vk_session = vk_api.VkApi(token = key)
vk = vk_session.get_api()
longpoll = MyVkBotLongPoll(vk_session, '205847122')

def send(id, msg):
    vk.messages.send(peer_id = id, random_id = 0,
    v = '5.122', message = msg)

data = load("data")
logs = load("logs")

bot = Bot(data)
log = Logs(logs)

print('Загрузка завершена\n')

# send(elite_id, 'Бот Элиты ВСО запущен!')
for event in longpoll.listen():
    try:
        if event.type == VkBotEventType.GROUP_LEAVE:
            obj = event.object
            leaved_id = obj["user_id"]
            user = User(leaved_id, stars_id, data)
            if user.inConversation(stars_id):
                send(stars_id, "Вышел из группы - кик")
                user.kick(stars_id)
        elif event.type == VkBotEventType.GROUP_JOIN:
            obj = event.object
            joined_id = obj["user_id"]
            try:
                link = vk.messages.getInviteLink(peer_id = stars_id, reset = 0)
                send(joined_id, "Благодарим за вступление в группу! Вы получили доступ к беседе Звезд ВСО: " + link["link"])
            except:
                None
        elif event.type == VkBotEventType.MESSAGE_NEW:
            obj = event.object.message
            conversation_id = obj["peer_id"]
            user_id = obj["from_id"]
            if user_id < 0:
                continue
            user = User(user_id, conversation_id, data)
            if conversation_id < 2 * 10**9:
                send(conversation_id, "Хотите получить доступ к Звездам ВСО? Вступите в группу и вы получите приглашение в нашу беседу!<br>Заинтересовал бот? Пригласите его в свою беседу для доступа у интересным функциям (не забудьте выдать права администратора для корректной работы бота)")
                continue
            elif conversation_id == elite_id and "action" in obj and obj["action"]["type"] == "chat_invite_user":
                action_user_id = obj["action"]["member_id"]
                if action_user_id < 0 and obj["action"]["user_id"] not in admins:
                    try:
                        send(conversation_id, "Вы не можете пригласить бота!")
                        vk.messages.removeChatUser(
                    		chat_id = conversation_id - 2000000000,
                    		member_id = action_user_id)
                    except:
                        None
            elif conversation_id == stars_id and "action" in obj and obj["action"]["type"] == "chat_invite_user":
                action_user_id = obj["action"]["member_id"]
                if action_user_id < 0 and not user.inConversation(elite_id):
                    send(conversation_id, "Приглашать ботов могут только члены Элиты ВСО!")
                    vk.messages.removeChatUser(
                		chat_id = conversation_id - 2000000000,
                		member_id = action_user_id)
                    continue
                elif not vk.groups.isMember(group_id = group_id, user_id = action_user_id):
                    action_user = (action_user_id, conversation_id, data)
                    send(conversation_id, "Ишь хитрый какой, прежде чем зайти в беседу подпишись ➡ vk.com/elita_vso")
                    action_user.kick(conversation_id)
            elif 'action' in obj and obj["action"]["type"] == "chat_invite_user" and obj["action"]["member_id"] == -197016013:
                    send(conversation_id, "🔥 Приветствуем! 🔥\nБлагодарим за добавление бота Элиты ВСО в беседу, чтобы ознакомиться со всеми командами бота напишите !help\nПо всем вопросам, связанным с работой бота, пишите в сообщения группы")
            if log.enabled:
                log.save(obj)
            attachments = vk.messages.getByConversationMessageId(peer_id = conversation_id, conversation_message_ids = obj["conversation_message_id"], group_id = int(group_id))["items"][0]["attachments"]
            if not user.profile.isBlocked():
                if obj["text"] != "":
                    user.profile.giveExp(1)
                user.profile.giveExp(len(attachments) * 2)
                for i in attachments:
                    type = i["type"]
                    if type in user.allowedTypes:
                        user.types[type].giveStat(1)
            messageSplit = obj["text"].lower().split(" ")
            command = messageSplit[0]
            arg1 = messageSplit[1] if len(messageSplit) > 1 else None
            arg2 = messageSplit[2] if len(messageSplit) > 2 else None
            try:
                arg2 = float(arg2)
            except:
                None
            if command == "!top" and bot.getModule(arg1) in bot.modules:
                send(conversation_id, bot.getTop(conversation_id, 20, bot.getModule(arg1)))
            elif command == "!gtop":
                if arg1 == "on" or arg1 == "off":
                    if bot.isConvAdmin(conversation_id, user_id):
                        data = bot.switchTop(conversation_id)
                        if data["conversations"][conversation_id]["disableTop"]:
                            send(conversation_id, "Вы выключили отображение этой беседы в глобальных топах!")
                        else:
                            send(conversation_id, "Вы включили отображение этой беседы в глобальных топах!")
                    else:
                        send(conversation_id, "Эта команда доступна только администратору беседы!")
                elif bot.getModule(arg1) in bot.modules:
                    send(conversation_id, bot.getTopGlobal(20, bot.getModule(arg1)))
            elif command == "!crypt" and arg1 != None:
                send(conversation_id, bot.crypt(obj["text"][7:]))
            elif command == "!profile":
                if "reply_message" in obj:
                    reply_user = User(obj["reply_message"]["from_id"], conversation_id, data)
                    send(conversation_id, reply_user.getProfile())
                else:
                    send(conversation_id, user.getProfile())
            elif command == "!help":
                send(conversation_id, user.getHelp(arg1))
            elif command == "!news":
                send(conversation_id, bot.getNews(arg1))
            elif command == "!ver":
                send(conversation_id, bot.getVer())
            if not user.inConversation(elite_id):
                data = user.save()
                continue
            if command == "!mcrypt" and arg1 != None:
                send(conversation_id, bot.megacrypt(obj["text"][11:]))
            elif command == "!mdecrypt" and arg1 != None:
                send(conversation_id, bot.megadecrypt(obj["text"][13:]))
            data = user.save()
            if not user.isAdmin():
                data = user.save()
                continue
            if command == "!kick" and "reply_message" in obj:
                reply_user = User(obj["reply_message"]["from_id"], conversation_id, data)
                reply_user.kick(conversation_id)
            elif command == "!getid":
                send(conversation_id, conversation_id)
            elif command == "!logs":
                log.switchLogs()
            elif command == "!admin" and "reply_message" in obj:
                bot.switchAdmin(obj["reply_message"]["from_id"])
            elif command == '!off':
                send(conversation_id, "Бот Элиты ВСО выключен!")
                exit(0)
            elif command == "!give" and isinstance(arg2, float) and "reply_message" in obj:
                reply_user = User(obj["reply_message"]["from_id"], conversation_id, data)
                if arg1 == "exp":
                    reply_user.profile.giveExp(arg2)
                elif arg1 in reply_user.allowedTypes:
                    reply_user.types[arg1].giveStat(arg2)
                data = reply_user.save()
            elif command == "!block" and "reply_message" in obj:
                try:
                    arg1 = int(arg1)
                except:
                    continue
                if user_id == obj["reply_message"]["from_id"]:
                    user.profile.blockUser(arg1)
                    data = user.save()
                else:
                    reply_user = User(obj["reply_message"]["from_id"], conversation_id, data)
                    reply_user.profile.blockUser(arg1)
                    data = reply_user.save()
            elif command == "!delete" and "reply_message" in obj:
                if user_id == obj["reply_message"]["from_id"]:
                    user.delete()
                    data = user.save()
                else:
                    reply_user = User(obj["reply_message"]["from_id"], conversation_id, data)
                    reply_user.delete()
                    data = reply_user.save()
    except Exception as e:
        print(e)

