import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
import threading
from utils import check_ban

app = Flask(__name__)

load_dotenv()
APPLICATION_ID = os.getenv("APPLICATION_ID")
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

DEFAULT_LANG = "pt"
user_languages = {}

nomBot = "None"

@app.route('/')
def home():
    global nomBot
    return f"Bot {nomBot} está funcionando"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask).start()

@bot.event
async def on_ready():
    global nomBot
    nomBot = f"{bot.user}"
    print(f"O bot está conectado como {bot.user}")

@bot.command(name="guilds")
async def show_guilds(ctx):
    guild_names = [f"{i+1}. {guild.name}" for i, guild in enumerate(bot.guilds)]
    guild_list = "\n".join(guild_names)
    await ctx.send(f"O bot está nos seguintes servidores:\n{guild_list}")

@bot.command(name="lang")
async def change_language(ctx, lang_code: str):
    lang_code = lang_code.lower()
    if lang_code not in ["pt", "en", "fr"]:
        await ctx.send("❌ Idioma inválido. Disponíveis: `pt`, `en`, `fr`")
        return

    user_languages[ctx.author.id] = lang_code
    messages = {
        "pt": "✅ Idioma definido para português.",
        "en": "✅ Language set to English.",
        "fr": "✅ Langue définie sur le français."
    }
    await ctx.send(f"{ctx.author.mention} {messages[lang_code]}")

@bot.command(name="ID")
async def check_ban_command(ctx):
    content = ctx.message.content
    user_id = content[3:].strip()
    lang = user_languages.get(ctx.author.id, "pt")

    print(f"Comando feito por {ctx.author} (lang={lang})")

    if not user_id.isdigit():
        message = {
            "pt": f"{ctx.author.mention} ❌ **UID inválido!**\n➡️ Use o comando assim: `!ID 123456789`",
            "en": f"{ctx.author.mention} ❌ **Invalid UID!**\n➡️ Please use: `!ID 123456789`",
            "fr": f"{ctx.author.mention} ❌ **UID invalide !**\n➡️ Veuillez fournir un UID valide sous la forme : `!ID 123456789`"
        }
        await ctx.send(message[lang])
        return

    async with ctx.typing():
        try:
            ban_status = await check_ban(user_id)
        except Exception as e:
            await ctx.send(f"{ctx.author.mention} ⚠️ Erro:\n```{str(e)}```")
            return

        if ban_status is None:
            message = {
                "pt": f"{ctx.author.mention} ❌ **Não foi possível obter informações.**\nTente novamente mais tarde.",
                "en": f"{ctx.author.mention} ❌ **Could not get information. Please try again later.**",
                "fr": f"{ctx.author.mention} ❌ **Impossible d'obtenir les informations.**\nVeuillez réessayer plus tard."
            }
            await ctx.send(message[lang])
            return

        is_banned = int(ban_status.get("is_banned", 0))
        period = ban_status.get("period", "N/A")
        nickname = ban_status.get("nickname", "NA")
        region = ban_status.get("region", "N/A")
        id_str = f"`{user_id}`"

        if isinstance(period, int):
            period_str = {
                "pt": f"mais de {period} meses",
                "en": f"more than {period} months",
                "fr": f"plus de {period} mois"
            }[lang]
        else:
            period_str = {
                "pt": "indisponível",
                "en": "unavailable",
                "fr": "indisponible"
            }[lang]

        embed = discord.Embed(
            color=0xFF0000 if is_banned else 0x00FF00,
            timestamp=ctx.message.created_at
        )

        if is_banned:
            titles = {
                "pt": "**▌ Conta Banida 🛑 **",
                "en": "**▌ Banned Account 🛑 **",
                "fr": "**▌ Compte banni 🛑 **"
            }
            embed.title = titles[lang]
            embed.description = (
                f"**• {'Motivo' if lang == 'pt' else 'Reason' if lang == 'en' else 'Raison'} :** "
                f"{'Esta conta foi confirmada por uso de trapaças.' if lang == 'pt' else 'This account was confirmed for using cheats.' if lang == 'en' else 'Ce compte a été confirmé comme utilisant des hacks.'}\n"
                f"**• {'Duração da suspensão' if lang == 'pt' else 'Suspension duration' if lang == 'en' else 'Durée de la suspension'} :** {period_str}\n"
                f"**• {'Apelido' if lang == 'pt' else 'Nickname' if lang == 'en' else 'Pseudo'} :** `{nickname}`\n"
                f"**• {'ID do jogador' if lang == 'pt' else 'Player ID' if lang == 'en' else 'ID du joueur'} :** {id_str}\n"
                f"**• {'Região' if lang == 'pt' else 'Region' if lang == 'en' else 'Région'} :** `{region}`"
            )
            file = discord.File("assets/banned.gif", filename="banned.gif")
            embed.set_image(url="attachment://banned.gif")
        else:
            titles = {
                "pt": "**▌ Conta Limpa ✅ **",
                "en": "**▌ Clean Account ✅ **",
                "fr": "**▌ Compte non banni ✅ **"
            }
            embed.title = titles[lang]
            embed.description = (
                f"**• {'Status' if lang == 'pt' else 'Status'} :** "
                f"{'Sem evidências suficientes de uso de trapaças nesta conta.' if lang == 'pt' else 'No sufficient evidence of cheat usage on this account.' if lang == 'en' else 'Aucune preuve suffisante pour confirmer l’utilisation de hacks sur ce compte.'}\n"
                f"**• {'Apelido' if lang == 'pt' else 'Nickname' if lang == 'en' else 'Pseudo'} :** `{nickname}`\n"
                f"**• {'ID do jogador' if lang == 'pt' else 'Player ID' if lang == 'en' else 'ID du joueur'} :** {id_str}\n"
                f"**• {'Região' if lang == 'pt' else 'Region' if lang == 'en' else 'Région'} :** `{region}`"
            )
            file = discord.File("assets/notbanned.gif", filename="notbanned.gif")
            embed.set_image(url="attachment://notbanned.gif")

        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed.set_footer(text="DESENVOLVIDO POR Two9")
        await ctx.send(f"{ctx.author.mention}", embed=embed, file=file)

bot.run(TOKEN)
