import discord
from discord.ext import commands
import os

# =======================================================================
#                  *** قِسْم التَعْدِيلات الضَرورية  ***
# =======================================================================

# 🔑 السطر 14: استيراد التوكن من متغيرات البيئة (Secrets) في Replit
# يجب عليك إضافة التوكن في Replit تحت اسم Key: BOT_TOKEN
try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
except KeyError:
    print("❌ خطأ: لم يتم العثور على التوكن في متغيرات البيئة (Secrets).")
    print("الرجاء إضافة Key: BOT_TOKEN و Value: [توكن البوت] في Replit Secrets.")
    exit()

# =======================================================================
#                  *** قِسْم الإعْدادات الأساسية  ***
# =======================================================================

# تعريف الصلاحيات بأقل استهلاك للموارد
intents = discord.Intents.none()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True

# تعريف البادئة (الرمز الذي يبدأ به الأمر) - ! هو البادئة الافتراضية
bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    chunk_guilds_at_startup=False,
    member_cache_flags=discord.MemberCacheFlags.none()
)

# =======================================================================
#                  *** قِسْم الأوامر البرمجية  ***
# =======================================================================

@bot.event
async def on_ready():
    print(f'✅ البوت {bot.user} يعمل بنجاح!')
    print('-------------------------------')

# 🔒 الأمر الأول: لإغلاق الشات (الاسم: !اغلق)
@bot.command(name='اغلق')
@commands.has_permissions(manage_channels=True)
async def lock_chat(ctx):
    channel = ctx.channel
    everyone_role = ctx.guild.default_role

    await channel.set_permissions(everyone_role, send_messages=False)
    await ctx.send(f'🔒 تم إغلاق الشات في قناة {channel.mention} بواسطة {ctx.author.mention}.')

# 🔓 الأمر الثاني: لفتح الشات (الاسم: !افتح)
@bot.command(name='افتح')
@commands.has_permissions(manage_channels=True)
async def unlock_chat(ctx):
    channel = ctx.channel
    everyone_role = ctx.guild.default_role

    await channel.set_permissions(everyone_role, send_messages=True)
    await ctx.send(f'🔓 تم فتح الشات في قناة {channel.mention} بواسطة {ctx.author.mention}.')

# التعامل مع خطأ نقص الصلاحيات لأوامر الإغلاق والفتح
@lock_chat.error
@unlock_chat.error
async def chat_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 عذراً، يجب أن يكون لديك صلاحية **إدارة القنوات** لاستخدام هذا الأمر.")

# 👑 الأمر الثالث: إعطاء رتبة محددة عبر المنشن (الاسم: !منح)
@bot.command(name='منح')
@commands.is_owner() 
async def give_any_role(ctx, member: discord.Member, role: discord.Role):

    if role:
        try:
            if role not in member.roles:
                await member.add_roles(role)
                await ctx.send(f'🎉 تم إعطاء العضو {member.mention} رتبة **{role.name}** بنجاح.')
            else:
                await ctx.send(f'⚠️ العضو {member.mention} يمتلك هذه الرتبة بالفعل.')
        except discord.Forbidden:
             await ctx.send("❌ لا أستطيع إعطاء هذه الرتبة. تأكد أن رتبة البوت في قائمة الرتب أعلى من الرتبة التي تحاول إعطاءها.")

# ❌ الأمر الرابع: إزالة رتبة محددة عبر المنشن (الاسم: !ازالة)
@bot.command(name='ازالة')
@commands.is_owner()
async def remove_any_role(ctx, member: discord.Member, role: discord.Role):

    if role:
        try:
            if role in member.roles:
                await member.remove_roles(role)
                await ctx.send(f'✅ تم إزالة رتبة **{role.name}** من العضو {member.mention} بنجاح.')
            else:
                await ctx.send(f'⚠️ العضو {member.mention} لا يمتلك رتبة **{role.name}** أصلاً.')
        except discord.Forbidden:
            await ctx.send("❌ لا أستطيع إزالة هذه الرتبة. تأكد من ترتيب رتبة البوت في قائمة الرتب.")

# 🤫 الأمر الخامس: منع شخص محدد من الكتابة (الاسم: !منع)
@bot.command(name='منع')
@commands.has_permissions(manage_channels=True)
async def mute_user_text(ctx, member: discord.Member, *, reason="لا يوجد سبب"):

    overwrites = ctx.channel.overwrites_for(member)
    overwrites.send_messages = False

    try:
        await ctx.channel.set_permissions(member, overwrite=overwrites, reason=reason)
        await ctx.send(f'🔇 تم **منع** العضو {member.mention} من الكتابة في هذه القناة. السبب: {reason}')
    except discord.Forbidden:
        await ctx.send("❌ لا أستطيع تعديل صلاحيات هذا العضو (قد تكون رتبته أعلى من رتبة البوت).")

# ✅ الأمر السادس: السماح لشخص محدد بالكتابة (الاسم: !سماح)
@bot.command(name='سماح')
@commands.has_permissions(manage_channels=True)
async def unmute_user_text(ctx, member: discord.Member):

    overwrites = ctx.channel.overwrites_for(member)
    overwrites.send_messages = None

    try:
        await ctx.channel.set_permissions(member, overwrite=overwrites)
        await ctx.send(f'🔊 تم **السماح** للعضو {member.mention} بالكتابة في هذه القناة مجدداً.')
    except discord.Forbidden:
        await ctx.send("❌ لا أستطيع تعديل صلاحيات هذا العضو (قد تكون رتبته أعلى من رتبة البوت).")


# التعامل مع خطأ "ليس المالك" والأخطاء الأخرى لأوامر المنح والإزالة
@give_any_role.error
@remove_any_role.error
async def owner_error_handler(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("🚫 هذا الأمر متاح فقط لمالك البوت.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("الرجاء ذكر العضو ومنشن الرتبة: `!منح/@ازالة @اسم_العضو @الرتبة`")
    elif isinstance(error, commands.BadArgument):
         await ctx.send("🚫 صيغة خاطئة. تأكد أنك تقوم بـ **منشن** العضو ومنشن **الرتبة**.")

# التعامل مع خطأ أمر المنع والسماح
@mute_user_text.error
@unmute_user_text.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 عذراً، يجب أن يكون لديك صلاحية **إدارة القنوات** لاستخدام هذا الأمر.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("الرجاء ذكر العضو: `!منع @اسم_العضو [السبب اختياري]` أو `!سماح @اسم_العضو`")


# تشغيل البوت
bot.run(BOT_TOKEN, log_handler=None)