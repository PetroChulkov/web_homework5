import argparse
from datetime import datetime
from datetime import timedelta
import platform

import aiohttp
import asyncio

DEFAULT_CURRENCIES = ['USD', 'EUR']


parser = argparse.ArgumentParser(description='Exchange rates getter')
parser.add_argument('--days', '-d', required=True, help='Days range to get rates in')
args = vars(parser.parse_args())
count_days = int(args.get('days'))

def link_creator(num: int):
    links_list = []
    default_link = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='
    current_date = datetime.now()
    if num > 10:
        print(f'Max days range is 10')
    elif num < 0:
        print(f'Incorrect range. Number MUST be positive')
    else:
        for i in range(0, num):
            date = current_date - timedelta(days=i)
            complete_link = default_link + date.strftime('%d.%m.%Y')
            links_list.append(complete_link)
        return links_list



async def main(link):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(link) as response:
                result = await response.json()
                result = output_parser(result)
                return result
        except aiohttp.ClientConnectionError:
            return None
            
def output_parser(info_dict):
    date = info_dict.get('date')
    final_dict = {}
    exchange_rate_dict = {}
    for el in info_dict['exchangeRate']:
        if el['currency'] in DEFAULT_CURRENCIES:
            exchange_rate_dict[el.get('currency')] = f"{{sale: {el.get('saleRate')}, 'purchase': {el.get('purchaseRate')}}}"
    final_dict[date] = exchange_rate_dict    
    return final_dict
            
    


async def run(count_days):
    list_of_links = link_creator(count_days)
    output_list = []
    for el in list_of_links:
        output_list.append(main(el))
    
    result = await asyncio.gather(*output_list)
    return result
    
if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    res = asyncio.run(run(count_days))
    print(res)
        
         
    
    