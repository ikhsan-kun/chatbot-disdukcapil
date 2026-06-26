"""
Jalankan script ini SEKALI untuk men-download model embedding ke folder lokal.
Setelah itu, aplikasi bisa berjalan OFFLINE tanpa koneksi internet.

Cara pakai:
    python download_model.py
"""

from sentence_transformers import SentenceTransformer
import os

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
SAVE_PATH = os.path.join("app", "chatbot", "model_lokal")

print(f"Downloading model '{MODEL_NAME}'...")
print("Ini hanya perlu dilakukan SEKALI. Mohon tunggu...\n")

model = SentenceTransformer(MODEL_NAME)
model.save(SAVE_PATH)

print(f"\n✅ Model berhasil disimpan ke: {SAVE_PATH}")
print("Sekarang aplikasi bisa berjalan OFFLINE.")
