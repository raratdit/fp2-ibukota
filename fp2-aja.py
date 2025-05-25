import streamlit as st
from openrouter_client import OpenRouterClient
import pandas as pd
import os

# Model list
model_options = {
    "DeepSeek Chat V3 (Free)": "deepseek/deepseek-chat-v3-0324",
    "LLaMA 3.3 8B Instruct (Free)": "meta-llama/llama-3.3-8b-instruct",
    "Qwen3 235B A22B (Free)": "qwen/qwen3-235b-a22b"
}

# Load dataset
data_path = "assets/data_penduduk_indonesia.csv"
df = pd.read_csv(data_path) if os.path.exists(data_path) else None

# Sidebar: pilih model
st.sidebar.title("⚙️ Pengaturan")
selected_model_label = st.sidebar.selectbox("Pilih Model AI", list(model_options.keys()))
selected_model = model_options[selected_model_label]

# Inisialisasi chatbot
chatbot = OpenRouterClient(model=selected_model)

# Judul dan subjudul
st.title("🧠 AI Chatbot Bubble Style")
st.markdown(f"Powered by `{selected_model}` via OpenRouter 🤖")

# Session state untuk riwayat chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Tampilkan riwayat
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])
# Input pengguna
user_input = st.chat_input("Tulis pesan di sini...")

if user_input:
    # Simpan dan tampilkan pesan pengguna
    st.chat_message("user").markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.spinner("Mengetik..."):

        # Contoh fungsi yang kamu panggil
        maksud_user = chatbot.chat_with_context(user_input)
        istrue = chatbot.chat_with_context_citcat(maksud_user)
        # st.markdown(f"**Klasifikasi Pertanyaan:** {istrue}")
        final_data = ""
        if istrue == "no" :

            st.markdown("**Step yang dijalankan akan hilang di chat setelahnya**")

            query = chatbot.query_pandas(maksud_user)

            try:
                data_query = eval(query)
            except Exception as e:
                st.error(f"Error saat evaluasi query: {e}")
                data_query = None

            grafik_type = chatbot.generate_type_grafik(data_query)
            summery = chatbot.summary_from_data_pandas(
                data_result=data_query,
                original_question=maksud_user
            )

            # Tampilkan maksud pengguna
            with st.expander("🔍 1. Maksud Pengguna"):
                st.markdown(f"**Maksud Pengguna:** {maksud_user}")

            # Tampilkan query
            with st.expander("📊 2. Query Pandas"):
                st.markdown(f"**Query Pandas:** `{query}`")

            # Tampilkan hasil eksekusi query
            with st.expander("📄 3. Eksekusi Query"):
                if data_query is not None:
                    try:
                        st.dataframe(data_query)
                    except Exception as e:
                        st.error(f"Terjadi kesalahan saat mengeksekusi query: {e}")
                        data_query = None
                else:
                    st.warning("Data tidak tersedia.")

            # Tampilkan grafik
            grafik_type_str = ""
            if data_query is not None:
                with st.expander("📈 4. Tipe dan Visualisasi Grafik"):
                    try:
                        grafik_type_str = f"**Tipe Grafik:** `{grafik_type}`"
                        st.markdown(grafik_type_str)
                        df = data_query  # df dibutuhkan jika dipakai di exec()
                        exec(grafik_type)
                    except Exception as e:
                        st.error(f"Gagal menampilkan grafik: {e}")
                        grafik_type_str = f"Gagal menampilkan grafik: {e}"

            # Tampilkan rangkuman
            if data_query is not None:
                with st.expander("📝 5. Resume Data"):
                    st.markdown(f"**Resume:** {summery}")
            else:
                summery = "Tidak ada data yang dapat dirangkum."
            final_data = summery
        else:
        # Simpan dan tampilkan ke UI
            chitchat = chatbot.chat_with_chitchat(user_input)
            final_data = chitchat

        st.session_state.chat_history.append({"role": "assistant", "content": final_data})
        st.chat_message("assistant").markdown(final_data)