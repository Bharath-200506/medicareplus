from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
import json


# ─── Specialisation keyword map for local fallback ───────────────────────────
SYMPTOM_SPECIALTY_MAP = {
    'cardiologist':      ['chest pain', 'heart', 'palpitation', 'shortness of breath',
                          'hypertension', 'blood pressure', 'cardiac'],
    'dermatologist':     ['rash', 'skin', 'acne', 'eczema', 'allergy', 'itching',
                          'hair loss', 'psoriasis', 'dermat'],
    'neurologist':       ['headache', 'migraine', 'seizure', 'numbness', 'dizziness',
                          'memory', 'stroke', 'tremor', 'nerve', 'neurol'],
    'pediatrician':      ['child', 'baby', 'infant', 'toddler', 'pediatr', 'vaccination'],
    'orthopedist':       ['bone', 'joint', 'knee', 'back pain', 'fracture', 'arthritis',
                          'spine', 'shoulder', 'orthop'],
    'general physician': ['fever', 'cold', 'flu', 'cough', 'fatigue', 'weakness',
                          'general', 'body ache', 'nausea', 'vomiting'],
}


def _detect_specialty_locally(text):
    """Rule-based fallback: return the best-matching specialisation or None."""
    text_lower = text.lower()
    for specialty, keywords in SYMPTOM_SPECIALTY_MAP.items():
        if any(kw in text_lower for kw in keywords):
            return specialty
    return None


def _get_doctors_for_specialty(specialty):
    """Return a list of available doctors whose specialisation matches."""
    from accounts.models import DoctorProfile
    profiles = (
        DoctorProfile.objects
        .filter(is_available=True, specialization__icontains=specialty)
        .select_related('user')[:5]
    )
    doctors = []
    for p in profiles:
        doctors.append({
            'id':             p.user.id,
            'name':           f"Dr. {p.user.get_full_name()}",
            'specialization': p.specialization,
            'experience':     p.experience_years,
            'fee':            float(p.consultation_fee),
            'image':          p.doctor_image.url if p.doctor_image else '/static/images/default-doctor.jpg',
        })
    return doctors


# ─── Views ────────────────────────────────────────────────────────────────────

@login_required
def chat_view(request):
    return render(request, 'chatbot/chat.html')


@login_required
def chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    data = json.loads(request.body)
    user_message = data.get('message', '').strip()
    if not user_message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')

        system_prompt = """You are MediBot, an AI health assistant for MediCarePlus online pharmacy.
You help users with:
- Medicine information and usage
- Appointment booking guidance (recommend specialists based on symptoms)
- General health FAQs
- Order and prescription queries

When a user describes symptoms or asks which doctor to see, identify the most appropriate medical specialist from:
Cardiologist, Dermatologist, Neurologist, Pediatrician, Orthopedist, General Physician.

Always recommend consulting a doctor for medical advice.
Be concise, friendly, and professional. Use plain text only (no markdown)."""

        response = model.generate_content(f"{system_prompt}\n\nUser: {user_message}")
        bot_reply = response.text
    except Exception:
        bot_reply = ("I'm sorry, I'm having trouble connecting right now. "
                     "Please try again later or contact our support team.")

    # ── Detect specialty to auto-surface doctor cards ──────────────────────
    specialty = _detect_specialty_locally(user_message + " " + bot_reply)
    doctors = _get_doctors_for_specialty(specialty) if specialty else []

    return JsonResponse({
        'reply':     bot_reply,
        'doctors':   doctors,
        'specialty': specialty or '',
    })


@login_required
def suggest_doctors(request):
    """Dedicated endpoint: POST {specialty} → returns matching doctors."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    data = json.loads(request.body)
    specialty = data.get('specialty', '').strip()
    doctors = _get_doctors_for_specialty(specialty) if specialty else []
    return JsonResponse({'doctors': doctors, 'specialty': specialty})