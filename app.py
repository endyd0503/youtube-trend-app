import streamlit as st
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import isodate

# --- 설정 및 API 연결 ---
API_KEY = 'AIzaSyBENckPL5h82KTND9FZ1iNT02xKwLxOmvw' 
youtube = build('youtube', 'v3', developerKey=API_KEY)

st.set_page_config(page_title="유튜브 트렌드 분석기", layout="wide")
st.title("🚀 유튜브 섹션별 트렌드 분석기")

def get_trending_videos(query, lang="ko", days=10, min_views=30000):
    published_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    
    search_response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=20,
        publishedAfter=published_after,
        type="video",
        relevanceLanguage=lang,
        order="viewCount"
    ).execute()

    video_data = []
    for item in search_response.get('items', []):
        v_id = item['id']['videoId']
        v_response = youtube.videos().list(id=v_id, part="statistics,contentDetails").execute()
        
        if not v_response['items']: continue
        
        stats = v_response['items'][0]['statistics']
        details = v_response['items'][0]['contentDetails']
        views = int(stats.get('view_count', 0))
        duration_sec = isodate.parse_duration(details['duration']).total_seconds()

        # 조건: 조회수 3만 이상 & 롱폼(1분 초과)
        if views >= min_views and duration_sec > 60:
            video_data.append({
                'title': item['snippet']['title'],
                'views': views,
                'link': f"https://youtube.com/watch?v={v_id}",
                'date': item['snippet']['publishedAt'][:10]
            })
    return video_data

# --- 화면 구성 ---
st.subheader("관심 섹션을 클릭하세요 (최근 10일, 조회수 3만↑)")
col1, col2 = st.columns(2)

# 1. 일본 시니어 섹션 (키워드 보강)
if col1.button("🇯🇵 일본 시니어 롱폼"):
    with st.spinner('일본 트렌드 분석 중...'):
        # 키워드를 더 넓게 잡았습니다 (70대, 혼자살기, 노후, 연금 등)
        results = get_trending_videos("70代 一人暮らし 老後 年金 暮らし", lang="ja") 
        if results:
            for v in results:
                st.write(f"### {v['title']}")
                st.write(f"🔥 조회수: {v['views']:,}회 | 📅 {v['date']}")
                st.write(f"[영상 보기]({v['link']})")
                st.divider()
        else:
            st.warning("현재 조건에 맞는 일본 영상이 없습니다. 조회수 기준을 조금 낮춰보시겠어요?")

# 2. 노후/인생 사연 섹션 (활성화)
if col2.button("👵 노후/인생 사연"):
    with st.spinner('사연 트렌드 분석 중...'):
        # 한국 노후 관련 핵심 키워드
        results = get_trending_videos("노후 사연 인생지혜 자식후회 은퇴생활", lang="ko")
        if results:
            for v in results:
                st.write(f"### {v['title']}")
                st.write(f"🔥 조회수: {v['views']:,}회 | 📅 {v['date']}")
                st.write(f"[영상 보기]({v['link']})")
                st.divider()
        else:
            st.warning("조건에 맞는 한국 사연 영상이 없습니다.")
