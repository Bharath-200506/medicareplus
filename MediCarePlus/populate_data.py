import os
import shutil
import sys
from datetime import date, time
from decimal import Decimal
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MediCarePlus.settings')

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import django
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import DoctorProfile, PatientProfile
from appointments.models import DoctorAvailability
from medicines.models import MedicineCategory, Medicine
from reviews.models import DoctorReview, MedicineReview

User = get_user_model()

def ensure_fallback_images():
    print("Ensuring fallback images exist...")
    static_img_dir = BASE_DIR / 'static' / 'images'
    media_doctors_dir = BASE_DIR / 'media' / 'doctors'
    media_profiles_dir = BASE_DIR / 'media' / 'profiles'
    media_categories_dir = BASE_DIR / 'media' / 'categories'

    static_img_dir.mkdir(parents=True, exist_ok=True)
    media_doctors_dir.mkdir(parents=True, exist_ok=True)
    media_profiles_dir.mkdir(parents=True, exist_ok=True)
    media_categories_dir.mkdir(parents=True, exist_ok=True)

    # 1. doctor1.jpg in static/images
    doctor1_target = static_img_dir / 'doctor1.jpg'
    if not doctor1_target.exists():
        src = media_doctors_dir / 'rameez.jpg'
        if not src.exists():
            src = media_doctors_dir / 'avinash.png'
        if src.exists():
            shutil.copy(src, doctor1_target)
            print(f"Created {doctor1_target} from {src.name}")

    # 2. default-doctor.jpg in media/doctors
    default_doc_target = media_doctors_dir / 'default-doctor.jpg'
    if not default_doc_target.exists():
        src = media_doctors_dir / 'rameez.jpg'
        if not src.exists():
            src = media_doctors_dir / 'avinash.png'
        if src.exists():
            shutil.copy(src, default_doc_target)
            print(f"Created {default_doc_target} from {src.name}")

    # 3. default-user.png in static/images and media/profiles
    default_user_static = static_img_dir / 'default-user.png'
    default_user_media = media_profiles_dir / 'default-user.png'
    profile_src = None
    for p in media_profiles_dir.glob('*.jpeg'):
        profile_src = p
        break
    if not profile_src:
        profile_src = media_doctors_dir / 'rameez.jpg'

    if profile_src and profile_src.exists():
        if not default_user_static.exists():
            shutil.copy(profile_src, default_user_static)
            print(f"Created {default_user_static}")
        if not default_user_media.exists():
            shutil.copy(profile_src, default_user_media)
            print(f"Created {default_user_media}")

    # 4. Copy category images to media/categories
    cat_img_map = {
        'analgesics.jpg': 'analgesics.jpg',
        'antibiotics.jpg': 'antibiotics.jpg',
        'cardiovascular.jpg': 'cardiovascular.jpg',
        'antidiabetics.jpg': 'antidiabetics.jpg',
        'respiratory.jpg': 'respiratory.jpg',
        'vitamins.jpg': 'vitamins.jpg',
        'gastrointestinal.jpg': 'gastrointestinal.jpg',
        'dermatology.jpg': 'dermatology.jpg',
    }
    for src_name, dst_name in cat_img_map.items():
        s = static_img_dir / src_name
        d = media_categories_dir / dst_name
        if s.exists() and not d.exists():
            shutil.copy(s, d)
            print(f"Copied {s.name} to media/categories/{dst_name}")


def seed_doctors():
    print("\n--- Seeding Doctors ---")
    doctors_data = [
        {
            'first_name': 'Avinash',
            'last_name': 'Pallapothu',
            'email': 'avinash@medicareplus.com',
            'username': 'avinash',
            'phone': '9876543210',
            'specialization': 'Cardiologist',
            'qualification': 'MBBS, MD (Cardiology), FACC',
            'experience_years': 12,
            'consultation_fee': Decimal('800.00'),
            'bio': 'Senior Interventional Cardiologist with over 12 years of experience in treating complex cardiovascular conditions, hypertension, and preventative cardiac care.',
            'image': 'doctors/avinash.png',
        },
        {
            'first_name': 'Varun',
            'last_name': 'Gogada',
            'email': 'varun@medicareplus.com',
            'username': 'varun',
            'phone': '9876543211',
            'specialization': 'Dermatologist',
            'qualification': 'MBBS, MD (Dermatology & Venereology)',
            'experience_years': 8,
            'consultation_fee': Decimal('600.00'),
            'bio': 'Consultant Dermatologist and Aesthetic Specialist skilled in treating acne, eczema, psoriasis, hair loss treatments, and advanced clinical skincare.',
            'image': 'doctors/varun.jpg',
        },
        {
            'first_name': 'Bharath',
            'last_name': 'Ganta',
            'email': 'bharath@medicareplus.com',
            'username': 'bharath',
            'phone': '9876543212',
            'specialization': 'Pediatrician',
            'qualification': 'MBBS, DCH, MD (Pediatrics)',
            'experience_years': 10,
            'consultation_fee': Decimal('700.00'),
            'bio': 'Dedicated and compassionate Pediatrician focused on newborn healthcare, childhood vaccinations, growth monitoring, and pediatric infectious disease management.',
            'image': 'doctors/bharath.jpg',
        },
        {
            'first_name': 'Praneeth',
            'last_name': 'Mallipudi',
            'email': 'praneeth@medicareplus.com',
            'username': 'praneeth',
            'phone': '9876543213',
            'specialization': 'Neurologist',
            'qualification': 'MBBS, MD, DM (Neurology)',
            'experience_years': 14,
            'consultation_fee': Decimal('1000.00'),
            'bio': 'Senior Consultant Neurologist specializing in stroke management, epilepsy, Parkinson’s disease, migraine, and comprehensive neuromuscular disorder care.',
            'image': 'doctors/praneeth.jpg',
        },
        {
            'first_name': 'Mohith',
            'last_name': 'Taninki',
            'email': 'mohith@medicareplus.com',
            'username': 'mohith',
            'phone': '9876543214',
            'specialization': 'Orthopedist',
            'qualification': 'MBBS, MS (Orthopedics), MCh Ortho',
            'experience_years': 9,
            'consultation_fee': Decimal('750.00'),
            'bio': 'Orthopedic and Joint Replacement Surgeon with rich experience in sports medicine, arthroscopy, fracture care, and arthritis management.',
            'image': 'doctors/mohith.jpg',
        },
        {
            'first_name': 'Rameez',
            'last_name': 'Sheik',
            'email': 'rameez@medicareplus.com',
            'username': 'rameez',
            'phone': '9876543215',
            'specialization': 'General Physician',
            'qualification': 'MBBS, MD (General Medicine)',
            'experience_years': 7,
            'consultation_fee': Decimal('500.00'),
            'bio': 'Experienced General Physician providing holistic primary care, lifestyle disease management, fever investigations, and chronic health counseling.',
            'image': 'doctors/rameez.jpg',
        },
    ]

    days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
    seed_password = os.environ.get('SEED_DOCTOR_PASSWORD')

    for doc_data in doctors_data:
        user, created = User.objects.get_or_create(
            email=doc_data['email'],
            defaults={
                'username': doc_data['username'],
                'first_name': doc_data['first_name'],
                'last_name': doc_data['last_name'],
                'phone': doc_data['phone'],
                'role': 'DOCTOR',
                'is_verified': True,
                'is_active': True,
            }
        )
        if created:
            if seed_password:
                user.set_password(seed_password)
            else:
                user.set_unusable_password()
        user.role = 'DOCTOR'
        user.is_verified = True
        user.is_active = True
        user.first_name = doc_data['first_name']
        user.last_name = doc_data['last_name']
        user.phone = doc_data['phone']
        user.save()

        # Doctor profile
        profile, p_created = DoctorProfile.objects.get_or_create(
            user=user,
            defaults={
                'specialization': doc_data['specialization'],
                'qualification': doc_data['qualification'],
                'experience_years': doc_data['experience_years'],
                'consultation_fee': doc_data['consultation_fee'],
                'bio': doc_data['bio'],
                'doctor_image': doc_data['image'],
                'is_available': True,
            }
        )
        if not p_created:
            profile.specialization = doc_data['specialization']
            profile.qualification = doc_data['qualification']
            profile.experience_years = doc_data['experience_years']
            profile.consultation_fee = doc_data['consultation_fee']
            profile.bio = doc_data['bio']
            profile.doctor_image = doc_data['image']
            profile.is_available = True
            profile.save()

        # Doctor availability slots (MON-SAT 09:00 - 17:00)
        for d in days:
            DoctorAvailability.objects.update_or_create(
                doctor=user,
                day=d,
                defaults={
                    'start_time': time(9, 0),
                    'end_time': time(17, 0),
                    'is_available': True,
                }
            )

        print(f"Doctor seeded: Dr. {user.get_full_name()} ({profile.specialization})")


def seed_medicines():
    print("\n--- Seeding Medicine Categories & Medicines ---")
    categories_data = [
        {
            'name': 'Pain Relief & Analgesics',
            'description': 'Medications for pain management, headache, fever reduction, and anti-inflammatory relief.',
            'image': 'categories/analgesics.jpg',
            'medicines': [
                {
                    'name': 'Dolo 650 Tablet',
                    'description': 'Dolo 650 is a widely trusted antipyretic and analgesic tablet containing Paracetamol 650mg. Provides rapid relief from fever, body ache, headache, and mild muscle pain.',
                    'price': Decimal('34.50'),
                    'discount': Decimal('10.00'),
                    'stock': 120,
                    'manufacturer': 'Micro Labs Ltd',
                    'expiry_date': date(2027, 8, 31),
                    'prescription_required': False,
                    'is_featured': True,
                },
                {
                    'name': 'Brufen 400 Tablet',
                    'description': 'Contains Ibuprofen 400mg, a non-steroidal anti-inflammatory drug (NSAID) effective for dental pain, joint pain, backache, and inflammation.',
                    'price': Decimal('48.00'),
                    'discount': Decimal('15.00'),
                    'stock': 85,
                    'manufacturer': 'Abbott Healthcare',
                    'expiry_date': date(2027, 6, 30),
                    'prescription_required': False,
                    'is_featured': True,
                },
                {
                    'name': 'Combiflam Tablet',
                    'description': 'Combination of Paracetamol (325mg) and Ibuprofen (400mg) for fast relief from severe headache, toothache, muscular pain, and fever.',
                    'price': Decimal('52.00'),
                    'discount': Decimal('5.00'),
                    'stock': 95,
                    'manufacturer': 'Sanofi India Ltd',
                    'expiry_date': date(2027, 10, 31),
                    'prescription_required': False,
                    'is_featured': False,
                },
                {
                    'name': 'Volini Pain Relief Gel 50g',
                    'description': 'Advanced pain relief formula with Diclofenac and Menthol for deep penetration and instant relief from sprains, backache, and joint stiffness.',
                    'price': Decimal('165.00'),
                    'discount': Decimal('12.00'),
                    'stock': 60,
                    'manufacturer': 'Sun Pharmaceutical',
                    'expiry_date': date(2028, 1, 31),
                    'prescription_required': False,
                    'is_featured': False,
                },
            ]
        },
        {
            'name': 'Antibiotics & Anti-Infectives',
            'description': 'Broad-spectrum antibiotics and antimicrobial medications to fight bacterial infections.',
            'image': 'categories/antibiotics.jpg',
            'medicines': [
                {
                    'name': 'Augmentin 625 Duo Tablet',
                    'description': 'Potent combination of Amoxicillin (500mg) and Clavulanic Acid (125mg). Effectively treats respiratory tract, skin, ear, and urinary tract infections.',
                    'price': Decimal('225.00'),
                    'discount': Decimal('10.00'),
                    'stock': 50,
                    'manufacturer': 'GlaxoSmithKline (GSK)',
                    'expiry_date': date(2027, 5, 31),
                    'prescription_required': True,
                    'is_featured': True,
                },
                {
                    'name': 'Azithral 500 Tablet',
                    'description': 'Contains Azithromycin 500mg, an azalide antibiotic prescribed for throat infections, pneumonia, bronchitis, and sinusitis.',
                    'price': Decimal('142.00'),
                    'discount': Decimal('8.00'),
                    'stock': 70,
                    'manufacturer': 'Alembic Pharmaceuticals',
                    'expiry_date': date(2027, 9, 30),
                    'prescription_required': True,
                    'is_featured': True,
                },
                {
                    'name': 'Ciplox 500 Tablet',
                    'description': 'Contains Ciprofloxacin 500mg, a broad-spectrum fluoroquinolone antibiotic used to treat bacterial gastrointestinal, urinary, and skin infections.',
                    'price': Decimal('82.00'),
                    'discount': Decimal('5.00'),
                    'stock': 65,
                    'manufacturer': 'Cipla Ltd',
                    'expiry_date': date(2027, 7, 31),
                    'prescription_required': True,
                    'is_featured': False,
                },
            ]
        },
        {
            'name': 'Cardiovascular & Heart Health',
            'description': 'Medications for blood pressure regulation, cholesterol control, and cardiovascular wellness.',
            'image': 'categories/cardiovascular.jpg',
            'medicines': [
                {
                    'name': 'Atorva 10 Tablet',
                    'description': 'Contains Atorvastatin 10mg. Lowers LDL ("bad") cholesterol and triglycerides, reducing the risk of heart attacks and stroke.',
                    'price': Decimal('118.00'),
                    'discount': Decimal('15.00'),
                    'stock': 80,
                    'manufacturer': 'Zydus Cadila',
                    'expiry_date': date(2027, 11, 30),
                    'prescription_required': True,
                    'is_featured': True,
                },
                {
                    'name': 'Telma 40 Tablet',
                    'description': 'Contains Telmisartan 40mg, an angiotensin receptor blocker (ARB) used for lowering high blood pressure and protecting kidney function.',
                    'price': Decimal('112.00'),
                    'discount': Decimal('10.00'),
                    'stock': 90,
                    'manufacturer': 'Glenmark Pharmaceuticals',
                    'expiry_date': date(2027, 12, 31),
                    'prescription_required': True,
                    'is_featured': False,
                },
                {
                    'name': 'EcoSprin 75 Capsule',
                    'description': 'Low-dose Aspirin (75mg) antiplatelet medication used to prevent blood clots, heart attacks, and stroke in high-risk patients.',
                    'price': Decimal('24.00'),
                    'discount': Decimal('0.00'),
                    'stock': 200,
                    'manufacturer': 'USV Pvt Ltd',
                    'expiry_date': date(2028, 4, 30),
                    'prescription_required': False,
                    'is_featured': True,
                },
            ]
        },
        {
            'name': 'Antidiabetics & Sugar Control',
            'description': 'Oral antidiabetic agents and glycemic control medications for Type-2 Diabetes.',
            'image': 'categories/antidiabetics.jpg',
            'medicines': [
                {
                    'name': 'Glycomet 500 SR Tablet',
                    'description': 'Contains Metformin 500mg in sustained release form. Helps control high blood sugar levels in Type-2 Diabetes by improving insulin sensitivity.',
                    'price': Decimal('45.00'),
                    'discount': Decimal('10.00'),
                    'stock': 140,
                    'manufacturer': 'USV Pvt Ltd',
                    'expiry_date': date(2027, 8, 31),
                    'prescription_required': True,
                    'is_featured': True,
                },
                {
                    'name': 'Amaryl 2mg Tablet',
                    'description': 'Contains Glimepiride 2mg, a sulfonylurea medication that stimulates insulin secretion from the pancreas to lower blood glucose.',
                    'price': Decimal('98.00'),
                    'discount': Decimal('12.00'),
                    'stock': 75,
                    'manufacturer': 'Sanofi India Ltd',
                    'expiry_date': date(2027, 10, 31),
                    'prescription_required': True,
                    'is_featured': False,
                },
                {
                    'name': 'Januvia 100mg Tablet',
                    'description': 'Contains Sitagliptin 100mg (DPP-4 inhibitor). Enhances the natural incretin hormones to safely regulate post-meal blood sugar levels.',
                    'price': Decimal('360.00'),
                    'discount': Decimal('8.00'),
                    'stock': 40,
                    'manufacturer': 'MSD Pharmaceuticals',
                    'expiry_date': date(2028, 2, 28),
                    'prescription_required': True,
                    'is_featured': False,
                },
            ]
        },
        {
            'name': 'Respiratory & Cold Care',
            'description': 'Inhalers, antihistamines, decongestants, and cough syrups for respiratory wellness.',
            'image': 'categories/respiratory.jpg',
            'medicines': [
                {
                    'name': 'Montair LC Tablet',
                    'description': 'Combination of Montelukast (10mg) and Levocetirizine (5mg). Prescribed for allergic rhinitis, chronic asthma, sneezing, and runny nose.',
                    'price': Decimal('198.00'),
                    'discount': Decimal('15.00'),
                    'stock': 85,
                    'manufacturer': 'Cipla Ltd',
                    'expiry_date': date(2027, 9, 30),
                    'prescription_required': False,
                    'is_featured': True,
                },
                {
                    'name': 'Ascoril LS Syrup 100ml',
                    'description': 'Productive cough syrup containing Levosalbutamol, Ambroxol, and Guaiphenesin. Relieves chest congestion and eases breathing.',
                    'price': Decimal('132.00'),
                    'discount': Decimal('10.00'),
                    'stock': 60,
                    'manufacturer': 'Glenmark Pharmaceuticals',
                    'expiry_date': date(2027, 7, 31),
                    'prescription_required': False,
                    'is_featured': True,
                },
                {
                    'name': 'Budecort 200 Inhaler',
                    'description': 'Contains Budesonide 200mcg corticosteroid. Reduces swelling and irritation in airways for ongoing management of asthma and COPD.',
                    'price': Decimal('345.00'),
                    'discount': Decimal('5.00'),
                    'stock': 35,
                    'manufacturer': 'Cipla Ltd',
                    'expiry_date': date(2028, 3, 31),
                    'prescription_required': True,
                    'is_featured': False,
                },
            ]
        },
        {
            'name': 'Vitamins & Dietary Supplements',
            'description': 'Essential multivitamins, minerals, calcium, and immunity enhancers for daily health.',
            'image': 'categories/vitamins.jpg',
            'medicines': [
                {
                    'name': 'Becosules Z Capsules',
                    'description': 'Vitamin B-Complex with Vitamin C and Zinc. Boosts immune function, supports metabolism, speeds wound healing, and treats oral ulcers.',
                    'price': Decimal('58.00'),
                    'discount': Decimal('10.00'),
                    'stock': 160,
                    'manufacturer': 'Pfizer Ltd',
                    'expiry_date': date(2028, 1, 31),
                    'prescription_required': False,
                    'is_featured': True,
                },
                {
                    'name': 'Shelcal 500 Tablet',
                    'description': 'Contains Calcium (500mg) and Vitamin D3 (250 IU). Essential for maintaining bone density, joint health, and preventing osteoporosis.',
                    'price': Decimal('145.00'),
                    'discount': Decimal('12.00'),
                    'stock': 110,
                    'manufacturer': 'Torrent Pharmaceuticals',
                    'expiry_date': date(2028, 5, 31),
                    'prescription_required': False,
                    'is_featured': True,
                },
                {
                    'name': 'Limcee 500mg Chewable Tablet',
                    'description': 'Delicious orange-flavored Vitamin C 500mg chewable tablets. Powerful antioxidant that supports immunity, collagen synthesis, and skin health.',
                    'price': Decimal('32.00'),
                    'discount': Decimal('5.00'),
                    'stock': 220,
                    'manufacturer': 'Abbott Healthcare',
                    'expiry_date': date(2028, 8, 31),
                    'prescription_required': False,
                    'is_featured': True,
                },
                {
                    'name': 'Evion 400 Capsule',
                    'description': 'Contains Vitamin E (Tocopheryl Acetate 400mg). Renowned antioxidant supplement for radiant skin, nourished hair, and muscular endurance.',
                    'price': Decimal('42.00'),
                    'discount': Decimal('0.00'),
                    'stock': 130,
                    'manufacturer': 'Merck Ltd / Procter & Gamble',
                    'expiry_date': date(2028, 6, 30),
                    'prescription_required': False,
                    'is_featured': False,
                },
            ]
        },
        {
            'name': 'Gastrointestinal & Digestive Health',
            'description': 'Antacids, proton-pump inhibitors, and digestive enzymes for hyperacidity, GERD, and gut balance.',
            'image': 'categories/gastrointestinal.jpg',
            'medicines': [
                {
                    'name': 'Pan 40 Tablet',
                    'description': 'Contains Pantoprazole 40mg. Inhibits stomach acid production to provide long-lasting relief from acid reflux, heartburn, and peptic ulcers.',
                    'price': Decimal('162.00'),
                    'discount': Decimal('15.00'),
                    'stock': 100,
                    'manufacturer': 'Alkem Laboratories',
                    'expiry_date': date(2027, 11, 30),
                    'prescription_required': False,
                    'is_featured': True,
                },
                {
                    'name': 'Digene Gel Antacid Mint 200ml',
                    'description': 'Fast-acting liquid antacid gel with magnesium hydroxide and simethicone for instant neutralization of stomach acid, gas, and bloating.',
                    'price': Decimal('148.00'),
                    'discount': Decimal('10.00'),
                    'stock': 70,
                    'manufacturer': 'Abbott Healthcare',
                    'expiry_date': date(2027, 9, 30),
                    'prescription_required': False,
                    'is_featured': True,
                },
                {
                    'name': 'Omez 20 Capsule',
                    'description': 'Contains Omeprazole 20mg. Highly effective treatment for gastroesophageal reflux disease (GERD) and prevention of NSAID-induced ulcers.',
                    'price': Decimal('78.00'),
                    'discount': Decimal('8.00'),
                    'stock': 90,
                    'manufacturer': "Dr. Reddy's Laboratories",
                    'expiry_date': date(2027, 12, 31),
                    'prescription_required': False,
                    'is_featured': False,
                },
            ]
        },
        {
            'name': 'Dermatology & Skin Care',
            'description': 'Topical antiseptic creams, anti-fungal ointments, and acne treatments for healthy skin.',
            'image': 'categories/dermatology.jpg',
            'medicines': [
                {
                    'name': 'Candid B Cream 20g',
                    'description': 'Combination of Clotrimazole (1% w/w) and Beclomethasone (0.025% w/w). Effectively treats fungal skin infections, redness, itching, and ringworm.',
                    'price': Decimal('152.00'),
                    'discount': Decimal('12.00'),
                    'stock': 75,
                    'manufacturer': 'Glenmark Pharmaceuticals',
                    'expiry_date': date(2027, 8, 31),
                    'prescription_required': False,
                    'is_featured': True,
                },
                {
                    'name': 'Clindac A Gel 15g',
                    'description': 'Contains Clindamycin 1% w/w. Topical antibacterial gel that clears active acne lesions, prevents breakouts, and reduces skin inflammation.',
                    'price': Decimal('210.00'),
                    'discount': Decimal('10.00'),
                    'stock': 50,
                    'manufacturer': 'Alkem Laboratories',
                    'expiry_date': date(2027, 6, 30),
                    'prescription_required': True,
                    'is_featured': False,
                },
                {
                    'name': 'Soframycin Skin Cream 30g',
                    'description': 'Contains Framycetin sulphate (1% w/w). Trusted antiseptic ointment for cuts, minor burns, scrapes, and skin bacterial infections.',
                    'price': Decimal('56.00'),
                    'discount': Decimal('5.00'),
                    'stock': 120,
                    'manufacturer': 'Sanofi India Ltd',
                    'expiry_date': date(2028, 2, 28),
                    'prescription_required': False,
                    'is_featured': False,
                },
            ]
        },
    ]

    for cat_data in categories_data:
        category, _ = MedicineCategory.objects.update_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'image': cat_data['image'],
            }
        )
        print(f"Category: {category.name}")

        for med in cat_data['medicines']:
            medicine, _ = Medicine.objects.update_or_create(
                name=med['name'],
                defaults={
                    'category': category,
                    'description': med['description'],
                    'price': med['price'],
                    'discount': med['discount'],
                    'stock': med['stock'],
                    'manufacturer': med['manufacturer'],
                    'expiry_date': med['expiry_date'],
                    'prescription_required': med['prescription_required'],
                    'is_featured': med['is_featured'],
                    'is_active': True,
                }
            )
            print(f"  - Medicine: {medicine.name} (INR {medicine.price})")


def seed_reviews():
    print("\n--- Seeding Sample Reviews ---")
    patient = User.objects.filter(role='PATIENT').first()
    if not patient:
        print("No patient user found to author reviews.")
        return

    doctors = User.objects.filter(role='DOCTOR')
    doctor_comments = [
        "Excellent doctor! Listened to all my symptoms very patiently and explained the diagnosis clearly.",
        "Very knowledgeable and caring specialist. The prescribed treatment worked within days.",
        "Punctual and highly professional consultation. Felt in safe hands throughout.",
        "Kind, compassionate and very thorough in examinations. Highly recommended!",
    ]
    for i, doc in enumerate(doctors):
        comment = doctor_comments[i % len(doctor_comments)]
        DoctorReview.objects.update_or_create(
            doctor=doc,
            patient=patient,
            defaults={
                'rating': 5,
                'comment': comment,
            }
        )
    print("Doctor reviews added.")

    featured_meds = Medicine.objects.filter(is_featured=True)[:4]
    for med in featured_meds:
        MedicineReview.objects.update_or_create(
            medicine=med,
            user=patient,
            defaults={
                'rating': 5,
                'comment': f"Genuine {med.name}. Received in great packaging and worked very effectively.",
            }
        )
    print("Medicine reviews added.")


def sync_to_root_db():
    print("\n--- Syncing db.sqlite3 ---")
    inner_db = BASE_DIR / 'db.sqlite3'
    root_db = BASE_DIR.parent / 'db.sqlite3'
    if inner_db.exists():
        shutil.copy(inner_db, root_db)
        print(f"Copied {inner_db} to {root_db}")


if __name__ == '__main__':
    ensure_fallback_images()
    seed_doctors()
    seed_medicines()
    seed_reviews()
    sync_to_root_db()
    print("\n=== Seeding completed successfully! ===")
