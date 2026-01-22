import streamlit as st
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import isodate
from deep_translator import GoogleTranslator

# --- 설정 및 API 연결 ---
API_KEY = 'AIzaSyBENckPL5h82KTND9FZ1iNT02xKwLxOmvw' 
youtube = build('youtube', 'v3', developerKey=API_KEY)

st.set_page_config(page_title="유튜브 트렌드 분석기", layout="wide")
st.title("🚀 유튜브 섹션별 트렌드 분석기")
st.caption("최근 10일 이내 업로드, 조회수 10,000회 이상 영상 (롱폼 전용)")

# --- 번역 함수 ---
def translate_text(text, target_lang='ko'):
    try:
        # 일본어 등 외국어를 한국어로 번역
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except:
        return "번역 오류"

# --- 분석 핵심 함수 ---
def get_trending_videos(query, lang="ko", days=10, min_views=10000):
    published_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    
    try:
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=25,
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

            if views >= min_views and duration_sec > 60:
                original_title = item['snippet']['title']
                
                # 일본어 섹션이거나 제목에 외국어가 섞인 경우 번역 수행
                translated_title = translate_text(original_title) if lang != "ko" else original_title

                video_data.append({
                    'original_title': original_title,
                    'translated_title': translated_title,
                    'views': views,
                    'link': f"https://youtube.com/watch?v={v_id}",
                    'date': item['snippet']['publishedAt'][:10],
                    'channel': item['snippet']['channelTitle']
                })
        return video_data
    except Exception as e:
        st.error(f"오류 발생: {e}")
        return []

# --- 화면 구성 ---
st.write("### 분석할 섹션을 선택하세요")
row1 = st.columns(3)
row2 = st.columns(3)

sections = [
    {"name": "🇯🇵 일본 시니어", "query": "70代 一人暮らし 老後 年金 暮らし", "lang": "ja"},
    {"name": "👵 노후/인생 사연", "query": "노후 사연 인생지혜 은퇴후회", "lang": "ko"},
    {"name": "🌍 해외 감동 사연", "query": "해외 감동 실화 감동스토리 훈훈한", "lang": "ko"},
    {"name": "⚽ 스포츠 트렌드", "query": "스포츠 하이라이트 해외반응 국뽕", "lang": "ko"},
    {"name": "🎬 연예 이슈", "query": "연예인 근황 소식 단독공개", "lang": "ko"},
    {"name": "🇰🇷 북한 이야기", "query": "북한 실상 탈북민 증언 김정은", "lang": "ko"}
]

for i, sec in enumerate(sections):
    col = row1[i] if i < 3 else row2[i-3]
    if col.button(sec['name'], use_container_width=True):
        with st.spinner(f"{sec['name']} 분석 중... 잠시만 기다려주세요."):
            results = get_trending_videos(sec['query'], lang=sec['lang'])
            
            if results:
                st.success(f"총 {len(results)}개의 영상을 찾았습니다.")
                for v in results:
                    # 번역된 제목을 메인으로 보여주고 원문은 아래에 병기
                    with st.expander(f"[{v['views']:,}회] {v['translated_title']}"):
                        if v['original_title'] != v['translated_title']:
                            st.write(f"**원문:** {v['original_title']}")
                        st.write(f"📺 채널: {v['channel']}")
                        st.write(f"📅 게시일: {v['date']}")
                        st.write(f"🔗 [영상 바로가기]({v['link']})")
            else:
                st.warning("조건에 맞는 영상이 없습니다.")
