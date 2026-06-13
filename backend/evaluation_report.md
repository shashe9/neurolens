# Neurolens Observation Intelligence Engine (OIE) Evaluation Report

This report presents the live evaluation and benchmarking of the Neurolens retrieval engine, executed on **2026-06-13 13:01:24**.

## 1. Overall Benchmarking Metrics

The evaluation was performed against the complete gold-standard benchmark dataset comprising **160 labeled parent observations** representing realistic inputs across all 5 active developmental domains.

| Metric | Result | Target / Standard | Description |
| :--- | :---: | :---: | :--- |
| **Top-1 Milestone Accuracy** | **80.62%** | > 65.0% | Ground-truth milestone matches the absolute top recommended suggestion. |
| **Top-3 Milestone Accuracy** | **96.25%** | > 85.0% | Ground-truth milestone is present within the top 3 recommendations. |
| **Domain Classification Accuracy** | **86.88%** | > 90.0% | The domain of the top recommendation matches the ground-truth domain. |

---

## 2. Domain-Level Confusion Matrix

The following matrix shows the counts of ground-truth domains (rows) versus domain classifications predicted by the top retrieval result (columns).

| Actual \ Predicted | Communication | Social Emotional | Cognitive | Gross Motor | Fine Motor |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Communication** | 30 | 3 | 1 | 3 | 3 |
| **Social Emotional** | 3 | 27 | 0 | 0 | 0 |
| **Cognitive** | 4 | 2 | 23 | 1 | 0 |
| **Gross Motor** | 0 | 0 | 0 | 30 | 0 |
| **Fine Motor** | 0 | 0 | 1 | 0 | 29 |

---

## 3. Representative Success Cases

Below are three examples of observations where the SentenceTransformer model successfully identified the correct milestone as the top suggestion at Rank 1.

### Success Case 1
*   **Observation Text:** *"She looked directly at her dog when I asked 'where is the dog?'."*
*   **Child Age:** 15 months
*   **Domain:** Communication
*   **Matched Milestone:** **Looks at familiar object when named**
*   **Cosine Similarity Score:** 0.2390

### Success Case 2
*   **Observation Text:** *"He handed me his toy cup when I held out my hand and requested it."*
*   **Child Age:** 15 months
*   **Domain:** Communication
*   **Matched Milestone:** **Follows simple one-step verbal directions**
*   **Cosine Similarity Score:** 0.3110

### Success Case 3
*   **Observation Text:** *"She says three single words clearly: ball, cup, and bye-bye."*
*   **Child Age:** 15 months
*   **Domain:** Communication
*   **Matched Milestone:** **Uses several single words besides mama or dada**
*   **Cosine Similarity Score:** 0.4650

---

## 4. Analysis of Retrieval Failure Cases

Out of 160 test samples, there were **6 failure cases** where the correct ground-truth milestone was NOT returned within the top 3 recommendations. Below is the detailed analysis of all failure cases.

### Failure Case 1
*   **Observation Text:** *"Chammach uthao aur plate me rakho bola to usne dono kaam kiye."*
*   **Child Age:** 30 months
*   **Ground-Truth Domain:** Communication
*   **Expected Milestone:** **Follows instructions with two related steps**
*   **Retrieved Top 3 Suggestions:**
    1. "Uses spoon to feed self partially" (Fine Motor, score: 0.2680)
    2. "Greets familiar people spontaneously" (Social Emotional, score: 0.2560)
    3. "Says sentences of 3 or 4 words" (Communication, score: 0.2300)

### Failure Case 2
*   **Observation Text:** *"Kitab me apple aur car ko dekh kar bolta hai."*
*   **Child Age:** 30 months
*   **Ground-Truth Domain:** Communication
*   **Expected Milestone:** **Identifies common objects in books**
*   **Retrieved Top 3 Suggestions:**
    1. "Greets familiar people spontaneously" (Social Emotional, score: 0.4020)
    2. "Says sentences of 3 or 4 words" (Communication, score: 0.3780)
    3. "Says two-word descriptive phrases" (Communication, score: 0.2820)

### Failure Case 3
*   **Observation Text:** *"She explained that she played with Eli on the slides in the park."*
*   **Child Age:** 42 months
*   **Ground-Truth Domain:** Communication
*   **Expected Milestone:** **Recounts a simple story or event**
*   **Retrieved Top 3 Suggestions:**
    1. "Plays cooperatively taking turns" (Social Emotional, score: 0.2700)
    2. "Acts out complex pretend scenarios" (Social Emotional, score: 0.2470)
    3. "Draws simple person with 2 to 4 parts" (Cognitive, score: 0.2060)

### Failure Case 4
*   **Observation Text:** *"Dabbe ko gadi bana kar chala raha tha."*
*   **Child Age:** 30 months
*   **Ground-Truth Domain:** Cognitive
*   **Expected Milestone:** **Engages in simple pretend play scenarios**
*   **Retrieved Top 3 Suggestions:**
    1. "Draws simple circle closed loop" (Cognitive, score: 0.1810)
    2. "Pedals a tricycle independently" (Gross Motor, score: 0.1810)
    3. "Greets familiar people spontaneously" (Social Emotional, score: 0.1710)

### Failure Case 5
*   **Observation Text:** *"Ek jaise socks ko laundry basket me sath rakha."*
*   **Child Age:** 30 months
*   **Ground-Truth Domain:** Cognitive
*   **Expected Milestone:** **Matches identical items or colors**
*   **Retrieved Top 3 Suggestions:**
    1. "Balances on one foot briefly for 2s" (Gross Motor, score: 0.3240)
    2. "Follows instructions with two related steps" (Communication, score: 0.3190)
    3. "Screws and unscrews jar lids" (Fine Motor, score: 0.3110)

### Failure Case 6
*   **Observation Text:** *"Poocha ki inme se kaunsa block sabse alag hai to bataya."*
*   **Child Age:** 42 months
*   **Ground-Truth Domain:** Cognitive
*   **Expected Milestone:** **Correctly matches same and different items**
*   **Retrieved Top 3 Suggestions:**
    1. "Uses sentences of 4 or 5 words" (Communication, score: 0.2470)
    2. "Plays cooperatively taking turns" (Social Emotional, score: 0.2360)
    3. "Tries to comfort distressed family or friends" (Social Emotional, score: 0.2170)

