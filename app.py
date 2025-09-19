import streamlit as st
import pandas as pd
import random
import os
from datetime import datetime

# =======================
# Load Questions Function
# =======================
@st.cache_data
def load_questions(tahun):
    file = f"questions_tahun{tahun}.csv"
    if os.path.exists(file):
        return pd.read_csv(file)
    else:
        st.error(f"❌ File {file} tidak dijumpai.")
        return pd.DataFrame()

# =======================
# Save Results Function
# =======================
def save_results(name, score, total, subject, chapter, tahun):
    result_file = "results.csv"
    if os.path.exists(result_file):
        df = pd.read_csv(result_file)
    else:
        df = pd.DataFrame(columns=["Name", "Year", "Subject", "Chapter", "Score", "Total", "Date"])

    new_data = pd.DataFrame([{
        "Name": name,
        "Year": tahun,
        "Subject": subject,
        "Chapter": chapter,
        "Score": score,
        "Total": total,
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    df = pd.concat([df, new_data], ignore_index=True)

    df.to_csv(result_file, index=False)

# =======================
# Main App
# =======================
st.title("📘 Aplikasi Latihan Soalan Tahun 3 & 5")

menu = st.sidebar.radio("Menu", ["Pelajar", "Ibu Bapa"])

# ---------------- Pelajar ----------------
if menu == "Pelajar":
    name = st.text_input("Nama Pelajar")
    tahun = st.selectbox("Pilih Tahun", [3, 5])

    df = load_questions(tahun)

    if not df.empty:
        subject = st.selectbox("Pilih Subjek", df["subject"].unique())
        chapter_options = df[df["subject"] == subject]["chapter"].unique()
        chapter = st.selectbox("Pilih Bab", chapter_options)

        if name and subject and chapter:
            # Filter ikut subjek + chapter
            df_filtered = df[(df["subject"] == subject) & (df["chapter"] == chapter)]

            if df_filtered.empty:
                st.warning("⚠️ Tiada soalan untuk subjek & bab ini.")
            else:
                # Shuffle semua soalan
                df_filtered = df_filtered.sample(frac=1).reset_index(drop=True)

                st.subheader(f"Soalan untuk {subject} - {chapter}")
                answers = {}

                for i, row in df_filtered.iterrows():
                    st.markdown(f"**{i+1}. {row['question']}**")
                    options = [row["option_a"], row["option_b"], row["option_c"], row["option_d"]]
                    random.shuffle(options)
                    answer = st.radio("Jawapan:", options, key=f"q{i}")
                    answers[i] = {"selected": answer, "correct": row["answer"]}

                if st.button("Hantar Jawapan"):
                    score = 0
                    for i in answers:
                        if answers[i]["selected"].strip().lower() == answers[i]["correct"].strip().lower():
                            score += 1

                    total = len(answers)
                    st.success(f"✅ Markah: {score}/{total} ({(score/total)*100:.1f}%)")

                    save_results(name, score, total, subject, chapter, tahun)

# ---------------- Ibu Bapa ----------------
elif menu == "Ibu Bapa":
    st.header("📊 Dashboard Ibu Bapa")

    result_file = "results.csv"
    if os.path.exists(result_file):
        df = pd.read_csv(result_file)

        st.dataframe(df)

        if not df.empty:
            avg_score = df["Score"].sum() / df["Total"].sum() * 100
            st.metric("Purata Prestasi Keseluruhan", f"{avg_score:.2f}%")
    else:
        st.info("❌ Belum ada rekod jawapan pelajar.")
