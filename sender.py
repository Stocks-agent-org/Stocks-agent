def poslji_email(subject, body, prejemnik="prejemnik@example.com"):
    posiljatelj = "tvoj_email@gmail.com"
    geslo = "tvoje_geslo"

    msg = MIMEMultipart()
    msg['From'] = posiljatelj
    msg['To'] = prejemnik
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(posiljatelj, geslo)
        text = msg.as_string()
        server.sendmail(posiljatelj, prejemnik, text)
        server.quit()
        print(f"✅ E-pošta za {subject} poslana.")
    except Exception as e:
        print(f"❌ Napaka pri pošiljanju e-pošte: {e}")
