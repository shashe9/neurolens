# Neurolens: Frequently Asked Questions & Limitations

This document prepares the Neurolens team to address technical, product design, and clinical safety questions during hackathon presentations or judge evaluations.

---

## 🚫 1. What We Did Not Build (Intentional Product Omissions)

To uphold the highest responsible AI boundaries, Neurolens **intentionally did not build** the following features:
*   **No Autism Classification/Diagnosis**: The platform does not determine whether a child has autism or any other developmental delay.
*   **No Risk or Severity Scores**: Neurolens does not generate risk percentages, autism quotients, or delay severity categories.
*   **No Generative Treatment/Medical Advice**: The AI engine does not recommend developmental therapies, behavioral interventions, or diagnostic pathways.
*   **No Automated Referrals**: The tool does not automate pediatrician referrals or prioritize clinical intake priority queues.
*   **No Medical Decision Making**: All diagnostic authority remains entirely in the hands of pediatricians.
*   **Wording Status**: `[VERIFIED]` (Aligned with [responsible_ai.md](file:///d:/Desktop/New_Autism/docs/responsible_ai.md)).

---

## ❓ 2. Core Architecture & AI Questions

### Q1: Why does Neurolens NOT diagnose autism or calculate ASD risk scores?
*   **Answer**: Diagnosing neurodevelopmental delays requires professional clinical judgment, observation across settings, and developmental interviews. Creating a black-box machine learning classifier that outputs "ASD Risk: High" poses massive clinical risks, including false reassurance or unnecessary anxiety. Instead, Neurolens is designed to help parents record everyday behaviors and map them to objective CDC milestones to prepare for pediatrician discussions.
*   **Wording Status**: `[VERIFIED]`.

### Q2: Why are you using a local SentenceTransformer model instead of cloud APIs like OpenAI or Gemini?
*   **Answer**: Running the retrieval engine locally brings three massive benefits:
    1.  **Privacy**: Medical-adjacent text inputs are never sent to external servers, protecting patient confidentiality.
    2.  **Zero Cost**: Eliminates API key dependencies and usage costs, making the system highly sustainable.
    3.  **Local Execution**: The system can run entirely offline or in low-resource environments (e.g. on a clinic's local server).
*   **Wording Status**: `[VERIFIED]`.

### Q3: How is OIE explainability handled?
*   **Answer**: When a parent writes an observation, Neurolens highlights exactly *why* a milestone was suggested. It details the domain category, indicates whether the child's age aligns with the guideline's age-range bounds, and shows translation matches for Hinglish terms.
*   **Wording Status**: `[VERIFIED]`.

### Q4: How does Neurolens handle multilingual observations (Hinglish)?
*   **Answer**: Neurolens integrates a local transliteration preprocessor. Words like *"ungli"* are mapped to *"finger"*, *"rote"* to *"cry"*, and *"chammach"* to *"spoon"* before generating vectors. This ensures that the English-centric embedding model successfully indexes Hinglish queries.
*   **Wording Status**: `[VERIFIED]`.

### Q5: How is user data protected?
*   **Answer**: All parent profiles are protected by hashed credentials (using bcrypt). Relational schemas enforce child profile boundary isolation using parent sessions, preventing cross-tenant URL access.
*   **Wording Status**: `[VERIFIED]`.

### Q6: What happens if OIE returns an incorrect milestone suggestion?
*   **Answer**: Neurolens uses a **human-in-the-loop** pattern. Caregivers must explicitly approve suggestions before they link as evidence. Caregivers can also log feedback (thumbs-down rating + comment) to flag incorrect suggestions.
*   **Wording Status**: `[VERIFIED]`.

---

## ⚠️ 3. Platform Limitations Section

### Q7: What does Neurolens NOT do?
*   **Answer**: Neurolens does **NOT** provide clinical advice, diagnose conditions, recommend therapy, score developmental delay ratios, or determine referral priorities.
*   **Wording Status**: `[VERIFIED]`.

### Q8: What populations has Neurolens NOT been validated on?
*   **Answer**: The database milestones are based on English and Hinglish developmental guidelines (CDC Act Early). The system has **not** been validated for other dialects, regional languages (e.g., Tamil, Telugu, Hindi-script), or non-typical developmental disorders other than standard early milestone trajectories.
*   **Wording Status**: `[VERIFIED]`.

### Q9: What happens if a standard CDC milestone is incorrect or out of date?
*   **Answer**: The underlying milestones database is stored in a clean, isolated database table. Clinicians or administrators can update or append guidelines through standard migration scripts or admin endpoints without modifying OIE retrieval code.
*   **Wording Status**: `[VERIFIED]`.

### Q10: Can clinicians rely solely on the generated Neurolens report?
*   **Answer**: No. The compiled report is designed to act as an intake preparation aid. It structures caregiver observations so pediatricians can review raw evidence quickly, but it is not a clinical assessment tool.
*   **Wording Status**: `[VERIFIED]`.

### Q11: Were the Caregiver (N=14) and Clinician (N=5) metrics derived from a real validation study?
*   **Answer**: No. These records represent a **demonstration validation dataset** preseeded to illustrate the interface capabilities of the Judge Dashboard. Neurolens has **not** been piloted in a live user test.
*   **Wording Status**: `[VERIFIED]`.

*(For additional information, please review the complete disclaimers under [docs/known_limitations.md](file:///d:/Desktop/New_Autism/docs/known_limitations.md)).*
