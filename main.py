import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import json
import requests

print("import完成")

print("開始讀取設定")
try:
    with open("Config.json", "r") as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    with open("Config.json", "w") as f:
        json.dump({'Discord_Bot_Token': 'YOURTOKEN', 'Prefix': 'tree.', 'guild_id': '', 'whitelist_role_id': ''}, f, indent=4)
    raise Exception("找不到Config.json... 我把它放到資料夾裡了，請去設定它的內容! (第一次執行會這樣很正常)")
except json.decoder.JSONDecodeError:
    print('file empty')

wlsttree = {}
try:
    with open("treedata.json", "r") as f:
        wlsttree = json.load(f)
except FileNotFoundError:
    print('tree file not fond')
    pass
except json.decoder.JSONDecodeError:
    print('file empty')

mcwhitelist = []
try:
    with open("whitelist.json", "r") as f:
        mcwhitelist = json.load(f)
except FileNotFoundError:
    print('mc whitelist file not fond')
    pass
except json.decoder.JSONDecodeError:
    print('file empty')

#存檔
def save_tree():
    with open("treedata.json", 'w') as file:
        json.dump(wlsttree, file, indent=4)

def save_mcwhitelist():
    with open("whitelist.json", 'w') as file:
        json.dump(mcwhitelist, file, indent=2)

#檢查樹上存在用戶
def check_user_data(dcid):
    dcid = str(dcid)
    if dcid not in wlsttree:
        wlsttree[dcid] = {'mcid':'', 'uuid':'', 'in_whitelist' : 0, 'parent':'', 'child':[]}

#嘗試增加身分組
async def try_addrole(dcid):
    try:
        guild_id = int(CONFIG['guild_id'])
        guild = bot.get_guild(guild_id)
        role_id = int(CONFIG['whitelist_role_id'])
        if guild is None:
            print(f'增加身分組guild not found.')
            return
        usr = await bot.fetch_user(dcid)
        role = discord.utils.get(guild.roles, id=role_id)
        if usr is None:
            print(f'增加身分組user not found.')
            return
        if role is None:
            print(f'增加身分組role not found.')
            return
        member = await guild.fetch_member(usr.id)
        if member is None:
            print(f'增加身分組member not found.')
            return
        try:
            await member.add_roles(role)
            print(f'增加{usr}身分組{role}')
        except:
            print(f'增加{usr}身分組{role}失敗')
            return
    except:
        print(f'嘗試增加身分組失敗')

#嘗試移除身分組
async def try_rmrole(dcid):
    try:
        guild_id = int(CONFIG['guild_id'])
        guild = bot.get_guild(guild_id)
        role_id = int(CONFIG['whitelist_role_id'])
        if guild is None:
            print(f'移除身分組guild not found.')
            return
        usr = await bot.fetch_user(dcid)
        role = discord.utils.get(guild.roles, id=role_id)
        if usr is None:
            print(f'移除身分組user not found.')
            return
        if role is None:
            print(f'移除身分組role not found.')
            return
        member = await guild.fetch_member(usr.id)
        if member is None:
            print(f'移除身分組member not found.')
            return
        try:
            await member.remove_roles(role)
            print(f'移除{usr}身分組{role}')
        except:
            print(f'移除{usr}身分組{role}失敗')
            return
    except:
        print(f'嘗試移除身分組失敗')

#連帶解編
async def chain_rm(target,reason,interaction: discord.Interaction):
    check_user_data(target)
    tgtchildlist = wlsttree[target]['child']
    for tgtchild in tgtchildlist:
        tgtchild = str(tgtchild)
        check_user_data(tgtchild)
        wlsttree[tgtchild]['parent'] = ''
        wlsttree[tgtchild]['in_whitelist'] = 0
        try:
            tgtchildname = await bot.fetch_user(tgtchild)
        except:
            tgtchildname = tgtchild
            print('username not found')
        newreason = f'{reason}連帶{tgtchildname}'
        print(f'{newreason}解編')
        try_rmrole(tgtchild)
        try_rmwhitelist(tgtchild)
        await interaction.message.channel.send(f'<@{tgtchild}>已被解編，{newreason}')
        await chain_rm(tgtchild,newreason,interaction)
    wlsttree[target]['child'] = []
    pass

#嘗試加入白名單
def try_addwhitelist(dcid):
    print(f'嘗試加入{dcid}白名單')

#嘗試移除白名單
def try_rmwhitelist(mcid):
    print(f'嘗試移除{mcid}白名單')

       

print("設定")
bot = commands.Bot(command_prefix=CONFIG['Prefix'], intents=discord.Intents.default())
slash_cmd = bot.tree

@bot.event
async def on_ready():
    global owner
    print(f'logging as : {bot.user.name}')
    app_info = await bot.application_info()
    owner = app_info.owner
    print(f'bot owner : {owner.name}@{owner.id}')
    try:
        synced = await slash_cmd.sync()
        print(f"已同步 {len(synced)} 條slash指令")
        status_w = discord.Status.online
        activity_w = discord.Activity(type=discord.ActivityType.playing, name="Minecraft")
        await bot.change_presence(status= status_w, activity=activity_w)
        print(f'已設定機器人狀態')
    except Exception as e:
        print(e)

###slash指令###

#註冊
#檢查mcid
def check_mcid(mcid, usr):
    response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{mcid}")
    if response.status_code == 200:
        uuid = response.json()['id']
        #尋找樹資料
        search_mcid = response.json()['name']
        for dcid, data in wlsttree.items():
            if data.get('mcid') == search_mcid:
                found_dcid = dcid
                return f'已被<@{found_dcid}>使用', True
        else:
            usr = str(usr)
            check_user_data(usr)
            if wlsttree[usr]['mcid'] != "":
                try_rmwhitelist(wlsttree[usr]['mcid'])
            wlsttree[usr]['mcid'] = search_mcid
            wlsttree[usr]['uuid'] = uuid
            print(wlsttree)
            save_tree()
            try_addwhitelist(usr)
            return f'成功將<@{usr}>的minecraftID註冊為{search_mcid}',False
    elif response.status_code == 404:
        return '請輸入正確ID', True
    else:
        return '似乎出現了什麼問題', False
@bot.tree.command(name="註冊" ,description="登記您的minecraft供白名單使用")
async def registermcid(interaction: discord.Interaction, mcid:str):
    msg,msghide = check_mcid(mcid, interaction.user.id)
    await interaction.response.send_message(f'{msg}',ephemeral=msghide)

#收編
@slash_cmd.command(name = "收編",description= "將別人經由自己連接到白名單樹上")
async def hire_user(interaction: discord.Interaction, target: discord.User):
    author_id = str(interaction.user.id)
    target_id = str(target.id)
    check_user_data(author_id)
    if wlsttree[author_id]['in_whitelist'] == 0:
        await interaction.response.send_message(f'你也不在白名單內呀',ephemeral=True)
    else:
        check_user_data(target_id)
        if wlsttree[target_id]['in_whitelist'] == 1:
            tgtparent = wlsttree[target_id]['parent']
            await interaction.response.send_message(f'<@{target_id}>已被<@{tgtparent}>收編',ephemeral=True)
        else:
            wlsttree[author_id]['child'].append(target_id)
            wlsttree[target_id]['parent'] = author_id
            wlsttree[target_id]['in_whitelist'] = 1
            save_tree()
            await try_addrole(target_id)
            try_addwhitelist(target_id)
            await interaction.response.send_message(f'<@{author_id}>已成功收編<@{target_id}>')


#解編
class dissmissButtonView(discord.ui.View):
    def __init__(self, author_name: str, author_id: str, target_name:str, target_id: str, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.author_name = author_name
        self.author_id = author_id
        self.target_name = target_name
        self.target_id = target_id
    @discord.ui.button(label="確定", style=discord.ButtonStyle.danger)
    async def confirmbtn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=f"您已確認要將<@{self.target_id}>及他收編的對象移出白名單",view=None)
        wlsttree[self.author_id]['child'].remove(self.target_id)
        wlsttree[self.target_id]['parent'] = ''
        wlsttree[self.target_id]['in_whitelist'] = 0
        print(wlsttree)
        await try_rmrole(self.target_id)
        try_rmwhitelist(self.target_id)
        await interaction.message.channel.send(f'<@{self.author_id}>已將<@{self.target_id}>解編')
        reason = f'因{self.author_name}解編{self.target_name}'
        await chain_rm(self.target_id,reason,interaction)
        print(wlsttree)
        save_tree()
    @discord.ui.button(label="取消", style=discord.ButtonStyle.blurple)
    async def cancelbtn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="已取消",view=None)

@slash_cmd.command(name = "解編",description= "解編")
async def dismiss_user(interaction: discord.Interaction, target: discord.User):
    author_name = str(interaction.user.name)
    author_id = str(interaction.user.id)
    target_name = str(target.name)
    target_id = str(target.id)
    check_user_data(author_id)
    if target_id not in wlsttree[author_id]['child']:
        await interaction.response.send_message(f'你沒有權利把他解編',ephemeral=True)
    else:
        view = dissmissButtonView(author_name, author_id,target_name, target_id)
        await interaction.response.send_message(f'請小心，這個操作會將<@{target_id}>及他收編的對象移出白名單，確定要這麼做嗎?',view=view,ephemeral=True)

bot.run(CONFIG['Discord_Bot_Token'])