from fastapi import FastAPI, Request, Form, UploadFile, File, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware
from typing import Optional, List

import shutil
import os
import uuid
import bcrypt
import pymysql

from database import engine
from pydantic import BaseModel

# Import fungsi chatbot AI kita
from app.chatbot.chatbot_ai import chatbot_response

def get_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="disdukcapil_ta",
        cursorclass=pymysql.cursors.DictCursor
    )

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="secret123")

# Download template F-1.06 secara otomatis jika belum tersedia
import urllib.request
f106_path = "static/F1.06-SURAT-PERNYATAAN-PERUBAHAN-ELEMEN-DATA.pdf"
if not os.path.exists(f106_path):
    try:
        os.makedirs("static", exist_ok=True)
        url_f106 = "https://ugc.production.linktr.ee/e486752d-6fb1-46cf-8131-5ca60f403d0c_F1.06-SURAT-PERNYATAAN-PERUBAHAN-ELEMEN-DATA.pdf"
        with urllib.request.urlopen(url_f106, timeout=10) as response, open(f106_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print("Template F-1.06 berhasil diunduh secara otomatis ke folder static.")
    except Exception as e:
        print(f"Gagal mengunduh template F-1.06 secara otomatis: {e}")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user": request.session.get("user")
        }
    )

@app.get("/chatbot", response_class=HTMLResponse)
async def chatbot(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chatbot.html",
        context={
            "user": request.session.get("user")
        }
    )

class ChatRequest(BaseModel):
    message: str

def tampilkan_menu_utama():
    return """
Halo 👋
Saya chatbot Disdukcapil Kota Tegal.

Silakan pilih layanan berikut:

1. KTP
2. Kartu Keluarga
3. KIA
4. Akta Kelahiran
5. Akta Kematian
6. Pindah Datang
7. Perkawinan / Perceraian
8. Pengakuan / Pengesahan Anak
9. Perubahan Nama
10. Dokumen Hilang / Rusak

Ketik angka menu, contoh: 2
Atau ketik manual, contoh: syarat membuat KK baru

Ketik "menu" untuk melihat daftar ini lagi.
"""

def tampilkan_submenu(message):

    submenu = {
        "1": """
Menu KTP:

1. Syarat membuat KTP baru
2. Syarat cetak ulang KTP rusak
3. Syarat cetak ulang KTP hilang
4. Prosedur pembuatan KTP

Ketik 0 untuk kembali ke menu utama.
""",

        "2": """
Menu Kartu Keluarga:

1. Syarat membuat KK baru
2. Syarat perubahan KK
3. Syarat cetak ulang KK hilang/rusak
4. Syarat perubahan KK karena kematian
5. Syarat perubahan KK karena kedatangan/pindahan
6. Syarat perubahan status pendidikan
7. Prosedur pembuatan KK

Ketik 0 untuk kembali ke menu utama.
""",

        "3": """
Menu KIA:

1. Syarat KIA usia 0-5 tahun
2. Syarat KIA usia 5-17 tahun
3. Prosedur pembuatan KIA

Ketik 0 untuk kembali ke menu utama.
""",

        "4": """
Menu Akta Kelahiran:

1. Syarat pembuatan Akta Kelahiran
2. Prosedur pembuatan Akta Kelahiran

Ketik 0 untuk kembali ke menu utama.
""",

        "5": """
Menu Akta Kematian:

1. Syarat pencatatan kematian
2. Prosedur pencatatan kematian

Ketik 0 untuk kembali ke menu utama.
""",

        "6": """
Menu Pindah Datang:

1. Syarat pindah datang antar daerah (SKDWNI)
2. Prosedur pindah datang antar daerah
3. Syarat membuat Surat Pindah ke Luar Negeri
4. Prosedur membuat Surat Pindah ke Luar Negeri
5. Syarat pindah datang dari luar negeri
6. Prosedur pindah datang dari luar negeri

Ketik 0 untuk kembali ke menu utama.
""",

        "7": """
Menu Perkawinan / Perceraian:

1. Syarat pencatatan perkawinan
2. Prosedur pencatatan perkawinan
3. Syarat pencatatan perceraian
4. Prosedur pencatatan perceraian

Ketik 0 untuk kembali ke menu utama.
""",

        "8": """
Menu Pengakuan / Pengesahan Anak:

1. Syarat pencatatan pengakuan anak
2. Prosedur pencatatan pengakuan anak
3. Syarat pencatatan pengesahan anak
4. Prosedur pencatatan pengesahan anak
5. Syarat pencatatan pengangkatan anak
6. Prosedur pencatatan pengangkatan anak
7. Syarat pencatatan pengakuan status kewarganegaraan
8. Prosedur pencatatan pengakuan status kewarganegaraan

Ketik 0 untuk kembali ke menu utama.
""",

        "9": """
Menu Perubahan Nama:

1. Syarat perubahan nama
2. Prosedur perubahan nama

Ketik 0 untuk kembali ke menu utama.
""",

        "10": """
Menu Dokumen Hilang / Rusak:

1. Syarat penerbitan kembali dokumen kependudukan karena hilang/rusak
2. Prosedur penerbitan kembali dokumen kependudukan
3. Syarat pencatatan peristiwa penting lainnya
4. Prosedur pencatatan peristiwa penting lainnya

Ketik 0 untuk kembali ke menu utama.
"""
    }

    return submenu.get(message)

def pertanyaan_dari_kode(message):

    kode = {
        "1.1": "Apa saja persyaratan membuat KTP baru?",
        "1.2": "Apa saja persyaratan cetak ulang KTP karena rusak?",
        "1.3": "Apa saja persyaratan cetak ulang KTP karena hilang?",
        "1.4": "Bagaimana prosedur pembuatan KTP?",


        "2.1": "Apa persyaratan membuat Kartu Keluarga baru?",
        "2.2": "Apa persyaratan perubahan Kartu Keluarga?",
        "2.3": "Apa persyaratan percetakan KK karena hilang atau rusak?",
        "2.4": "Apa persyaratan perubahan KK karena kematian?",
        "2.5": "Apa persyaratan perubahan KK karena kedatangan?",
        "2.6": "Apa persyaratan perubahan status pendidikan?",
        "2.7": "Bagaimana prosedur pembuatan Kartu Keluarga?",

        "3.1": "Apa persyaratan membuat KIA usia 0 sampai 5 tahun?",
        "3.2": "Apa persyaratan membuat KIA usia 5 sampai 17 tahun?",
        "3.3": "Bagaimana prosedur pembuatan KIA?",

        "4.1": "Apa saja persyaratan pembuatan Akta Kelahiran?",
        "4.2": "Bagaimana prosedur pembuatan Akta Kelahiran?",

        "5.1": "Apa saja persyaratan pencatatan kematian?",
        "5.2": "Bagaimana prosedur pencatatan kematian?",

        "6.1": "Apa persyaratan pindah datang antar daerah (SKDWNI)?",
        "6.2": "Bagaimana prosedur pindah datang antar daerah?",
        "6.3": "Apa persyaratan membuat Surat Pindah ke Luar Negeri?",
        "6.4": "Bagaimana prosedur membuat Surat Pindah ke Luar Negeri?",
        "6.5": "Apa persyaratan pindah datang dari luar negeri?",
        "6.6": "Bagaimana prosedur pindah datang dari luar negeri?",

        "7.1": "Apa saja persyaratan pencatatan perkawinan?",
        "7.2": "Bagaimana prosedur pencatatan perkawinan?",
        "7.3": "Apa saja persyaratan pencatatan perceraian?",
        "7.4": "Bagaimana prosedur pencatatan perceraian?",

        "8.1": "Apa saja persyaratan pencatatan pengakuan anak?",
        "8.2": "Bagaimana prosedur pencatatan pengakuan anak?",
        "8.3": "Apa saja persyaratan pencatatan pengesahan anak?",
        "8.4": "Bagaimana prosedur pencatatan pengesahan anak?",
        "8.5": "Apa saja persyaratan pencatatan pengangkatan anak?",
        "8.6": "Bagaimana prosedur pencatatan pengangkatan anak?",
        "8.7": "Apa saja persyaratan pencatatan pengakuan status kewarganegaraan?",
        "8.8": "Bagaimana prosedur pencatatan pengakuan status kewarganegaraan?",

        "9.1": "Apa saja persyaratan perubahan nama?",
        "9.2": "Bagaimana prosedur perubahan nama?",

        "10.1": "Apa saja persyaratan penerbitan kembali dokumen kependudukan karena hilang atau rusak?",
        "10.2": "Bagaimana prosedur penerbitan kembali dokumen kependudukan?",
        "10.3": "Apa saja persyaratan pencatatan peristiwa penting lainnya?",
        "10.4": "Bagaimana prosedur pencatatan peristiwa penting lainnya?"
    }

    return kode.get(message)


# CHATBOT
@app.post("/api/chatbot")
async def api_chatbot(request: Request):

    body = await request.json()
    message = body.get("message", "").strip().lower()

    if not message:
        return JSONResponse({
            "reply": "Silakan ketik pertanyaan terlebih dahulu."
        })

    if message == "menu" or message == "0":
        return JSONResponse({
            "reply": tampilkan_menu_utama()
        })

    submenu = tampilkan_submenu(message)

    if submenu:
        return JSONResponse({
            "reply": submenu
        })

    pertanyaan = pertanyaan_dari_kode(message)

    if pertanyaan:
        reply = chatbot_response(pertanyaan)

        return JSONResponse({
            "reply": reply
        })

    reply = chatbot_response(message)

    return JSONResponse({
        "reply": reply
    })

@app.get("/pengajuan", response_class=HTMLResponse)
async def pengajuan(request: Request):

    user = request.session.get("user")

    if not user:
        return templates.TemplateResponse(
            request=request,
            name="login_required.html",
            context={
                "user": request.session.get("user")
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="pengajuan.html",
        context={
            "user": user
        }
    )

@app.get("/pengajuan-kk", response_class=HTMLResponse)
async def pengajuan_kk(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="form_kk.html",
        context={
            "user": request.session.get("user")
        }
    )

@app.post("/pengajuan-kk")
async def submit_kk(

    request: Request,

    # form
    no_kk: str = Form(...),
    nama: str = Form(...),
    jenis_pengajuan: str = Form(...),
    alamat: str = Form(...),
    provinsi: str = Form(...),
    kabupaten: str = Form(...),
    kecamatan: str = Form(...),
    desa: str = Form(...),
    catatan: str = Form(None),

    # multi file
    file_upload: List[UploadFile] = File(None)

):

    user = request.session.get("user")

    if not user:
        return RedirectResponse("/login", status_code=303)

    # simpan pengajuan
    with engine.connect() as conn:

        result = conn.execute(

            text("""
                INSERT INTO pengajuan
                (
                    nik,
                    nama,
                    jenis_layanan,
                    detail_pengajuan,
                    status,
                    catatan_user,
                    no_kk,
                    alamat,
                    provinsi,
                    kabupaten,
                    kecamatan,
                    desa
                )
                VALUES
                (
                    :nik,
                    :nama,
                    :jenis_layanan,
                    :detail_pengajuan,
                    :status,
                    :catatan_user,
                    :no_kk,
                    :alamat,
                    :provinsi,
                    :kabupaten,
                    :kecamatan,
                    :desa
                )
            """),

            {
                "nik": user["nik"],
                "nama": nama,
                "jenis_layanan": "Cetak Ulang KK",
                "detail_pengajuan": jenis_pengajuan,
                "status": "Menunggu Verifikasi",
                "catatan_user": catatan,
                "no_kk": no_kk,
                "alamat": alamat,
                "provinsi": provinsi,
                "kabupaten": kabupaten,
                "kecamatan": kecamatan,
                "desa": desa
            }

        )

        # ambil id pengajuan
        pengajuan_id = result.lastrowid

        conn.commit()

        # folder upload
        upload_folder = "static/uploads"

        os.makedirs(upload_folder, exist_ok=True)

        # simpan semua file
        for file in file_upload:

            if file.filename != "":

                filename = f"{uuid.uuid4()}_{file.filename}"

                file_path = os.path.join(upload_folder, filename)

                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

                conn.execute(

                    text("""
                        INSERT INTO dokumen_pengajuan
                        (
                            pengajuan_id,
                            nama_file
                        )
                        VALUES
                        (
                            :pengajuan_id,
                            :nama_file
                        )
                    """),

                    {
                        "pengajuan_id": pengajuan_id,
                        "nama_file": filename
                    }

                )

        conn.commit()

    return RedirectResponse("/dashboard", status_code=303)

@app.post("/pengajuan-pendidikan")
async def submit_pendidikan(
    request: Request,

    # form
    nama: str = Form(...),
    pendidikan_lama: str = Form(...),
    pendidikan_baru: str = Form(...),
    catatan: str = Form(None),

    # multi file
    file_upload: List[UploadFile] = File(None)
):
    user = request.session.get("user")

    if not user:
        return RedirectResponse("/login", status_code=303)

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                INSERT INTO pengajuan
                (
                    nik,
                    nama,
                    pendidikan_lama,
                    jenis_layanan,
                    detail_pengajuan,
                    status,
                    catatan_user
                )
                VALUES
                (
                    :nik,
                    :nama,
                    :pendidikan_lama,
                    :jenis_layanan,
                    :detail_pengajuan,
                    :status,
                    :catatan_user
                )
            """),
            {
                "nik": user["nik"],
                "nama": nama,
                "pendidikan_lama": pendidikan_lama,
                "jenis_layanan": "Perubahan Status Pendidikan",
                "detail_pengajuan": pendidikan_baru,
                "status": "Menunggu Verifikasi",
                "catatan_user": catatan
            }
        )

        pengajuan_id = result.lastrowid

        conn.commit()

        upload_folder = "static/uploads"

        os.makedirs(upload_folder, exist_ok=True)

        if file_upload:

            for file in file_upload:

                if file.filename != "":

                    filename = f"{uuid.uuid4()}_{file.filename}"

                    file_path = os.path.join(upload_folder, filename)

                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(file.file, buffer)

                    conn.execute(
                        text("""
                            INSERT INTO dokumen_pengajuan
                            (
                                pengajuan_id,
                                nama_file
                            )
                            VALUES
                            (
                                :pengajuan_id,
                                :nama_file
                            )
                        """),
                        {
                            "pengajuan_id": pengajuan_id,
                            "nama_file": filename
                        }
                    )

            conn.commit()

    return RedirectResponse("/dashboard", status_code=303)

@app.get("/pengajuan-pendidikan", response_class=HTMLResponse)
async def pengajuan_pendidikan(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="form_pendidikan.html",
        context={
            "user": request.session.get("user")
        }
    )

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )

@app.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={}
    )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):

    user = request.session.get("user")

    if not user:
        return RedirectResponse("/login", status_code=303)

    if user["role"] == "admin":
        return RedirectResponse("/admin", status_code=303)

    with engine.connect() as conn:

        data = conn.execute(
            text("""
                SELECT *
                FROM pengajuan
                WHERE nik = :nik
                ORDER BY id DESC
            """),
            {
                "nik": user["nik"]
            }
        ).mappings().all()

        data = [dict(row) for row in data]

        for item in data:

            if item["tanggal_pengajuan"]:
                item["tanggal_pengajuan"] = (
                    item["tanggal_pengajuan"]
                    .strftime("%d-%m-%Y %H:%M")
                )

            dokumen = conn.execute(
                text("""
                    SELECT *
                    FROM dokumen_pengajuan
                    WHERE pengajuan_id = :id
                """),
                {
                    "id": item["id"]
                }
            ).mappings().all()

            item["dokumen"] = [dict(d) for d in dokumen]

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": user,
            "pengajuan": data
        }
    )

@app.post("/login")
async def process_login(
    request: Request,
    nik: str = Form(...),
    password: str = Form(...)
):
    with engine.connect() as conn:
        user = conn.execute(
            text("SELECT * FROM users WHERE nik = :nik"),
            {"nik": nik}
        ).mappings().first()

    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        request.session["user"] = {
            "id": user["id"],
            "nik": user["nik"],
            "nama": user["nama"],
            "email": user["email"],
            "role": user["role"],
            "foto_profile": user["foto_profile"]
        }

        if user["role"] == "admin":
            return RedirectResponse("/admin", status_code=303)
        else:
            return RedirectResponse("/dashboard", status_code=303)

    else:
        return RedirectResponse("/login", status_code=303)

@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="forgot_password.html",
        context={}
    )

@app.post("/forgot-password")
async def process_forgot_password(
    request: Request,
    nik: str = Form(...),
    new_password: str = Form(...),
    confirm_new_password: str = Form(...)
):
    if not nik.startswith("3376"):
        return templates.TemplateResponse(
            request=request,
            name="forgot_password.html",
            context={"error": "Pengisian NIK harus diawali 3376"}
        )

    if new_password != confirm_new_password:
        return templates.TemplateResponse(
            request=request,
            name="forgot_password.html",
            context={"error": "Konfirmasi password baru tidak cocok"}
        )

    if len(new_password) < 6:
        return templates.TemplateResponse(
            request=request,
            name="forgot_password.html",
            context={"error": "Password baru minimal 6 karakter"}
        )

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE nik = %s", (nik,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return templates.TemplateResponse(
            request=request,
            name="forgot_password.html",
            context={"error": "NIK tidak terdaftar"}
        )

    hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    cursor.execute("UPDATE users SET password = %s WHERE nik = %s", (hashed_pw, nik))
    conn.commit()
    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="forgot_password.html",
        context={"success": "Password berhasil diubah. Silakan masuk dengan password baru."}
    )

@app.post("/register")
async def process_register(
    nik: str = Form(...),
    nama: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    if not nik.startswith("3376"):
        return RedirectResponse("/register", status_code=303)

    if password != confirm_password:
        return RedirectResponse("/register", status_code=303)

    with engine.connect() as conn:
        check_user = conn.execute(
            text("SELECT * FROM users WHERE nik = :nik OR email = :email"),
            {
                "nik": nik,
                "email": email
            }
        ).fetchone()

        if check_user:
            return RedirectResponse("/register", status_code=303)

        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        conn.execute(
            text("""
                INSERT INTO users (nik, nama, email, password)
                VALUES (:nik, :nama, :email, :password)
            """),
            {
                "nik": nik,
                "nama": nama,
                "email": email,
                "password": hashed.decode("utf-8")
            }
        )

        conn.commit()

    return RedirectResponse("/login", status_code=303)

with engine.connect() as conn:
    print("Database berhasil terhubung")


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):

    user = request.session.get("user")

    if not user or user["role"] != "admin":
        return RedirectResponse("/dashboard", status_code=303)

    with engine.connect() as conn:

        data = conn.execute(text("""
            SELECT *
            FROM pengajuan
            ORDER BY tanggal_pengajuan DESC
        """)).mappings().all()

    total = len(data)

    menunggu = len([
        d for d in data
        if d["status"] == "Menunggu Verifikasi"
    ])

    diproses = len([
        d for d in data
        if d["status"] == "Diproses"
    ])

    disetujui = len([
        d for d in data
        if d["status"] == "Disetujui"
    ])

    ditolak = len([
        d for d in data
        if d["status"] == "Ditolak"
    ])

    selesai = len([
        d for d in data
        if d["status"] == "Selesai"
    ])

    layanan_count = {}

    for d in data:
        if d["detail_pengajuan"]:
            layanan = f"{d['jenis_layanan']} ({d['detail_pengajuan']})"
        else:
            layanan = d["jenis_layanan"]

        layanan_count[layanan] = layanan_count.get(layanan, 0) + 1

    status_count = {
        "Menunggu Verifikasi": menunggu,
        "Diproses": diproses,
        "Disetujui": disetujui,
        "Ditolak": ditolak,
        "Selesai": selesai
    }

    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={
            "user": user,
            "pengajuan": data,
            "total": total,
            "menunggu": menunggu,
            "diproses": diproses,
            "disetujui": disetujui,
            "ditolak": ditolak,
            "selesai": selesai,
            "layanan_labels": list(layanan_count.keys()),
            "layanan_values": list(layanan_count.values()),
            "status_labels": list(status_count.keys()),
            "status_values": list(status_count.values())
        }
    )

@app.post("/admin/proses/{id}")
async def proses_pengajuan(
    request: Request,
    id: int,
    status: str = Form(...),
    catatan: str = Form(None),
    file_admin: UploadFile = File(None)
):
    user = request.session.get("user")

    if not user or user["role"] != "admin":
        return RedirectResponse("/dashboard", status_code=303)

    filename = None

    if file_admin and file_admin.filename != "":
        upload_folder = "static/uploads"
        os.makedirs(upload_folder, exist_ok=True)

        filename = f"{uuid.uuid4()}_{file_admin.filename}"
        file_path = os.path.join(upload_folder, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_admin.file, buffer)

    with engine.connect() as conn:

        if filename:
            conn.execute(text("""
                UPDATE pengajuan
                SET status = :status,
                    catatan_admin = :catatan,
                    file_balasan = :file_admin
                WHERE id = :id
            """), {
                "status": status,
                "catatan": catatan,
                "file_admin": filename,
                "id": id
            })

        else:
            conn.execute(text("""
                UPDATE pengajuan
                SET status = :status,
                    catatan_admin = :catatan
                WHERE id = :id
            """), {
                "status": status,
                "catatan": catatan,
                "id": id
            })

        conn.commit()

    return RedirectResponse("/admin", status_code=303)


@app.get("/admin/detail/{id}", response_class=HTMLResponse)
async def admin_detail(id: int, request: Request):

    user = request.session.get("user")

    if not user:
        return RedirectResponse("/login", status_code=303)

    if user["role"] != "admin":
        return RedirectResponse("/dashboard", status_code=303)

    with engine.connect() as conn:

        data = conn.execute(
            text("""
                SELECT *
                FROM pengajuan
                WHERE id = :id
            """),
            {
                "id": id
            }
        ).mappings().first()

        dokumen = conn.execute(
            text("""
                SELECT *
                FROM dokumen_pengajuan
                WHERE pengajuan_id = :id
            """),
            {
                "id": id
            }
        ).mappings().all()

        if not data:
            return HTMLResponse("Data tidak ditemukan", status_code=404)

        data = dict(data)
        data["dokumen"] = [dict(d) for d in dokumen]

    return templates.TemplateResponse(
        request=request,
        name="admin_detail.html",
        context={
            "user": user,
            "item": data
        }
    )

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)

@app.post("/edit-profile")
async def update_profile(
    request: Request,
    nama: str = Form(...),
    email: str = Form(...),
    old_password: Optional[str] = Form(None),
    new_password: Optional[str] = Form(None),
    confirm_new_password: Optional[str] = Form(None),
    foto_profile: UploadFile = File(None)
):
    user = request.session.get("user")

    if not user:
        return RedirectResponse("/login", status_code=303)

    old_password = old_password.strip() if old_password else ""
    new_password = new_password.strip() if new_password else ""
    confirm_new_password = confirm_new_password.strip() if confirm_new_password else ""

    update_pw = False
    hashed_pw = None

    if old_password or new_password or confirm_new_password:
        if not old_password or not new_password or not confirm_new_password:
            return templates.TemplateResponse(
                request=request,
                name="edit_profile.html",
                context={"user": user, "error": "Mohon lengkapi seluruh field password jika ingin mengubah password"}
            )
        
        if new_password != confirm_new_password:
            return templates.TemplateResponse(
                request=request,
                name="edit_profile.html",
                context={"user": user, "error": "Konfirmasi password baru tidak cocok"}
            )
            
        if len(new_password) < 6:
            return templates.TemplateResponse(
                request=request,
                name="edit_profile.html",
                context={"user": user, "error": "Password baru minimal 6 karakter"}
            )
            
        conn_check = get_db()
        cursor_check = conn_check.cursor()
        cursor_check.execute("SELECT password FROM users WHERE id = %s", (user["id"],))
        db_user = cursor_check.fetchone()
        conn_check.close()
        
        if not db_user or not bcrypt.checkpw(old_password.encode("utf-8"), db_user["password"].encode("utf-8")):
            return templates.TemplateResponse(
                request=request,
                name="edit_profile.html",
                context={"user": user, "error": "Password lama tidak sesuai"}
            )
            
        hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        update_pw = True

    filename = user.get("foto_profile")

    if foto_profile and foto_profile.filename != "":
        upload_folder = "static/uploads"
        os.makedirs(upload_folder, exist_ok=True)

        filename = f"{uuid.uuid4()}_{foto_profile.filename}"
        file_path = os.path.join(upload_folder, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(foto_profile.file, buffer)

    conn = get_db()
    cursor = conn.cursor()

    if update_pw:
        cursor.execute("""
            UPDATE users
            SET nama = %s,
                email = %s,
                foto_profile = %s,
                password = %s
            WHERE id = %s
        """, (nama, email, filename, hashed_pw, user["id"]))
    else:
        cursor.execute("""
            UPDATE users
            SET nama = %s,
                email = %s,
                foto_profile = %s
            WHERE id = %s
        """, (nama, email, filename, user["id"]))

    print("rows affected:", cursor.rowcount)  # cek di terminal

    conn.commit()
    conn.close()

    user_session = request.session.get("user")
    user_session["nama"] = nama
    user_session["email"] = email
    user_session["foto_profile"] = filename
    request.session["user"] = user_session

    return RedirectResponse("/dashboard", status_code=303)

@app.get("/edit-profile", response_class=HTMLResponse)
async def edit_profile_page(request: Request):

    user = request.session.get("user")

    if not user:
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="edit_profile.html",
        context={
            "user": user
        }
    )

@app.get("/admin/riwayat", response_class=HTMLResponse)
async def admin_riwayat(
    request: Request,
    bulan: str = None,
    tahun: str = None
):

    user = request.session.get("user")

    if not user or user["role"] != "admin":
        return RedirectResponse("/dashboard", status_code=303)

    query = """
        SELECT * FROM pengajuan
        WHERE 1=1
    """

    params = {}

    if bulan and bulan != "":
        query += " AND MONTH(tanggal_pengajuan) = :bulan"
        params["bulan"] = int(bulan)

    if tahun and tahun != "":
        query += " AND YEAR(tanggal_pengajuan) = :tahun"
        params["tahun"] = int(tahun)

    query += " ORDER BY tanggal_pengajuan DESC"

    with engine.connect() as conn:
        data = conn.execute(text(query), params).mappings().all()

    return templates.TemplateResponse(
        request=request,
        name="admin_riwayat.html",
        context={
            "user": user,
            "pengajuan": data,
            "bulan_selected": bulan,
            "tahun_selected": tahun
        }
    )

@app.get("/admin/pengajuan", response_class=HTMLResponse)
async def admin_pengajuan(
    request: Request,
    status: str = "Semua",
    nik: str = None
):

    user = request.session.get("user")

    if not user or user["role"] != "admin":
        return RedirectResponse("/dashboard", status_code=303)

    query = """
        SELECT *
        FROM pengajuan
        WHERE 1=1
    """

    params = {}

    if status != "Semua":
        query += " AND status = :status"
        params["status"] = status

    if nik and nik.strip() != "":
        query += " AND nik LIKE :nik"
        params["nik"] = f"%{nik}%"

    query += " ORDER BY tanggal_pengajuan DESC"

    with engine.connect() as conn:
        data = conn.execute(text(query), params).mappings().all()

    return templates.TemplateResponse(
        request=request,
        name="admin_pengajuan.html",
        context={
            "user": user,
            "pengajuan": data,
            "selected_status": status,
            "nik_selected": nik
        }
    )

@app.get("/admin/laporan", response_class=HTMLResponse)
async def cetak_laporan(
    request: Request,
    bulan: Optional[str] = None,
    tahun: Optional[str] = None
):

    user = request.session.get("user")

    if not user or user["role"] != "admin":
        return RedirectResponse("/dashboard", status_code=303)

    query = """
        SELECT *
        FROM pengajuan
        WHERE 1=1
    """

    params = {}

    if bulan and bulan != "":
        query += " AND MONTH(tanggal_pengajuan) = :bulan"
        params["bulan"] = int(bulan)

    if tahun and tahun != "":
        query += " AND YEAR(tanggal_pengajuan) = :tahun"
        params["tahun"] = int(tahun)

    query += " ORDER BY tanggal_pengajuan DESC"

    with engine.connect() as conn:
        data = conn.execute(text(query), params).mappings().all()

    return templates.TemplateResponse(
        request=request,
        name="laporan_pengajuan.html",
        context={
            "pengajuan": data,
            "bulan": bulan,
            "tahun": tahun
        }
    )

@app.get("/layanan", response_class=HTMLResponse)
async def layanan_page(request: Request):

    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM layanan")
    layanan = cursor.fetchall()
    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="layanan.html",
        context={
            "layanan": layanan,
            "user": request.session.get("user")
        }
    )

@app.get("/admin/layanan", response_class=HTMLResponse)
def admin_layanan(request: Request):

    user = request.session.get("user")

    if not user or user["role"] != "admin":
        return RedirectResponse("/dashboard", status_code=303)

    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM layanan ORDER BY id DESC")
    layanan = cursor.fetchall()
    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="admin_layanan.html",
        context={
            "user": user,
            "layanan": layanan
        }
    )

@app.get("/admin/layanan/hapus/{id}")
def hapus_layanan(id: int):

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM layanan WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    return RedirectResponse("/admin/layanan", status_code=303)

@app.get("/admin/layanan/edit/{id}")
def edit_layanan(request: Request, id: int):

    user = request.session.get("user")

    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM layanan WHERE id=%s", (id,))
    layanan = cursor.fetchone()
    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="edit_layanan.html",
        context={
            "user": user,
            "layanan": layanan
        }
    )

@app.post("/admin/layanan/update/{id}")
def update_layanan(
    id: int,
    judul: str = Form(...),
    waktu_proses: str = Form(...),
    deskripsi: str = Form(...)
):

    conn = get_db()
    cursor = conn.cursor()

    sql = """
        UPDATE layanan
        SET judul=%s, waktu_proses=%s, deskripsi=%s
        WHERE id=%s
    """

    cursor.execute(sql, (judul, waktu_proses, deskripsi, id))
    conn.commit()
    conn.close()

    return RedirectResponse("/admin/layanan", status_code=303)

@app.post("/admin/layanan/tambah")
async def tambah_layanan_post(request: Request):

    form = await request.form()

    judul = form.get("judul")
    waktu = form.get("waktu_proses")
    deskripsi = form.get("deskripsi")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO layanan (judul, waktu_proses, deskripsi)
        VALUES (%s, %s, %s)
    """, (judul, waktu, deskripsi))

    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin/layanan", status_code=303)

@app.get("/admin/layanan/tambah")
def tambah_layanan_get(request: Request):

    user = request.session.get("user")

    return templates.TemplateResponse(
        request=request,
        name="tambah_layanan.html",
        context={
            "user": user
        }
    )
