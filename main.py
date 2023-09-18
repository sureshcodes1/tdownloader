import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import time
import os
import threading

bot_token = os.environ.get("TOKEN", None) 
api_hash = os.environ.get("HASH", None) 
api_id = os.environ.get("ID", None)
bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
ss = os.environ.get("STRING", None)
if ss is not None:
	acc = Client("myacc" ,api_id=api_id, api_hash=api_hash, session_string=ss)
	acc.start()
else: acc = None

lastmsgId = 0
msgId = 0
messageCopy = ""
chatid = 0
currMsgId = 0
uploading = False
targetChatId = 0

# download status
def downstatus(statusfile,message):
	global currMsgId
	while True:
		if os.path.exists(statusfile):
			break

	time.sleep(3)      
	while os.path.exists(statusfile):
		with open(statusfile,"r") as downread:
			txt = downread.read()
		try:
			bot.edit_message_text(message.chat.id, message.id, f"currIndex: **{currMsgId}** | __Downloaded__ : **{txt}**")
			time.sleep(40)
		except FloodWait as e:
			print("FLodd in Download", e)
			time.sleep(e.x or 40)


# upload status
def upstatus(statusfile,message):
	global currMsgId
	while True:
		if os.path.exists(statusfile):
			break

	time.sleep(3)      
	while os.path.exists(statusfile):
		with open(statusfile,"r") as upread:
			txt = upread.read()
		try:
			bot.edit_message_text(message.chat.id, message.id, f"currIndex: **{currMsgId}** |__Uploaded__ : **{txt}**")
			time.sleep(40)
		except FloodWait as e:
			print("FLodd in Upload", e)
			time.sleep(e.x or 50)


# progress writter
def progress(current, total, message, type):
	with open(f'{message.id}{type}status.txt',"w") as fileup:
		fileup.write(f"{current * 100 / total:.1f}%")


# start command
@bot.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
	bot.send_message(message.chat.id, f"__👋 Hi **{message.from_user.mention}**, I am Save Restricted Bot, I can send you restricted content by it's post link__",
	reply_markup=InlineKeyboardMarkup([[ InlineKeyboardButton("🌐 Source Code", url="https://github.com/bipinkrish/Save-Restricted-Bot")]]), reply_to_message_id=message.id)


@bot.on_message(filters.text)
def save(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):

	# joining chats
	# print(message)
	if "set" in message.text or "Set" in message.text: 
		global targetChatId
		targetChatId = message.text.split("/c/")[1].split('/')[0]
		bot.send_message(int(message.chat.id), "Target Folder is: " + targetChatId)
		print("currentTargetChatId: " + targetChatId)
		return

	if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:

		if acc is None:
			bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.id)
			return

		try:
			try: acc.join_chat(message.text)
			except Exception as e: 
				bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.id)
				return
			bot.send_message(message.chat.id,"**Chat Joined**", reply_to_message_id=message.id)
		except UserAlreadyParticipant:
			bot.send_message(message.chat.id,"**Chat alredy Joined**", reply_to_message_id=message.id)
		except InviteHashExpired:
			bot.send_message(message.chat.id,"**Invalid Link**", reply_to_message_id=message.id)
	
	# getting message
	elif "https://t.me/" in message.text:
		global  lastmsgId
		global messageCopy
		global msgId
		global chatid
		messageCopy = message
		temp = ''
		if len(message.text.split("|")) > 1:
			temp = message.text.split("|")[1]
		message.text = message.text.split("|")[0]
		datas = message.text.split("/")
		msgId = int(datas[-1].split("?")[0])
		if temp :
			lastmsgId = int(temp)
		else :
			lastmsgId = msgId
		# private
		if "https://t.me/c/" in message.text:
			chatid = int("-100" + datas[-2])
			if acc is None:
				bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.id)
				return
			try: handle_private(message,chatid,msgId)
			except Exception as e: bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.id)
		
		# public
		else:
			username = datas[-2]
			msg  = bot.get_messages(username,msgId)
			try: bot.copy_message(message.chat.id, msg.chat.id, msg.id,reply_to_message_id=message.id)
			except:
				if acc is None:
					bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.id)
					return
				try: handle_private(message,username,msgId)
				except Exception as e: bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.id)
	

# handle private
def handle_private(message,chatid,msgId):
		msg  = acc.get_messages(chatid,msgId)
		global lastmsgId
		global currMsgId
		currMsgId = msgId
		if "text" in str(msg):
			bot.send_message(message.chat.id, msg.text, entities=msg.entities, reply_to_message_id=message.id)
			if msgId < lastmsgId:
				try: handle_private(message,chatid,msgId + 1)
				except Exception as e: bot.send_message(message.chat.id,f"**Error123** : __{e}__", reply_to_message_id=message.id)
			return
		smsg = bot.send_message(message.chat.id, '__Downloading__' + str(msgId) , reply_to_message_id=message.id)
		# dosta = threading.Thread(target=lambda:downstatus(f'{message.id}downstatus.txt',smsg),daemon=True)
		# dosta.start()
		file = acc.download_media(msg)
		if os.path.exists(f'{message.id}downstatus.txt'): os.remove(f'{message.id}downstatus.txt')
		# upsta = threading.Thread(target=lambda:upstatus(f'{message.id}upstatus.txt',smsg),daemon=True)
		# upsta.start()

		localTargetChatId = message.chat.id
		global targetChatId, newMSg
		# if targetChatId:
			# localTargetChatId = int(targetChatId)
		# print(message.chat.id, localTargetChatId)
		try: 
			if "Document" in str(msg):
				try:
					thumb = acc.download_media(msg.document.thumbs[0].file_id)
				except: thumb = None
				
				newMSg = bot.send_document(localTargetChatId, file, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities)
				if thumb != None: os.remove(thumb)

			elif "Video" in str(msg):
				try: 
					thumb = acc.download_media(msg.video.thumbs[0].file_id)
				except: thumb = None
				newMSg = bot.send_video(localTargetChatId, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities)
				if thumb != None: os.remove(thumb)

			elif "Animation" in str(msg):
				newMSg = bot.send_animation(localTargetChatId, file, reply_to_message_id=message.id)
				
			elif "Sticker" in str(msg):
				newMSg = bot.send_sticker(localTargetChatId, file, reply_to_message_id=message.id)

			elif "Voice" in str(msg):
				newMSg = bot.send_voice(localTargetChatId, file, caption=msg.caption, thumb=thumb, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])

			elif "Audio" in str(msg):
				try:
					thumb = acc.download_media(msg.audio.thumbs[0].file_id)
				except: thumb = None
					
				newMSg = bot.send_audio(localTargetChatId, file, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])   
				if thumb != None: os.remove(thumb)

			elif "Photo" in str(msg):
				newMSg = bot.send_photo(localTargetChatId, file, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id)
		except Exception as e: print("erorr")
		finally:
			os.remove(file)
			if os.path.exists(f'{message.id}upstatus.txt'): os.remove(f'{message.id}upstatus.txt')
			bot.delete_messages(localTargetChatId,[smsg.id])
			# if newMSg and targetChatId: newMSg.forward(targetChatId)
			if msgId < lastmsgId:
				try: handle_private(message,chatid,msgId + 1)
				except Exception as e: bot.send_message(message.chat.id,f"**Error123** : __{e}__", reply_to_message_id=message.id)



# infinty polling
bot.run()
