from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Numeric
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='staff')
    branch = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    abn = db.Column(db.String(20), unique=True)
    contact_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(20))
    postal_code = db.Column(db.String(10))
    credit_limit = db.Column(Numeric(10, 2), default=0.00)
    payment_terms = db.Column(db.String(50), default='30 days')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    quotes = db.relationship('Quote', backref='customer', lazy=True)

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50))
    serial_number = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    daily_rate = db.Column(Numeric(10, 2), nullable=False)
    weekly_rate = db.Column(Numeric(10, 2), nullable=False)
    monthly_rate = db.Column(Numeric(10, 2), nullable=False)
    availability_status = db.Column(db.String(20), default='available')
    branch = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(200))
    specifications = db.Column(db.Text)  # Store JSON as text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_specifications(self):
        """Get specifications as a dictionary"""
        if self.specifications:
            try:
                return json.loads(self.specifications)
            except:
                return {}
        return {}
    
    def set_specifications(self, specs_dict):
        """Set specifications from a dictionary"""
        self.specifications = json.dumps(specs_dict) if specs_dict else None

class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    job_name = db.Column(db.String(200), nullable=False)
    job_address = db.Column(db.Text)
    hire_start_date = db.Column(db.Date, nullable=False)
    hire_end_date = db.Column(db.Date, nullable=False)
    subtotal = db.Column(Numeric(10, 2), nullable=False)
    discount = db.Column(Numeric(10, 2), default=0.00)
    gst = db.Column(Numeric(10, 2), nullable=False)
    total = db.Column(Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='draft')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('QuoteItem', backref='quote', lazy=True, cascade='all, delete-orphan')

class QuoteItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quote.id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    unit_rate = db.Column(Numeric(10, 2), nullable=False)
    total_amount = db.Column(Numeric(10, 2), nullable=False)
    equipment = db.relationship('Equipment', backref='quote_items')

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_number = db.Column(db.String(20), unique=True, nullable=False)
    quote_id = db.Column(db.Integer, db.ForeignKey('quote.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    job_name = db.Column(db.String(200), nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_date = db.Column(db.DateTime, nullable=False)
    pickup_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='confirmed')
    total_amount = db.Column(Numeric(10, 2), nullable=False)
    deposit_amount = db.Column(Numeric(10, 2), default=0.00)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('BookingItem', backref='booking', lazy=True, cascade='all, delete-orphan')

class BookingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_rate = db.Column(Numeric(10, 2), nullable=False)
    total_amount = db.Column(Numeric(10, 2), nullable=False)
    equipment = db.relationship('Equipment', backref='booking_items')

class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_number = db.Column(db.String(20), unique=True, nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    terms_conditions = db.Column(db.Text)
    signature_status = db.Column(db.String(20), default='pending')
    signed_date = db.Column(db.DateTime)
    pdf_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    booking = db.relationship('Booking', backref='contract')

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    old_values = db.Column(db.Text)  # Store JSON as text
    new_values = db.Column(db.Text)  # Store JSON as text
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='audit_logs')
    
    def get_old_values(self):
        """Get old values as a dictionary"""
        if self.old_values:
            try:
                return json.loads(self.old_values)
            except:
                return {}
        return {}
    
    def set_old_values(self, values_dict):
        """Set old values from a dictionary"""
        self.old_values = json.dumps(values_dict) if values_dict else None
        
    def get_new_values(self):
        """Get new values as a dictionary"""
        if self.new_values:
            try:
                return json.loads(self.new_values)
            except:
                return {}
        return {}
    
    def set_new_values(self, values_dict):
        """Set new values from a dictionary"""
        self.new_values = json.dumps(values_dict) if values_dict else None