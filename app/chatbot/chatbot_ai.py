import faiss
import pickle
import numpy as np
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================
# KONFIGURASI PATH LOKAL
# =============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PKL_PATH = os.path.join(BASE_DIR, "disdukcapil_data.pkl")
FAISS_PATH = os.path.join(BASE_DIR, "disdukcapil_index.faiss")
MODEL_LOCAL_PATH = os.path.join(BASE_DIR, "model_lokal")

# batas jarak FAISS
MAX_DISTANCE = 0.8

# =============================================
# LOAD MODEL EMBEDDING LOKAL
# =============================================
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError(
        "Package 'sentence-transformers' belum terinstall.\n"
        "Jalankan: pip install sentence-transformers"
    )

if os.path.isdir(MODEL_LOCAL_PATH):
    print(f"Memuat model dari folder lokal: {MODEL_LOCAL_PATH}")
    model = SentenceTransformer(MODEL_LOCAL_PATH)
else:
    print("Folder model lokal tidak ditemukan.")
    print("Mencoba memuat model 'all-MiniLM-L6-v2' dari cache HuggingFace...")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "0")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

print("Model embedding berhasil dimuat!")

# =============================================
# LOAD DATA FAQ & INDEX LOKAL
# =============================================
print("Mulai load file PKL...")

with open(PKL_PATH, "rb") as f:
    data = pickle.load(f)

print("PKL berhasil dimuat")

print("Mulai load FAISS...")

index = faiss.read_index(FAISS_PATH)

print("FAISS berhasil dimuat")

print("Data berhasil dimuat dari lokal!")

# =============================================
# FORMAT JAWABAN
# =============================================
def format_requirements(text):

    if not text:
        return "Maaf, jawaban belum tersedia."

    text = str(text).strip()

    # Kalau sudah ada nomor 1. 2. 3.
    if re.search(r"(^|\n)\s*1[\.\)]", text):
        return text

    # Pecah berdasarkan koma
    parts = re.split(r",\s*", text)

    # Kalau bukan daftar, tampilkan apa adanya
    if len(parts) <= 1:
        return text

    formatted = []

    for i, part in enumerate(parts, start=1):

        part = part.strip()

        # Hapus kata penghubung di awal
        part = re.sub(
            r"^(serta|dan)\s+",
            "",
            part,
            flags=re.IGNORECASE
        )

        # Huruf pertama kapital
        if part:
            part = part[:1].upper() + part[1:]

        if part:
            formatted.append(f"{i}. {part}")

    return "\n".join(formatted)
# =============================================
# FUNGSI EMBEDDING LOKAL
# =============================================
def get_embedding(text):
    embedding = model.encode(
        [text],
        convert_to_numpy=True
    ).astype(np.float32)

    if embedding.ndim == 1:
        embedding = embedding.reshape(1, -1)

    return embedding

# =============================================
# NORMALISASI PERTANYAAN
# =============================================
def normalize_question(text):

    text = text.lower()

    text = re.sub(
        r"\bkk\b",
        "kartu keluarga",
        text
    )

    # KTP variations -> 'ktp' (menghindari kata 'kartu' agar tidak bentrok dengan 'kartu keluarga')
    text = re.sub(
        r"\b(kartu tanda penduduk|ktp-el|e-ktp)\b",
        "ktp",
        text
    )

    # KIA variations -> 'kia'
    text = re.sub(
        r"\bkartu identitas anak\b",
        "kia",
        text
    )

    # Normalisasi sinonim untuk pencocokan FAISS (model all-MiniLM-L6-v2)
    text = re.sub(r"\bsyarat\b", "persyaratan", text)
    text = re.sub(r"\bbikin\b", "membuat", text)
    text = re.sub(r"\bbuat\b", "membuat", text)
    text = re.sub(r"\bcara\b", "prosedur", text)

    return text


# =============================================
# RULE BASED FAQ PRIORITAS
# =============================================
def direct_match(question):

    q = question.lower()

    # CETAK ULANG KK HILANG/RUSAK
    if (
        ("kk" in q or "kartu keluarga" in q)
        and (
            "hilang" in q
            or "rusak" in q
        )
    ):

        for i, pertanyaan in enumerate(data["questions"]):

            p = pertanyaan.lower()

            if (
                "kk" in p
                and (
                    "hilang" in p
                    or "rusak" in p
                )
            ):
                return format_requirements(data["answers"][i])

    # =================================
    # PERUBAHAN STATUS PENDIDIKAN
    # =================================
    if (
        "pendidikan" in q
        and (
            "syarat" in q
            or "persyaratan" in q
            or "cara" in q
        )
    ):

        for i, pertanyaan in enumerate(data["questions"]):

            if "perubahan status pendidikan" in pertanyaan.lower():
                return data["answers"][i]

    return None

# =============================================
# LOGIKA GENERATION (RAG) MENGGUNAKAN GEMINI API
# =============================================
def generate_rag_response(question, context):
    import time
    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    client = genai.Client(api_key=api_key)

    prompt = f"""Anda adalah asisten virtual resmi chatbot Disdukcapil Kota Tegal yang ramah, sopan, dan profesional.

Tugas Anda adalah menjawab pertanyaan warga HANYA berdasarkan informasi yang ada pada KONTEKS di bawah ini.

Aturan WAJIB:
1. Selalu mulai jawaban dengan sapaan singkat seperti "Halo!" atau "Tentu!".
2. Jika jawaban berisi daftar persyaratan atau langkah prosedur, WAJIB tampilkan dalam format poin bernomor (1. 2. 3. dst).
3. Akhiri jawaban dengan kalimat penutup yang menawarkan bantuan lanjutan, contoh: "Apakah ada yang ingin ditanyakan lagi?"
4. HANYA gunakan informasi dari KONTEKS. Jangan mengarang fakta di luar konteks.
5. Jika informasi tidak ditemukan dalam KONTEKS, jawab: "Maaf, informasi tersebut belum tersedia pada sistem kami. Silakan ketik 'menu' untuk melihat layanan yang tersedia."

======================
KONTEKS
======================
{context}

======================
PERTANYAAN WARGA
======================
{question}

======================
JAWABAN ANDA
======================""";

    # Retry otomatis hingga 3 kali jika terkena rate limit (429)
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            if response.text:
                return response.text.strip()
            return None
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and attempt < 2:
                # Rate limit — tunggu sebentar lalu coba lagi
                wait_seconds = 5 * (attempt + 1)  # 5s, 10s
                print(f"Rate limit Gemini, menunggu {wait_seconds}s sebelum retry ({attempt+1}/2)...")
                time.sleep(wait_seconds)
            else:
                print(f"Gagal generate respons RAG menggunakan Gemini: {e}")
                return None
    return None
# =============================================
# FUNCTION CHATBOT
# =============================================
def chatbot_response(question):

    allowed_keywords = [
        "ktp", "kk", "kartu keluarga", "kia",
        "kartu tanda penduduk", "kartu identitas anak",
        "akta", "kelahiran", "kematian",
        "pindah", "datang",
        "perkawinan", "perceraian",
        "pengakuan anak", "pengesahan anak",
        "perubahan nama",
        "dokumen", "hilang", "rusak",
        "disdukcapil", "kependudukan",
        "syarat", "persyaratan", "prosedur", "cara",
        "penduduk", "administrasi",
        "pendidikan",
        "golongan darah",
        "agama",
        "pekerjaan"
    ]

    question = normalize_question(question)
    question_lower = question.lower()
    
    # PRIORITAS RULE BASED
    hasil = direct_match(question)
    if hasil:
        return hasil
    

    if not any(keyword in question_lower for keyword in allowed_keywords):
        return (
            "Maaf, saya hanya dapat menjawab pertanyaan seputar "
            "layanan administrasi kependudukan Disdukcapil.\n"
            "Silakan ketik 'menu' untuk melihat daftar layanan."
        )

    embedding = get_embedding(question)

    D, I = index.search(embedding, k=3)

    for idx_val in I[0]:
        print(data["questions"][idx_val])

    idx = int(I[0][0])
    distance = float(D[0][0])

    if idx < 0:
        return (
            "Maaf, saya belum menemukan informasi yang sesuai.\n"
            "Silakan ketik 'menu' untuk melihat daftar layanan."
        )

    if distance > MAX_DISTANCE:
        return (
            "Mohon maaf, sistem belum memiliki informasi terkait pertanyaan tersebut.\n"
            "Silakan ketik 'menu' untuk melihat layanan yang tersedia."
        )

    # --- PROSES RAG (Retrieve Konteks dari Top-3 FAISS) ---
    context_list = []
    for rank, idx_val in enumerate(I[0]):
        dist = float(D[0][rank])
        if idx_val >= 0 and dist <= MAX_DISTANCE:
            q_text = data["questions"][idx_val]
            a_text = data["answers"][idx_val]
            context_list.append(f"- Pertanyaan: {q_text}\n  Jawaban: {a_text}")

    if context_list:
        context = "\n\n".join(context_list)
        # Panggil generator Gemini untuk menulis jawaban baru (RAG)
        rag_jawaban = generate_rag_response(question, context)
        if rag_jawaban is not None and rag_jawaban.strip() != "":
            return rag_jawaban

    # --- FALLBACK (Jika Gemini API gagal atau tidak ada API Key) ---
    jawaban = data["answers"][idx]
    return format_requirements(jawaban)



# =============================================
# TESTING SCRIPT
# =============================================
if __name__ == "__main__":
    print("-------------------------------------------------")
    print("TESTING CHATBOT (MODE LOKAL - OFFLINE)")
    print("-------------------------------------------------")

    while True:
        try:
            user_input = input("Anda: ")

            if user_input.lower() in ["exit", "quit", "keluar"]:
                break

            jawaban = chatbot_response(user_input)
            print(f"Bot:\n{jawaban}\n")

        except KeyboardInterrupt:
            break