from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime, timedelta
from email.message import EmailMessage
import smtplib
import webbrowser

app = Flask(__name__)

app.secret_key = "  "

DB = "  "

print("APP STARTED")


# ================= DATABASE =================

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


# ================= INIT DATABASE =================

def init_db():

    conn = get_db()
    c = conn.cursor()

    # Hospital Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS hospital(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT
    )
    """)

    # Donor Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS donor(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        blood_group TEXT,
        location TEXT,
        last_donation TEXT,
        status TEXT
    )
    """)

    # Patient Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS patient(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hospital_id INTEGER,
        name TEXT,
        location TEXT,
        blood_group TEXT
    )
    """)

    # Request Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        donor_id INTEGER,
        response TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ================= EMAIL =================

def send_email(to, subject, msg):

    sender = "   "

    password = "  "

    try:

        em = EmailMessage()

        em["From"] = sender
        em["To"] = to
        em["Subject"] = subject

        em.set_content("Blood Request")
        em.add_alternative(msg, subtype="html")

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

        server.login(sender, password)

        server.send_message(em)

        server.quit()

        print("EMAIL SENT")

    except Exception as e:

        print("EMAIL ERROR :", e)


# ================= HOME =================

@app.route("/")
def home():
    return render_template("home.html")

# ================= DONOR REGISTER =================

@app.route("/donor_register", methods=["GET", "POST"])
def donor_register():

    if request.method == "POST":

        conn = get_db()
        c = conn.cursor()

        c.execute("""
        INSERT INTO donor
        (name,email,phone,blood_group,location,last_donation,status)
        VALUES (?,?,?,?,?,?,?)
        """, (

            request.form["name"],
            request.form["email"],
            request.form["phone"],
            request.form["blood_group"],
            request.form["location"],
            "",
            "AVAILABLE"

        ))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("donor_register.html")


# ================= HOSPITAL REGISTER =================

@app.route("/hospital_register", methods=["GET", "POST"])
def hospital_register():

    if request.method == "POST":

        conn = get_db()
        c = conn.cursor()

        c.execute("""
        INSERT INTO hospital(name,email,password)
        VALUES (?,?,?)
        """, (
            request.form["name"],
            request.form["email"],
            request.form["password"]
        ))

        conn.commit()
        conn.close()

        return redirect("/hospital_login")

    return render_template("hospital_register.html")


# ================= HOSPITAL LOGIN =================

@app.route("/hospital_login", methods=["GET", "POST"])
def hospital_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()

        c.execute("SELECT * FROM hospital")
        hospitals = c.fetchall()

        print("\n===== HOSPITALS =====")
        for h in hospitals:
            print(dict(h))

        c.execute(
            "SELECT * FROM hospital WHERE email=?",
            (email,)
        )

        hospital = c.fetchone()

        if hospital:
            print("DATABASE PASSWORD =", hospital["password"])
            print("ENTERED PASSWORD =", password)

        conn.close()

        if hospital and hospital["password"] == password:
            session["hospital_id"] = hospital["id"]
            return redirect("/hospital_dashboard")

        return """
        <h2>Invalid Email or Password ❌</h2>
        <a href='/hospital_login'>Try Again</a>
        """

    return render_template("hospital_login.html")

# ================= DASHBOARD =================

@app.route("/hospital_dashboard")
def hospital_dashboard():

    if "hospital_id" not in session:
        return redirect("/hospital_login")

    return render_template("hospital_dashboard.html")


# ================= ADD DONOR =================

@app.route("/add_donor", methods=["GET", "POST"])
def add_donor():

    # if "hospital_id" not in session:
    #     return redirect("/hospital_login")

    if request.method == "POST":

        conn = get_db()
        c = conn.cursor()

        c.execute("""
       INSERT INTO donor
       (name,email,phone,blood_group,location,last_donation,status)
       VALUES (?,?,?,?,?,?,?)
       """, (

             request.form["name"],
             request.form["email"],
             request.form["phone"],
             request.form["blood_group"],
             request.form["location"],
             request.form.get("last_donation", ""),
             request.form.get("status", "AVAILABLE")

             ))

        conn.commit()
        conn.close()

        return redirect("/donors")

    return render_template("add_donor.html")

# ================= VIEW DONORS =================
 
@app.route("/donors")
def donors():

    if "hospital_id" not in session:
        return redirect("/hospital_login")

    conn = get_db()

    c = conn.cursor()

    c.execute("SELECT * FROM donor")

    data = c.fetchall()

    donors = []

    for donor in data:

        donor = list(donor)

        # CHECK LAST DONATION DATE
        if donor[6]:

            donation_date = datetime.strptime(
                donor[6],
                "%Y-%m-%d"
            )

            next_date = donation_date + timedelta(days=90)

            remaining_days = (
                next_date - datetime.now()
            ).days

            # IF 90 DAYS COMPLETED
            if remaining_days <= 0:

                remaining_days = 0

                donor[7] = "AVAILABLE"

            else:

                donor[7] = "CONFIRMED"

        else:

            donor[6] = "Never Donated"

            remaining_days = "Available"

            donor[7] = "AVAILABLE"

        # ADD REMAINING DAYS
        donor.append(remaining_days)

        donors.append(donor)

    conn.close()

    return render_template(
        "donors.html",
        donors=donors
    )

# ================= ADD PATIENT =================

@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():

    if "hospital_id" not in session:
        return redirect("/hospital_login")


    if request.method == "POST":

        conn = get_db()
        c = conn.cursor()


        c.execute("""
        INSERT INTO patient(hospital_id,name,location,blood_group)
        VALUES (?,?,?,?)
        """, (
            session["hospital_id"],
            request.form["name"],
            request.form["location"],
            request.form["blood_group"]
        ))


        patient_id = c.lastrowid


        c.execute("""
        SELECT * FROM donor
        WHERE blood_group=?
        ORDER BY id DESC
        """, (
            request.form["blood_group"],
            
        ))


        all_donors = c.fetchall()

        donor_list = []

        remaining_days = 0


        for donor in all_donors:


            if donor["last_donation"] == "" or donor["last_donation"] is None:

                donor_list.append(donor)


            else:

                donation_date = datetime.strptime(
                    donor["last_donation"],
                    "%Y-%m-%d"
                )


                next_available = donation_date + timedelta(days=90)


                days = (
                    next_available - datetime.now()
                ).days



                if days <= 0:

                    donor_list.append(donor)

                else:

                    remaining_days = days




        # NO DONOR AVAILABLE
        if not donor_list:


            if remaining_days < 0:
                remaining_days = 0


            conn.close()


            return f"""
            <h2>No Donor Available ❌</h2>

            <p>This blood group donor already donated blood.</p>

            <p>Please contact after {remaining_days} days.</p>

            <br>

            <a href='/hospital_dashboard'>
            Back to Dashboard
            </a>
            """




        # SEND EMAIL
        for donor in donor_list:


            donor_id = donor["id"]

            email = donor["email"]


            send_email(
                email,
                "Blood Request",
                f"""
                <h2>Emergency Blood Request</h2>

                <p>Patient Name :
                {request.form['name']}</p>

                <p>Location :
                {request.form['location']}</p>

                <p>Blood Group :
                {request.form['blood_group']}</p>

                <p>Please contact after 0 days.</p>


                <a href='http://127.0.0.1:5000/response/{patient_id}/YES/{donor_id}'>
                ACCEPT
                </a>


                <br><br>


                <a href='http://127.0.0.1:5000/response/{patient_id}/NO/{donor_id}'>
                REJECT
                </a>
                """
            )


        conn.commit()
        conn.close()


        return redirect("/hospital_dashboard")


    return render_template("add_patient.html")
# ================= RESPONSE =================

@app.route("/response/<int:patient_id>/<answer>/<int:donor_id>")
def response(patient_id, answer, donor_id):

    conn = get_db()
    c = conn.cursor()

    # SAVE REQUEST RESPONSE
    c.execute("""
    INSERT INTO requests(patient_id, donor_id, response)
    VALUES (?,?,?)
    """, (
        patient_id,
        donor_id,
        answer
    ))

    # IF DONOR ACCEPTS
    if answer == "YES":

        today = datetime.now().strftime("%Y-%m-%d")

        # GET DONOR DETAILS
        c.execute("""
        SELECT * FROM donor
        WHERE id=?
        """, (donor_id,))

        donor = c.fetchone()

        # UPDATE DONOR STATUS
        c.execute("""
        UPDATE donor
        SET
        status=?,
        last_donation=?
        WHERE id=?
        """, (
            "NOT AVAILABLE",
            today,
            donor_id
        ))

        # SEND EMAIL
        send_email(
            donor["email"],
            "Blood Donation Confirmed",
            f"""
            <h2>❤️ Blood Donation Successful</h2>

            <p>Dear {donor['name']},</p>

            <p>Thank you for your generous blood donation.</p>

            <p><b>Donation Date:</b> {today}</p>

            <p>
            For your safety and well-being, you are not eligible
            to donate blood again for the next <b>90 days</b>.
            </p>

            <p>
            Please take proper rest, stay hydrated,
            and maintain a healthy diet.
            </p>

            <p>Thank you for helping save a life. ❤️</p>
            """
        )

        conn.commit()
        conn.close()

        return f"""
        <h1>❤️ Donation Confirmed</h1>

        <h3>Thank You For Donating Blood</h3>

        <p><b>Donation Date:</b> {today}</p>

        <p>
        You are not eligible to donate blood again
        for the next <b>90 days</b>.
        </p>

        <p>
        Please take care of your health and stay hydrated.
        </p>

        <br>

        <a href='/donors'>
        View Donors List
        </a>
        """

    conn.commit()
    conn.close()

    return """
    <h1>Donation Declined ❌</h1>
    """


# ================= EDIT DONOR =================

@app.route("/edit_donor/<int:donor_id>", methods=["GET", "POST"])
def edit_donor(donor_id):

    if "hospital_id" not in session:
        return redirect("/hospital_login")

    conn = get_db()

    c = conn.cursor()

    c.execute("""
    SELECT * FROM donor WHERE id=?
    """, (donor_id,))

    donor = c.fetchone()

    if request.method == "POST":

        c.execute("""
        UPDATE donor
        SET
        name=?,
        email=?,
        phone=?,
        blood_group=?,
        location=?,
        last_donation=?,
        status=?
        WHERE id=?
        """, (

            request.form["name"],
            request.form["email"],
            request.form["phone"],
            request.form["blood_group"],
            request.form["location"],
            request.form["last_donation"],
            request.form["status"],
            donor_id

        ))

        conn.commit()
        conn.close()

        return redirect("/donors")

    conn.close()

    return render_template(
        "edit_donor.html",
        donor=donor
    )


# ================= DELETE DONOR =================

@app.route("/delete_donor/<int:donor_id>")
def delete_donor(donor_id):

    if "hospital_id" not in session:
        return redirect("/hospital_login")

    conn = get_db()

    c = conn.cursor()

    c.execute("""
    DELETE FROM donor WHERE id=?
    """, (donor_id,))

    conn.commit()

    conn.close()

    return redirect("/donors")


# ================= LOGOUT =================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ================= ALL HOSPITALS =================

@app.route("/all_hospitals")
def all_hospitals():

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM hospital")

    hospitals = c.fetchall()

    conn.close()

    return str([dict(x) for x in hospitals])


# ================= CHECK DONOR =================

@app.route("/reset_donor")
def reset_donor():

    conn = get_db()
    c = conn.cursor()

    c.execute("DELETE FROM donor")
    c.execute("DELETE FROM sqlite_sequence WHERE name='donor'")

    conn.commit()
    conn.close()

    return "Donor table reset successfully"

# ================= RUN =================

if __name__ == "__main__":

    webbrowser.open("http://127.0.0.1:5000")

    app.run(debug=True) 
