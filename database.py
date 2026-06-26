from sqlalchemy import create_engine, text

DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_NAME = "disdukcapil_TA"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

# Auto-migration to ensure required columns exist in 'pengajuan' table
try:
    with engine.connect() as conn:
        # Check columns
        columns_result = conn.execute(text("SHOW COLUMNS FROM pengajuan")).mappings().all()
        existing_cols = {col['Field'].lower() for col in columns_result}
        
        required_cols = {
            "no_kk": "VARCHAR(16) NULL",
            "alamat": "TEXT NULL",
            "provinsi": "VARCHAR(100) NULL",
            "kabupaten": "VARCHAR(100) NULL",
            "kecamatan": "VARCHAR(100) NULL",
            "desa": "VARCHAR(100) NULL"
        }
        
        needs_commit = False
        for col_name, col_type in required_cols.items():
            if col_name not in existing_cols:
                conn.execute(text(f"ALTER TABLE pengajuan ADD COLUMN {col_name} {col_type}"))
                print(f"Added column {col_name} to table pengajuan")
                needs_commit = True
        
        if needs_commit:
            conn.commit()
except Exception as e:
    print(f"Migration error: {e}")