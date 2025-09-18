import streamlit as st
import pandas as pd
import random
import json
import os

# ============================
# Load data mengikut tahun
# ============================
@st.cache_data
def load_questions(tahun):
    file_path = f"questions_tahun{tahun}.csv"
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        st.error(f"File {file_path} tidak dijumpai.")
        return pd.DataFrame()

# ============================
# Save progress ke JSON
# ============================
def save_progress(username, tahun, subject, chapter, score, total):
    progress_file = "progress.json"
    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            data = json.load(f)
    else:
        data = {}

    if username not in data:
        data[username] = []

    data[username].append({
        "tahun": tahun,
        "subject": subject,
        "chapter": chapter,
        "score": score,
        "total": total
    })

    with open(progress_file, "w") as f:
        json.dump(data, f, indent=4)

# ============================
# Streamlit UI
# ============================
st.title("📚 Quiz Interaktif Tahun 3 & 5")
st.write("Pilih Tahun → Subjek → Chapter → Jawab Soalan!")

# Input nama anak
username = st.text_input("Masukkan Nama Anak 👇")

# Pilih tahun
tahun = st.selectbox("Pilih Tahun", [3, 5])

# Load soalan ikut tahun
df = load_questions(tahun)

if not df.empty:
    # Pilih subjek
    subject = st.selectbox("Pilih Subjek", df["subject"].unique())

    # Pilih chapter ikut subjek
    chapter_options = df[df["subject"] == subject]["chapter"].unique()
    chapter = st.selectbox("Pilih Chapter", chapter_options)

    # Filter soalan ikut subjek + chapter
    df_filtered = df[(df["subject"] == subject) & (df["chapter"] == chapter)]

    if st.button("Mula Kuiz 🎯"):
        if username == "":
            st.warning("Sila masukkan nama anak dahulu!")
        else:
            score = 0
            total = len(df_filtered)
            
            for i, row in df_filtered.iterrows():
                st.subheader(f"Soalan {i+1}: {row['question']}")
                options = [row['option_a'], row['option_b'], row['option_c'], row['option_d']]
                random.shuffle(options)
                answer = st.radio("Jawapan anda:", options, key=f"q{i}")
                
                if answer == row['answer']:
                    score += 1

            if st.button("Hantar Jawapan ✅"):
                st.success(f"Markah: {score} / {total}")
                save_progress(username, tahun, subject, chapter, score, total)

# Dashboard untuk ibu bapa
st.markdown("---")
st.header("📊 Dashboard Ibu Bapa")

if os.path.exists("progress.json"):
    with open("progress.json", "r") as f:
        progress_data = json.load(f)

    for user, records in progress_data.items():
        st.subheader(f"👦 {user}")
        for r in records:
            st.write(f"Tahun {r['tahun']} | {r['subject']} - {r['chapter']} → {r['score']}/{r['total']}")
else:
    st.info("Belum ada progres direkodkan.")
