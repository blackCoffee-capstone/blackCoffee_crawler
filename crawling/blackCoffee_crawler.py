import time
import os
import random
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def file_in():
    d = datetime.today()
    file_path = 'D:\FourOne\SW\data\data_%d월%d일.csv' % (d.month, d.day)
    fi = open(file_path, mode = 'a', encoding='utf-8-sig', newline='')
    return fi, file_path

def login(driver):
    driver.get('https://www.instagram.com/')
    driver.implicitly_wait(30)
    time.sleep(random.uniform(4, 6))
    
    id_input = driver.find_element(by=By.XPATH, value='//*[@id="loginForm"]/div/div[1]/div/label/input')
    id_input.send_keys('email')
    pw_input = driver.find_element(by=By.XPATH, value='//*[@id="loginForm"]/div/div[2]/div/label/input')
    pw_input.send_keys('password')
    
    driver.implicitly_wait(30)
    time.sleep(random.uniform(4, 6))
    
    driver.find_element(by=By.XPATH, value='//*[@id="loginForm"]/div/div[3]').click()
    driver.implicitly_wait(30)
    time.sleep(random.uniform(4, 6))
    print('로그인')
    
def location(driver, lists):
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    place = soup.find_all("div", class_='_aacl _aacn _aacu _aacy _aada _aade')
    driver.implicitly_wait(30)
    time.sleep(random.uniform(5, 7))
    
    if len(place) != 0:
        place = place[0].get_text()
        place_name = re.compile('[0-9가-힣ㄱ-ㅎ.]+').findall(place)
        if place_name:
            place_name = ' '.join(place_name)
            lists.append(place_name)
        else:
            place_name = re.compile('[a-zA-Z0-9.]+').findall(place)
            if place_name:
                place_name = ' '.join(place_name)
                lists.append(place_name)
            else:
                print('위치 추출 불가')
        
        driver.implicitly_wait(30)
        time.sleep(random.uniform(5, 7))
    else:
        print('위치 기반 없음')
    
    driver.implicitly_wait(30)
    time.sleep(random.uniform(4, 6))
    
    return lists

def datetime_like_text(driver, lists, soup):    
    datetime = soup.find("time", class_='_aaqe').get('datetime')
    lists.append(datetime)
    driver.implicitly_wait(30)
    time.sleep(random.uniform(4, 6))
    print('날짜 추가')
    
    likes = soup.find_all('div', class_='_aacl _aaco _aacw _aacx _aada _aade')
    if len(likes) == 0:
        zero = soup.find_all('button', class_='_acan _acao _acat')
        one_like = soup.find_all('div', class_='_aacl _aaco _aacw _aacx _aad6')
        if one_like:
            lists.append(1)
            print('좋아요(1) 추가')
        elif zero:
            lists.append(0)
            print('좋아요(0) 추가')
        else:
            views = soup.find_all('div', class_='_aacl _aaco _aacw _aacx _aad6 _aade')
            if len(views):
                view = views[1].get_text().split()[1].strip("회") + '(조회수)'
                lists.append(view)
                print('조회수 추가')
    else: 
        like_pre = likes[0]
        like_num = like_pre.get_text().split()[1].strip("개")
        lists.append(like_num)
        print('좋아요 추가')
    driver.implicitly_wait(30)
    time.sleep(random.uniform(4, 6))
    
    photo_url = soup.head.find('meta', property="og:image").get('content')
    lists.append(photo_url)
    driver.implicitly_wait(30)
    time.sleep(random.uniform(4, 6))
    print('사진 링크 추가')
       
    infos = soup.find("span", class_='_aacl _aaco _aacu _aacx _aad7 _aade').get_text()
    lists.append(infos)
    driver.implicitly_wait(30)
    time.sleep(random.uniform(4, 6))
    print('본문 추가')
    
    return lists

    
def insert_link(driver, lists, step, nun):
    tmp = ['https://www.naver.com/', 'https://www.daum.net/', 'https://www.google.com/']
    
    if step == 0:
        time.sleep(random.uniform(2, 3))
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        driver.implicitly_wait(30)
        time.sleep(random.uniform(7, 9))
        
        inven = soup.find_all('div', class_='_aabd _aa8k _aanf')
        print('본문 수: ', len(inven))
        if len(inven) == 9:
            return lists, nun

        for i in inven[9:len(inven) - 1]:
            step += 1        
            
            link = i.find('a').get('href')
            driver.implicitly_wait(30)
            time.sleep(random.uniform(6, 8))
            
            full_link = 'https://www.instagram.com%s' % link
            driver.get(full_link)
            print(full_link)
            driver.implicitly_wait(30)
            time.sleep(random.uniform(5, 7))
            print('게시물 접속')
            
            html_text = driver.page_source
            soup_text = BeautifulSoup(html_text, 'html.parser')
            driver.implicitly_wait(30)
            time.sleep(random.uniform(4, 6))
            
            len_lists = len(lists)
            lists = location(driver, lists)
            
            if step % 2 == 0:
                ran = random.randint(0, 2)
                driver.get(tmp[ran])
                driver.implicitly_wait(30)
                time.sleep(random.uniform(5, 7))
            
            if len(lists) == len_lists:
                nun += 1
                print("nun: %d" % nun)
                continue            
            
            lists.append(full_link)
            print('게시물 링크 추가')
            
            lists = datetime_like_text(driver, lists, soup_text)
        
        
        return lists, nun

def search(driver, lists):
    hash_tag = ['전시장', '미술관', '패러글라이딩', '절', '캠핑']
    suffic = ['여행/', '여행지/', '여행지추천/', '여행추천/']
    prefix = ['한국', '국내']

    for i in prefix:
        for j in suffic:
            tag = i + j
            hash_tag.append(tag)
    time.sleep(3)
    
    for i in hash_tag:
        driver.get('https://www.instagram.com/explore/tags/%s' % i)
        driver.implicitly_wait(30)
        time.sleep(random.uniform(5, 7))
        print('%s 검색' % i)
        
        lists, nun = insert_link(driver, lists, 0, 0) 
        time.sleep(5)
        
        save(lists)
        lists  = []
        time.sleep(random.uniform(3, 5))
        
        if nun > 21:
            driver.close()
            driver.quit()
            print("접속 종료")
            time.sleep(5)
            return 0
    
    return 0
        
def save(lists):
    arr = np.array(lists)
    arr = arr.reshape(-1, 6)
    df = pd.DataFrame(arr, columns = ['place', 'snsPostUrl', 'datetime', 'like', 'photoUrl', 'text'])
    time.sleep(2)
    
    csv_file, file_path = file_in()
    if os.stat(file_path).st_size == 0:
        df.to_csv(csv_file, index = False)
    else:
        df.to_csv(csv_file, index = False, header = False)
    
    csv_file.close()
    print("[O]\n\n")
    
option = Options()
option.add_argument('headless')
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
option.add_argument('user-agent=' + user_agent)
option.add_argument('window-size=1920x1080')
option.add_argument("disable-gpu")
option.add_argument('incognito')
driver = webdriver.Chrome(service=Service('D:/Program/Eclipse/chromedriver.exe'), options=option)

lists = []
login(driver) 
done = search(driver, lists)

time.sleep(10)
driver.close()
driver.quit()