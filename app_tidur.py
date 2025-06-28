import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import os
import datetime

# --- Load Dataset & Model ---
data = pd.read_csv('kualitas_tidur.csv')
X = data[['Durasi_Tidur', 'Tingkat_Stres', 'Kafein', 'Olahraga']]
y = data['Kualitas_Tidur']

model = LinearRegression()
model.fit(X, y)

# --- Setup ---
st.set_page_config(page_title="Prediksi Kualitas Tidur", page_icon="🌙", layout="centered")
st.markdown("""
    <div style="text-align:center; padding: 20px 10px;">
        <h1 style="color:#2E86C1;">🌙 Prediksi Kualitas Tidur</h1>
        <p style="font-size:18px; color:#555;">Gunakan model machine learning sederhana untuk mengetahui seberapa baik kualitas tidur Anda!</p>
    </div>
""", unsafe_allow_html=True)

# --- Input Form ---
with st.form("form_prediksi"):
    col1, col2 = st.columns(2)
    with col1:
        durasi = st.slider("🕒 Durasi Tidur (jam)", 4, 10, 7)
        kafein = st.slider("☕ Konsumsi Kafein (0-5)", 0, 5, 2)
    with col2:
        stres = st.slider("😫 Tingkat Stres (1-10)", 1, 10, 5)
        olahraga = st.slider("🏃‍♂️ Frekuensi Olahraga (per minggu)", 0, 7, 3)

    submit = st.form_submit_button("🔍 Prediksi Sekarang")

# --- Inisialisasi sesi untuk grafik ---
if "riwayat" not in st.session_state:
    st.session_state.riwayat = pd.DataFrame(columns=["Tanggal", "Skor"])

# --- Prediksi ---
if submit:
    input_data = pd.DataFrame({
        'Durasi_Tidur': [durasi],
        'Tingkat_Stres': [stres],
        'Kafein': [kafein],
        'Olahraga': [olahraga]
    })

    prediksi = model.predict(input_data)[0]
    skor = round(prediksi, 2)

    # Kategori
    if skor >= 8:
        tingkat = '😴 Sangat Baik'
        warna = '#27AE60'
    elif skor >= 6:
        tingkat = '🙂 Baik'
        warna = '#2980B9'
    elif skor >= 4:
        tingkat = '😐 Cukup'
        warna = '#F39C12'
    else:
        tingkat = '😟 Buruk'
        warna = '#E74C3C'

    # Tampilkan Hasil
    st.markdown("---")
    st.markdown(f"""
        <div style="padding:20px; border-radius:10px; border: 2px solid {warna};">
            <h2 style="color:{warna}; text-align:center;">Skor Kualitas Tidur: {skor}/10</h2>
            <h3 style="text-align:center;">Tingkat: {tingkat}</h3>
            <div style="text-align:center;">
                <progress value="{skor}" max="10" style="width: 100%; height: 20px;"></progress>
            </div>
        </div>
    """, unsafe_allow_html=True)
    # --- Rekomendasi Otomatis ---
    st.markdown("## 💬 Rekomendasi Personal")
    if skor < 4:
        st.error("⚠️ Kualitas tidur kamu sangat rendah. Cobalah atur ulang jadwal tidur dan hindari stres berat.")
    elif skor < 6:
        st.warning("😟 Kualitas tidur masih kurang. Kurangi konsumsi kafein, tingkatkan olahraga ringan.")
    elif skor < 8:
        st.info("🙂 Sudah cukup baik. Tetap pertahankan pola tidur dan aktivitas sehat.")
    else:
        st.success("😴 Tidur kamu sangat baik! Pertahankan gaya hidup sehat dan konsisten.")

    st.markdown("""
        <div style="margin-top:20px; padding:15px; border-radius:10px;">
            <p><b>💡 Tips:</b> Tidur yang berkualitas sangat dipengaruhi oleh stres, kafein, dan aktivitas fisik. Usahakan tidur cukup dan hindari gadget sebelum tidur.</p>
        </div>
    """, unsafe_allow_html=True)

    # --- Simpan ke File CSV ---
    data_simpan = pd.DataFrame([{
        "Tanggal": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Durasi_Tidur": durasi,
        "Tingkat_Stres": stres,
        "Kafein": kafein,
        "Olahraga": olahraga,
        "Skor_Kualitas": skor
    }])

    file_path = "riwayat_tidur.csv"
    if os.path.exists(file_path):
        data_simpan.to_csv(file_path, mode='a', header=False, index=False)
    else:
        data_simpan.to_csv(file_path, index=False)

    # --- Tambah ke session_state untuk grafik ---
    st.session_state.riwayat = pd.concat([
        st.session_state.riwayat,
        pd.DataFrame([{"Tanggal": data_simpan["Tanggal"][0], "Skor": skor}])
    ])

# --- Tampilkan Riwayat sebagai Grafik ---
if not st.session_state.riwayat.empty:
    st.markdown("## 📈 Riwayat Prediksi Anda")
    chart_data = st.session_state.riwayat.copy()
    chart_data["Tanggal"] = pd.to_datetime(chart_data["Tanggal"])
    st.line_chart(chart_data.set_index("Tanggal"))
