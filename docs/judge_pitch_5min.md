# Neurolens: 5-Minute Pitch Script

**Goal**: Walk judges through the Problem ➡️ Solution ➡️ Demo ➡️ AI Evaluation ➡️ Responsible AI & Sustainability.

---

## 🎙️ Pitch Script Timeline

### 0:00 - 1:00 | Slide 1-2: The Problem & Clinical Gap
"Every parent notices when their toddler first points to a toy, looks at their face, or uses a two-word phrase. But during brief clinical visits, parents frequently suffer from recall bias, and pediatricians lack structured, longitudinal evidence to assess development. 

This communication gap leads to delayed evaluations and missed early intervention windows. Current solutions in the market try to solve this by building automated AI classifiers that generate 'autism probability percentages' directly to parents. This approach poses significant safety issues, causing false anxiety or false reassurance without clinical oversight."

### 1:00 - 2:00 | Slide 3-4: The Neurolens Solution
"Neurolens is an **evidence-first developmental observation platform**. We do not replace clinicians, and we strictly do not calculate diagnosis scores. Instead, we act as a context compiler:
1.  **Caregivers log observations** in their own words.
2.  **Our local AI (OIE)** maps observations to official CDC guidelines, supporting Hinglish terminology (e.g. *chammach*, *rote*, *ishaara*).
3.  **Caregivers review and link** these to milestones.
4.  **Neurolens compiles an immutable report** containing clear citations, preparing the clinician for the visit."

### 2:00 - 3:15 | Slide 5-7: Demo Walkthrough (Visualizing the Script)
"Let's walk through our preseeded judge demo environment. Logging in as `judge_typical@neurolens.demo` shows a typical childhood milestone track child. If we log in as `judge_concern@neurolens.demo`, we see a timeline populated with concern flags—such as repetitive play behaviors and lack of eye contact. 

When a parent logs a Hinglish observation like *'ball dikhane ke liye point kiya'*, and clicks 'Analyze', our preprocessor translates the terms and maps them directly to the CDC milestone *'Points to ask for something'*. The parent confirms the linkage. In the Reports tab, we can view a compiled clinical summary. When printed or exported as a PDF, our print stylesheets automatically strip interactive UI components, generating a clean, clinical document designed to improve parent-reported evidence organization and reduce clinician prep effort.

We also show our Judge Portal. We preseeded a demonstration validation dataset—Caregivers N=14 and Clinicians N=5—to display how Neurolens tracks metrics like usability (average 4.4/5) and caregiver trust (average 4.5/5)."

### 3:15 - 4:15 | Slide 8-9: Technical Architecture & Quantitative Evaluation
"Technically, Neurolens is built on FastAPI, Next.js, and SQLite/PostgreSQL. Privacy is a core requirement: our AI runs entirely locally on CPU, ensuring patient data is never sent to external APIs.

We evaluated our retrieval engine against an independent dataset of 160 labeled parent observations. The OIE achieves a verified **Top-3 Milestone Accuracy of 96.25%** and a **Domain Accuracy of 86.88%** against 85 milestones. Furthermore, all 55 backend unit and integration tests are fully passing."

### 4:15 - 5:00 | Slide 10: Responsible AI, Sustainability & Conclusion
"We keep human validation at the center: AI suggests, parents confirm, and clinicians diagnose. By running models locally, we operate at zero AI inference costs, making the project highly sustainable.

Neurolens transforms scattered parent memories into structured, clinican-ready evidence safely and transparently. Thank you."
