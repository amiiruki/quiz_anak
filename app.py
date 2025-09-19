import streamlit as st
import pandas as pd
import random
import os
from datetime import datetime

# =======================
# Load Questions Function
# =======================
@st.cache_data
def load_questions(file):
    df = pd.read_csv(file)
    return df

# =======================
# Save Results Function
# =======================
def save_results(name, score, total, subject, chapter):
    result_file = "results.csv"
    if os.path.exists(result_file):
        df = pd.read_csv(result_file)
    else:
        df = pd.DataFrame(columns=["Name", "Subject", "Chapter", "Score", "Total", "Date"])

    new_data = pd.DataFrame([{
        "Name": name,
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
st.title("📘 Aplikasi Latihan Soalan Tahun 5")

menu = st.sidebar.radio("Menu", ["Pelajar", "Ibu Bapa"])

# ---------------- Pelajar ----------------
if menu == "Pelajar":
    name = st.text_input("Nama Pelajar")
    subject = st.selectbox("Pilih Subjek", ["Ibadah", "Tauhid"])
    chapter = st.selectbox("Pilih Bab", ["Solat", "Rukun Iman"])

    if name and subject and chapter:
        df = load_questions("questions_tahun5.csv")

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
                options = [row["option1"], row["option2"], row["option3"], row["option4"]]
                answer = st.radio("Jawapan:", options, key=f"q{i}")
                answers[i] = {"selected": answer, "correct": row["answer"]}

            if st.button("Hantar Jawapan"):
                score = 0
                for i in answers:
                    if answers[i]["selected"] == answers[i]["correct"]:
                        score += 1

                total = len(answers)
                st.success(f"✅ Markah: {score}/{total}")

                save_results(name, score, total, subject, chapter)

# ---------------- Ibu Bapa ----------------
elif menu == "Ibu Bapa":
    st.header("📊 Dashboard Ibu Bapa")

    result_file = "results.csv"
    if os.path.exists(result_file):
        df = pd.read_csv(result_file)

        st.dataframe(df)

        avg_score = df["Score"].sum() / df["Total"].sum() * 100 if not df.empty else 0
        st.metric("Purata Prestasi Keseluruhan", f"{avg_score:.2f}%")

    else:
        st.info("❌ Belum ada rekod jawapan pelajar.")
