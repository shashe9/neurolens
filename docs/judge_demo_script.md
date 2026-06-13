# Neurolens: Click-by-Click Judge Demo Script

This document details the exact sequence of UI actions, credentials, and narrative focus areas to demonstrate the Neurolens platform.

---

## 🔐 1. Demo Environments & Credentials

Every account has the same password: **`secure_judge_2026`** `[VERIFIED]`

1.  **Typical Development Scenario**: `judge_typical@neurolens.demo`
2.  **Developmental Concern Scenario**: `judge_concern@neurolens.demo`
3.  **Mixed/Typical & Concern Track**: `judge_mixed@neurolens.demo`

---

## 🖱️ 2. Step-by-Step Demo Flow

### Step 1: Login
1.  Navigate to the `/login` route.
2.  Enter the email: `judge_typical@neurolens.demo` and password: `secure_judge_2026`.
3.  **Expected Outcome**: User is redirected to `/dashboard` showing `Typical Child` as the active profile.
4.  **Narrative**: Introduce Neurolens as a secure, multi-user caregiver portal.

### Step 2: Observe
1.  Navigate to the `/observations` tab.
2.  Review the preseeded observation log timeline.
3.  **Expected Outcome**: Shows chronological observations like *"Pointed directly to the apple on the kitchen table..."* or *"Said 'more milk'..."* organized by developmental domain.
4.  **Narrative**: Show how caregivers log everyday childhood observations in a timeline.

### Step 3: AI Suggestion
1.  Click **"Add Observation"** (or use the text input area).
2.  Type the Hinglish observation:
    > *"Baccha khilona lane ke liye bolta hai aur bolte waqt rote hue gusse me ungli se ishara karta hai."*
3.  Click the **"Analyze Observation with AI"** button.
4.  **Expected Outcome**: The local OIE suggestion drawer opens, displaying matching milestone cards (e.g., *'Points to ask for something'*) and domain categories.
5.  **Narrative**: Demonstrate OIE parsing localized language entries locally on host CPU without cloud costs or third-party data sharing.

### Step 4: Explainability
1.  Click the **"Why was this suggested?"** dropdown on the suggested milestone card.
2.  **Expected Outcome**: The explainability panel expands, showcasing translated words (*"rote" ➡️ "crying"*, *"gusse" ➡️ "anger"*, *"ungli" ➡️ "finger"*) and demonstrating age-band suitability comparisons.
3.  **Narrative**: Show how OIE breaks down transliterations and guidelines, establishing clear evidence tracing.

### Step 5: Human Confirmation
1.  Click the **"Link to Milestone"** button on the suggested card.
2.  **Expected Outcome**: The milestone status updates, and a green confirmed link badge is attached.
3.  **Narrative**: Emphasize the core rule: *"AI suggests, humans decide."* No automatic linking occurs.

### Step 6: Feedback Loop
1.  Locate the rating buttons (**"👍 Helpful"** and **"👎 Not Helpful"**) next to the milestone match.
2.  Click **"👎 Not Helpful"** and write: *"Good translation, but age range was slightly off."*
3.  Click submit.
4.  **Expected Outcome**: The feedback rating is stored in the database.
5.  **Narrative**: Explain how caregivers flag incorrect matches, driving local data updates.

### Step 7: Report Compilation
1.  Navigate to the `/report` tab.
2.  Click **"Compile Clinician Report"**.
3.  Review the aggregated summary table showing all linked parent observations and milestone evidence.
4.  Press `Ctrl + P` (or click Print).
5.  **Expected Outcome**: The browser print preview renders a clean, A4-aligned clinician-ready PDF, automatically hiding navigation controls and interactive buttons.
6.  **Narrative**: Illustrate the final output: a professional report compiling observations into structured evidence for the pediatrician visit.

### Step 8: Judge Portal & Demonstration Validation Metrics
1.  Navigate to the `/judge` route.
2.  Review the OIE benchmark accuracy ratings (Top-3: 96.25%).
3.  Scroll down to the validation data tables.
4.  **Expected Outcome**: Shows the N=19 Caregiver and Clinician usability and trust metric averages.
5.  **Narrative**: **CRITICAL TRANSITION**: Explicitly explain that these stats represent a **demonstration validation dataset** preseeded to illustrate the portal metrics capabilities. State honestly that no clinical studies have been conducted.

### Step 9: Responsible AI
1.  Scroll through the disclaimers rendered in red and bold on the `/judge`, `/dashboard`, `/observations`, and `/report` screens.
2.  **Expected Outcome**: Highlights text warning that Neurolens is not a medical diagnostic tool.
3.  **Narrative**: Show how Neurolens integrates safety disclaimers directly into the UI design system.
