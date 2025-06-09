import streamlit as st
import time
from openai import OpenAI

# OpenAI 클라이언트 객체 생성
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# 초기 세션 설정
if "stage" not in st.session_state:
    st.session_state.stage = 1
    st.session_state.lives = 3
    st.session_state.start_time = time.time()
    st.session_state.question = ""
    st.session_state.image_url = ""
    st.session_state.correct = False
    st.session_state.result_checked = False

# ❤️ 목숨 하트 표시
def render_lives():
    hearts = "❤️" * st.session_state.lives + "🖤" * (3 - st.session_state.lives)
    st.markdown(f"### 목숨: {hearts}")

# 🎯 GPT로 문제 생성 (난이도는 스테이지 수 기반)
def generate_question(stage):
    prompt = f"너는 코딩 마법사야. 난이도 {stage}짜리 파이썬 초급 문제 하나만 출제해줘. 짧게 문제 설명만 해줘. 말투는 마법사들이 쓸것 같은 말투로 문제를 내줘."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "당신은 친절한 코딩 마스터 마법사입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# 🧙 마법사 이미지 생성
def generate_wizard_image(stage):
    styles = [
        "digital painting, anime wizard casting fire spell, detailed illustration",
        "digital painting, anime ice mage, detailed illustration",
        "digital painting, cyberpunk wizard, neon highlights",
        "digital painting, shadow wizard, dark fantasy",
        "digital painting, cosmic wizard in galaxy"
    ]
    prompt = styles[(stage - 1) % len(styles)]
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response.data[0].url

# GPT로 코드 평가
def evaluate_answer(question, code):
    prompt = f"문제: {question}\n코드: {code}\n정답이면 YES, 아니면 NO만 대답해."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "채점 마법사입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    return "YES" in response.choices[0].message.content

# 제한시간 설정
TIME_LIMIT = 90

# UI 출력 및 로직
st.title(f"🧙 GPT 마법사와 코딩 RPG - Stage {st.session_state.stage}")
render_lives()

elapsed = int(time.time() - st.session_state.start_time)
remaining = max(0, TIME_LIMIT - elapsed)
st.markdown(f"### ⏱️ 제한시간: {remaining}초")

# 문제 없을 때 새로 생성
if st.session_state.question == "":
    with st.spinner("마법사가 문제를 만들고 있어요..."):
        st.session_state.question = generate_question(st.session_state.stage)
        st.session_state.image_url = generate_wizard_image(st.session_state.stage)
        st.session_state.start_time = time.time()
        st.session_state.result_checked = False

# 이미지 표시 (방어적 처리 추가)
if st.session_state.image_url:
    st.image(st.session_state.image_url, use_column_width=True)
else:
    st.warning("이미지 생성 중입니다...")

st.markdown(f"### ✨ 마법사의 문제: {st.session_state.question}")

code_input = st.text_area("📝 파이썬 코드 입력:")

# 결과 처리
if st.button("제출하기") and not st.session_state.result_checked:
    if remaining <= 0:
        st.session_state.lives -= 1
        st.warning("제한시간 초과로 목숨이 하나 줄어듭니다 💔")
    else:
        with st.spinner("마법사가 채점 중..."):
            correct = evaluate_answer(st.session_state.question, code_input)

        if correct:
            st.success("정답입니다! 다음 스테이지로 진행하세요 ✨")
            st.session_state.correct = True
        else:
            st.session_state.lives -= 1
            st.warning("틀렸습니다! 목숨이 하나 줄어듭니다 💔")

    st.session_state.result_checked = True

# 틀린 경우에도 다음 문제로 넘어가는 버튼 생성
if st.session_state.result_checked:
    if st.button("👉 다음 문제로 이동하기"):
        if st.session_state.correct:
            st.session_state.stage += 1
        st.session_state.question = ""
        st.session_state.correct = False
        st.session_state.start_time = time.time()
        st.session_state.result_checked = False

# 게임 오버 처리
if st.session_state.lives <= 0:
    st.error("💀 GAME OVER 💀 다시 시작하려면 새로고침하세요.")
    st.stop()
