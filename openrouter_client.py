import os
import requests
import json
import pandas as pd
from dotenv import load_dotenv

class OpenRouterClient:
    def __init__(self, model: str, referer: str = "https://your-site.com", title: str = "Streamlit Chatbot"):
        load_dotenv()
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": referer,
            "X-Title": title,
            "Content-Type": "application/json"
        }
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    def chat(self, messages: list[dict]) -> str:
        try:
            response = requests.post(
                url=self.api_url,
                headers=self.headers,
                data=json.dumps({
                    "model": self.model,
                    "messages": messages
                })
            )
            response.raise_for_status()
            reply = response.json()["choices"][0]["message"]["content"]
            return reply
        except Exception as e:
            return f"⚠️ Terjadi kesalahan saat memanggil API: {e}"

    def summarize_prompt(self, prompt: str) -> str:
        """Mendeskripsikan maksud dari input manusia menjadi kalimat yang lebih formal dan jelas"""
        system = {
            "role": "system",
            "content": (
                "Tugasmu adalah mendeskripsikan maksud dari input manusia menjadi kalimat yang lebih formal dan jelas.\n"
                "Contoh:\n"
                "Input: 'carikan saya info tentang kalsel dong'\n"
                "Output: 'Pengguna meminta informasi tentang provinsi Kalimantan Selatan.'\n"
                "Buat satu kalimat singkat dan deskriptif."
            )
        }
        messages = [
            system,
            {"role": "user", "content": prompt}
        ]
        return self.chat(messages)

    def query_pandas_prompt(self, user_question: str, df_info: str) -> str:
        """Generate kode pandas berdasarkan pertanyaan user dan info DataFrame"""
        system = {
            "role": "system", 
            "content": (
                "Anda adalah expert data analyst yang dapat menggenerate kode pandas untuk menjawab pertanyaan user.\n"
                "Berdasarkan informasi DataFrame yang diberikan, buatlah kode pandas yang tepat.\n"
                "Hanya berikan kode python saja, tanpa penjelasan tambahan.\n"
                "Gunakan variabel 'df' untuk DataFrame.\n"
                "Contoh output:\n"
                "df.groupby('kategori')['nilai'].sum()\n"
                "df[df['umur'] > 25]['nama'].tolist()\n"
                "df.describe()"
            )
        }
        
        user_prompt = f"""
        Pertanyaan user: {user_question}
        
        Informasi DataFrame:
        {df_info}
        
        Buatlah kode pandas untuk menjawab pertanyaan tersebut:
        """
        
        messages = [
            system,
            {"role": "user", "content": user_prompt}
        ]
        return self.chat(messages)

    def summary_from_data_pandas(self, data_result: str, original_question: str) -> str:
        """Membuat ringkasan dari hasil data pandas dalam bahasa natural"""
        system = {
            "role": "system",
            "content": (
                "Anda adalah data analyst yang ahli menjelaskan hasil analisis data.\n"
                "Berdasarkan hasil data yang diberikan, buatlah ringkasan dalam bahasa Indonesia yang mudah dipahami.\n"
                "Fokus pada insight yang paling penting dan relevan dengan pertanyaan user.\n"
                "Gunakan bahasa yang natural dan tidak terlalu teknis."
            )
        }
        
        user_prompt = f"""
        Pertanyaan original user: 
        {original_question}
        
        data untuk di analisis:
        {data_result}
        
        Buatlah ringkasan yang mudah dipahami dari hasil data ini:
        """
        
        messages = [
            system,
            {"role": "user", "content": user_prompt}
        ]
        return self.chat(messages)

    def get_dataframe_info(self, df: pd.DataFrame) -> str:
        """Helper function untuk mendapatkan informasi DataFrame"""
        info = []
        info.append(f"Shape: {df.shape}")
        info.append(f"Columns: {list(df.columns)}")
        
        # Info tipe data
        dtype_info = []
        for col in df.columns:
            dtype_info.append(f"{col}: {df[col].dtype}")
        info.append(f"Data types: {dtype_info}")
        
        # Sample data (5 baris pertama)
        info.append(f"Sample data:\n{df.head().to_string()}")
        
        # Info statistik untuk kolom numerik
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            info.append(f"Numeric columns stats:\n{df[numeric_cols].describe().to_string()}")
        
        return "\n".join(info)

    def analyze_data_question(self, user_question: str, df: pd.DataFrame) -> dict:
        """
        Fungsi lengkap untuk menganalisis pertanyaan user tentang data
        Return: {
            'question_summary': str,
            'pandas_code': str, 
            'result': any,
            'explanation': str,
            'error': str (jika ada)
        }
        """
        try:
            # 1. Summarize pertanyaan user
            question_summary = self.summarize_prompt(user_question)
            
            # 2. Get DataFrame info
            df_info = self.get_dataframe_info(df)
            
            # 3. Generate pandas code
            pandas_code = self.query_pandas_prompt(user_question, df_info)
            
            # 4. Execute pandas code
            try:
                # Clean code (remove ```python if exists)
                clean_code = pandas_code.strip()
                if clean_code.startswith('```python'):
                    clean_code = clean_code[9:]
                if clean_code.endswith('```'):
                    clean_code = clean_code[:-3]
                clean_code = clean_code.strip()
                
                # Execute code
                result = eval(clean_code, {'df': df, 'pd': pd})
                
                # 5. Generate explanation
                result_str = str(result) if not isinstance(result, pd.DataFrame) else result.to_string()
                explanation = self.summary_from_data_pandas(result_str, user_question)
                
                return {
                    'question_summary': question_summary,
                    'pandas_code': clean_code,
                    'result': result,
                    'explanation': explanation,
                    'error': None
                }
                
            except Exception as code_error:
                return {
                    'question_summary': question_summary,
                    'pandas_code': pandas_code,
                    'result': None,
                    'explanation': f"Error executing code: {str(code_error)}",
                    'error': str(code_error)
                }
                
        except Exception as e:
            return {
                'question_summary': "Error processing question",
                'pandas_code': "",
                'result': None,
                'explanation': f"Error in analysis: {str(e)}",
                'error': str(e)
            }

    def chat_with_context(self, user_message: str, context: str = "", system_prompt: str = None) -> str:
        """Chat dengan konteks tambahan"""
        messages = []
        
        # Default system prompt jika tidak ada
        if system_prompt is None:
            system_prompt = """
            kembalikan chat masuk ke bahasa Indonesia
            atau perjelas kalimatnya jika terlalu singkat.
            jangan tambahakan informasi apapun selain kemabalian chat ke bahasa Indonesia.
            Jika ada singkatan, kembalikan ke bentuk lengkapnya.
            contoh 
            input : data kalsel
            output : data kalimantan selatan
            """
        
        messages.append({"role": "system", "content": system_prompt})
    
        # Tambahkan pesan user
        messages.append({"role": "user", "content": user_message})
        
        return self.chat(messages)
    

    def chat_with_chitchat(self, user_message: str, context: str = "", system_prompt: str = None) -> str:
        """Chat dengan konteks tambahan"""
        messages = []
        
        # Default system prompt jika tidak ada
        if system_prompt is None:
            system_prompt = """
            "Kamu adalah asisten AI profesional dan ramah bernama Avida. "
            "Kamu membantu pelanggan menganalisis data pertumbuhan dan penurunan penduduk di Indonesia"
            "Kamu bisa menampilkan grafik dari data tersebut dan menjawab pertanyaan terkait analisis data. "
            "\n\n"
            "Berikut peraturan interaksi:\n"
            "- Selalu sapa pelanggan dengan 'Kaka' jika belum tahu nama.\n"
            "- Jika tahu nama, gunakan 'Kaka [Nama]' sebagai sapaan.\n"
            "- Jika belum pernah kenalan, selalu kenalkan dirimu hanya satu kali di awal:\n"
            "Contoh: 'Halo Kaka, kenalin aku Avida dari Data Insight AI. Boleh tahu nama Kaka?'\n"
            "- Jika pelanggan sudah menyebut nama, sapa dia dengan: 'Salam kenal Kaka [Nama], aku bisa bantu menganalisis data dan menampilkan grafik.'\n"
            "- Contoh pertanyaannya : 1. Berikan grafik pertumbuhan penduduk di provinsi [nama provinsi].\n"
            "  2. Berikan grafik perbandingan jumlah penduduk di provinsi [provinsi1] dan [provinsi2] pada tahun [tahun].\n"     
            """
        
        messages.append({"role": "system", "content": system_prompt})
    
        # Tambahkan pesan user
        messages.append({"role": "user", "content": user_message})
        
        return self.chat(messages)
    
    def chat_with_context_citcat(self, user_message: str, system_prompt: str = None) -> str:
        """Chat dengan konteks tambahan"""
        messages = []

        # Default system prompt jika tidak ada
        if system_prompt is None:
            system_prompt = """
    Kamu adalah asisten yang bertugas mengklasifikasikan jenis pertanyaan dari user.

    Tugasmu adalah menentukan apakah pesan user merupakan:
    1. Percakapan santai / ngobrol biasa (chat ringan), atau
    2. Permintaan data pertumbuhan jumlah penduduk per provinsi.

    Balas hanya dengan:
    - "yes" → jika ini adalah percakapan santai
    - "no" → jika ini adalah permintaan data

    Jangan berikan penjelasan tambahan apa pun.
            """.strip()

        messages.append({"role": "system", "content": system_prompt})

        # Tambahkan pesan user
        messages.append({"role": "user", "content": user_message})

        return self.chat(messages)

    

    def query_pandas(self, user_question: str) -> str:
        """Generate kode pandas berdasarkan pertanyaan user dan info DataFrame"""
        system = {
            "role": "system", 
            "content": (
                "Anda adalah expert data analyst yang dapat menggenerate kode pandas untuk menjawab pertanyaan user.\n"
                "Berdasarkan informasi DataFrame yang diberikan, buatlah kode pandas yang tepat.\n"
                "Hanya berikan kode python saja, tanpa penjelasan tambahan.\n"
                "buatkan tanpa import matplotlib.pyplot as plt"
                "Gunakan variabel 'df' untuk DataFrame.\n"
                "Contoh output:\n"
                "df.groupby('kategori')['nilai'].sum()\n"
                "df[df['umur'] > 25]['nama'].tolist()\n"
                "df.describe()"
            )
        }
        
        user_prompt = f"""
        Pertanyaan user: {user_question}
        
        Informasi DataFrame:
        Provinsi,Tahun,Jumlah Penduduk (juta)
        Aceh,2015,6.24
        Aceh,2016,7.4
        Aceh,2017,8.28
        
        Buatlah query pandas untuk menjawab pertanyaan tersebut:
        """
        
        messages = [
            system,
            {"role": "user", "content": user_prompt}
        ]
        return self.chat(messages)
        
    def generate_type_grafik(self, data: str) -> str:
        """
        Menghasilkan kode Python visualisasi menggunakan Streamlit (line chart, area chart, map)
        berdasarkan pertanyaan user dan struktur DataFrame.
        """
        system = {
            "role": "system",
            "content": (
                "Tugas Anda adalah memilih jenis grafik yang paling sesuai untuk menampilkan data "
                "berdasarkan struktur DataFrame dan pertanyaan pengguna.\n"
                "Gunakan hanya library Streamlit untuk visualisasi.\n"
                "Pilih antara: st.line_chart, st.area_chart, st.bar_chart.\n"
                "Gunakan nama DataFrame 'df'.\n"
                "Tampilkan hanya kode Python, tanpa penjelasan.\n"
                "Contoh output:\n"
                """
st.chat_message("assistant").line_chart(df.pivot(index='Tahun', columns='Provinsi', values='Jumlah Penduduk (juta)'))\n
"""

                """
st.chat_message("assistant").bar_chart(
    df.pivot(index='Tahun', columns='Provinsi', values='Jumlah Penduduk (juta)')
)
"""
            )
        }

        user_prompt = f"""
        Pertanyaan user: Dari data berikut, grafik apa yang cocok untuk ditampilkan?

        Informasi DataFrame:
        {data}

        Pilih jenis grafik paling sesuai dan berikan hanya kode visualisasinya.
        """

        messages = [
            system,
            {"role": "user", "content": user_prompt}
        ]
        return self.chat(messages)
