import streamlit as st
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import isodate

# --- 설정 및 API 연결 ---
API_KEY = 'AIzaSyBENckPL5h82KTND9FZ1iNT02xKwLxOmvw' 
youtube = build('youtube', 'v3', developerKey=API_KEY)

st.set_page_config(page_title="유튜브 트렌드 분석기", layout="wide")

st.title("유튜브 트렌드 분석기")
st.info("현재 설정: 최근 30일 이내 업로드 | 3,000회 이상 우선 검색 | 실시간 조회수 보정 완료")

# --- 분석 함수 (실시간 조회수 데이터 강제 호출) ---
def get_trending_videos(query, days=30, min_views=3000):
    published_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    
    try:
        # 1. 검색 결과 가져오기
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
    
    if not video_ids:
        return []

    # 2. 영상 ID 리스트를 사용하여 상세 정보(조회수, 길이) 한 번에 다시 요청
    # 이 과정이 있어야 '조회수 0' 문제를 해결할 수 있습니다.
    v_response = youtube.videos().list(
        id=','.join(video_ids),
        part="statistics,contentDetails,snippet"
    ).execute()

    video_data = []
    for v_item in v_response.get('items', []):
        stats = v_item['statistics']
        details = v_item['contentDetails']
        snippet = v_item['snippet']
        
        # 실제 실시간 조회수 추출
        views = int(stats.get('view_count', 0))
        duration_sec = isodate.parse_duration(details['duration']).total_seconds()

        # 필터: 롱폼(60초 초과)만 수집
        if duration_sec > 60:
            video_data.append({
                'title': snippet['title'],
                'views': views,
                'link': f"https://youtube.com/watch?v={v_item['id']}",
                'date': snippet['publishedAt'][:10],
                'thumbnail': snippet['thumbnails']['high']['url'],
                'channel': snippet['channelTitle']
            })

    # 조회수 기준 필터링 (결과가 너무 적으면 상위 노출)
    filtered_data = [v for v in video_data if v['views'] >= min_views]
    
    if not filtered_data:
        return sorted(video_data, key=lambda x: x['views'], reverse=True)[:10]
    
    return sorted(filtered_data, key=lambda x: x['views'], reverse=True)

# --- 카테고리 버튼 ---
st.write("---")
st.subheader("관심 섹션을 클릭하세요")
row1 = st.columns(3)
row2 = st.columns(3)

selected_query = None

with row1[0]:
    if st.button("일본 시니어", use_container_width=True):
        selected_query = "70代 60代 一人暮らし 老後 年金 暮らし"
with row1[1]:
    if st.button("노후 사연", use_container_width=True):
        selected_query = "노후 사연 인생 조언 은퇴 지혜"
with row1[2]:
    if st.button("북한 이야기", use_container_width=True):
        selected_query = "북한 실상 탈북 근황 북한여자"

with row2[0]:
    if st.button("해외 감동 사연", use_container_width=True):
        selected_query = "해외 감동 실화 스토리"
with row2[1]:
    if st.button("스포츠", use_container_width=True):
        selected_query = "해외반응 스포츠 하이라이트"
with row2[2]:
    if st.button("연예 이슈", use_container_width=True):
        selected_query = "연예인 근황 소식 뉴스"

# --- 결과 출력 ---
if selected_query:
    st.write("---")
    with st.spinner('정확한 실시간 조회수를 가져오는 중입니다...'):
        results = get_trending_videos(selected_query)
        
        if results:
            st.success(f"조회수가 높은 영상을 {len(results)}개 찾았습니다.")
            for v in results:
                with st.container():
                    col_img, col_txt = st.columns([1.5, 2])
                    with col_img:
                        st.image(v['thumbnail'], use_container_width=True)
                    with col_txt:
                        st.markdown(f"### [🔗 {v['title']}]({v['link']})")
                        st.write(f"🏢 **채널:** {v['channel']}")
                        st.write(f"📅 **일자:** {v['date']}  |  🔥 **조회수:** {v['views']:,}회")
                        st.markdown(f"[**▶️ 영상 보기**]({v['link']})")
                    st.divider()
        else:
            st.warning("영상을 불러오지 못했습니다.")
