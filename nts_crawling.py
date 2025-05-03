#!/usr/bin/env python
# coding: utf-8

# # *국세청 세무서식 변경사항 메일 알림*

# # Selenium - 동적 웹페이지 스크래핑

# In[80]:


# Seleium 드라이버 생성
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Chrome 옵션 설정
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # 화면없이 실행

# 드라이버 서비스 생성
service = Service(ChromeDriverManager().install())

# 웹 드라이버 초기화
# driver = webdriver.Chrome(service=service, options=options)
driver = webdriver.Chrome(options=options)


# # 국세청 사이트 접속

# In[81]:


import time
# 국세청 url
url = "https://www.nts.go.kr/"

driver.get(url)
time.sleep(2)


# In[82]:


# 페이지 소스 가져오기
from bs4 import BeautifulSoup
page_source = driver.page_source

soup = BeautifulSoup(page_source, 'html.parser')

# 태그 검색
print('title 태그 요소: ', soup.title)
print('title 태그 이름: ', soup.title.name)
print('title 태그 문자열: ', soup.title.text)


# # 세무서식 조회
# ### 근로소득 원천징수영수증, 퇴직소득원천징수영수증, 퇴직급여 등 지급명세서, 간이지급명세서

# In[83]:


from selenium.webdriver.common.by import By

# '국세정책/제도' 메뉴 찾기 (텍스트로 찾기)
try:
    menu_menu = driver.find_element(By.LINK_TEXT, "국세정책/제도")
    menu_menu.click()
    driver.implicitly_wait(5)
    print("✅ '국세정책/제도' 메뉴를 클릭했습니다.")
    # 2️⃣ 하위 메뉴 '세무서식' 클릭
    sub_menu = driver.find_element(By.XPATH, '//a[text()="세무서식"]')
    sub_menu.click()
    print("✅ '세무서식' 서브 메뉴 클릭 완료")
except Exception as e:
    print("❌ 메뉴 클릭 실패:", e)
    


# In[84]:


import pandas as pd


def search_func(search_keyword, date_filter):
    
    try:
        # 3. 검색창에 키워드 입력
        search_input = driver.find_element(By.ID, 'searchValue')
        search_input.clear()
        search_input.send_keys(search_keyword)
        
        # 4. 검색 버튼 클릭 (onClick="javascript:searchEvent();"인 버튼)
        search_button = driver.find_element(By.XPATH, '//button[@title="검색" and contains(@onclick, "searchEvent")]')
        search_button.click()
        time.sleep(2)
        
        # print("✅ 검색 완료! 현재 페이지:", driver.current_url)
        print("✅ 검색 완료! 키워드:", search_keyword)
    except Exception as e:
        print("❌ 검색 실패:", e)
    
    try:
        # 2. 결과 테이블 가져오기
        rows = driver.find_elements(By.CSS_SELECTOR, ".bbs_ListA tbody tr")
        
        for row in rows:
            tds = row.find_elements(By.TAG_NAME, "td")
            
            number = tds[0].text.strip()
            pub_date = tds[1].text.strip()
            form_number = tds[2].text.strip()
            form_title = row.find_element(By.CLASS_NAME, "bbs_tit").text.strip()
            # 첨부파일 링크 추출
            file_links = tds[4].find_elements(By.TAG_NAME, "a")
            file_urls = [link.get_attribute("href") for link in file_links]
            
            # 2025년 데이터만 필터
            if pub_date.startswith(date_filter):
                data.append({
                    "검색키워드": search_keyword,
                    "번호": number,
                    "공포일자": pub_date,
                    "서식번호": form_number,
                    "서식명": form_title,
                    "첨부파일": file_urls
                })
    except Exception as e:
        print("❌ 결과추출 실패:", e)



# In[85]:


# 검색 키워드 설정
search_keywords = ["근로소득 원천징수영수증", "퇴직소득원천징수영수증", "퇴직급여 등 지급명세서", "간이지급명세서"]
date_filter = "2025"
data = []

for search_keyword in search_keywords:
    search_func(search_keyword, date_filter)

# Pandas DataFrame으로 변환
df = pd.DataFrame(data)
    
# 출력 확인
df

# 필요하면 CSV 저장도 가능
# df.to_csv("세무서식_2025년.csv", index=False)


# # 이전 데이터랑 비교해서 변경 감지(diff)

# In[88]:


from pathlib import Path

today_df = df.copy()  # 위에서 크롤링한 결과

# 저장 경로 설정
data_dir = Path("./nts_data")
data_dir.mkdir(exist_ok=True)
today_file = data_dir / "today.csv"
previous_file = data_dir / "previous.csv"

# 1. 오늘 파일 저장
today_df.to_csv(today_file, index=False)

# 2. 이전 파일 존재 여부 확인
if previous_file.exists():
    old_df = pd.read_csv(previous_file)

    # 타입 통일: 모두 문자열로 변환
    today_df["공포일자"] = today_df["공포일자"].astype(str)
    old_df["공포일자"] = old_df["공포일자"].astype(str)
    today_df["서식명"] = today_df["서식명"].astype(str)
    old_df["서식명"] = old_df["서식명"].astype(str)

    # 3. 변경 감지 (기준: 공포일자 + 서식명)
    merged = today_df.merge(old_df, how="outer", on=["공포일자", "서식명"], indicator=True)

    # 4. 추가된 행만 필터
    added = pd.DataFrame()
    added = merged[merged["_merge"] == "left_only"]

    if not added.empty:
        print("🔔 변경 감지됨! 새로운 서식이 있습니다:")
        print(added[["공포일자", "서식명"]])
    else:
        print("✅ 변경 없음")

else:
    print("📂 이전 데이터 없음 — 오늘 데이터가 기준이 됩니다.")

# 5. 오늘 파일 → previous 로 백업 (덮어쓰기)
today_file.replace(previous_file)


# # 메일발송

# In[89]:


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_diff_email(diff_df=None):
    sender_email = "woojung0618@gmail.com"
    receiver_emails = [
        "woojung0618@gmail.com"
    ]
    subject = "[자동알림] 국세청 서식 변경 감지"
    password = "csfynrkgszrqbwbx"  # Gmail 앱 비밀번호 등

    # 제목 설정
    if diff_df is not None and not diff_df.empty:
        change_count = len(diff_df)
        subject = f"[자동알림] 국세청 서식 변경 감지 - {change_count}건 변경"
        html = diff_df.to_html(index=False, escape=False)
        body = f"""
        <html>
            <body>
                <p>총 <strong>{change_count}건</strong>의 변경사항이 감지되었습니다.</p>
                {html}
            </body>
        </html>
        """
    else:
        subject = "[자동알림] 국세청 서식 변경 감지 - 변경 없음"
        body = """
        <html>
            <body>
                <p>이번 달에는 변경된 서식이 없습니다.</p>
            </body>
        </html>
        """

    # 메일 구성
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = ", ".join(receiver_emails)
    msg.attach(MIMEText(body, "html"))

    # 메일 서버 연결 및 발송 (Gmail 기준)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_emails, msg.as_string())
        print("📧 변경사항 메일 발송 완료!")
    except Exception as e:
        print("❌ 메일 발송 실패:", e)


# In[90]:


send_diff_email(added if not added.empty else None)

