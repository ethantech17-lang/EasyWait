# ================= IMPORTS =================
from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
import os
import requests
import uuid
from apscheduler.schedulers.background import BackgroundScheduler

# ================= APP =================

app = Flask(__name__)

# ================= DATABASE =================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///easywait.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ================= EMAIL CONFIG =================

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True

db = SQLAlchemy(app)
mail = Mail(app)

PESAPAL_CONSUMER_KEY = "MTH6KAHvTneDUBx11LK3+IHOHLjs2+tL"
PESAPAL_CONSUMER_SECRET = "W5icrl/m4kvAu2p9cexK32UXE/4="
PESAPAL_BASE_URL = "https://cybqa.pesapal.com/pesapalv3"

# ================= ADMIN MODEL =================

class Admin(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )
    password = db.Column(
        db.String(100),
        nullable=False
    )

# ================= BUSINESS MODEL =================

class Business(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    admin_id = db.Column(
        db.Integer,
        nullable=False
    )
    name = db.Column(
        db.String(200),
        nullable=False
    )
    type = db.Column(
        db.String(200),
        nullable=False
    )
    location = db.Column(
        db.String(200),
        nullable=False
    )
    email = db.Column(
        db.String(200),
        nullable=False
    )
    business_password = db.Column(
        db.String(200),
        nullable=False
    )
    phone = db.Column(
        db.String(100),
        nullable=False
    )
    is_active = db.Column(db.Boolean, default=False)
    payment_status = db.Column(db.String(50), default="pending")
    subscription_start = db.Column(db.DateTime)
    subscription_end = db.Column(db.DateTime)

# ================= QUEUE MODEL =================

class Queue(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    business_id = db.Column(
        db.Integer,
        nullable=False
    )
    customer_name = db.Column(
        db.String(200),
        nullable=False
    )
    phone = db.Column(
        db.String(100),
        nullable=False
    )
    email = db.Column(
        db.String(200),
        nullable=False
    )
    booking_date = db.Column(
        db.String(100),
        nullable=False
    )
    booking_time = db.Column(
        db.String(100),
        nullable=False
    )
    status = db.Column(
        db.String(100),
        default="Waiting"
    )

#================== GET PESAPAL TOKEN =================

def get_pesapal_token():
    url = f"{PESAPAL_BASE_URL}/api/Auth/RequestToken"

    payload = {
        "consumer_key": "MTH6KAHvTneDUBx11LK3+IHOHLjs2+tL",
        "consumer_secret": "W5icrl/m4kvAu2p9cexK32UXE/4="
    }

    res = requests.post(url, json=payload)
    return res.json()["token"]  

#================== PAY BUSINESS =================
@app.route("/pay/<int:business_id>")
def pay_business(business_id):
    business = Business.query.get(business_id)

    if not business:
        return "Business not found"

    token = get_pesapal_token()
    order_id = str(uuid.uuid4())

    payload = {
        "id": order_id,
        "currency": "KES",
        "amount": 500,
        "description": "EasyWait Subscription",
        "callback_url": "http://127.0.0.1:5000/pesapal/callback",
        "notification_id": "your_ipn_id",
        "billing_address": {
            "phone_number": business.phone,
            "email_address": business.email,
            "country_code": "KE"
        }
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = f"{PESAPAL_BASE_URL}/api/Transactions/SubmitOrderRequest"
    res = requests.post(url, json=payload, headers=headers)

    return redirect(res.json()["redirect_url"])

# ================= HOME PAGE =================

@app.route("/")
def home():
    return render_template("index.html")

# ================= BUSINESS PAGE =================

@app.route("/business")
def business():
    return render_template("business.html")

# ================= ADMIN PAGE =================

@app.route("/admin")
def admin():
    return render_template("admin.html")

# ================= CUSTOMER PAGE =================

@app.route("/customer")
def customer():
    return render_template("customer.html")

# ================= REGISTER ADMIN =================

@app.route("/register_admin", methods=["POST"])
def register_admin():
    try:
        data = request.get_json()
        existing_admin = Admin.query.filter_by(
            username=data["username"]
        ).first()

        if existing_admin:
            return jsonify({
                "success": False,
                "message": "Username already exists"
            })

        admin = Admin(
            username=data["username"],
            password=data["password"]
        )

        db.session.add(admin)
        db.session.commit()

        return jsonify({
            "success": True,
            "admin_id": admin.id
        })

    except Exception as e:
        print(e)
        return jsonify({
            "success": False,
            "message": "Server Error"
        })

# ================= LOGIN ADMIN =================

@app.route("/login_admin", methods=["POST"])
def login_admin():
    try:
        data = request.get_json()
        admin = Admin.query.filter_by(
            username=data["username"],
            password=data["password"]
        ).first()

        if not admin:
            return jsonify({
                "success": False,
                "message": "Invalid Login"
            })

        return jsonify({
            "success": True,
            "admin_id": admin.id
        })

    except Exception as e:
        print(e)
        return jsonify({
            "success": False,
            "message": "Server Error"
        })

# ================= REGISTER BUSINESS =================

@app.route("/register_business", methods=["POST"])
def register_business():
    try:
        data = request.get_json()
        business = Business(
            admin_id=int(data["admin_id"]),
            name=data["name"],
            type=data["type"],
            location=data["location"],
            email=data["email"],
            business_password=data["business_password"],
            phone=data["phone"]
        )

        db.session.add(business)
        db.session.commit()

        return jsonify({
            "success": True
        })

    except Exception as e:
        print(e)
        return jsonify({
            "success": False,
            "message": str(e)
        })

# ================= GET BUSINESSES =================

@app.route("/get_businesses")
def get_businesses():
    businesses = Business.query.all()
    results = []

    for business in businesses:
        results.append({
            "id": business.id,
            "admin_id": business.admin_id,
            "name": business.name,
            "type": business.type,
            "location": business.location,
            "email": business.email,
            "phone": business.phone
        })

    return jsonify(results)

# ================= JOIN QUEUE =================

@app.route("/join_queue", methods=["POST"])
def join_queue():
    try:
        data = request.get_json()
        queue = Queue(
            business_id=data["business_id"],
            customer_name=data["customer_name"],
            phone=data["phone"],
            email=data["email"],
            booking_date=data["booking_date"],
            booking_time=data["booking_time"]
        )

        db.session.add(queue)
        db.session.commit()

        # ================= GET BUSINESS =================
        business = Business.query.get(data["business_id"])

        # ================= QUEUE NUMBER =================
        queue_number = Queue.query.filter_by(
            business_id=data["business_id"]
        ).count()

        # ================= PDF FILE =================
        pdf_file = f"ticket_{queue.id}.pdf".strip()

        # ================= CREATE PDF =================
        pdf = canvas.Canvas(pdf_file)
        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawString(170, 800, "EasyWait Ticket")
        pdf.setFont("Helvetica", 14)
        pdf.drawString(50, 730, f"Business: {business.name}")
        pdf.drawString(50, 700, f"Customer: {data['customer_name']}")
        pdf.drawString(50, 670, f"Queue Number: {queue_number}")
        pdf.drawString(50, 640, f"Date: {data['booking_date']}")
        pdf.drawString(50, 610, f"Time: {data['booking_time']}")
        pdf.drawString(50, 580, "Status: Waiting")
        pdf.drawString(50, 520, "Thank you for using EasyWait")
        pdf.save()

        # ================= EMAIL CONFIG =================
        app.config["MAIL_USERNAME"] = business.email
        app.config["MAIL_PASSWORD"] = business.business_password

        global mail
        mail = Mail(app)

        # ================= EMAIL =================
        message = Message(
            subject="EasyWait Queue Ticket",
            sender=business.email,
            recipients=[data["email"]]
        )

        message.body = f"""
Hello {data['customer_name']}

Your booking was successful.

Queue Number: {queue_number}

Please check the attached PDF ticket.

Thank you for using EasyWait.
        """

        with app.open_resource(pdf_file) as pdf_attachment:
            message.attach(
                pdf_file,
                "application/pdf",
                pdf_attachment.read()
            )

        mail.send(message)
        os.remove(pdf_file)

        return jsonify({
            "success": True,
            "queue_number": queue_number
        })

    except Exception as e:
        print(e)
        return jsonify({
            "success": False,
            "message": str(e)
        })

# ================= GET QUEUE =================

@app.route("/get_queue/<int:business_id>")
def get_queue(business_id):
    queues = Queue.query.filter_by(
        business_id=business_id
    ).all()

    results = []
    count = 1

    for queue in queues:
        results.append({
            "id": queue.id,
            "queue_number": count,
            "customer_name": queue.customer_name,
            "phone": queue.phone,
            "email": queue.email,
            "booking_date": queue.booking_date,
            "booking_time": queue.booking_time,
            "status": queue.status
        })
        count += 1

    return jsonify(results)

# ================= UPDATE STATUS =================

@app.route("/update_status/<int:id>", methods=["POST"])
def update_status(id):
    try:
        data = request.get_json()
        queue = Queue.query.get(id)

        if queue:
            queue.status = data["status"]
            db.session.commit()

        return jsonify({"success": True})

    except Exception as e:
        print(e)
        return jsonify({"success": False})

# ================= DELETE QUEUE =================

@app.route("/delete_queue/<int:id>", methods=["DELETE"])
def delete_queue(id):
    try:
        queue = Queue.query.get(id)

        if queue:
            db.session.delete(queue)
            db.session.commit()

        return jsonify({"success": True})

    except Exception as e:
        print(e)
        return jsonify({"success": False})

# ================= DELETE BUSINESS =================

@app.route("/delete_business/<int:id>", methods=["DELETE"])
def delete_business(id):
    try:
        business = Business.query.get(id)

        if business:
            Queue.query.filter_by(business_id=id).delete()
            db.session.delete(business)
            db.session.commit()

        return jsonify({"success": True})

    except Exception as e:
        print(e)
        return jsonify({"success": False})

# ================= CREATE DATABASE =================

with app.app_context():
    db.create_all()

# ================= START APP =================

if __name__ == "__main__":
    app.run(debug=True)