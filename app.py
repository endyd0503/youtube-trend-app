import streamlit as st
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import isodate
from deep_translator import GoogleTranslator
import pandas as pd

# --- 설정 및 API 연결 ---
API_KEY = 'AIzaSyBENckPL5h82KTND9FZ1iNT02xKwLxOmvw' 
youtube = build('youtube', 'v3', developerKey=API_KEY)

st.set_page_config(page_title="유튜브 트렌드 분석기", layout="wide")
st.title("🚀 유튜브 섹션별 트렌드 분석기 (범위 확장 버전)")
st.caption("최근 10일 이내 업로드, 조회수 1,000회 이상 영상 (롱폼 전용)")

# --- 번역 함수 ---
def translate_text(text, target_lang='ko'):
    try:
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except:
        return text # 번역 실패 시 원문 유지

# --- 분석 핵심 함수 ---
def get_trending_videos(query, lang="ko", days=10, min_views=1000): # 기준을 1,000회로 낮춤
    published_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    
    try:
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=30, # 더 많은 후보군 검색
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

            # 필터: 조회수 1천 이상 & 롱폼(60초 초과)
            if views >= min_views and duration_sec > 60:
                original_title = item['snippet']['title']
                translated_title = translate_text(original_title) if lang != "ko" else original_title

                video_data.append({
                    '번역제목': translated_title,
                    '원문제목': original_title,
                    '조회수': views,
                    '채널명': item['snippet']['channelTitle'],
                    '게시일': item['snippet']['publishedAt'][:10],
                    '링크': f"https://youtube.com/watch?v={v_id}"
                })
        return video_data
    except Exception as e:
        st.error(f"오류 발생: {e}")
        return []

# --- 화면 구성 ---
st.write("### 분석할 섹션을 선택하세요")
row1 = st.columns(3)
row2 = st.columns(3)

# 키워드를 더 단순하고 강력한 단어로 수정
sections = [
    {"name": "🇯🇵 일본 시니어", "query": "70代 暮らし 一人暮らし", "lang": "ja"},
    {"name": "👵 노후/인생 사연", "query": "노후 사연 인생", "lang": "ko"},
    {"name": "🌍 해외 감동 사연", "query": "감동 실화", "lang": "ko"},
    {"name": "⚽ 스포츠 트렌드", "query": "축구 하이라이트", "lang": "ko"},
    {"name": "🎬 연예 이슈", "query": "연예 근황", "lang": "ko"},
    {"name": "🇰🇷 북한 이야기", "query": "북한 실상", "lang": "ko"}
]

for i, sec in enumerate(sections):
    col = row1[i] if i < 3 else row2[i-3]
    if col.button(sec['name'], use_container_width=True):
        with st.spinner(f"{sec['name']} 분석 중..."):
            results = get_trending_videos(sec['query'], lang=sec['lang'])
            
            if results:
                df = pd.DataFrame(results)
                st.success(f"총 {len(results)}개의 영상을 찾았습니다.")
                
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📂 결과 엑셀(CSV) 다운로드", csv, f"{sec['name']}_결과.csv", "text/csv")
                
                for v in results:
                    with st.expander(f"[{v['조회수']:,}회] {v['번역제목']}"):
                        st.write(f"**원문:** {v['원문제목']}")
                        st.write(f"📺 채널: {v['채널명']} | 📅 {v['게시일']}")
                        st.write(f"🔗 [영상 바로가기]({v['링크']})")
            else:
                st.warning("여전히 조건에 맞는 영상이 없습니다. 키워드를 더 단순하게 바꿔볼까요?")
