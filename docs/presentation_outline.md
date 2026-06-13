# Neurolens Pitch Deck Outline

This outline details the slide structure, visual highlights, and core talking points for the Neurolens hackathon presentation deck.

---

## 🛝 Slide-by-Slide Outline

### Slide 1: Title & Value Proposition
*   **Slide Title**: Neurolens: Evidence-First Developmental Observation Platform
*   **Visuals**: Neurolens Logo, tagline: *"Transforming parent observations into clinician-ready evidence safely and transparently."*
*   **Talking Points**: Introduce the team, define the product as an intake preparation aid, and emphasize the clinical pivot away from black-box ASD classification.

### Slide 2: The Developmental Screening Gap
*   **Slide Title**: The intake bottle-neck in pediatric screening
*   **Visuals**: Process map showing long diagnostic waitlists, brief 15-minute clinical visits, and a timeline of parent recall errors.
*   **Talking Points**: Highlight parent recall bias and pediatrician time constraints that delay developmental delay interventions.

### Slide 3: The Risk of AI Diagnostics
*   **Slide Title**: Why automated ASD screening models fail in the real world
*   **Visuals**: Illustration of a black-box model outputting "90% Autism Probability" alongside lists of trust risks (anxiety, false reassurance).
*   **Talking Points**: Argue against automated, diagnostic AI classifiers. Present the Neurolens philosophy: *"AI suggests, humans decide."*

### Slide 4: How Neurolens Works
*   **Slide Title**: The Caregiver-Clinician Evidence Bridge
*   **Visuals**: Flow diagram: Observation Entry ➡️ Local OIE Translation/Mapping ➡️ Parent Confirmation ➡️ Immutable Report Compilation.
*   **Talking Points**: Walk through the user workflow, detailing how parent logs translate to objective CDC milestones.

### Slide 5: The Observation Intelligence Engine (OIE)
*   **Slide Title**: Local, Privacy-Preserving AI
*   **Visuals**: OIE pipeline architecture. Mention the embedding model: `paraphrase-multilingual-MiniLM-L12-v2` and Hinglish preprocessing dictionary.
*   **Talking Points**: Explain the local SentenceTransformer setup that ensures absolute privacy and zero cloud API costs.

### Slide 6: Quantitative AI Evaluation & Benchmarks
*   **Slide Title**: Measured Performance & Testing Rigor
*   **Visuals**: Matrix of scores (Top-3 Accuracy: **96.25%**, Domain Accuracy: **86.88%**). Mention the N=160 labeled evaluation samples and 55/55 passing unit tests.
*   **Talking Points**: Share baseline benchmarks, proving that our OIE engine delivers highly accurate results without server dependencies.

### Slide 7: Demonstration User Trust Metrics
*   **Slide Title**: Verified Caregiver & Clinician Validation
*   **Visuals**: Role-split grids (Caregivers N=14, Clinicians N=5) showing average usability (4.4/5) and trust (4.5/5) metrics from our demonstration validation dataset.
*   **Talking Points**: Walk through feedback analytics, showing high usability scores and clinician endorsement of report utility.

### Slide 8: Responsible AI & Data Security
*   **Slide Title**: Safeguards and Operational Integrity
*   **Visuals**: List of compliance banners, JWT auth barriers, and database isolation schemas.
*   **Talking Points**: Discuss secure parent-child boundary mapping and explain the immutability of compiled reports.

### Slide 9: Sustainability & Scaling Path
*   **Slide Title**: Projected Growth & Open-Source Evolution
*   **Visuals**: Estimated cost comparison table (Local clinic servers: $0/month vs Cloud Fargate hosting: ~$50/month). Highlight the ONNX client-side scaling roadmap.
*   **Talking Points**: Show how the platform remains highly cost-effective and outline clinical pilot stages.

### Slide 10: Conclusion & Core Message
*   **Slide Title**: Empowering Families, Assisting Clinicians
*   **Visuals**: Brief mockup of the printable PDF report.
*   **Talking Points**: Conclude with a strong pitch: Neurolens bridges the gap between home and clinic safely, responsibly, and immediately.
