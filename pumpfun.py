import requests
from loguru import logger
import uuid
import time
from utils import *
import aiohttp
import asyncio
import discord_helper

class PUMPFUN:
    def __init__(self) -> None:
        self.headers = {
            'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'origin':'https://pump.fun'
        }
        self.processed_mints = set()
        self.validated_websites = {}

    async def fetch_new_token(self):
        got_response = False
        while not got_response:
            try:
                async with aiohttp.ClientSession() as session:
                    r = await session.get('https://client-api-2-74b1891ee9f9.herokuapp.com/coins/latest')
                    if r.status == 200:
                        return await r.json()
                    else:
                        logger.error(r.reason)
            except Exception as err:
                logger.error(err)
            await asyncio.sleep(1)

    async def fetch_dev_created(self, dev):
        got_response = False
        while not got_response:
            try:
                async with aiohttp.ClientSession() as session:
                    r= await session.get('https://client-api-2-74b1891ee9f9.herokuapp.com/coins?offset=0&limit=50&sort=created_timestamp&order=desc&includeNsfw=true&creator=' + dev)
                    if r.status == 200:
                        data = await r.json()
                        return data
                    else:
                        logger.error(r.reason)
            except Exception as err:
                logger.error(err)
            await asyncio.sleep(1)

    async def fetch_coin_info(self, token_address):
        got_response = False
        while not got_response:
            try:
                async with aiohttp.ClientSession() as session:
                    r= await session.get('https://client-api-2-74b1891ee9f9.herokuapp.com/coins/' + token_address)
                    if r.status == 200:
                        return await r.json()
                    else:
                        logger.error(r.reason)
            except Exception as err:
                logger.error(err)
            await asyncio.sleep(1)

    async def fetch_holder(self, token_address):
        got_response = False
        while not got_response:
            try:
                async with aiohttp.ClientSession() as session:
                    r = await session.post('https://pump-fe.helius-rpc.com/?api-key=1b8db865-a5a1-4535-9aec-01061440523b',json=
                                  {"method": "getTokenLargestAccounts", "jsonrpc": "2.0", "params": [token_address, { "commitment": "confirmed" }], "id": "633310da-8246-4a63-a250-311b2bc92d5b" }, headers=self.headers)
                    if r.status == 200:
                        data = await r.json()
                        if data:
                            return data['result']['value']
            except Exception as err:
                logger.error(err)
            await asyncio.sleep(1)

    async def fetch_account_info(self, token_address):
        max_retry = 5
        for _ in range(max_retry):
            try:
                async with aiohttp.ClientSession() as session:
                    r = await session.post('https://pump-fe.helius-rpc.com/?api-key=1b8db865-a5a1-4535-9aec-01061440523b',json=
                                 { "method": "getAccountInfo", "jsonrpc": "2.0", "params": [token_address, { "encoding": "jsonParsed", "commitment": "confirmed" }], "id": "633310da-8246-4a63-a250-311b2bc92d5b"  }, headers=self.headers)
                    if r.status == 200:
                        data = await r.json()
                        if data:
                            return data['result']['value']['data']['parsed']['info']['owner']
            except Exception as err:
                logger.error(err)
            await asyncio.sleep(1)

    async def check_website(self, website_url, token_address):
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                r = await session.get(url=website_url)
                if r.status == 200:
                    text = await r.text()
                    return token_address in text
                else:
                    logger.error(f"HTTP error: {r.status} - {r.reason}")
        except Exception as err:
            logger.error(f"Request failed: {err}")
        return False
    
    async def new_launch(self):
        data = await self.fetch_new_token()
        if not data and data['mint'] in self.processed_mints:
            return
        self.processed_mints.add(data['mint'])
        created, holding = await asyncio.gather(self.fetch_dev_created(data['creator']), self.fetch_holder(data['mint']))
        if not holding or not created:
            return
        holding = holding[:5]
        top_holder = []
        for h in holding:
            if h['uiAmount'] > 1:
                owner = await self.fetch_account_info(h['address'])
                if not owner:
                    return
            top_holder.append({
                'amount' : round(h['uiAmount'] / 1e7, 2),
                'owner' : owner,
                'isBondingCurve' : h['address'] == data['associated_bonding_curve'],
                'isDev' : owner == data['creator']
            })
            if owner == data['creator']:
                break
        unique_created = [next(filter(lambda item: item['symbol'] == symbol, created)) for symbol in set(item['symbol'] for item in created)]
        last_five_created = unique_created[:5]
        valid_website = False
        if data['website'] and not is_in_blacklist(data['website']):
            if data['website'] in self.validated_websites:
                valid_website = self.validated_websites[data['website']]
            else:
                valid_website = await self.check_website(website_url=data['website'], token_address=data['mint'])
                self.validated_websites[data['website']] = valid_website
        data['holders'] = top_holder
        data['valid_website'] = valid_website
        data['created_tokens'] = last_five_created
        discord_helper.send_webhook(token=data)



if __name__ == "__main__":
    async def main():
        pumpfun = PUMPFUN()
        while True:
            await pumpfun.new_launch()
    asyncio.run(main())