from werkzeug.security import generate_password_hash

hashed = generate_password_hash("11")
print(hashed)