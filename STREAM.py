import os
import time
import requests
import re
from discord_webhook import DiscordWebhook

# 치지직 API URL
chzzk_api_url = "https://api.chzzk.naver.com/service/v1/channels/68f895c59a1043bc5019b5e08c83a5c5"

# AfreecaTV 페이지의 URL
afreeca_url = "https://play.afreecatv.com/nanajam/"

# 디스코드 웹 후크 URL
webhook_url = 'https://discord.com/api/webhooks/1213033795578757163/h_1eU9NdiERaZOQBhCI5r6aoOMaXGxp2HiMRDtaKeN-zbhHOa8nvThtkR70r_D3YAyEz'

# 스트리머 이름 설정
streamer_name = "우정잉" if "nanajam" else "Unknown"

# User-Agent 설정
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

#방송 상태를 저장할 변수
live_status_chzzk = None
live_status_afreeca = None

# 무한 반복
while True:
    try:
        # 치지직 API에 GET 요청을 보내 방송 정보를 받음
        response = requests.get(chzzk_api_url, headers=headers)
        # JSON 형식으로 변환
        data = response.json()
        # openLive 부분의 값을 가져옴
        status = data["content"]["openLive"]
        # openLive 부분의 값이 true이면
        if status == True and live_status_chzzk != status: # 이전에 저장한 값과 비교하는 조건을 추가
            # 방송이 켜졌다는 메시지를 생성
            message = f"<@758654943670042674> 라디유님의 치치직 방송이 시작되었습니다! \n링크: https://chzzk.naver.com/live/68f895c59a1043bc5019b5e08c83a5c5"
            # 디스코드 웹 후크에 POST 요청을 보내 메시지를 전송
            requests.post(webhook_url, json={"content": message})
        elif status == False and live_status_chzzk == True: # 이전에 저장한 값과 비교하는 조건을 추가
            # 방송이 꺼졌다는 메시지를 생성
            message = "라디유님의 치치직 방송이 종료되었습니다!"
            # 디스코드 웹 후크에 POST 요청을 보내 메시지를 전송
            requests.post(webhook_url, json={"content": message})
        # openLive 부분의 값을 이전에 저장한 값으로 갱신
        live_status_chzzk = status
        
        
        # 아프리카 URL에 GET 요청을 보내 방송 정보를 받음
        response = requests.get(afreeca_url, headers=headers)

        # URL에서 260으로 시작하는 6자리 숫자를 찾습니다.
        match = re.search(r'260\d{6}', response.text)

        # 숫자를 찾았다면, 스트림이 재생 중인 것으로 판단합니다.
        new_status_afreeca = match is not None

        if new_status_afreeca != live_status_afreeca:
            # 방송 상태가 바뀌었다면, 디스코드에 알림을 보냅니다.
            if new_status_afreeca:
                # 방송이 켜졌다면, 방송이 켜졌다는 메시지를 보냅니다.
                broadcast_link = f"https://play.afreecatv.com/nanajam/{match.group()}"
                webhook = DiscordWebhook(url=webhook_url, content=f"<@758654943670042674> {streamer_name}님의 아프리카 방송이 시작되었습니다! \n링크: {broadcast_link}")
                webhook.execute()
            elif live_status_afreeca is not None:
                # 방송이 꺼졌다면, 방송이 꺼졌다는 메시지를 보냅니다.
                message = f"{streamer_name}님의 방송이 종료되었습니다!"
                webhook = DiscordWebhook(url=webhook_url, content=message)
                webhook.execute()

            # 방송 상태를 갱신합니다.
            live_status_afreeca = new_status_afreeca

        # 각 반복 사이에 약간의 지연 시간을 둡니다.
    except requests.exceptions.ConnectionError as e:
        print(f"A network error occurred: {e}")
        time.sleep(60)  # wait for 60 seconds before retrying

    except requests.exceptions.RequestException as e:
        print(f"A request error occurred: {e}")
        break  # stop the program

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        break  # stop the program