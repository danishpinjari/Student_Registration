import psycopg2

try:
    conn = psycopg2.connect(
        host="dpg-d1ko4hndiees73eq3v3g-a.oregon-postgres.render.com",  # Full hostname
        database="student_db_dz7u",
        user="student_admin",
        password="QELmjYG4FZ6ot17yCTkCAgdNvwmjNPBS",
        port=5432,
        sslmode="require"
    )
    print("✅ Connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")