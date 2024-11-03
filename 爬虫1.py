import re
import threading
import time
from datetime import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup
import schedule

news1 = []
news2 = []

#获取消息网址


def parse_detail1(href):
    try:
        response = requests.get(href)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.find('div', class_="article")
        if articles:
            article = articles.get_text()
            return article
        else:
            return None
    except Exception as e:
        print(f'解析人民网详情出错：{e}')

def parse_detail2(href):
    try:
        response = requests.get(href)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.find('div', id="ozoom")
        if articles:
            article = articles.get_text()
            return article
    except Exception as e:
        print(f'解析新华日报详情出错：{e}')


def get_1(URL,formatted_date1):
    try:
        #请求网址
        response=requests.get(URL)
        response.encoding='utf-8'
        soup=BeautifulSoup(response.text,'lxml')
        news1.append({'来源': '人民日报'})
        #获取基本信息
        elements=soup.find_all(class_='news-list')
        for element in elements:
            titles=element.find_all('a')
            for title in titles:
                href_0 = title.get('href')
                href = 'http://paper.people.com.cn/rmrb/html/' + formatted_date1 + '/' + href_0
                pattern = re.compile('<p class="date left">(.*?)<span>.*?</span></p>', re.S)
                dates = re.findall(pattern, response.text)
                for temp in dates:
                    date=re.sub('[\r\n]','',temp)
                    content = parse_detail1(href)
                    if content:
                        news1.append({'标题': title.string, '网址': href, '日期': date.strip(),'内容':content.strip()})
    except Exception as e:
        print(f'解析人民网新闻出错：{e}')




def get_2(URL):
    try:
        response = requests.get(URL)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        date_ = soup.select('#ScroLeft > div.newslisttit > span')
        date = date_[0].string
        all_data = soup.select('#ScroLeft > div.newslist > ul > li > h3 > a')
        news2.append({'来源':'新华日报'})
        for data in all_data:
            href_0 = data.get('href')
            href_1 = href_0[9:43]
            href = 'https://xh.xhby.net/pc/' + href_1
            title = data.string
            content = parse_detail2(href)
            news2.append({'标题': title, '网址': href, '日期': date, '内容': content})
    except Exception as e:
        print(f'解析新华日报新闻出错：{e}')

#获取网址
def main1():
    today=datetime.now().date()
    formatted_date1=today.strftime('%Y-%m/%d')
    formatted_date2=today.strftime('%Y%m/%d')
    URLS=['http://paper.people.com.cn/rmrb/html/'+formatted_date1+'/nbs.D110000renmrb_01.htm'
            ,'https://xh.xhby.net/pc/layout/'+formatted_date2+'/node_2.html']
    for URL in URLS:
        if URL==URLS[0]:
            get_1(URL,formatted_date1)
        else:
            get_2(URL)
    news=news1+news2
    df=pd.DataFrame(news)
    try:
        df.to_excel('news.xlsx', index=False)
    except PermissionError as e:
        print(f'无法保存文件：{e}')

def main2():
    while True:
        input('请在下一行中按下Enter键执行查询任务，输入q退出：')
        if input() == 'q':
            print('你已退出查询任务')
            break
        year=int(input('请输入想要查询的年份:'))
        month=int(input('请输入想要查询的月份:'))
        day=int(input('请输入想要查询的天:'))
        query_date=datetime(year,month,day).date()
        formatted_date1=query_date.strftime('%Y-%m/%d')
        formatted_date2=query_date.strftime('%Y%m/%d')
        URLS=['http://paper.people.com.cn/rmrb/html/'+formatted_date1+'/nbs.D110000renmrb_01.htm'
                ,'https://xh.xhby.net/pc/layout/'+formatted_date2+'/node_1.html']
        for URL in URLS:
            if URL==URLS[0]:
                get_1(URL,formatted_date1)
            else:
                get_2(URL)
        news=news1+news2
        df=pd.DataFrame(news)
        try:
            df.to_excel('news.xlsx', index=False)
        except PermissionError as e:
            print(f'无法保存文件：{e}')


def sche():
    schedule.every().day.at('08:00').do(main1)
    while True:
        schedule.run_pending()
        time.sleep(1)

t=threading.Thread(target=sche)

if __name__ == '__main__':
    t.start()
    main2()




