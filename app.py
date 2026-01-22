import streamlit as st
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import isodate

# --- 설정 및 API 연결 ---
API_KEY = 'AIzaSyBENckPL5h82KTND9FZ1iNT02xKwLxOmvw' 
youtube = build('youtube', 'v3', developerKey=API_KEY)

st.set_page_config(page_title="유튜브 트렌드 분석기", layout="wide")

st.title("유튜브 트렌드 분석기")
st.info("현재 설정: 최근 30일 이내 업로드 | 3,000회 이상 우선 검색 (미검색 시 하향 조정) | 롱폼 영상")

# --- 분석 함수 (검색 실패 시 기준 자동 완화) ---
def get_trending_videos(query, days=30, min_views=3000):
    published_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    
    # 1. 1차 검색 (조회수 높은 순)
    try:
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=50, # 검색 풀을 더 넓게 잡음
            publishedAfter=published_after,
            type="video",
            order="viewCount" 
        ).execute()
    except Exception as e:
        st.error(f"API 호출 오류: {e}")
        return []

    video_data = []
    items = search_response.get('items', [])
    
    if not items:
        return []

    # 상세 데이터 분석
    for item in items:
        v_id = item['id']['videoId']
        snippet = item['snippet']
        
        v_response = youtube.videos().list(id=v_id, part="statistics,contentDetails").execute()
        if not v_response['items']: continue
        
        stats = v_response['items'][0]['statistics']
        details = v_response['items'][0]['contentDetails']
        
        views = int(stats.get('view_count', 0))
        duration_sec = isodate.parse_duration(details['duration']).total_seconds()

        # 필터: 롱폼(60초 초과)만 수집 (조회수는 일단 다 담음)
        if duration_sec > 60:
            video_data.append({
                'title': snippet['title'],
                'views': views,
                'link': f"https://youtube.com/watch?v={v_id}",
                'date': snippet['publishedAt'][:10],
                'thumbnail': snippet['thumbnails']['high']['url'],
                'channel': snippet['channelTitle']
            })

    # 2. 필터링 로직: 3000회 이상이 없으면 그냥 조회수 순으로 다 보여줌
    filtered_data = [v for v in video_data if v['views'] >= min_views]
    
    if not filtered_data:
        # 3000회 이상이 한 개도 없으면 상위 10개 그냥 표시
        return sorted(video_data, key=lambda x: x['views'], reverse=True)[:10]
    
    return sorted(filtered_data, key=lambda x: x['views'], reverse=True)

# --- 카테고리 버튼 (키워드 대폭 확장) ---
st.write("---")
st.subheader("관심 섹션을 클릭하세요")
row1 = st.columns(3)
row2 = st.columns(3)

selected_query = None

# 키워드 조합을 더 포괄적으로 변경 (띄어쓰기 활용)
with row1[0]:
    if st.button("일본 시니어", use_container_width=True):
        selected_query = "70代 60代 一人暮らし 老後 年金 暮らし" # 60대 및 생활 전반으로 확장
with row1[1]:
    if st.button("노후 사연", use_container_width=True):
        selected_query = "노후 사연 인생 조언 은퇴 지혜"
with row1[2]:
    if st.button("북한 이야기", use_container_width=True):
        selected_query = "북한 실상 탈북 근황 북한여자"

with row2[0]:
    if st.button("해외 감동 사연", use_container_width=True):
        selected_query = "해외 감동 실화 스토리 눈물"
with row2[1]:
    if st.button("스포츠", use_container_width=True):
        selected_query = "해외반응 스포츠 하이라이트"
with row2[2]:
    if st.button("연예 이슈", use_container_width=True):
        selected_query = "연예인 근황 소식 뉴스"

# --- 결과 출력 ---
if selected_query:
    st.write("---")
    with st.spinner('실시간 데이터를 분석 중입니다...'):
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
            st.warning("영상을 불러오지 못했습니다. 잠시 후 다시 시도하거나 키워드를 확인해 주세요.")
