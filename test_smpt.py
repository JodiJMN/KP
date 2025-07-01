import smtplib

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('chatgptkw1@gmail.com', 'iojsrwmtzsnmmomd')  # Bukan password biasa!
    print("Berhasil login SMTP Gmail!")
    server.quit()
except Exception as e:
    print("Gagal login SMTP:", e)
