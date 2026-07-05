import os
from dotenv import load_dotenv

# Memuat file .env
load_dotenv()

print("=== CHECKING CONFIGURATION ===")
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    # Tampilkan beberapa karakter awal saja demi keamanan
    masked_key = api_key[:6] + "..." + api_key[-4:] if len(api_key) > 10 else "Terlalu pendek"
    print(f"✅ GEMINI_API_KEY ditemukan: {masked_key}")
else:
    print("❌ GEMINI_API_KEY TIDAK ditemukan di environment / file .env")

print("\n=== TESTING GENERATIVE RAG CHATBOT ===")
try:
    from app.chatbot.chatbot_ai import chatbot_response
    question = "apa syarat membuat KTP baru?"
    print(f"Tanya: '{question}'")
    response = chatbot_response(question)
    print(f"Jawab:\n{response}")
except Exception as e:
    print(f"❌ Terjadi error saat memuat/menjalankan chatbot: {e}")
