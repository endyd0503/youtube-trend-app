import streamlit as st
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import isodate

# --- 설정 및 API 연결 ---
API_KEY = 'AIzaSyBENckPL5h82KTND9FZ1iNT02xKwLxOmvw' 
youtube = build('youtube', 'v3', developerKey=API_KEY)

st.set_page_config(page_title="유튜브 초간편 트렌드 분석기", layout="wide")
st.title("🚀 유튜브 초간편 트렌드 분석기")
st.caption("최근 10일 이내, 조회수 3만회 이상 롱폼 영상 분석 리스트")

# --- 분석 함수 ---
def get_trending_videos(query, days=10, min_views=30000):
    published_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    
    search_response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=20,
        publishedAfter=published_after,
        type="video",
        relevanceLanguage="ja",
        order="viewCount"
    ).execute()

    video_data = []
    for item in search_response.get('items', []):
        v_id = item['id']['videoId']
        snippet = item['snippet']
        
        v_response = youtube.videos().list(
            id=v_id,
            part="statistics,contentDetails"
        ).execute()
        
        if not v_response['items']: continue
        
        stats = v_response['items'][0]['statistics']
        details = v_response['items'][0]['contentDetails']
        
        views = int(stats.get('view_count', 0))
        duration_sec = isodate.parse_duration(details['duration']).total_seconds()

        # 조건: 조회수 3만 이상 & 롱폼(60초 초과)
        if views >= min_views and duration_sec > 60:
            video_data.append({
                'title': snippet['title'],
                'views': views,
                'link': f"https://youtube.com/watch?v={v_id}",
                'date': snippet['publishedAt'][:10],
                'thumbnail': snippet['thumbnails']['high']['url'], # 고화질 썸네일
                'channel': snippet['channelTitle']
            })
    return video_data

# --- 화면 구성 ---
col1, col2, col3, col4 = st.columns(4)

# 버튼 클릭 이벤트 처리
selected_query = None
if col1.button("🇯🇵 일본 시니어"):
    selected_query = "70대 一人暮らし 老後 年金"
if col2.button("👵 노후 사연"):
    selected_query = "노후 사연 인생 지혜 은퇴후"
if col3.button("⚽ 스포츠"):
    selected_query = "해외반응 손흥민 하이라이트"
if col4.button("🎬 연예"):
    selected_query = "연예인 근황 충격보도"

if selected_query:
    with st.spinner('최신 트렌드 분석 중...'):
        results = get_trending_videos(selected_query)
        
        if results:
            for v in results:
                # 카드형 레이아웃 구성
                with st.container():
                    col_img, col_txt = st.columns([1, 2]) # 썸네일과 텍스트 비율 1:2
                    
                    with col_img:
                        st.image(v['thumbnail'], use_container_width=True)
                    
                    with col_txt:
                        st.subheader(v['title'])
                        st.write(f"📺 채널: **{v['channel']}**")
                        st.write(f"📅 업로드: `{v['date']}`  |  🔥 조회수: **{v['views']:,}회**")
                        st.write(f"[▶️ 영상 보러가기]({v['link']})")
                    st.divider()
        else:
            st.warning("조건에 맞는 영상이 없습니다.")
