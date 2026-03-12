"""
vaidya-care — Database Models
All models use SQLite via SQLAlchemy ORM.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import uuid

db = SQLAlchemy()


# ─── Auth ───────────────────────────────────────────────────────────────────

class Practitioner(UserMixin, db.Model):
    """The Ayurvedic doctor / app admin. Single user initially."""
    __tablename__ = 'practitioners'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    patients   = db.relationship('Patient', back_populates='practitioner', lazy='dynamic')
    followups  = db.relationship('FollowUp', back_populates='practitioner', lazy='dynamic')


# ─── Patients ────────────────────────────────────────────────────────────────

class Patient(db.Model):
    """Core patient/client record."""
    __tablename__ = 'patients'
    id               = db.Column(db.Integer, primary_key=True)
    practitioner_id  = db.Column(db.Integer, db.ForeignKey('practitioners.id'), nullable=False)

    # Demographics
    first_name       = db.Column(db.String(80), nullable=False)
    last_name        = db.Column(db.String(80), nullable=False)
    dob              = db.Column(db.Date)
    sex              = db.Column(db.String(10))          # Male / Female / Other
    location         = db.Column(db.String(200))
    occupation       = db.Column(db.String(200))
    phone            = db.Column(db.String(30))
    email            = db.Column(db.String(200))

    # Physical
    weight_lbs       = db.Column(db.Float)
    weight_note      = db.Column(db.String(200))         # e.g. "recent ~20 lbs loss"

    # Lifestyle
    exercise_notes   = db.Column(db.Text)
    diet_pattern     = db.Column(db.Text)
    alcohol_notes    = db.Column(db.String(200))
    caffeine_notes   = db.Column(db.String(200))

    # Status
    active           = db.Column(db.Boolean, default=True)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at       = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    practitioner     = db.relationship('Practitioner', back_populates='patients')
    health_profile   = db.relationship('HealthProfile', back_populates='patient', uselist=False, cascade='all, delete-orphan')
    plans            = db.relationship('ConsultationPlan', back_populates='patient', lazy='dynamic', cascade='all, delete-orphan')
    checkins         = db.relationship('DailyCheckIn', back_populates='patient', lazy='dynamic', cascade='all, delete-orphan')
    checkin_token    = db.relationship('CheckInToken', back_populates='patient', uselist=False, cascade='all, delete-orphan')
    followups        = db.relationship('FollowUp', back_populates='patient', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def active_plan(self):
        return self.plans.filter_by(active=True).first()


class HealthProfile(db.Model):
    """Lab values, chief complaints, medical history, Ayurvedic notes."""
    __tablename__ = 'health_profiles'
    id             = db.Column(db.Integer, primary_key=True)
    patient_id     = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    # Lab values — Lipid
    cholesterol_total = db.Column(db.Float)
    hdl               = db.Column(db.Float)
    ldl               = db.Column(db.Float)
    triglycerides     = db.Column(db.Float)

    # Lab — Blood counts
    hemoglobin        = db.Column(db.Float)
    hematocrit        = db.Column(db.Float)
    eosinophils_pct   = db.Column(db.Float)

    # Lab — Metabolic
    glucose           = db.Column(db.Float)
    hba1c             = db.Column(db.Float)
    creatinine        = db.Column(db.Float)
    egfr              = db.Column(db.Float)

    # Lab — Hormonal / Other
    testosterone      = db.Column(db.Float)
    tsh               = db.Column(db.Float)
    psa               = db.Column(db.Float)

    lab_date          = db.Column(db.Date)
    lab_notes         = db.Column(db.Text)

    # Chief complaints (free text)
    chief_complaints  = db.Column(db.Text)

    # Medical history
    medical_history   = db.Column(db.Text)

    # Ayurvedic observations
    dosha_primary     = db.Column(db.String(20))         # Vata / Pitta / Kapha
    dosha_secondary   = db.Column(db.String(20))
    dosha_imbalances  = db.Column(db.Text)               # free text notes
    agni_assessment   = db.Column(db.Text)               # digestive fire notes
    ama_assessment    = db.Column(db.Text)               # toxin accumulation notes
    prakriti_notes    = db.Column(db.Text)               # constitution notes
    vikriti_notes     = db.Column(db.Text)               # current imbalance notes

    updated_at        = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    patient           = db.relationship('Patient', back_populates='health_profile')


# ─── Plans ───────────────────────────────────────────────────────────────────

class ConsultationPlan(db.Model):
    """A personalized protocol assigned to a patient."""
    __tablename__ = 'consultation_plans'
    id              = db.Column(db.Integer, primary_key=True)
    patient_id      = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    title           = db.Column(db.String(200), default='Initial Protocol')
    active          = db.Column(db.Boolean, default=True)
    duration_weeks  = db.Column(db.Integer, default=3)
    start_date      = db.Column(db.Date)
    end_date        = db.Column(db.Date)

    # Structured notes
    foods_to_avoid  = db.Column(db.Text)
    foods_to_include = db.Column(db.Text)
    lifestyle_notes = db.Column(db.Text)
    breathing_notes = db.Column(db.Text)
    nasal_care_notes = db.Column(db.Text)
    followup_notes  = db.Column(db.Text)

    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    patient          = db.relationship('Patient', back_populates='plans')
    plan_supplements = db.relationship('PlanSupplement', back_populates='plan', cascade='all, delete-orphan')
    plan_recipes     = db.relationship('PlanRecipe', back_populates='plan', cascade='all, delete-orphan')


class Supplement(db.Model):
    """Master supplement/herb library."""
    __tablename__ = 'supplements'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False)
    brand       = db.Column(db.String(200))
    category    = db.Column(db.String(80))       # Herbal / Tea / Tablet
    purpose     = db.Column(db.Text)
    source_url  = db.Column(db.String(500))
    notes       = db.Column(db.Text)

    plan_supplements = db.relationship('PlanSupplement', back_populates='supplement')


class PlanSupplement(db.Model):
    """Links a supplement to a plan with specific dosing."""
    __tablename__ = 'plan_supplements'
    id             = db.Column(db.Integer, primary_key=True)
    plan_id        = db.Column(db.Integer, db.ForeignKey('consultation_plans.id'), nullable=False)
    supplement_id  = db.Column(db.Integer, db.ForeignKey('supplements.id'), nullable=False)
    dose           = db.Column(db.String(100))    # e.g. "½ tsp"
    timing         = db.Column(db.String(100))    # Before meals / After meals
    frequency      = db.Column(db.String(100))    # Twice daily
    special_notes  = db.Column(db.Text)

    plan        = db.relationship('ConsultationPlan', back_populates='plan_supplements')
    supplement  = db.relationship('Supplement', back_populates='plan_supplements')


class Recipe(db.Model):
    """Master recipe library."""
    __tablename__ = 'recipes'
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(200), nullable=False)
    meal_type    = db.Column(db.String(50))       # Breakfast / Lunch / Dinner / Tea / Snack
    ingredients  = db.Column(db.Text)
    instructions = db.Column(db.Text)
    notes        = db.Column(db.Text)
    is_tea       = db.Column(db.Boolean, default=False)

    plan_recipes = db.relationship('PlanRecipe', back_populates='recipe')


class PlanRecipe(db.Model):
    """Links a recipe to a plan with meal slot context."""
    __tablename__ = 'plan_recipes'
    id         = db.Column(db.Integer, primary_key=True)
    plan_id    = db.Column(db.Integer, db.ForeignKey('consultation_plans.id'), nullable=False)
    recipe_id  = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    meal_slot  = db.Column(db.String(50))         # Breakfast / Lunch / Dinner / Tea

    plan    = db.relationship('ConsultationPlan', back_populates='plan_recipes')
    recipe  = db.relationship('Recipe', back_populates='plan_recipes')


# ─── Check-In ────────────────────────────────────────────────────────────────

class CheckInToken(db.Model):
    """Unique shareable token per patient for public check-in form."""
    __tablename__ = 'checkin_tokens'
    id         = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    token      = db.Column(db.String(64), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    active     = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', back_populates='checkin_token')

    @property
    def url_path(self):
        return f"/checkin/{self.token}"


class DailyCheckIn(db.Model):
    """Daily habit log submitted by patient via shareable link."""
    __tablename__ = 'daily_checkins'
    id         = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    date       = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Morning routine
    warm_water        = db.Column(db.Boolean, default=False)
    breathing_exercise = db.Column(db.Boolean, default=False)
    nasal_oil         = db.Column(db.Boolean, default=False)

    # Meals
    warm_breakfast    = db.Column(db.Boolean, default=False)
    avoided_cold_food = db.Column(db.Boolean, default=False)
    avoided_yogurt    = db.Column(db.Boolean, default=False)
    herbal_tea_am     = db.Column(db.Boolean, default=False)
    warm_lunch        = db.Column(db.Boolean, default=False)
    included_barley   = db.Column(db.Boolean, default=False)
    no_cold_drinks    = db.Column(db.Boolean, default=False)
    warm_dinner       = db.Column(db.Boolean, default=False)
    dinner_before_8pm = db.Column(db.Boolean, default=False)

    # Supplements
    supplements_am    = db.Column(db.Boolean, default=False)
    supplements_pm    = db.Column(db.Boolean, default=False)

    # Lifestyle
    cardio_today      = db.Column(db.Boolean, default=False)
    consistent_sleep  = db.Column(db.Boolean, default=False)

    # Symptom ratings 1–5
    digestion_score   = db.Column(db.Integer)
    urinary_score     = db.Column(db.Integer)
    sinus_score       = db.Column(db.Integer)
    energy_score      = db.Column(db.Integer)

    # Free text
    notes             = db.Column(db.Text)

    patient = db.relationship('Patient', back_populates='checkins')

    @property
    def habit_completion_pct(self):
        """Percentage of boolean habit fields checked."""
        fields = [
            self.warm_water, self.breathing_exercise, self.nasal_oil,
            self.warm_breakfast, self.avoided_cold_food, self.avoided_yogurt,
            self.herbal_tea_am, self.warm_lunch, self.included_barley,
            self.no_cold_drinks, self.warm_dinner, self.dinner_before_8pm,
            self.supplements_am, self.supplements_pm,
        ]
        done = sum(1 for f in fields if f)
        return round(done / len(fields) * 100)

    @property
    def avg_symptom_score(self):
        scores = [s for s in [self.digestion_score, self.urinary_score, self.sinus_score, self.energy_score] if s]
        return round(sum(scores) / len(scores), 1) if scores else None


# ─── Follow-Ups ──────────────────────────────────────────────────────────────

class FollowUp(db.Model):
    """Scheduled follow-up reminder for a patient."""
    __tablename__ = 'followups'
    id              = db.Column(db.Integer, primary_key=True)
    patient_id      = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    practitioner_id = db.Column(db.Integer, db.ForeignKey('practitioners.id'), nullable=False)
    scheduled_date  = db.Column(db.Date, nullable=False)
    reason          = db.Column(db.String(300))
    notes           = db.Column(db.Text)
    completed       = db.Column(db.Boolean, default=False)
    completed_at    = db.Column(db.DateTime)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    patient      = db.relationship('Patient', back_populates='followups')
    practitioner = db.relationship('Practitioner', back_populates='followups')


# ─── Seed Data ───────────────────────────────────────────────────────────────

SEED_SUPPLEMENTS = [
    {'name': 'Avipattikar Churna', 'brand': 'Dhootpapeshwar', 'category': 'Herbal',
     'purpose': 'Supports digestion; take with water before meals', 'source_url': 'https://eayur.com'},
    {'name': 'Haridrakhandam', 'brand': 'Kottakkal', 'category': 'Herbal',
     'purpose': 'Anti-inflammatory; supports respiratory and skin health', 'source_url': 'https://eayur.com'},
    {'name': 'Vyoshadi Vatkam', 'brand': 'Kottakkal', 'category': 'Herbal',
     'purpose': 'Supports respiratory tract and digestion', 'source_url': 'https://eayur.com'},
    {'name': 'Neeri Tablets', 'brand': 'Aimil', 'category': 'Tablet',
     'purpose': 'Urinary tract support', 'source_url': 'https://eayur.com'},
    {'name': 'Tulsi Tea', 'brand': None, 'category': 'Tea',
     'purpose': 'Supports respiratory health and immunity'},
    {'name': 'Licorice Tea', 'brand': None, 'category': 'Tea',
     'purpose': 'Soothes respiratory and digestive irritation'},
    {'name': 'Coriander-Barley Tea', 'brand': None, 'category': 'Tea',
     'purpose': 'Supports urinary tract health; boil barley + coriander seeds'},
]

SEED_RECIPES = [
    {'name': 'Warm Oat Bowl', 'meal_type': 'Breakfast',
     'ingredients': '½ cup oats, 1 cup water or milk, chopped figs, 1 date, 6–8 almonds, 1 Brazil nut',
     'instructions': 'Cook oats on low heat 5–7 min. Add figs, date, almonds, Brazil nuts. Serve warm.'},
    {'name': 'Savory Vegetable Oats', 'meal_type': 'Breakfast',
     'ingredients': '½ cup oats, 1 cup water, carrots, zucchini or spinach, pinch turmeric, pinch cumin, salt',
     'instructions': 'Heat oil/ghee. Add cumin and turmeric. Sauté vegetables. Add oats and water. Cook 5–6 min.'},
    {'name': 'Eggs with Vegetables', 'meal_type': 'Breakfast',
     'ingredients': '2 eggs, spinach or zucchini, pinch turmeric, pinch cumin',
     'instructions': 'Sauté vegetables. Add eggs and cook gently. Serve with small portion of barley or oats.'},
    {'name': 'Barley Vegetable Bowl', 'meal_type': 'Lunch',
     'ingredients': '½ cup barley, carrots, green beans, zucchini, turmeric, cumin, ginger',
     'instructions': 'Cook barley until soft. Sauté cumin and ginger. Add vegetables and cook. Mix with barley. Add salt and turmeric.'},
    {'name': 'Light Chicken Vegetable Soup', 'meal_type': 'Lunch',
     'ingredients': 'Chicken pieces, carrots, zucchini, ginger, turmeric, cumin, salt',
     'instructions': 'Add chicken and vegetables to pot. Add water, ginger, cumin, turmeric. Simmer 20–25 min.'},
    {'name': 'Simple Fish with Vegetables', 'meal_type': 'Lunch',
     'ingredients': 'Fish fillet, zucchini or asparagus, turmeric, coriander powder, ginger, olive oil or ghee',
     'instructions': 'Marinate fish with turmeric, coriander, ginger. Cook in pan. Sauté vegetables separately. Serve with barley.'},
    {'name': 'Coriander-Barley Tea', 'meal_type': 'Tea', 'is_tea': True,
     'ingredients': 'Barley, coriander seeds (daniya)',
     'instructions': 'Coarsely grind barley and coriander seeds. Boil 1 tsp in water for several minutes. Drink warm 2–3x daily.'},
    {'name': 'Tulsi Tea', 'meal_type': 'Tea', 'is_tea': True,
     'ingredients': 'Tulsi tea bags or fresh tulsi leaves',
     'instructions': 'Steep in hot water 5 min. Drink warm.'},
    {'name': 'Licorice Tea', 'meal_type': 'Tea', 'is_tea': True,
     'ingredients': 'Licorice root / mulethi',
     'instructions': 'Boil licorice root in water 5–7 min. Strain and drink warm.'},
]


def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _seed_if_empty()


def _seed_if_empty():
    if Supplement.query.count() == 0:
        for s in SEED_SUPPLEMENTS:
            db.session.add(Supplement(**s))
    if Recipe.query.count() == 0:
        for r in SEED_RECIPES:
            db.session.add(Recipe(**{k: v for k, v in r.items()}))
    db.session.commit()
