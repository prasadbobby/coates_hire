from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models import db, User, Customer, Equipment, Quote, QuoteItem, Booking, BookingItem, Contract, AuditLog
from config import Config
import os
from datetime import datetime, timedelta
from decimal import Decimal
import json

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_dummy_data():
    """Create dummy data for testing"""
    if User.query.count() == 0:
        # Create users
        admin = User(
            username='admin',
            email='admin@coates.com.au',
            first_name='Admin',
            last_name='User',
            role='admin',
            branch='Sydney'
        )
        admin.set_password('admin123')
        
        staff1 = User(
            username='john.smith',
            email='john.smith@coates.com.au',
            first_name='John',
            last_name='Smith',
            role='staff',
            branch='Melbourne'
        )
        staff1.set_password('staff123')
        
        staff2 = User(
            username='sarah.jones',
            email='sarah.jones@coates.com.au',
            first_name='Sarah',
            last_name='Jones',
            role='manager',
            branch='Brisbane'
        )
        staff2.set_password('manager123')
        
        db.session.add_all([admin, staff1, staff2])
        
        # Create customers
        customers = [
            Customer(
                company_name='ABC Construction Pty Ltd',
                abn='12345678901',
                contact_name='Michael Johnson',
                email='michael@abcconstruction.com.au',
                phone='0412345678',
                address='123 Builder Street',
                city='Sydney',
                state='NSW',
                postal_code='2000',
                credit_limit=Decimal('50000.00'),
                payment_terms='30 days'
            ),
            Customer(
                company_name='XYZ Mining Corp',
                abn='98765432109',
                contact_name='Lisa Chen',
                email='lisa@xyzmining.com.au',
                phone='0487654321',
                address='456 Mining Road',
                city='Perth',
                state='WA',
                postal_code='6000',
                credit_limit=Decimal('100000.00'),
                payment_terms='14 days'
            ),
            Customer(
                company_name='Green Energy Solutions',
                abn='11223344556',
                contact_name='Robert Taylor',
                email='robert@greenenergy.com.au',
                phone='0411223344',
                address='789 Solar Avenue',
                city='Adelaide',
                state='SA',
                postal_code='5000',
                credit_limit=Decimal('75000.00'),
                payment_terms='45 days'
            )
        ]
        
        db.session.add_all(customers)
        
        # Create equipment
        equipment_list = [
            Equipment(
                name='20T Excavator',
                category='Earthmoving',
                model='CAT 320',
                serial_number='EX001',
                description='Heavy duty excavator for earthmoving operations',
                daily_rate=Decimal('850.00'),
                weekly_rate=Decimal('4250.00'),
                monthly_rate=Decimal('15000.00'),
                availability_status='available',
                branch='Sydney',
                image_url='https://via.placeholder.com/300x200/FF6B35/FFFFFF?text=20T+Excavator',
                specifications='{"weight": "20000kg", "engine": "CAT C7.1", "bucket_capacity": "1.2m³"}'
            ),
            Equipment(
                name='Skid Steer Loader',
                category='Earthmoving',
                model='Bobcat S650',
                serial_number='SS001',
                description='Compact skid steer loader for tight spaces',
                daily_rate=Decimal('320.00'),
                weekly_rate=Decimal('1600.00'),
                monthly_rate=Decimal('5600.00'),
                availability_status='available',
                branch='Melbourne',
                image_url='https://via.placeholder.com/300x200/FF6B35/FFFFFF?text=Skid+Steer',
                specifications='{"weight": "3200kg", "engine": "Kubota V2607", "bucket_capacity": "0.4m³"}'
            ),
            Equipment(
                name='Mobile Crane 25T',
                category='Lifting',
                model='Grove RT530E',
                serial_number='CR001',
                description='All-terrain mobile crane for heavy lifting',
                daily_rate=Decimal('1200.00'),
                weekly_rate=Decimal('6000.00'),
                monthly_rate=Decimal('21000.00'),
                availability_status='available',
                branch='Brisbane',
                image_url='https://via.placeholder.com/300x200/FF6B35/FFFFFF?text=Mobile+Crane',
                specifications='{"capacity": "25000kg", "boom_length": "31m", "engine": "Cummins QSB6.7"}'
            ),
            Equipment(
                name='Scissor Lift 10m',
                category='Lifting',
                model='Genie GS-3390RT',
                serial_number='SL001',
                description='Self-propelled scissor lift for aerial work',
                daily_rate=Decimal('180.00'),
                weekly_rate=Decimal('900.00'),
                monthly_rate=Decimal('3150.00'),
                availability_status='available',
                branch='Perth',
                image_url='https://via.placeholder.com/300x200/FF6B35/FFFFFF?text=Scissor+Lift',
                specifications='{"height": "10m", "capacity": "680kg", "engine": "Deutz D2011L04W"}'
            ),
            Equipment(
                name='Compactor Roller',
                category='Compaction',
                model='Dynapac CC1200',
                serial_number='CM001',
                description='Smooth drum compactor for road construction',
                daily_rate=Decimal('450.00'),
                weekly_rate=Decimal('2250.00'),
                monthly_rate=Decimal('7875.00'),
                availability_status='on_hire',
                branch='Adelaide',
                image_url='https://via.placeholder.com/300x200/FF6B35/FFFFFF?text=Compactor',
                specifications='{"weight": "1200kg", "engine": "Hatz 1B40", "drum_width": "610mm"}'
            ),
            Equipment(
                name='Generator 100kVA',
                category='Power',
                model='Caterpillar C4.4',
                serial_number='GN001',
                description='Diesel generator for temporary power supply',
                daily_rate=Decimal('220.00'),
                weekly_rate=Decimal('1100.00'),
                monthly_rate=Decimal('3850.00'),
                availability_status='available',
                branch='Sydney',
                image_url='https://via.placeholder.com/300x200/FF6B35/FFFFFF?text=Generator',
                specifications='{"power": "100kVA", "fuel_tank": "400L", "engine": "CAT C4.4"}'
            ),
            Equipment(
                name='Telehandler 4T',
                category='Lifting',
                model='JCB 540-170',
                serial_number='TH001',
                description='Telescopic handler for material handling',
                daily_rate=Decimal('380.00'),
                weekly_rate=Decimal('1900.00'),
                monthly_rate=Decimal('6650.00'),
                availability_status='maintenance',
                branch='Melbourne',
                image_url='https://via.placeholder.com/300x200/FF6B35/FFFFFF?text=Telehandler',
                specifications='{"capacity": "4000kg", "lift_height": "17m", "engine": "JCB EcoMAX"}'
            ),
            Equipment(
                name='Dump Truck 10T',
                category='Transport',
                model='Isuzu FVZ1400',
                serial_number='DT001',
                description='Medium duty dump truck for material transport',
                daily_rate=Decimal('680.00'),
                weekly_rate=Decimal('3400.00'),
                monthly_rate=Decimal('11900.00'),
                availability_status='available',
                branch='Brisbane',
                image_url='https://via.placeholder.com/300x200/FF6B35/FFFFFF?text=Dump+Truck',
                specifications='{"capacity": "10000kg", "engine": "Isuzu 6HK1", "transmission": "Manual"}'
            )
        ]
        
        db.session.add_all(equipment_list)
        db.session.commit()

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get dashboard statistics
    total_customers = Customer.query.count()
    total_equipment = Equipment.query.count()
    available_equipment = Equipment.query.filter_by(availability_status='available').count()
    active_bookings = Booking.query.filter_by(status='confirmed').count()
    
    # Recent quotes
    recent_quotes = Quote.query.order_by(Quote.created_at.desc()).limit(5).all()
    
    # Equipment utilization - Convert Row objects to serializable data with proper type conversion
    equipment_stats_raw = db.session.query(
        Equipment.category,
        db.func.count(Equipment.id).label('total'),
        db.func.sum(
            db.case(
                (Equipment.availability_status == 'available', 1),
                else_=0
            )
        ).label('available')
    ).group_by(Equipment.category).all()
    
    # Convert to JSON-serializable format with proper type handling
    equipment_stats = []
    for row in equipment_stats_raw:
        total_count = int(row.total) if row.total else 0
        available_count = int(row.available) if row.available else 0
        
        equipment_stats.append({
            'category': str(row.category),
            'total': total_count,
            'available': available_count,
            'percentage': round((available_count / total_count * 100) if total_count > 0 else 0, 1)
        })
    
    return render_template('dashboard.html', 
                         total_customers=total_customers,
                         total_equipment=total_equipment,
                         available_equipment=available_equipment,
                         active_bookings=active_bookings,
                         recent_quotes=recent_quotes,
                         equipment_stats=equipment_stats)

@app.route('/customers')
@login_required
def customers():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Customer.query
    if search:
        query = query.filter(Customer.company_name.contains(search) | 
                           Customer.contact_name.contains(search) |
                           Customer.email.contains(search))
    
    customers = query.paginate(page=page, per_page=10, error_out=False)
    return render_template('customers.html', customers=customers, search=search)

@app.route('/customers/new', methods=['GET', 'POST'])
@login_required
def new_customer():
    if request.method == 'POST':
        customer = Customer(
            company_name=request.form['company_name'],
            abn=request.form['abn'],
            contact_name=request.form['contact_name'],
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form['address'],
            city=request.form['city'],
            state=request.form['state'],
            postal_code=request.form['postal_code'],
            credit_limit=Decimal(request.form['credit_limit']) if request.form['credit_limit'] else Decimal('0'),
            payment_terms=request.form['payment_terms']
        )
        
        db.session.add(customer)
        db.session.commit()
        flash('Customer created successfully!')
        return redirect(url_for('customers'))
    
    return render_template('customer_form.html')

@app.route('/quote')
@login_required
def quote():
    customers = Customer.query.all()
    equipment = Equipment.query.filter_by(availability_status='available').all()
    return render_template('quote.html', customers=customers, equipment=equipment)

@app.route('/api/equipment')
@login_required
def api_equipment():
    category = request.args.get('category')
    query = Equipment.query.filter_by(availability_status='available')
    
    if category:
        query = query.filter_by(category=category)
    
    equipment = query.all()
    return jsonify([{
        'id': eq.id,
        'name': eq.name,
        'category': eq.category,
        'daily_rate': float(eq.daily_rate),
        'weekly_rate': float(eq.weekly_rate),
        'monthly_rate': float(eq.monthly_rate),
        'image_url': eq.image_url,
        'description': eq.description,
        'specifications': eq.get_specifications()
    } for eq in equipment])

@app.route('/api/quote', methods=['POST'])
@login_required
def api_create_quote():
    data = request.get_json()
    
    try:
        # Create quote
        quote = Quote(
            quote_number=f"Q{datetime.now().strftime('%Y%m%d%H%M%S')}",
            customer_id=data['customer_id'],
            job_name=data['job_name'],
            job_address=data['job_address'],
            hire_start_date=datetime.strptime(data['hire_start_date'], '%Y-%m-%d').date(),
            hire_end_date=datetime.strptime(data['hire_end_date'], '%Y-%m-%d').date(),
            subtotal=Decimal(str(data['subtotal'])),
            discount=Decimal(str(data.get('discount', 0))),
            gst=Decimal(str(data['gst'])),
            total=Decimal(str(data['total'])),
            created_by=current_user.id
        )
        
        db.session.add(quote)
        db.session.flush()
        
        # Create quote items
        for item_data in data['items']:
            item = QuoteItem(
                quote_id=quote.id,
                equipment_id=item_data['equipment_id'],
                quantity=item_data['quantity'],
                duration=item_data['duration'],
                unit_rate=Decimal(str(item_data['unit_rate'])),
                total_amount=Decimal(str(item_data['total_amount']))
            )
            db.session.add(item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'quote_id': quote.id,
            'quote_number': quote.quote_number
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/booking')
@login_required
def booking():
    quote_id = request.args.get('quote_id')
    quote = None
    if quote_id:
        quote = Quote.query.get_or_404(quote_id)
    
    customers = Customer.query.all()
    return render_template('booking.html', quote=quote, customers=customers)

@app.route('/api/booking', methods=['POST'])
@login_required
def api_create_booking():
    data = request.get_json()
    
    try:
        # Create booking
        booking = Booking(
            booking_number=f"B{datetime.now().strftime('%Y%m%d%H%M%S')}",
            quote_id=data.get('quote_id'),
            customer_id=data['customer_id'],
            job_name=data['job_name'],
            delivery_address=data['delivery_address'],
            delivery_date=datetime.strptime(data['delivery_date'], '%Y-%m-%dT%H:%M'),
            pickup_date=datetime.strptime(data['pickup_date'], '%Y-%m-%dT%H:%M'),
            total_amount=Decimal(str(data['total_amount'])),
            deposit_amount=Decimal(str(data.get('deposit_amount', 0))),
            created_by=current_user.id
        )
        
        db.session.add(booking)
        db.session.flush()
        
        # Create booking items and update equipment availability
        for item_data in data['items']:
            item = BookingItem(
                booking_id=booking.id,
                equipment_id=item_data['equipment_id'],
                quantity=item_data['quantity'],
                unit_rate=Decimal(str(item_data['unit_rate'])),
                total_amount=Decimal(str(item_data['total_amount']))
            )
            db.session.add(item)
            
            # Update equipment availability
            equipment = Equipment.query.get(item_data['equipment_id'])
            if equipment:
                equipment.availability_status = 'on_hire'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'booking_id': booking.id,
            'booking_number': booking.booking_number
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/contracts')
@login_required
def contracts():
    contracts = Contract.query.order_by(Contract.created_at.desc()).all()
    return render_template('contracts.html', contracts=contracts)

@app.route('/reports')
@login_required
def reports():
    # Get date range from query parameters
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    # Convert to datetime objects
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Quote statistics
    quotes_in_period = Quote.query.filter(Quote.created_at.between(start_dt, end_dt)).count()
    bookings_in_period = Booking.query.filter(Booking.created_at.between(start_dt, end_dt)).count()
    
    # Revenue statistics
    revenue_query = db.session.query(db.func.sum(Quote.total)).filter(
        Quote.created_at.between(start_dt, end_dt),
        Quote.status == 'approved'
    ).scalar() or 0
    
    # Equipment utilization - Convert Row objects to serializable data
    try:
        equipment_utilization_raw = db.session.query(
            Equipment.category,
            db.func.count(BookingItem.id).label('bookings')
        ).join(BookingItem, isouter=True).join(Booking, isouter=True).filter(
            db.or_(Booking.created_at.between(start_dt, end_dt), Booking.created_at.is_(None))
        ).group_by(Equipment.category).all()
    except:
        # Fallback if there are no bookings yet
        equipment_utilization_raw = db.session.query(
            Equipment.category,
            db.func.count(Equipment.id).label('bookings')
        ).group_by(Equipment.category).all()
    
    # Convert to JSON-serializable format
    equipment_utilization = []
    for row in equipment_utilization_raw:
        equipment_utilization.append({
            'category': row.category,
            'bookings': row.bookings or 0
        })
    
    return render_template('reports.html',
                         start_date=start_date,
                         end_date=end_date,
                         quotes_in_period=quotes_in_period,
                         bookings_in_period=bookings_in_period,
                         revenue_in_period=float(revenue_query) if revenue_query else 0,
                         equipment_utilization=equipment_utilization)
# Add missing route for customer form
@app.route('/customer_form')
@login_required
def customer_form():
    return render_template('customer_form.html')
# Add these routes to your app.py file

@app.route('/api/dashboard/metrics')
@login_required
def api_dashboard_metrics():
    return jsonify({
        'total_customers': Customer.query.count(),
        'total_equipment': Equipment.query.count(),
        'available_equipment': Equipment.query.filter_by(availability_status='available').count(),
        'active_bookings': Booking.query.filter_by(status='confirmed').count()
    })

@app.route('/api/dashboard/recent-activity')
@login_required
def api_dashboard_recent_activity():
    recent_quotes = Quote.query.order_by(Quote.created_at.desc()).limit(5).all()
    
    quotes_data = []
    for quote in recent_quotes:
        quotes_data.append({
            'id': quote.id,
            'quote_number': quote.quote_number,
            'customer_name': quote.customer.company_name,
            'total': float(quote.total),
            'status': quote.status
        })
    
    return jsonify({
        'quotes': quotes_data,
        'deliveries': []  # Add delivery data if needed
    })

@app.route('/api/dashboard/alerts')
@login_required
def api_dashboard_alerts():
    alerts = []
    
    # Check for equipment maintenance alerts
    maintenance_equipment = Equipment.query.filter_by(availability_status='maintenance').count()
    if maintenance_equipment > 0:
        alerts.append({
            'title': 'Equipment Maintenance',
            'message': f'{maintenance_equipment} equipment items require maintenance',
            'type': 'warning'
        })
    
    # Check for low availability
    total_equipment = Equipment.query.count()
    available_equipment = Equipment.query.filter_by(availability_status='available').count()
    
    if total_equipment > 0 and (available_equipment / total_equipment) < 0.2:
        alerts.append({
            'title': 'Low Equipment Availability',
            'message': 'Less than 20% of equipment is currently available',
            'type': 'warning'
        })
    
    return jsonify({'alerts': alerts})

# Fix the user loader deprecation warning
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # Use session.get instead of query.get
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_dummy_data()
    app.run(debug=True)