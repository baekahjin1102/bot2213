import discord
from discord.ext import commands
import json
import os

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # 멤버 인텐트 활성화

bot = commands.Bot(command_prefix='!', intents=intents)

# 경고 로그 파일 경로
WARNINGS_FILE = "warnings.json"

# 경고 횟수에 따른 역할 이름
WARNING_ROLES = {
    1: "경고1회",  # 경고 1회 역할 이름
    2: "경고2회",  # 경고 2회 역할 이름
    3: "경고3회",  # 경고 3회 역할 이름
}

# 경고 로그 파일 로드 함수
def load_warnings():
    if os.path.exists(WARNINGS_FILE):
        with open(WARNINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# 경고 로그 파일 저장 함수
def save_warnings(warnings):
    with open(WARNINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(warnings, f, ensure_ascii=False, indent=4)

# 경고 역할 갱신 함수
async def update_warning_roles(member: discord.Member, warning_count: int):
    guild = member.guild
    for count, role_name in WARNING_ROLES.items():
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            if warning_count >= count:
                if role not in member.roles:
                    await member.add_roles(role)
            else:
                if role in member.roles:
                    await member.remove_roles(role)

# 경고 추가 명령어
@bot.command(name='경고추가')
async def add_warning(ctx, member: discord.Member, *, reason=None):
    warnings = load_warnings()
    user_warnings = warnings.get(str(member.id), [])
    user_warnings.append(reason)
    warnings[str(member.id)] = user_warnings
    save_warnings(warnings)
    await update_warning_roles(member, len(user_warnings))
    await ctx.send(f'{member.mention}님에게 경고를 추가했습니다. 이유: {reason}')
    
    # 경고 로그
    with open("경고로그.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f'{member.name}님에게 경고 추가: {reason} (추가한 사람: {ctx.author.name}, 시간: {ctx.message.created_at})\n')

# 경고 확인 명령어
@bot.command(name='경고확인')
async def check_warnings(ctx, member: discord.Member):
    warnings = load_warnings()
    user_warnings = warnings.get(str(member.id), [])
    if user_warnings:
        await ctx.send(f'{member.mention}님의 경고 목록:\n' + '\n'.join([f'{i+1}. {w}' for i, w in enumerate(user_warnings)]))
    else:
        await ctx.send(f'{member.mention}님은 경고가 없습니다.')

# 경고 삭제 명령어
@bot.command(name='경고삭제')
async def remove_warning(ctx, member: discord.Member, index: int):
    warnings = load_warnings()
    user_warnings = warnings.get(str(member.id), [])
    if 0 < index <= len(user_warnings):
        removed_warning = user_warnings.pop(index - 1)
        if user_warnings:
            warnings[str(member.id)] = user_warnings
        else:
            del warnings[str(member.id)]
        save_warnings(warnings)
        await update_warning_roles(member, len(user_warnings))
        await ctx.send(f'{member.mention}님의 경고를 삭제했습니다. 삭제된 경고: {removed_warning}')
        
        # 경고 삭제 로그
        with open("경고로그.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f'{member.name}님의 경고 삭제: {removed_warning} (삭제한 사람: {ctx.author.name}, 시간: {ctx.message.created_at})\n')
    else:
        await ctx.send(f'{member.mention}님의 해당 인덱스의 경고가 없습니다.')

# 봇 준비 완료 이벤트
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# 봇 토큰으로 봇 실행
bot.run('MTIyNzU3MTk2OTk3Nzg4MDU5Ng.G79oYi.zjFaVSufpINuwSMTyFxc2ALcvDbO65aXTi8bmM')


