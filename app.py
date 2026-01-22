import streamlit as st
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import isodate

# --- 설정 및 API 연결 ---
API_KEY = 'AIzaSyBENckPL5h82KTND9FZ1iNT02xKwLxOmvw' 
youtube = build('youtube', 'v3', developerKey=API_KEY)

st.set_page_config(page_title="유튜브 트렌드 분석기", layout="wide")

st.title("유튜브 트렌드 분석기")
st.info("최근 30일 이내 | 3,000회 이상 우선 검색 | 썸네일 크기 최적화 버전")

# --- 분석 함수 ---
def get_trending_videos(query, days=30, min_views=3000):
    published_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    
    try:
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=30,
            publishedAfter=published_after,
            type="video",
            order="viewCount" 
        ).execute()
    except Exception as e:
        st.error(f"API 호출 오류: {e}")
        return []

    video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
    if not video_ids: return []

    v_response = youtube.videos().list(
        id=','.join(video_ids),
        part="statistics,contentDetails,snippet"
    ).execute()

    video_data = []
    for v_item in v_response.get('items', []):
        stats = v_item['statistics']
        details = v_item['contentDetails']
        snippet = v_item['snippet']
        
        views = int(stats.get('view_count', 0))
        duration_sec = isodate.parse_duration(details['duration']).total_seconds()

        if duration_sec > 60:
            video_data.append({
                'title': snippet['title'],
                'views': views,
                'link': f"https://youtube.com/watch?v={v_item['id']}",
                'date': snippet['publishedAt'][:10],
                'thumbnail': snippet['thumbnails']['medium']['url'], # 화질을 medium으로 낮춰 크기 조절 용이하게 함
                'channel': snippet['channelTitle']
            })

    filtered_data = [v for v in video_data if v['views'] >= min_views]
    if not filtered_data:
        return sorted(video_data, key=lambda x: x['views'], reverse=True)[:10]
    
    return sorted(filtered_data, key=lambda x: x['views'], reverse=True)

# --- 카테고리 버튼 ---
st.write("---")
st.subheader("관심 섹션을 클릭하세요")
row = st.columns(6) # 버튼을 한 줄에 더 많이 배치

categories = {
    "일본 시니어": "70代 60代 一人暮らし 老後 年金 暮らし",
    "노후 사연": "노후 사연 인생 조언 은퇴 지혜",
    "북한 이야기": "북한 실상 탈북 근황 북한여자",
    "해외 감동": "해외 감동 실화 스토리",
    "스포츠": "해외반응 스포츠 하이라이트",
    "연예 이슈": "연예인 근황 소식 뉴스"
}

selected_query = None
for i, (name, query) in enumerate(categories.items()):
    if row[i].button(name, use_container_width=True):
        selected_query = query

# --- 결과 출력 (썸네일 크기 축소 레이아웃) ---
if selected_query:
    st.write("---")
    with st.spinner('데이터를 불러오고 있습니다...'):
        results = get_trending_videos(selected_query)
        
        if results:
            for v in results:
                with st.container():
                    # 컬럼 비율 조정 (썸네일 1 : 텍스트 4) -> 사진 크기가 확 줄어듭니다.
                    col_img, col_txt = st.columns([1, 4]) 
                    
                    with col_img:
                        # 이미지를 작게 표시하기 위해 width를 지정하거나 레이아웃 비율로 조절
                        st.image(v['thumbnail'], use_container_width=True)
                    
                    with col_txt:
                        st.markdown(f"**[{v['title']}]({v['link']})**")
                        st.caption(f"채널: {v['channel']} | 일자: {v['date']} | 조회수: {v['views']:,}회")
                    st.divider()
        else:
            st.warning("영상을 불러오지 못했습니다.")
