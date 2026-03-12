"""
vaidya-care — Ayurvedic Practice Management
Flask application entry point.
"""
import os
import logging
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, Response, stream_with_context
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, init_db, Practitioner, Patient, HealthProfile, ConsultationPlan, \
    Supplement, PlanSupplement, Recipe, PlanRecipe, CheckInToken, DailyCheckIn, FollowUp

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
log = logging.getLogger(__name__)

# ─── App Factory ─────────────────────────────────────────────────────────────

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), '..', 'vaidya.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail config
app.config['MAIL_SERVER']   = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT']     = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS']  = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

CORS(app)
mail = Mail(app)
init_db(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

app.jinja_env.globals['now'] = datetime.now
app.jinja_env.globals['today'] = date.today

PRACTITIONER_EMAIL = os.environ.get('PRACTITIONER_EMAIL', '')
ANTHROPIC_API_KEY  = os.environ.get('ANTHROPIC_API_KEY', '')


@login_manager.user_loader
def load_user(user_id):
    return Practitioner.query.get(int(user_id))


# ─── Auth ─────────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = Practitioner.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ─── Dashboard ───────────────────────────────────────────────────────────────

@app.route('/')
@login_required
def dashboard():
    today_date = date.today()

    # Follow-ups due today or overdue
    followups_due = (FollowUp.query
        .join(Patient)
        .filter(Patient.practitioner_id == current_user.id,
                FollowUp.completed == False,
                FollowUp.scheduled_date <= today_date)
        .order_by(FollowUp.scheduled_date)
        .all())

    # Recent check-ins (last 7 days)
    from datetime import timedelta
    week_ago = today_date - timedelta(days=7)
    recent_checkins = (DailyCheckIn.query
        .join(Patient)
        .filter(Patient.practitioner_id == current_user.id,
                DailyCheckIn.date >= week_ago)
        .order_by(DailyCheckIn.submitted_at.desc())
        .limit(10)
        .all())

    # Patient count
    total_patients = Patient.query.filter_by(practitioner_id=current_user.id, active=True).count()

    # Patients with active plans
    active_plans = (ConsultationPlan.query
        .join(Patient)
        .filter(Patient.practitioner_id == current_user.id,
                ConsultationPlan.active == True)
        .count())

    # Patients who haven't checked in today
    checked_in_today_ids = {c.patient_id for c in
        DailyCheckIn.query.filter_by(date=today_date).all()}
    patients_due_checkin = (Patient.query
        .filter_by(practitioner_id=current_user.id, active=True)
        .filter(Patient.id.notin_(checked_in_today_ids))
        .count())

    return render_template('dashboard.html',
        active_page='dashboard',
        followups_due=followups_due,
        recent_checkins=recent_checkins,
        total_patients=total_patients,
        active_plans=active_plans,
        patients_due_checkin=patients_due_checkin,
        today=today_date,
    )


# ─── Patients ────────────────────────────────────────────────────────────────

@app.route('/patients')
@login_required
def patients():
    from datetime import timedelta
    patients_list = (Patient.query
        .filter_by(practitioner_id=current_user.id, active=True)
        .order_by(Patient.last_name)
        .all())

    # Annotate each patient with last check-in and compliance
    result = []
    for p in patients_list:
        last_ci = p.checkins.order_by(DailyCheckIn.date.desc()).first()
        next_fu = (p.followups
            .filter(FollowUp.completed == False, FollowUp.scheduled_date >= date.today())
            .order_by(FollowUp.scheduled_date)
            .first())
        result.append({
            'patient': p,
            'last_checkin': last_ci,
            'next_followup': next_fu,
            'has_active_plan': p.active_plan is not None,
        })

    return render_template('patients.html',
        active_page='patients',
        patients=result,
    )


@app.route('/patients/new', methods=['GET', 'POST'])
@login_required
def patient_new():
    if request.method == 'POST':
        p = Patient(
            practitioner_id=current_user.id,
            first_name=request.form.get('first_name', '').strip(),
            last_name=request.form.get('last_name', '').strip(),
            email=request.form.get('email', '').strip(),
            phone=request.form.get('phone', '').strip(),
            location=request.form.get('location', '').strip(),
            occupation=request.form.get('occupation', '').strip(),
            sex=request.form.get('sex'),
            exercise_notes=request.form.get('exercise_notes', '').strip(),
            diet_pattern=request.form.get('diet_pattern', '').strip(),
            alcohol_notes=request.form.get('alcohol_notes', '').strip(),
            caffeine_notes=request.form.get('caffeine_notes', '').strip(),
            sleep_notes=request.form.get('sleep_notes', '').strip() or None,
            stress_level=request.form.get('stress_level') or None,
        )
        dob_str = request.form.get('dob')
        if dob_str:
            try:
                p.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        db.session.add(p)
        db.session.flush()

        # Create health profile with form data
        def _float(key):
            v = request.form.get(key, '').strip()
            try: return float(v) if v else None
            except ValueError: return None

        hp = HealthProfile(
            patient_id=p.id,
            chief_complaints=request.form.get('chief_complaints', '').strip() or None,
            medical_history=request.form.get('medical_history', '').strip() or None,
            current_medications=request.form.get('current_medications', '').strip() or None,
            allergies=request.form.get('allergies', '').strip() or None,
            dosha_primary=request.form.get('dosha_primary') or None,
            dosha_secondary=request.form.get('dosha_secondary') or None,
            dosha_imbalances=request.form.get('dosha_imbalances', '').strip() or None,
            agni_assessment=request.form.get('agni_assessment', '').strip() or None,
            ama_assessment=request.form.get('ama_assessment', '').strip() or None,
            cholesterol_total=_float('cholesterol_total'),
            hdl=_float('hdl'),
            ldl=_float('ldl'),
            hba1c=_float('hba1c'),
            creatinine=_float('creatinine'),
            egfr=_float('egfr'),
            testosterone=_float('testosterone'),
            tsh=_float('tsh'),
        )
        db.session.add(hp)

        # Generate check-in token
        token = CheckInToken(patient_id=p.id)
        db.session.add(token)

        db.session.commit()
        flash(f'{p.full_name} added successfully.', 'success')
        return redirect(url_for('patient_detail', patient_id=p.id))

    return render_template('patient_new.html', active_page='patients')


@app.route('/patients/<int:patient_id>')
@login_required
def patient_detail(patient_id):
    patient = Patient.query.filter_by(id=patient_id, practitioner_id=current_user.id).first_or_404()
    recent_checkins = patient.checkins.order_by(DailyCheckIn.date.desc()).limit(14).all()
    followups = (patient.followups
        .order_by(FollowUp.completed, FollowUp.scheduled_date)
        .all())
    token = patient.checkin_token

    # Chart data: last 14 days in chronological order
    chart_checkins = list(reversed(recent_checkins))
    chart_data = [{
        'date': ci.date.strftime('%b %d'),
        'digestion': ci.digestion_score,
        'energy':    ci.energy_score,
        'urinary':   ci.urinary_score,
        'sinus':     ci.sinus_score,
        'habits':    ci.habit_completion_pct,
    } for ci in chart_checkins]

    return render_template('patient_detail.html',
        active_page='patients',
        patient=patient,
        profile=patient.health_profile,
        active_plan=patient.active_plan,
        recent_checkins=recent_checkins,
        followups=followups,
        checkin_token=token,
        chart_data=chart_data,
    )


# ─── Patient Edit APIs ───────────────────────────────────────────────────────

@app.route('/api/patients/<int:patient_id>/edit', methods=['POST'])
@login_required
def patient_edit(patient_id):
    p = Patient.query.filter_by(id=patient_id, practitioner_id=current_user.id).first_or_404()
    data = request.json
    for field in ['first_name','last_name','email','phone','location','occupation','sex',
                  'exercise_notes','diet_pattern','alcohol_notes','caffeine_notes',
                  'sleep_notes','stress_level']:
        if field in data:
            setattr(p, field, data[field] or None)
    if 'dob' in data and data['dob']:
        try: p.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
        except ValueError: pass
    db.session.commit()
    return jsonify({'status': 'updated', 'full_name': p.full_name})


@app.route('/api/patients/<int:patient_id>/profile', methods=['POST'])
@login_required
def patient_profile_edit(patient_id):
    patient = Patient.query.filter_by(id=patient_id, practitioner_id=current_user.id).first_or_404()
    hp = patient.health_profile
    if not hp:
        hp = HealthProfile(patient_id=patient_id)
        db.session.add(hp)
    data = request.json
    for field in ['chief_complaints','medical_history','current_medications','allergies',
                  'dosha_primary','dosha_secondary','dosha_imbalances',
                  'agni_assessment','ama_assessment']:
        if field in data:
            setattr(hp, field, data[field] or None)
    for field in ['cholesterol_total','hdl','ldl','hba1c','creatinine','egfr','testosterone','tsh']:
        if field in data:
            try: setattr(hp, field, float(data[field]) if data[field] else None)
            except (ValueError, TypeError): pass
    db.session.commit()
    return jsonify({'status': 'updated'})


# ─── Follow-Ups ──────────────────────────────────────────────────────────────

@app.route('/followups')
@login_required
def followups():
    from datetime import timedelta
    upcoming = (FollowUp.query
        .join(Patient)
        .filter(Patient.practitioner_id == current_user.id,
                FollowUp.completed == False)
        .order_by(FollowUp.scheduled_date)
        .all())
    completed = (FollowUp.query
        .join(Patient)
        .filter(Patient.practitioner_id == current_user.id,
                FollowUp.completed == True)
        .order_by(FollowUp.completed_at.desc())
        .limit(20)
        .all())
    patients = Patient.query.filter_by(practitioner_id=current_user.id, active=True).order_by(Patient.first_name).all()
    overdue = [fu for fu in upcoming if fu.scheduled_date < date.today()]
    return render_template('followups.html',
        active_page='followups',
        upcoming=upcoming,
        completed=completed,
        patients=patients,
        overdue_count=len(overdue),
        today=date.today(),
    )


@app.route('/api/followups', methods=['POST'])
@login_required
def create_followup():
    data = request.json
    patient = Patient.query.filter_by(id=data.get('patient_id'), practitioner_id=current_user.id).first_or_404()
    fu = FollowUp(
        patient_id=patient.id,
        practitioner_id=current_user.id,
        scheduled_date=datetime.strptime(data['scheduled_date'], '%Y-%m-%d').date(),
        reason=data.get('reason', ''),
        notes=data.get('notes', ''),
    )
    db.session.add(fu)
    db.session.commit()
    return jsonify({'id': fu.id, 'status': 'created'})


@app.route('/api/followups/<int:fu_id>/complete', methods=['POST'])
@login_required
def complete_followup(fu_id):
    fu = FollowUp.query.join(Patient).filter(
        FollowUp.id == fu_id,
        Patient.practitioner_id == current_user.id
    ).first_or_404()
    fu.completed = True
    fu.completed_at = datetime.utcnow()
    fu.notes = request.json.get('notes', fu.notes)
    db.session.commit()
    return jsonify({'status': 'completed'})


# ─── Public Check-In ─────────────────────────────────────────────────────────

@app.route('/checkin/<token>', methods=['GET', 'POST'])
def checkin(token):
    tok = CheckInToken.query.filter_by(token=token, active=True).first_or_404()
    patient = tok.patient

    if request.method == 'POST':
        ci = DailyCheckIn(
            patient_id=patient.id,
            date=date.today(),
            warm_water=bool(request.form.get('warm_water')),
            breathing_exercise=bool(request.form.get('breathing_exercise')),
            nasal_oil=bool(request.form.get('nasal_oil')),
            warm_breakfast=bool(request.form.get('warm_breakfast')),
            avoided_cold_food=bool(request.form.get('avoided_cold_food')),
            avoided_yogurt=bool(request.form.get('avoided_yogurt')),
            herbal_tea_am=bool(request.form.get('herbal_tea_am')),
            warm_lunch=bool(request.form.get('warm_lunch')),
            included_barley=bool(request.form.get('included_barley')),
            no_cold_drinks=bool(request.form.get('no_cold_drinks')),
            warm_dinner=bool(request.form.get('warm_dinner')),
            dinner_before_8pm=bool(request.form.get('dinner_before_8pm')),
            supplements_am=bool(request.form.get('supplements_am')),
            supplements_pm=bool(request.form.get('supplements_pm')),
            cardio_today=bool(request.form.get('cardio_today')),
            consistent_sleep=bool(request.form.get('consistent_sleep')),
            digestion_score=int(request.form.get('digestion_score') or 0) or None,
            urinary_score=int(request.form.get('urinary_score') or 0) or None,
            sinus_score=int(request.form.get('sinus_score') or 0) or None,
            energy_score=int(request.form.get('energy_score') or 0) or None,
            notes=request.form.get('notes', '').strip(),
        )
        db.session.add(ci)
        db.session.commit()

        # Email doctor
        _notify_checkin(patient, ci)

        return render_template('checkin_thankyou.html', patient=patient, checkin=ci)

    # Check if already submitted today
    already_submitted = DailyCheckIn.query.filter_by(
        patient_id=patient.id, date=date.today()
    ).first()

    return render_template('checkin.html',
        patient=patient,
        already_submitted=already_submitted,
        active_plan=patient.active_plan,
    )


def _notify_checkin(patient, checkin):
    """Send email to practitioner when a patient submits a check-in."""
    if not PRACTITIONER_EMAIL or not app.config.get('MAIL_USERNAME'):
        return
    try:
        scores = []
        for label, score in [('Digestion', checkin.digestion_score),
                              ('Urinary', checkin.urinary_score),
                              ('Sinus', checkin.sinus_score),
                              ('Energy', checkin.energy_score)]:
            if score:
                scores.append(f'{label}: {score}/5')

        body = f"""
New check-in from {patient.full_name}
Date: {checkin.date.strftime('%B %d, %Y')}
Habit completion: {checkin.habit_completion_pct}%

Symptom scores:
{chr(10).join(scores) if scores else 'None recorded'}

Notes: {checkin.notes or 'None'}
        """.strip()

        msg = Message(
            subject=f'Check-in: {patient.full_name} — {checkin.date.strftime("%b %d")}',
            recipients=[PRACTITIONER_EMAIL],
            body=body,
        )
        mail.send(msg)
    except Exception as e:
        log.warning(f'Failed to send check-in email: {e}')


# ─── Recipes & Supplements ───────────────────────────────────────────────────

@app.route('/recipes')
@login_required
def recipes():
    all_recipes = Recipe.query.order_by(Recipe.meal_type, Recipe.name).all()
    return render_template('recipes.html', active_page='recipes', recipes=all_recipes)


@app.route('/supplements')
@login_required
def supplements_page():
    all_supps = Supplement.query.order_by(Supplement.category, Supplement.name).all()
    return render_template('supplements.html', active_page='supplements', supplements=all_supps)


# ─── AI Chat ─────────────────────────────────────────────────────────────────

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    if not ANTHROPIC_API_KEY:
        return jsonify({'error': 'ANTHROPIC_API_KEY not configured.'}), 503

    import anthropic as ac
    data = request.json or {}
    user_message  = data.get('message', '').strip()
    patient_id    = data.get('patient_id')
    session_id    = data.get('session_id', 'default')

    if not user_message:
        return jsonify({'error': 'No message provided.'}), 400

    # Build context
    context_parts = [
        "You are an AI assistant for an Ayurvedic practice management tool called Vaidya Care.",
        "You help practitioners like Dr. Meenakshi manage patients, review check-in data, analyze symptom trends, and plan follow-ups.",
        "Always be warm, professional, and grounded in Ayurvedic principles.",
    ]

    if patient_id:
        p = Patient.query.filter_by(id=patient_id, practitioner_id=current_user.id).first()
        if p:
            context_parts.append(f"\nCurrent patient context: {p.full_name}, {p.location or 'location unknown'}.")
            if p.health_profile:
                hp = p.health_profile
                if hp.chief_complaints:
                    context_parts.append(f"Chief complaints: {hp.chief_complaints}")
                if hp.dosha_imbalances:
                    context_parts.append(f"Dosha notes: {hp.dosha_imbalances}")
            last_ci = p.checkins.order_by(DailyCheckIn.date.desc()).first()
            if last_ci:
                context_parts.append(
                    f"Last check-in ({last_ci.date}): {last_ci.habit_completion_pct}% habits, "
                    f"avg symptom score {last_ci.avg_symptom_score}/5."
                )

    system_prompt = '\n'.join(context_parts)

    def generate():
        client = ac.Anthropic(api_key=ANTHROPIC_API_KEY)
        with client.messages.stream(
            model='claude-sonnet-4-6',
            max_tokens=1024,
            system=system_prompt,
            messages=[{'role': 'user', 'content': user_message}],
        ) as stream:
            for text in stream.text_stream:
                yield f'data: {{"text": {__import__("json").dumps(text)}}}\n\n'
        yield 'data: {"done": true}\n\n'

    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@app.route('/api/chat/suggestions')
@login_required
def chat_suggestions():
    patient_id = request.args.get('patient_id', type=int)
    suggestions = [
        "Which patients haven't checked in this week?",
        "Summarize today's follow-ups",
        "What symptom trends should I watch for?",
    ]
    if patient_id:
        p = Patient.query.filter_by(id=patient_id, practitioner_id=current_user.id).first()
        if p:
            suggestions = [
                f"Summarize {p.first_name}'s recent check-ins",
                f"What should I focus on in {p.first_name}'s next follow-up?",
                f"Are there any concerning trends for {p.first_name}?",
            ]
    return jsonify({'suggestions': suggestions})


# ─── Setup (first-run) ───────────────────────────────────────────────────────

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """Create the initial practitioner account. Disabled once one exists."""
    if Practitioner.query.count() > 0:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not all([name, email, password]):
            flash('All fields are required.', 'danger')
        else:
            p = Practitioner(
                name=name,
                email=email,
                password_hash=generate_password_hash(password),
            )
            db.session.add(p)
            db.session.commit()
            login_user(p)
            flash(f'Welcome, {name}! Your account is ready.', 'success')
            return redirect(url_for('dashboard'))
    return render_template('auth/setup.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
