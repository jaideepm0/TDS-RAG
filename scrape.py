# //// script
# requires-python = '>=3.13'
# dependencies = [
#         'httpx',
#         'tqdm',
#         'python-dateutil'
#         ]
# ///


import httpx
import json
import os
from tqdm import tqdm
from dateutil import parser
from datetime import datetime, timezone

baseurl = "https://discourse.onlinedegree.iitm.ac.in/"
url = "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34.json"

cookie = '_gcl_au=1.1.480668264.1747761048; _fbp=fb.2.1747761048206.305080952846386080; _ga=GA1.1.1275298665.1747761048; _ga_5HTJMW67XK=GS2.1.s1747761048$o1$g0$t1747761057$j0$l0$h0; _ga_08NPRH5L4M=GS2.1.s1747761048$o1$g0$t1747761057$j51$l0$h0$dNlldYTZEMQalzo9C66ohQN6ghVAiLCrlxQ; _t=XdAXN%2BEE5kzz%2FiBTrWHOc0vT3q%2Fp%2BKtaehOIfUlRg55k4D14fWLdUTgJLHUhnmlZXTGyfQizjSgOT26BubdZbHbQAt2WGODjAvpK7ygXu%2BmETejtWk13Uyh7AmuhnVFhK1ZKkC5FfIMxi9LsGnGcm6%2FvKN7DDUFdPD2Avu5OHKrOG8lRygp1SVdfxT3QIdWmcov5kE%2FnrgnznhDfmfTbsxb2HCdggWZo3XMDG2hZy40%2B6tXMsMvJCSjwFUrdtQKrpTcA7B3Ty1Fd70T3cmzVK7iRDA%2BcB6uKdCBIivXp6JdlR%2BAHSYsXlO0TkAY%3D--MC%2BMm5vS8s%2FWQcDN--cvS73YdQvam%2FDdmFLleFRw%3D%3D; _bypass_cache=true; _forum_session=aGSbWE7MnohbODVAdym18WdOwE27Gkyj6RBIEWPChLfqx99GKM3u73cksBKB9foHhGpsICMERcFRpylBc0BBhPvzg2sIH3iBN%2Bqupor09xjk7PyoBQVobYUpxhachNB6yP6KaYqzS9Eu0GOzmUJhIFWB29p4Ig66No07GNA5FCTrod8GXR%2FQbEVERXosg7Ldhjuj77yihagtRPPJ1sbPXSoht%2FfNP6SFWYMe4b9GuHJVqy886isHFc5vXj42JXARU3pG%2Bb0Ah4FuOM%2BKuPRrzCmPvgU0DQA1K%2F1A17kKmiH85dwMboG8S8rUJyKq2%2BOFDlht1vDgBEIdiPPP9ASx012X29bp86mleH5K6sYKf1%2FwviVVAxshwNLpI6a8%2Bw%3D%3D--6uohN2yUDnkAWCKJ--PT7vDSVpyVk9%2FaIDpMX8HQ%3D%3D'

cookie = cookie.encode('ascii', 'ignore')

# this is a good practice but doesn't matter to scrape initially as cookie is ephermal
# with open('./cookie.txt', 'r') as f:
#     cookie = f.read().encode('ascii', 'ignore')[:-1]  # [:-1] to exclude '\n'


headers = {
    'Cookie': cookie
}

start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
end_date = datetime(2025, 4, 14, tzinfo=timezone.utc)

def date_filter(inp: str) -> bool:

    date = parser.isoparse(inp)
    return start_date <= date <= end_date


def scrape(url):

    for i in tqdm(range(20)):  # goes till august 2024 so very very safe to have 20

        """scraping and caching them safely so no issue will occur for posts extraction"""
        data = ...
        if not os.path.exists(f"./content/content_{i}.json"):
            params = {'page': i}
            response = httpx.get(url, headers=headers, params=params)

            response.raise_for_status()
            if response.status_code == 200:
                data = response.json()
                with open(f"./content/content_{i}.json", "w") as f:
                    json.dump(data, f)
        with open(f'./content/content_{i}.json', 'r') as f:
            data = json.load(f)

        # The Data is loaded now scrape the posts from the data

        for search in data['topic_list']['topics']:

            """The date filtering"""
            if not date_filter(search['created_at']):
                continue

            """Construct the url to send the request"""

            slug = search['slug']
            id_ = search['id']
            total_posts = search['posts_count']


            """Go through all the posts
                Observation:
                    Whenver going through the constructed url fetches number - 5 to number + (15 | 14)
                    having these things we can increase the loop size by 19 to be on safe side and have a set() to track the progress
            """
            construct_url = f'{baseurl}t/{slug}/{id_}/'
            track = set()
            complete_posts = {}
            for post_number in tqdm(range(1, total_posts + 15, 10)):  # +15 to be very very safe surely no errors wiill be thrown
                response = httpx.get(construct_url + f'{post_number}.json', headers=headers)
                posts_data = response.json()
                scraped_posts = posts_data['post_stream']['posts']
                for post in scraped_posts:
                    if not date_filter(post['updated_at']):
                        continue
                    if post['post_number'] not in track:
                        complete_posts[post['post_number']] = post
                        track.add(post['post_number'])

            os.makedirs(f'./content/posts/{slug}/{id_}', exist_ok=True)
            """Haven't checked for cache for these things. it's ok not be too strict in having good coding practices (consider deadlines)"""
            with open(f'./content/posts/{slug}/{id_}/posts.json', 'w') as f:
                json.dump(complete_posts, f)
            for key, value in complete_posts.items():
                with open(f'./content/posts/{slug}/{id_}/{key}.json', 'w') as f:
                    json.dump(value, f)


if __name__ == '__main__':

    """Check for the variables start_date and end_date and update them to scrape acorss the dates"""
    scrape(url)
    
