import sqlite3
import requests
from bs4 import BeautifulSoup

conn = sqlite3.connect('flyingv.db')
c = conn.cursor()

cates = ['art', 'design', 'freebird', 'film', 'tech', 'leisure', 'citizen', 'local', 'sport', 'game', 'publishing', 'traveling']

for cate in cates:
    c.execute("DROP TABLE IF EXISTS %s"%cate)
    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS %s (
            title text,
            url text,
            author text,
            excerpt text,
            goal_money real,
            goal_percent real,
            status text
            )'''%cate)
    cookies = {
    }

    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Accept': 'text/html, */*; q=0.01',
        'Sec-Fetch-Dest': 'empty',
        'X-CSRF-Token': 'ukLVUfkq3aX4h7iCwMwoBBANBlyc4yIiMumNYeMQ',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Referer': 'https://www.flyingv.cc/categories/%s/all?status=finish'%cate,
        'Accept-Language': 'en-US,en;q=0.9',
    }

    pg = 1
    while True:
        print("pg is %s"%pg)
        params = (
            ('status', 'finish'),
            ('page', pg),
        )

        response = requests.get('https://www.flyingv.cc/categories/%s/all'%cate, headers=headers, params=params, cookies=cookies)

        #NB. Original query string below. It seems impossible to parse and
        #reproduce query strings 100% accurately so the one below is given
        #in case the reproduced version is not "correct".
        # response = requests.get('https://www.flyingv.cc/categories/art/all?status=finish&page=2', headers=headers, cookies=cookies)


        soup = BeautifulSoup(response.text, 'html5lib')
        cards = soup.select('.projectCard')
        if not cards:
            break
        data = {}
        for row in cards:
            data['title'] = row.select('a.projectUrl')[0]['data-title']
            data['url'] = row.select('a.projectUrl')[0]['href']
            data['author'] = row.select('p.creator > a')[0].text
            data['excerpt'] = row.select('p.excerpt')[0].text
            data['goal_money'] = int(''.join(row.select('span.goalMoney')[0].text.split(',')))
            data['goal_percent'] = int(row.select('span.goalpercent')[0].text.replace('%',''))
            data['status'] = row.select('span.date.pull-right.small')[0].text
            print(data)
            c.execute("INSERT INTO %s VALUES (?,?,?,?,?,?,?)"%cate, (
                data['title'],
                data['url'],
                data['author'],
                data['excerpt'],
                data['goal_money'],
                data['goal_percent'],
                data['status']
                ))
        pg += 1
        conn.commit()
conn.close()
