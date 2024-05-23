import discord
from utils import format_timestamp, format_number
from loguru import logger
WEBHOOK_URL = 'https://discord.com/api/webhooks/1228385870399143996/rfydjC8inITwMFLJyqL7zi_uf-ll0opsgOXBuF4yETNMzp6csmIEernza6C-29yMM243'

def send_webhook(token):
    logger.info(token['name'])
    embed = discord.Embed(
        title=f"{token['name']} ({token['symbol']}) (${format_number(token['usd_market_cap'])})",
        color=0x1E90FF
    )
    valid_website = '✅' if token['valid_website'] else '❌'
    embed.set_image(url=token['image_uri'])
    embed.add_field(name="📝 Description", value=token['description'], inline=False)
    embed.add_field(name="Token Details", value='-----------------------------------------------------', inline=False)
    embed.add_field(name="💁 Creator", value=f"[Visit](https://pump.fun/profile/{token['creator']})", inline=True)
    embed.add_field(name="🐦 Twitter", value=f"[Vist]({token['twitter']})", inline=True)
    embed.add_field(name="☎️ Telegram", value=f"[Vist]({token['telegram']})", inline=True)
    embed.add_field(name="👨‍💻 Website First Check", value=f"{valid_website}{token['website']}", inline=False)
    embed.add_field(name="🧑‍🤝‍🧑 Top 10 holders: ", value='', inline=False)
    holders = token['holders']
    for h in holders:
        address = h['owner'][:10] if h['owner'] else 'Unknown'
        amount = h['amount']
        special_holder = ''
        if h['isDev']:
            special_holder = '(Dev)'
        elif h['isBondingCurve']:
            special_holder = '(Bonding curve)'

        embed.add_field(
            value=f"[{address}] - {str(amount)}% {special_holder}",
            name=f"",
            inline=False
        )
    embed.add_field(name="🚀 Creator Launched Tokens", value='', inline=False)
    created_tokens = token['created_tokens']
    if len(created_tokens) > 5:
        created_tokens = created_tokens[:5]
    for t in created_tokens:
        if t['mint'] != token['mint']:
            market_cap_icon = '🔴' if t['usd_market_cap'] < 10000 else '🟡' if t['usd_market_cap'] < 50000 else '🟢'
            embed.add_field(
                value=f"[{market_cap_icon} {t['name']} ({t['symbol']}) Market Cap: ${format_number(t['usd_market_cap'])}](https://pump.fun/{t['mint']})",
                name=f"",
                inline=False
            )
    if len(token['created_tokens']) > 5:
        embed.add_field(
            name=f"",
            value=f"...+" + str(len(token['created_tokens']) - 5),
            inline=False
        )    
    embed.add_field(name="", value=f"[PHOTON](https://photon-sol.tinyastro.io/en/lp/{token['mint']}) | [PLONK](https://t.me/PlonkBot_bot?start=a_${token['mint']}) | [PEPEBOOST](https://t.me/pepeboost_sol15_bot?start=a_{token['mint']})")
    embed.set_footer(text=f"@leductam • {format_timestamp(int(token['created_timestamp']) / 1000)}\n")

    embed.url=f"https://www.pump.fun/{token['mint']}"
    send_rq(embed)

def send_rq(embed):
    try:
        webhook = discord.SyncWebhook.from_url(WEBHOOK_URL)
        webhook.send(embed=embed)
    except Exception as err:
        logger.error(err)


