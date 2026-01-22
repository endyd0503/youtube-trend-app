import streamlit as st
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import isodate

# --- 설정 및 API 연결 ---
API_KEY = 'AIzaSyBENckPL5h82KTND9FZ1iNT02xKwLxOmvw' 
youtube = build('youtube', 'v3', developerKey=API_KEY)

st.set_page_config(page_title="유튜브 트렌드 분석기", layout="wide")
st.title("🚀 유튜브 초간편 트렌드 분석기")
st.caption("최근 30일 이내, 조회수 상관없이 모든 롱폼 영상 검색 테스트")

def get_videos(query, lang="ko"):
    # 기간을 30일로 늘려 데이터가 반드시 나오게 설정
    published_after = (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z"
    
    try:
        # 검색 필터 최소화
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=10,
            publishedAfter=published_after,
            type="video",
            order="viewCount"
        ).execute()

        video_data = []
        for item in search_response.get('items', []):
            v_id = item['id']['videoId']
            # 영상 길이만 체크 (쇼츠 제외)
            v_res = youtube.videos().list(id=v_id, part="contentDetails,statistics").execute()
            if not v_res['items']: continue
            
            details = v_res['items'][0]['contentDetails']
            stats = v_res['items'][0]['statistics']
            duration_sec = isodate.parse_duration(details['duration']).total_seconds()
            views = int(stats.get('view_count', 0))

            if duration_sec > 60: # 1분 넘는 영상만
                video_data.append({
                    'title': item['snippet']['title'],
                    'views': views,
                    'link': f"https://youtube.com/watch?v={v_id}",
                    'channel': item['snippet']['channelTitle']
                })
        return video_data
    except Exception as e:
        st.error(f"API 호출 중 오류 발생: {e}")
        return []

# --- 단순화된 섹션 버튼 ---
cols = st.columns(3)
sections = [
    {"name": "일본 시니어", "query": "70代 暮らし"},
    {"name": "노후 사연", "query": "노후 사연"},
    {"name": "해외 감동", "query": "감동 실화"},
    {"name": "스포츠", "query": "축구 하이라이트"},
    {"name": "연예", "query": "연예 근황"},
    {"name": "북한", "query": "북한 실상"}
]

for i, sec in enumerate(sections):
    if cols[i % 3].button(sec['name'], use_container_width=True):
        with st.spinner('검색 중...'):
            results = get_videos(sec['query'])
            if results:
                for v in results:
                    st.write(f"**[{v['views']:,}회]** {v['title']}")
                    st.write(f"🔗 [영상 보기]({v['link']}) (채널: {v['channel']})")
                    st.divider()
            else:
                st.warning("데이터를 가져오지 못했습니다. API 한도를 확인하세요.")
