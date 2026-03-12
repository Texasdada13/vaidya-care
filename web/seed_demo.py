"""
Vaidya Care — Demo Seed Script
Creates a demo practitioner account + 2 patients with realistic data
based on actual spreadsheets (Shuva / Kajori).

Run once:
    cd vaidya-care
    venv/Scripts/python web/seed_demo.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date, datetime, timedelta
import random
from werkzeug.security import generate_password_hash
from app import app, db
from models import (Practitioner, Patient, HealthProfile, ConsultationPlan,
                    PlanSupplement, PlanRecipe, Supplement, Recipe,
                    CheckInToken, DailyCheckIn, FollowUp)

DEMO_EMAIL    = "demo@vaidyacare.com"
DEMO_PASSWORD = "demo1234"

def run():
    with app.app_context():
        # ── Practitioner ──────────────────────────────────────────────────
        existing = Practitioner.query.filter_by(email=DEMO_EMAIL).first()
        if existing:
            print(f"Demo account already exists ({DEMO_EMAIL}). Skipping.")
            practitioner = existing
        else:
            practitioner = Practitioner(
                name="Dr. Meenakshi Gupta",
                email=DEMO_EMAIL,
                password_hash=generate_password_hash(DEMO_PASSWORD),
            )
            db.session.add(practitioner)
            db.session.flush()
            print(f"Created practitioner: {DEMO_EMAIL} / {DEMO_PASSWORD}")

        # ── Patient 1: Shuva Mukhopadhyay ────────────────────────────────
        shuva = Patient.query.filter_by(email="shuva.m@example.com").first()
        if not shuva:
            shuva = Patient(
                practitioner_id=practitioner.id,
                first_name="Shuva",
                last_name="Mukhopadhyay",
                email="shuva.m@example.com",
                phone="(352) 555-0142",
                dob=date(1984, 4, 23),
                sex="Male",
                location="Ocala, Florida",
                occupation="Business Owner — High work stress, long hours",
                weight_lbs=175,
                weight_note="Recent weight loss ~20 lbs",
                exercise_notes="Weight lifting ~4x/week. Abdominal exercises ~3x/week. Limited cardiovascular currently.",
                diet_pattern="Primarily non-vegetarian (chicken, fish, shrimp daily). Occasional vegetarian. Inconsistent meal timing. Nighttime snacking.",
                alcohol_notes="Approximately twice per month (whiskey or beer)",
                caffeine_notes="Occasionally during periods of heavy work. Nicotine occasional.",
            )
            db.session.add(shuva)
            db.session.flush()

            # Health profile
            hp = HealthProfile(
                patient_id=shuva.id,
                cholesterol_total=184,
                hdl=54,
                ldl=116,
                hemoglobin=16.4,
                hematocrit=50.5,
                eosinophils_pct=10.3,
                glucose=89,
                hba1c=5.5,
                creatinine=1.27,
                egfr=73,
                testosterone=1608,
                tsh=2.94,
                psa=1.05,
                lab_date=date(2026, 2, 15),
                lab_notes="Eosinophils elevated at 10.3% — correlates with allergic/inflammatory conditions. LDL mildly elevated above optimal <100. Testosterone significantly elevated at 1608.",
                chief_complaints=(
                    "Chronic ear infections — partially perforated eardrums\n"
                    "Recurrent urinary issues — frequent urination, incomplete emptying\n"
                    "History of urethral injury from childhood sports\n"
                    "Recurrent bladder infections\n"
                    "Gut inflammation, occasional acid reflux\n"
                    "Abdominal swelling after long work hours\n"
                    "Sinus congestion leading to ear infections\n"
                    "Allergies, asthma, breathing difficulty\n"
                    "Fatigue and body inflammation after prolonged work"
                ),
                medical_history=(
                    "Childhood urethral stricture — surgery and injury during football\n"
                    "Recurrent UTIs\n"
                    "Chronic ear infections due to eardrum perforation\n"
                    "Allergies and respiratory congestion\n"
                    "Vyvanse medication\n"
                    "Recent weight reduction ~20 lbs"
                ),
                dosha_primary="Vata",
                dosha_secondary="Kapha",
                dosha_imbalances=(
                    "Kapha accumulation in respiratory and sinus channels — congestion, ear infections\n"
                    "Vata disturbance in urinary tract and nervous system — linked to past trauma and irregular routines\n"
                    "Agni imbalance — gut inflammation and reflux\n"
                    "Elevated eosinophils indicate allergic/inflammatory tendency"
                ),
                agni_assessment="Vishamagni (irregular digestive fire) — irregular meal timing, nighttime snacking, and gut inflammation",
                prakriti_notes="Vata-Pitta constitution with current Kapha accumulation in upper respiratory channels",
            )
            db.session.add(hp)

            # Check-in token
            token_shuva = CheckInToken(patient_id=shuva.id)
            db.session.add(token_shuva)
            db.session.flush()

            # Active plan
            plan_shuva = ConsultationPlan(
                patient_id=shuva.id,
                title="Initial 3-Week Ayurvedic Protocol",
                active=True,
                duration_weeks=3,
                start_date=date(2026, 3, 1),
                end_date=date(2026, 3, 22),
                foods_to_avoid=(
                    "Yogurt\nFermented foods (kimchi, etc.)\nCold or refrigerated foods\n"
                    "Beetroot juice\nExcess sugar from juices\nCold beverages during meals\n"
                    "Raw salads (large amounts)\nLate-night heavy meals"
                ),
                foods_to_include=(
                    "Warm cooked meals as primary diet\nBarley as main grain\n"
                    "Cooked vegetables with moderate spices\nWell-prepared chicken or fish (marinated)\n"
                    "Warm breakfast daily\nFigs, dates, almonds, Brazil nuts"
                ),
                lifestyle_notes=(
                    "Maintain regular meal timing\nAvoid late-night snacking\n"
                    "Continue strength training\nAdd cardio: brisk walking or light jog 3-4x/week\n"
                    "Consistent sleep schedule\nReduce caffeine and nicotine during heavy work periods"
                ),
                breathing_notes="Morning breathing: Slow nasal breathing. Inhale 4 seconds, exhale 6 seconds. Continue 5–10 minutes.",
                nasal_care_notes="Apply 1–2 drops warm sesame oil or ghee in each nostril each morning if tolerated.",
                followup_notes="Observe digestion, urinary symptoms, sinus/respiratory symptoms, energy levels over 2–3 weeks. Reassess and adjust plan.",
            )
            db.session.add(plan_shuva)
            db.session.flush()

            # Assign supplements to Shuva's plan
            supp_map = {s.name: s for s in Supplement.query.all()}
            for name, dose, timing, freq in [
                ("Avipattikar Churna", "½ tsp", "Before meals", "Twice daily"),
                ("Haridrakhandam",     "¼ tsp", "After meals",  "Twice daily"),
                ("Vyoshadi Vatkam",    "¼ tsp", "After meals",  "Twice daily"),
                ("Neeri Tablets",      "1 tablet", "After meals", "Twice daily"),
                ("Tulsi Tea",          "1 cup", "Mid-morning",  "Daily"),
                ("Coriander-Barley Tea", "1 cup", "Morning & afternoon", "2-3x daily"),
            ]:
                if name in supp_map:
                    db.session.add(PlanSupplement(
                        plan_id=plan_shuva.id,
                        supplement_id=supp_map[name].id,
                        dose=dose, timing=timing, frequency=freq,
                    ))

            # Assign recipes
            recipe_map = {r.name: r for r in Recipe.query.all()}
            for name, slot in [
                ("Warm Oat Bowl",              "Breakfast"),
                ("Savory Vegetable Oats",      "Breakfast"),
                ("Eggs with Vegetables",       "Breakfast"),
                ("Barley Vegetable Bowl",      "Lunch"),
                ("Light Chicken Vegetable Soup", "Lunch"),
                ("Simple Fish with Vegetables","Lunch"),
                ("Coriander-Barley Tea",       "Tea"),
                ("Tulsi Tea",                  "Tea"),
            ]:
                if name in recipe_map:
                    db.session.add(PlanRecipe(
                        plan_id=plan_shuva.id,
                        recipe_id=recipe_map[name].id,
                        meal_slot=slot,
                    ))

            print("Created patient: Shuva Mukhopadhyay")

        # ── Patient 2: Kajori Dasgupta ────────────────────────────────────
        kajori = Patient.query.filter_by(email="kajori.d@example.com").first()
        if not kajori:
            kajori = Patient(
                practitioner_id=practitioner.id,
                first_name="Kajori",
                last_name="Dasgupta",
                email="kajori.d@example.com",
                phone="(416) 555-0287",
                dob=date(1952, 8, 14),
                sex="Female",
                location="Toronto, Ontario",
                occupation="Retired",
                weight_note="Stable weight",
                exercise_notes="30-minute outdoor walk daily (morning). Short walk after dinner (10–15 min). Gentle breathing practice.",
                diet_pattern="Warm home-cooked meals. Prefers Indian vegetarian. Regular meal timing. Occasional irregular schedule during travel.",
                alcohol_notes="None",
                caffeine_notes="Reduces caffeine after noon to support blood pressure and sleep.",
            )
            db.session.add(kajori)
            db.session.flush()

            # Health profile
            hp2 = HealthProfile(
                patient_id=kajori.id,
                lab_date=date(2026, 1, 20),
                lab_notes="Cholesterol elevated. Blood pressure monitoring required. Iron levels low-normal.",
                chief_complaints=(
                    "Elevated cholesterol — LDL management\n"
                    "Blood pressure — hypertension management\n"
                    "Digestive sluggishness\n"
                    "Low energy and fatigue\n"
                    "Sleep disturbance — wakes during night\n"
                    "Stress and mood fluctuations"
                ),
                medical_history=(
                    "Hypertension — managed with medication (Arjuna support)\n"
                    "Elevated LDL cholesterol\n"
                    "Low iron (borderline)\n"
                    "Granddaughter with respiratory/allergy symptoms"
                ),
                dosha_primary="Vata",
                dosha_secondary="Pitta",
                dosha_imbalances=(
                    "Elevated Vata — irregular sleep, anxiety, digestive sluggishness\n"
                    "Pitta in cardiovascular system — cholesterol and BP elevation\n"
                    "Agni weakness — needs warm, easy-to-digest meals\n"
                    "Depleted ojas — fatigue, low immunity"
                ),
                agni_assessment="Mandagni (slow digestive fire) — responds well to warming spices, ghee, and regular meal timing",
                prakriti_notes="Vata-Pitta constitution. Age-related Vata increase. 2-month support protocol with cruise travel follow-up scheduled before June 24.",
            )
            db.session.add(hp2)

            # Check-in token
            token_kajori = CheckInToken(patient_id=kajori.id)
            db.session.add(token_kajori)
            db.session.flush()

            # Active plan — Kajori
            plan_kajori = ConsultationPlan(
                patient_id=kajori.id,
                title="2-Month Ayurvedic Heart & Vata Support Protocol",
                active=True,
                duration_weeks=8,
                start_date=date(2026, 2, 1),
                end_date=date(2026, 3, 29),
                foods_to_avoid=(
                    "Cold foods and beverages\nHeavily fried foods\nLate dinners / heavy evening meals\n"
                    "Excess caffeine (especially after noon)\nRefined sugar and sweets\n"
                    "Screens after 9:30pm\nIrregular meal timing"
                ),
                foods_to_include=(
                    "Warm freshly prepared meals\nBarley (chapati/soup/porridge) or ragi\n"
                    "Recommended vegetables: spinach, lauki, moringa, zucchini, asparagus, beet greens, carrots, butternut squash\n"
                    "Dal: masoor or mung — well-cooked, served warm\n"
                    "Small amount of ghee with meals\n1–2 tsp amla pickle with lunch\n"
                    "Black sesame seeds (roasted/ground) — small amount daily\n"
                    "Pumpkin seeds (soaked or roasted) as snack\n"
                    "Fennel + mint + cardamom tea daily"
                ),
                lifestyle_notes=(
                    "30-minute outdoor walk each morning\nShort walk after dinner (10–15 min)\n"
                    "Consistent sleep schedule — no screens after 9:30pm\n"
                    "Gentle breathing / meditation if stress elevated\n"
                    "Regular meal timing — avoid skipping meals"
                ),
                breathing_notes="Gentle breathing practice daily for nervous system balance.",
                followup_notes="Check in before June 24 to prepare Vata-supportive travel routines for cruise. Email: meenakshi@ayurroots.com",
            )
            db.session.add(plan_kajori)
            db.session.flush()

            # Kajori supplements — add Arjuna if not in library
            arjuna = Supplement.query.filter_by(name="Arjuna Tablet").first()
            if not arjuna:
                arjuna = Supplement(
                    name="Arjuna Tablet",
                    brand="Himalaya Organic",
                    category="Tablet",
                    purpose="Heart & cholesterol support",
                    source_url="https://himalayawellness.in",
                )
                db.session.add(arjuna)
                db.session.flush()

            fennel_tea = Supplement.query.filter_by(name="Fennel-Mint-Cardamom Tea").first()
            if not fennel_tea:
                fennel_tea = Supplement(
                    name="Fennel-Mint-Cardamom Tea",
                    brand=None,
                    category="Tea",
                    purpose="Digestion, blood pressure support, Vata calming",
                )
                db.session.add(fennel_tea)
                db.session.flush()

            supp_map2 = {s.name: s for s in Supplement.query.all()}
            for name, dose, timing, freq in [
                ("Arjuna Tablet",             "1 tablet", "Once daily",   "Daily"),
                ("Fennel-Mint-Cardamom Tea",  "1 cup",    "Morning & afternoon", "Daily"),
            ]:
                if name in supp_map2:
                    db.session.add(PlanSupplement(
                        plan_id=plan_kajori.id,
                        supplement_id=supp_map2[name].id,
                        dose=dose, timing=timing, frequency=freq,
                    ))

            # Add Kajori-specific recipes
            kajori_recipes = [
                {"name": "Ragi Porridge", "meal_type": "Breakfast",
                 "ingredients": "½ cup ragi flour, 1½ cups water or warm milk, pinch cardamom, 1 tsp ghee, small amount jaggery (optional)",
                 "instructions": "Whisk ragi flour into cold water. Bring to low heat stirring constantly. Cook 5–7 min until thick. Add cardamom and ghee. Sweeten lightly if desired."},
                {"name": "Mung Dal Cheela", "meal_type": "Breakfast",
                 "ingredients": "½ cup mung dal (soaked overnight), grated zucchini or spinach, ginger, cumin, pinch turmeric, salt",
                 "instructions": "Blend soaked dal with ginger and cumin to a smooth batter. Add grated vegetables. Cook like a thin pancake on a non-stick pan. Serve warm."},
                {"name": "Barley Porridge", "meal_type": "Breakfast",
                 "ingredients": "½ cup pearl barley or barley flour, chopped carrots or spinach, cumin, ginger, salt, 1 tsp ghee",
                 "instructions": "Sauté cumin and ginger in ghee. Add chopped vegetables. Add barley and water. Cook until soft. Season with salt."},
                {"name": "Masoor Dal Soup", "meal_type": "Lunch",
                 "ingredients": "½ cup red lentils, spinach or moringa, carrots, turmeric, cumin, coriander, ginger, 1 tsp ghee",
                 "instructions": "Rinse lentils. Add all ingredients to pot with water. Cook 20 min until lentils soft. Temper with ghee and cumin. Serve warm with barley chapati."},
                {"name": "Mung Dal Khichdi", "meal_type": "Lunch",
                 "ingredients": "½ cup mung dal, ¼ cup barley or rice, zucchini, bottle gourd, asparagus, turmeric, cumin, ginger, 1 tsp ghee, salt",
                 "instructions": "Rinse mung dal and barley. Cook together with vegetables, turmeric, and ginger in plenty of water until very soft. Temper with ghee and cumin. Easy on digestion — excellent for Vata."},
                {"name": "Amla Pickle", "meal_type": "Snack",
                 "ingredients": "6–8 medium fresh amla, 2–3 tsp sesame oil, ½ tsp turmeric, ½ tsp roasted cumin powder, ½ tsp coriander powder, pinch hing, salt, optional: grated ginger",
                 "instructions": "Steam amla 5 min, remove seeds and cut. Heat oil on LOW, add hing and turmeric. Add amla and sauté 2–3 min. Add spice powders, stir well. Cool completely before adding salt. Store in glass jar in refrigerator. Take 1–2 tsp with lunch daily."},
                {"name": "Fennel-Mint-Cardamom Tea", "meal_type": "Tea", "is_tea": True,
                 "ingredients": "Fennel seeds, fresh or dried mint, 1–2 cardamom pods",
                 "instructions": "Add all ingredients to hot water. Steep 5 min. Drink warm. Benefits: digestion, blood pressure, Vata balance."},
            ]

            recipe_map2 = {r.name: r for r in Recipe.query.all()}
            for rd in kajori_recipes:
                if rd['name'] not in recipe_map2:
                    r = Recipe(**rd)
                    db.session.add(r)
                    db.session.flush()
                    recipe_map2[r.name] = r

            for name, slot in [
                ("Ragi Porridge",    "Breakfast"),
                ("Mung Dal Cheela",  "Breakfast"),
                ("Masoor Dal Soup",  "Lunch"),
                ("Mung Dal Khichdi", "Lunch"),
                ("Amla Pickle",      "Snack"),
                ("Fennel-Mint-Cardamom Tea", "Tea"),
            ]:
                if name in recipe_map2:
                    db.session.add(PlanRecipe(
                        plan_id=plan_kajori.id,
                        recipe_id=recipe_map2[name].id,
                        meal_slot=slot,
                    ))

            print("Created patient: Kajori Dasgupta")

        db.session.commit()

        # ── Synthetic Check-Ins ──────────────────────────────────────────
        _seed_checkins(shuva,  days=14)
        _seed_checkins(kajori, days=21)

        # ── Follow-Ups ───────────────────────────────────────────────────
        _seed_followups(shuva,  practitioner)
        _seed_followups(kajori, practitioner)

        db.session.commit()
        print("\nDemo seed complete!")
        print(f"  Login:    {DEMO_EMAIL}")
        print(f"  Password: {DEMO_PASSWORD}")
        print(f"  URL:      http://127.0.0.1:5001/setup  (or /login if account already exists)")


def _seed_checkins(patient, days=14):
    """Generate realistic daily check-ins with gradual improvement trend."""
    today = date.today()
    existing_dates = {ci.date for ci in patient.checkins.all()}

    for i in range(days, 0, -1):
        d = today - timedelta(days=i)
        if d in existing_dates:
            continue

        # Skip ~15% of days (missed check-ins)
        if random.random() < 0.15:
            continue

        # Gradual improvement: earlier days worse, recent days better
        progress = i / days  # 1.0 = oldest, 0.0 = most recent
        compliance = random.uniform(0.45 + (1 - progress) * 0.4, 0.85 + (1 - progress) * 0.15)

        def check(prob): return random.random() < min(prob, 1.0)

        base_score = max(2, min(5, round(2.5 + (1 - progress) * 1.8 + random.uniform(-0.5, 0.5))))

        ci = DailyCheckIn(
            patient_id=patient.id,
            date=d,
            submitted_at=datetime.combine(d, datetime.min.time()).replace(hour=20, minute=random.randint(0,59)),
            warm_water=check(compliance + 0.2),
            breathing_exercise=check(compliance),
            nasal_oil=check(compliance - 0.15),
            warm_breakfast=check(compliance + 0.1),
            avoided_cold_food=check(compliance + 0.1),
            avoided_yogurt=check(compliance + 0.2),
            herbal_tea_am=check(compliance),
            warm_lunch=check(compliance + 0.05),
            included_barley=check(compliance - 0.05),
            no_cold_drinks=check(compliance + 0.1),
            warm_dinner=check(compliance),
            dinner_before_8pm=check(compliance - 0.1),
            supplements_am=check(compliance),
            supplements_pm=check(compliance - 0.05),
            cardio_today=check(compliance - 0.2),
            consistent_sleep=check(compliance - 0.1),
            digestion_score=min(5, max(1, base_score + random.randint(-1, 1))),
            urinary_score=min(5, max(1, base_score + random.randint(-1, 1))) if patient.first_name == "Shuva" else None,
            sinus_score=min(5, max(1, base_score + random.randint(-1, 1))),
            energy_score=min(5, max(1, base_score + random.randint(-1, 1))),
            notes=random.choice([
                "", "", "", "",  # Most have no notes
                "Feeling better today",
                "Skipped evening supplements",
                "Had a stressful work day",
                "Good energy this morning",
                "Digestion felt off",
                "Slept well last night",
            ]),
        )
        db.session.add(ci)


def _seed_followups(patient, practitioner):
    """Create realistic follow-up schedule."""
    existing = {fu.scheduled_date for fu in patient.followups.all()}
    today = date.today()

    schedule = [
        (today - timedelta(days=14), "Initial 1-week check-in", True),
        (today - timedelta(days=7),  "2-week progress review",  True),
        (today,                       "3-week protocol review",  False),
        (today + timedelta(days=14),  "Month 1 assessment",     False),
    ]
    if patient.first_name == "Kajori":
        schedule.append((date(2026, 6, 20), "Pre-cruise Vata travel preparation", False))

    for fu_date, reason, completed in schedule:
        if fu_date in existing:
            continue
        fu = FollowUp(
            patient_id=patient.id,
            practitioner_id=practitioner.id,
            scheduled_date=fu_date,
            reason=reason,
            completed=completed,
            completed_at=datetime.combine(fu_date, datetime.min.time()).replace(hour=11) if completed else None,
            notes="Reviewed progress. Patient responding well to protocol." if completed else "",
        )
        db.session.add(fu)


if __name__ == "__main__":
    run()
