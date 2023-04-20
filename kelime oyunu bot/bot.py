import discord
from config import *
import asyncio
import pymongo
import random

client = pymongo.MongoClient(url)
db = client.kelime_bot

class TypingSendChannel(discord.TextChannel):
    async def edit(self, *, reason=None, **options):
        async with self.typing():
            return await super().edit(reason=reason, **options)

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None):
        async with self.typing():
            return await super().send(content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after,
                                      nonce=nonce)

discord.TextChannel = TypingSendChannel

class Mybot(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    def fixx(kelime, remove_hat=True, lowercase=True):
        # Tüm harfleri küçük harfe dönüştür
        if lowercase:
            kelime = kelime.lower()

        # Çok kelimeden oluşan kelimeleri kaldır
        if " " in kelime:
            kelime = kelime.split(" ")[0]

        # ' işaretiyle ayrılmış kelimeleri sadeleştir
        if "'" in kelime:
            kelime = kelime.split("'")[0]

        # Sonunda virgül olan kelimelerden virgül kaldır
        kelime = kelime.replace(',', '')

        # Ünlem Kaldır
        kelime = kelime.replace('!','')

        # Şapkalı harfleri kaldır
        if remove_hat:
            kelime = kelime.replace('â', 'a')
            kelime = kelime.replace('î', 'i')
            kelime = kelime.replace('û', 'u')

        # Kelime . ya da - ila başlıyorsa kelimeyi ekleme
        if kelime[0] in [".", "-"]:
            return None
        else:
            return kelime
    async def on_message(self, message):
        random_number = random.randint(4,6)
        def check(reaction, user):
            return user.id == bot_id and str(reaction.emoji) == '✅' and kkanal == message.channel.id
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            print("---------------")
            print(message.content)
            print("Onaylanmayan kelime")
        else:        
            db.kelimeler.insert_one(
                {
                    "Kelime": message.content,
                }
            )
            print(message.content)
            with open ('kelime.txt','r', encoding="utf-8") as dosya:
                for line in dosya.read().splitlines():
                    if(line.startswith(message.content[-1:])==True and len(line)>3):
                        hex = {"Kelime": line}
                        if db.kelimeler.count_documents(hex) == 0:
                            db.kelimeler.insert_one(
                                {
                                    "Kelime": line,
                                }
                            )
                            await asyncio.sleep(random_number)
                            await message.channel.send(line)
                            print("Yeni kelime dataya eklendi")
                            break
                        elif db.kelimeler.count_documents(hex) == 1:
                            print("Kelime daha önceden yazılmış")

bot = Mybot()
bot.run(token)