import streamlit as st
from gtts import gTTS
from deep_translator import GoogleTranslator
from supabase import create_client
import os

# =============================
# Supabase接続
# =============================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =============================
# 翻訳モデル（googletrans回避）
# =============================
@st.cache_resource
def get_translator():
    return GoogleTranslator(source="en", target="ja")

translator = get_translator()

# =============================
# 日本語意味取得
# =============================
def get_japanese_meaning(word):
    try:
        ja = translator.translate(word)
        return ja.strip() if ja else "N/A"
    except Exception:
        return "N/A"

# =============================
# 発音生成
# =============================
def generate_audio(word):
    tts = gTTS(text=word, lang="en")
    file_path = f"{word}.mp3"
    tts.save(file_path)
    return file_path

# =============================
# Supabase保存
# =============================
def save_word(word, meaning):
    try:
        supabase.table("words").insert({
            "word": word,
            "meaning": meaning
        }).execute()
        return True
    except Exception as e:
        st.error(f"保存エラー: {e}")
        return False

# =============================
# Supabase取得
# =============================
def load_words():
    try:
        response = supabase.table("words").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"取得エラー: {e}")
        return []

# =============================
# UI
# =============================
st.title("🎧 英単語 発音＋意味＋保存アプリ")

word = st.text_input("英単語を入力")

if st.button("実行"):
    if word:
        # 意味取得
        meaning = get_japanese_meaning(word)

        # 表示
        st.subheader("意味")
        st.write(meaning)

        # 発音
        audio_file = generate_audio(word)
        st.audio(audio_file)

        # 保存
        if save_word(word, meaning):
            st.success("保存しました")

# =============================
# 保存一覧
# =============================
st.subheader("📚 保存した単語")

words = load_words()

if words:
    for w in words:
        st.write(f"{w['word']} : {w['meaning']}")
else:
    st.write("まだ保存されていません")