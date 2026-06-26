import bcrypt
from sqlalchemy import text
from database import engine

with engine.connect() as conn:
    # ambil semua user
    users = conn.execute(text("SELECT id, password FROM users")).mappings().all()

    for user in users:
        password = user["password"]

        # skip kalau sudah di-hash (bcrypt selalu diawali $2b$)
        if password.startswith("$2b$"):
            print(f"User {user['id']} sudah di-hash, skip")
            continue

        # hash password lama
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # update ke database
        conn.execute(
            text("UPDATE users SET password = :password WHERE id = :id"),
            {
                "password": hashed.decode("utf-8"),
                "id": user["id"]
            }
        )

        print(f"User {user['id']} berhasil di-hash")

    conn.commit()

print("Selesai!")