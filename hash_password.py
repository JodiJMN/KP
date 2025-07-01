from flask_bcrypt import Bcrypt
from db import get_connection

bcrypt = Bcrypt()

def is_already_bcrypt(password):
    return password.startswith("$2b$") or password.startswith("$2a$")

def hash_all_user_passwords():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, password FROM tb_user")
    users = cursor.fetchall()

    updated = 0
    for user_id, password in users:
        if not is_already_bcrypt(password):
            hashed = bcrypt.generate_password_hash(password).decode('utf-8')
            cursor.execute("UPDATE tb_user SET password = %s WHERE user_id = %s", (hashed, user_id))
            updated += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ {updated} password berhasil di-hash dengan bcrypt.")
    
if __name__ == "__main__":
    print("🚀 Memulai proses hashing password dengan bcrypt...")
    hash_all_user_passwords()