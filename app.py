import streamlit as st
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import isodate

# --- 설정 및 API 연결 ---
# 사용자의 API 키 적용
API_KEY = 'AIzaSyBENckPL5h82KTND9FZ1iNT02xKwLxOmvw' 
youtube = build('youtube', 'v3', developerKey=API_KEY)

st.set_page_config(page_title="유튜브 트렌드 분석기", layout="wide")

st.title("유튜브 트렌드 분석기")
st.info("현재 설정: 최근 30일 이내 업로드 | 조회수 3,000회 이상 | 롱폼 영상 전용")

# --- 분석 함수 (기준: 30일, 3000회) ---
def get_trending_videos(query, days=30, min_views=3000):
    published_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    
    # 영상 검색
    search_response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=30, # 한 번에 검색할 최대 개수
        publishedAfter=published_after,
        type="video",
        order="viewCount" # 조회수 높은 순으로 정렬 요청
    ).execute()

    video_data = []
    for item in search_response.get('items', []):
        v_id = item['id']['videoId']
        snippet = item['snippet']
        
        # 상세 데이터 가져오기 (조회수, 영상 길이)
        v_response = youtube.videos().list(id=v_id, part="statistics,contentDetails").execute()
        if not v_response['items']: continue
        
        stats = v_response['items'][0]['statistics']
        details = v_response['items'][0]['contentDetails']
        
        views = int(stats.get('view_count', 0))
        # 영상 길이 변환 (쇼츠 제외용)
        duration_sec = isodate.parse_duration(details['duration']).total_seconds()

        # 필터: 조회수 3000회 이상 & 60초 초과 영상만
        if views >= min_views and duration_sec > 60:
            video_data.append({
                'title': snippet['title'],
                'views': views,
                'link': f"https://youtube.com/watch?v={v_id}",
                'date': snippet['publishedAt'][:10],
                'thumbnail': snippet['thumbnails']['high']['url'],
                'channel': snippet['channelTitle']
            })
    return video_data

# --- 카테고리 버튼 (한글 전용) ---
st.write("---")
st.subheader("관심 섹션을 클릭하세요")
row1 = st.columns(3)
row2 = st.columns(3)

selected_query = None

with row1[0]:
    if st.button("일본 시니어", use_container_width=True):
        # 일본 시니어 롱폼 타겟 키워드 보강
        selected_query = "70代 一人暮らし 老後 年金 ライフスタイル"
with row1[1]:
    if st.button("노후 사연", use_container_width=True):
        selected_query = "노후 사연 인생 지혜 은퇴"
with row1[2]:
    if st.button("북한 이야기", use_container_width=True):
        selected_query = "북한 실상 탈북민 근황"

with row2[0]:
    if st.button("해외 감동 사연", use_container_width=True):
        selected_query = "해외 감동 실화 감동 스토리"
with row2[1]:
    if st.button("스포츠", use_container_width=True):
        selected_query = "스포츠 하이라이트 주요장면"
with row2[2]:
    if st.button("연예 이슈", use_container_width=True):
        selected_query = "연예인 근황 충격 소식"

# --- 결과 출력 ---
if selected_query:
    st.write("---")
    with st.spinner('영상을 찾고 있습니다...'):
        results = get_trending_videos(selected_query)
        
        if results:
            st.success(f"조건에 맞는 영상을 {len(results)}개 찾았습니다.")
            for v in results:
                # 가독성 높은 카드 형태 레이아웃
                with st.container():
                    col_img, col_txt = st.columns([1.5, 2]) # 썸네일 크기 확보
                    
                    with col_img:
                        st.image(v['thumbnail'], use_container_width=True)
                    
                    with col_txt:
                        st.markdown(f"### [🔗 {v['title']}]({v['link']})")
                        st.write(f"🏢 **채널명:** {v['channel']}")
                        st.write(f"📅 **업로드 일자:** {v['date']}")
                        st.write(f"🔥 **현재 조회수:** {v['views']:,}회")
                        st.markdown(f"[**▶️ 영상 바로가기**]({v['link']})")
                    st.divider() # 영상 간 구분선
        else:
            st.warning("최근 30일 이내에 조회수 3,000회를 넘긴 영상이 검색되지 않습니다.")
