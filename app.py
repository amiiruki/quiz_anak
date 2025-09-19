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
            try:
                data = json.load(f)
            except:
                data = {}
    else:
        data = {}

    data.setdefault(username, {})
    data[username].setdefault(str(tahun), {})
    data[username][str(tahun)].setdefault(subject, {})
    
    # Simpan/update score untuk chapter
    data[username][str(tahun)][subject][chapter] = {"score": score, "total": total}

    with open(progress_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

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
    
    # Shuffle soalan
    df_filtered = df_filtered.sample(frac=1).reset_index(drop=True)

    if username != "":
        st.markdown("### Soalan")
        
        # ============================
        # Form untuk jawapan quiz
        # ============================
        with st.form("quiz_form"):
            for i, row in df_filtered.iterrows():
                st.subheader(f"Soalan {i+1}: {row['question']}")
                options = [row['option_a'], row['option_b'], row['option_c'], row['option_d']]
                random.shuffle(options)
                st.radio("Jawapan anda:", options, key=f"q{i}")
            
            submitted = st.form_submit_button("Hantar Jawapan ✅")
        
        if submitted:
            score = 0
            total = len(df_filtered)
            for i, row in df_filtered.iterrows():
                user_answer = st.session_state.get(f"q{i}")
                if user_answer == row['answer']:
                    score += 1
            st.success(f"Markah: {score}/{total} ({(score/total)*100:.1f}%)")
            save_progress(username, tahun, subject, chapter, score, total)
    else:
        st.warning("Sila masukkan nama anak dahulu!")

# ============================
# Dashboard untuk ibu bapa
# ============================
st.markdown("---")
st.header("📊 Dashboard Ibu Bapa")

if os.path.exists("progress.json"):
    with open("progress.json", "r", encoding="utf-8") as f:
        try:
            progress_data = json.load(f)
        except:
            progress_data = {}

    for user, records in progress_data.items():
        st.subheader(f"👦 {user}")
        for year, subjects in records.items():
            for subj, chapters in subjects.items():
                for chap, score_data in chapters.items():
                    score = score_data["score"]
                    total = score_data["total"]
                    percentage = (score / total) * 100
                    st.write(f"Tahun {year} | {subj} - {chap} → {score}/{total} ({percentage:.1f}%)")
else:
    st.info("Belum ada progres direkodkan.")
