from typing import Dict

ONE_SHOT_EXAMPLE = """You are a clinical pharmacist creating a care plan. Here is an example of the format and quality expected:
<example>
INPUT:
Name: A.B. (Fictional)
MRN: 00012345 (fictional)
DOB: 1979-06-08 (Age 46)
Sex: Female
Weight: 72 kg
Allergies: None known to medications (no IgA deficiency)
Medication: IVIG
Primary diagnosis: Generalized myasthenia gravis (AChR antibody positive), MGFA class IIb
Secondary diagnoses: Hypertension (well controlled), GERD
Home meds: 
  Pyridostigmine 60 mg PO q6h PRN (current avg 3–4 doses/day)
  Prednisone 10 mg PO daily
  Lisinopril 10 mg PO daily
  Omeprazole 20 mg PO daily
Recent history:
  Progressive proximal muscle weakness and ptosis over 2 weeks with worsening speech and swallowing fatigue.
  Neurology recommends IVIG for rapid symptomatic control (planned course prior to planned thymectomy).
  Baseline respiratory status: no stridor; baseline FVC 2.8 L (predicted 4.0 L; ~70% predicted). No current myasthenic crisis but declining strength.
A. Baseline clinic note (pre-infusion)
  Date: 2025-10-15
  Vitals: BP 128/78, HR 78, RR 16, SpO2 98% RA, Temp 36.7°C
  Exam: Ptosis bilateral, fatigable proximal weakness (4/5), speech slurred after repeated counting, no respiratory distress.
  Labs: CBC WNL; BMP: Na 138, K 4.1, Cl 101, HCO3 24, BUN 12, SCr 0.78, eGFR >90 mL/min/1.73m².
  IgG baseline: 10 g/L (for replacement context; note IVIG for immunomodulation here).
  Plan: IVIG 2 g/kg total (144 g for 72 kg) given as 0.4 g/kg/day x 5 days in outpatient infusion center. Premedicate with acetaminophen + diphenhydramine; monitor vitals and FVC daily; continue pyridostigmine and prednisone.
B. Infusion visit note — Day 1
  Date: 2025-10-16
  IVIG product: Privigen (10% IVIG) — lot #P12345 (fictional)
  Dose given: 28.8 g (0.4 g/kg × 72 kg) diluted per manufacturer instructions.
  Premeds: Acetaminophen 650 mg PO + Diphenhydramine 25 mg PO 30 minutes pre-infusion.
  Infusion start rate: 0.5 mL/kg/hr for first 30 minutes (per institution titration) then increased per tolerance to max manufacturer rate.
  Vitals: q15 minutes first hour then q30 minutes; no fever, transient mild headache at 2 hours (resolved after slowing infusion).
  Respiratory: FVC 2.7 L (stable).
  Disposition: Completed infusion; observed 60 minutes post-infusion; discharged with plan for days 2–5.
(Monitoring of vitals and slow titration recommended; stop/slow if reaction. 
C. Follow-up — 2 weeks post-course
  Date: 2025-10-30
  Clinical status: Subjective improvement in speech and proximal strength; fewer fatigability episodes. No thrombotic events or renal issues reported. Next neurology follow-up in 4 weeks to consider repeat course vs. thymectomy timing.

OUTPUT:
Problem list / Drug therapy problems (DTPs)
  1. Need for rapid immunomodulation to reduce myasthenic symptoms (efficacy).
  2. Risk of infusion-related reactions (headache, chills, fever, rare anaphylaxis).
  3. Risk of renal dysfunction or volume overload in susceptible patients (sucrose-stabilized products, older age, pre-existing renal disease).
  4. Risk of thromboembolic events (rare) — consider risk factors (immobility, prior clot, hypercoagulable state).
  5. Potential drug–drug interactions or dosing timing (pyridostigmine timing around infusion, steroids).
  6. Patient education / adherence gap (understanding infusion process, adverse signs to report).
Goals (SMART)
  Primary: Achieve clinically meaningful improvement in muscle strength and reduce fatigability within 2 weeks of completing IVIG course.
  Safety goal: No severe infusion reaction, no acute kidney injury (no increase in SCr >0.3 mg/dL within 7 days post-infusion), and no thromboembolic events.
  Process: Complete full 2 g/kg course (0.4 g/kg/day × 5 days) with documented vital sign monitoring and infusion logs.
(Typical immunomodulatory dosing is 2 g/kg divided over 2–5 days — e.g., 0.4 g/kg/day × 5 days).
Pharmacist interventions / plan
  1. Dosing & Administration
    Verify total dose: 2.0 g/kg total (calculate using actual body weight unless otherwise specified). For 72 kg → 144 g total = 28.8 g/day × 5 days. Document lot number and expiration of product.
  2. Premedication
    Recommend acetaminophen 650 mg PO and diphenhydramine 25–50 mg PO 30–60 minutes prior to infusion; consider low-dose corticosteroid premed if prior reactions or severe symptoms (institutional practice varies). (Premeds can reduce minor infusion reactions but are not foolproof).
  3. Infusion rates & titration
    Start at a low rate (per product label/manufacturer) — example: 0.5 mL/kg/hr for first 15–30 min, then increase in stepwise fashion with at least three planned rate escalations up to manufacturer maximum as tolerated. If any infusion reactions occur, slow or stop and treat per reaction algorithm. 
  4. Hydration & renal protection
    Ensure adequate hydration prior to infusion (e.g., 250–500 mL normal saline if not fluid-overloaded) especially in patients with risk factors for renal dysfunction. Avoid sucrose-containing IVIG products in patients with uncontrolled diabetes or high renal risk. Monitor renal function (SCr, BUN, eGFR) pre-course and within 3–7 days post-completion.
  5. Thrombosis risk mitigation
    Assess baseline thrombosis risk. For high-risk patients consider prophylactic measures per institutional protocol (early ambulation, hydration, consider hematology consult if prothrombotic). Educate patient to report chest pain, sudden dyspnea, or unilateral limb swelling immediately.
  6. Concomitant medications
    Continue pyridostigmine and prednisone; counsel re: timing of pyridostigmine (may cause increased secretions during infusion — evaluate symptoms). Adjustments to immunosuppression determined by neurology.
  7. Monitoring during infusion
    Vitals: BP, HR, RR, SpO₂, Temp q15 min for first hour, then q30–60 min per protocol.
    Respiratory: baseline FVC or NIF daily during hospitalization or before each infusion to detect early respiratory compromise.
    Document infusion rate changes, premeds, and any adverse events in the infusion log.
  8. Adverse event management
    Mild reaction (headache, chills, myalgia): slow infusion, give acetaminophen / antihistamine, observe.
    Moderate/severe (wheezing, hypotension, chest pain, anaphylaxis): stop infusion, follow emergency protocol (epinephrine for anaphylaxis, airway support), send labs, notify neurology and ordering prescriber.
  9. Documentation & communication
    Enter all interventions, patient education, and monitoring in the EMR. Communicate any dose modifications or adverse events to neurology and the infusion nursing team immediately.
Monitoring plan & lab schedule (example)
  Before first infusion: CBC, BMP (including SCr, BUN), baseline vitals, baseline FVC.
  During each infusion: Vitals q15–30 min; infusion log.
  Within 72 hours of each infusion day (if inpatient/outpatient center monitoring): assess for delayed adverse events (headache, rash, aseptic meningitis).
  Post-course (3–7 days): BMP to check renal function; evaluate for thrombotic events if symptomatic.
  Clinical follow-up: Neurology & pharmacy clinic at 2 weeks and 6–8 weeks to assess clinical response and need for further therapy.
(Renal monitoring and caution with certain stabilizers/sucrose-containing products recommended in guidelines). 
</example>
"""


def generate_prompt(data: Dict) -> str:
    task_prompt = f"""
Now create a similar comprehensive care plan for this patient:
Patient Information:
- Name: {data['patient_first_name']} {data['patient_last_name']}
- MRN: {data['patient_mrn']}
- Primary Diagnosis: {data['primary_diagnosis']}
- Medication: {data['medication']}
- Additional Diagnoses: {data['additional_diagnoses']}
- Medication History: {data["medication_history"]}

Patient Clinical Records: {data['patient_records']}

Generate a care plan with the same level of clinical detail, following this structure:
1. Problem list / Drug therapy problems (DTPs) - list 4-6 specific issues
2. Goals (SMART) - include primary goal, safety goal, and process goal
3. Pharmacist interventions / plan - detailed sections on dosing, monitoring, patient education, etc.
4. Monitoring plan & lab schedule - specific timing and parameters

Write in a professional clinical tone with specific details, avoid generic statements."""
    return ONE_SHOT_EXAMPLE + task_prompt