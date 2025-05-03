# nts-alarm
### 국세법령정보 법령 양식 변경안 메일 알림

국세청 사이트에서 국세법령정보 법령 양식 변경안이 있을 경우 메일로 선감지 메일을 송신한다.



1. Selenium 을 활용한 동적 스크래핑

  - 크롤링 대상 사이트: [국세청](https://www.nts.go.kr/search/search.jsp)


2. 메일링을 통해 변경안 사전알림

  - 변경사항 있을 경우
    <img width="1171" alt="스크린샷 2025-05-04 오전 12 37 58" src="https://github.com/user-attachments/assets/e87cc7c0-fe56-4360-8f4d-26175e9fdecb" />

  - 변경사항 없을 경우
    <img width="1171" alt="스크린샷 2025-05-04 오전 12 39 07" src="https://github.com/user-attachments/assets/bf275dd7-9950-4a89-a08f-0000c9c81c16" />


3. cron 스케줄링
  - 매주 월요일마다 스케줄러 실행
   
