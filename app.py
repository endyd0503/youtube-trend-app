import streamlit as st
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import isodate

# --- 설정 및 API 연결 ---
API_KEY = 'AIzaSyBENckPL5h82KTND9FZ1iNT02xKwLxOmvw' # 제공해주신 키 적용
youtube = build('youtube', 'v3', developerKey=API_KEY)

st.set_page_config(page_title="유튜브 트렌드 분석기", layout="wide")
st.title("🚀 유튜브 섹션별 트렌드 분석기")

# --- 분석 함수 ---
def get_trending_videos(query, days=10, min_views=30000):
    published_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    
    # 1. 영상 검색
    search_response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=20, # 한 번에 가져올 개수
        publishedAfter=published_after,
        type="video",
        relevanceLanguage="ja",
        order="viewCount"
    ).execute()

    video_data = []
    for item in search_response.get('items', []):
        v_id = item['id']['videoId']
        
        # 2. 상세 정보(조회수, 영상 길이) 가져오기
        v_response = youtube.videos().list(
            id=v_id,
            part="statistics,contentDetails"
        ).execute()
        
        stats = v_response['items'][0]['statistics']
        details = v_response['items'][0]['contentDetails']
        
        views = int(stats.get('view_count', 0))
        # ISO 8601 지속 시간 형식을 초 단위로 변환
        duration_sec = isodate.parse_duration(details['duration']).total_seconds()

        # 조건 필터링: 조회수 3만 이상 & 영상 길이 60초 초과(롱폼)
        if views >= min_views and duration_sec > 60:
            video_data.append({
                'title': item['snippet']['title'],
                'views': views,
                'link': f"https://youtube.com/watch?v={v_id}",
                'date': item['snippet']['publishedAt'][:10]
            })
    return video_data

# --- 화면 구성 (버튼) ---
st.subheader("관심 섹션을 클릭하세요")
col1, col2, col3, col4 = st.columns(4)

if col1.button("🇯🇵 일본 시니어 롱폼"):
    with st.spinner('데이터 분석 중...'):
        # 일본 시니어 타겟 핵심 키워드 조합
        results = get_trending_videos("70代 一人暮らし 老後 年금") 
        
        if results:
            for v in results:
                with st.container():
                    st.write(f"### {v['title']}")
                    st.write(f"📅 게시일: {v['date']}  |  🔥 조회수: {v['views']:,}회")
                    st.write(f"[영상 보러가기]({v['link']})")
                    st.divider()
        else:
            st.warning("조건에 맞는 영상이 없습니다.")

if col2.button("👵 노후/인생 사연"):
    st.info("키워드 세팅 후 바로 활성화 가능합니다.")

# 나머지 버튼들도 동일한 방식으로 추가 가능
