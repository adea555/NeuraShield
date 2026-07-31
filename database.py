import sqlite3
from datetime import date


DATABASE = "mental_health.db"



# --------------------------------
# Lidhja me databazen
# --------------------------------

def connect():

    conn = sqlite3.connect(
        DATABASE
    )

    conn.row_factory = sqlite3.Row

    return conn



# --------------------------------
# Krijimi i tabelave
# --------------------------------

def init_db():

    conn = connect()

    cursor = conn.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS moods
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            date TEXT NOT NULL,

            mood TEXT NOT NULL,

            note TEXT
        )
    """)


    conn.commit()

    conn.close()



# --------------------------------
# Ruajtja e check-in
# --------------------------------

def save_mood(
        mood_date,
        mood,
        note
):

    conn = connect()

    cursor = conn.cursor()


    cursor.execute(
        """
        INSERT INTO moods
        (
            date,
            mood,
            note
        )

        VALUES
        (
            ?,
            ?,
            ?
        )
        """,

        (
            mood_date,
            mood,
            note
        )

    )


    conn.commit()

    conn.close()



# --------------------------------
# Kontrollo check-in e sotem
# --------------------------------

def get_today_mood():

    today = date.today().isoformat()


    conn = connect()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM moods
        WHERE date = ?
        """,

        (today,)
    )


    result = cursor.fetchone()


    conn.close()


    return result



# --------------------------------
# Merr te gjitha te dhenat
# --------------------------------

def get_all_moods():

    conn = connect()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM moods
        ORDER BY date ASC
        """
    )


    rows = cursor.fetchall()


    conn.close()



    return [

        {

            "id": row["id"],

            "date": row["date"],

            "mood": row["mood"],

            "note": row["note"]

        }

        for row in rows

    ]



# --------------------------------
# Statistika per Dashboard
# --------------------------------

def get_statistics():

    moods = get_all_moods()


    total = len(moods)


    happy = sum(
        1
        for m in moods
        if m["mood"] == "happy"
    )


    sad = sum(
        1
        for m in moods
        if m["mood"] == "sad"
    )


    anxious = sum(
        1
        for m in moods
        if m["mood"] == "anxious"
    )


    calm = sum(
        1
        for m in moods
        if m["mood"] == "calm"
    )


    angry = sum(
        1
        for m in moods
        if m["mood"] == "angry"
    )


    # Streak aktual
    streak = 0

    today = date.today()


    dates = {

        m["date"]

        for m in moods

    }



    while today.isoformat() in dates:

        streak += 1

        today = today.fromordinal(
            today.toordinal()-1
        )


    return {

        "total": total,

        "happy": happy,

        "sad": sad,

        "anxious": anxious,

        "calm": calm,

        "angry": angry,

        "streak": streak

    }