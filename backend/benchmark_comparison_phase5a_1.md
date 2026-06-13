# Benchmark Comparison Report (Phase 5A.1)

This report details the performance impact of the Hinglish Retrieval Improvement implemented in Phase 5A.1. The improvements focused on resolving the **Hinglish Vocabulary Gap** by introducing safe regex tokenization and expanding the transliteration glossary.

---

## 1. Metrics Comparison

Below is the comparison of evaluation metrics before and after the improvements, tested against the complete **160 gold-standard labeled observations**.

| Metric | Before (OIE v1) | After (OIE v1.1) | Delta (Absolute) | Target | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Top-1 Milestone Accuracy** | 68.12% | **73.12%** | **+5.00%** | > 65.0% | **Passed** |
| **Top-3 Milestone Accuracy** | 80.00% | **88.12%** | **+8.12%** | > 85.0% | **Passed (Target Exceeded)** |
| **Domain Classification Accuracy** | 75.62% | **80.62%** | **+5.00%** | > 90.0% | **Improved** |

---

## 2. Analysis of Fixed Cases

The improvements successfully resolved **15 previous failure cases** by translating Roman-script Hinglish terms to English and ensuring punctuation did not break word matches:

1.  **Body Parts Mapping**: Observations like *"Aankh aur kaan poochne par..."* (Failure Case 6) were resolved because **"aankh"** and **"kaan"** now map to **"eye"** and **"ear"**, triggering the *"Points to at least two body parts"* milestone.
2.  **Affection and Social Play**: *"Mummy ko gale lagata hai..."* (Failure Case 12) was resolved by mapping **"mummy"** to **"mother"** and **"gale"** to **"hug"**, identifying *"Shows affection to familiar people"*. Similar fixes occurred for sandbox parallel play (using **"bacche"**, **"khel"**, **"baat"**) and peer imitation (using **"block stack"**, **"bacche"**).
3.  **Physical Motor Activities**: Gross/Fine motor observations such as independent walking (*"chal"* $\rightarrow$ *"walk"*), running (*"daudta"* $\rightarrow$ *"running"*), and hopping (*"kood"* $\rightarrow$ *"hop"*) now map correctly to their respective motor milestones.
4.  **Pincer Grasp**: *"Ungli aur anguthe se chote daane..."* was resolved by translating **"ungli"** $\rightarrow$ *"finger"* and **"anguthe"** $\rightarrow$ *"thumb"*, matching the neat pincer grasp milestone.

---

## 3. Remaining Failures & Observations

Out of 160 samples, **19 failure cases** remain.

### New Edge Cases Introduced by Preprocessing Changes
*   **Case A (Semantic Shift from Translation)**: *"Kitab me apple aur car ko dekh kar bolta hai."* previously passed, but now fails because translating **"bolta"** to **"speaks"** shifts the semantic focus of the SentenceTransformer to speech length milestones (*"Says sentences of 3 or 4 words"*), dropping the correct book-reading milestone out of the Top-3.
*   **Case B (Punctuation Removal and Decay Edge)**: *"He went to his room, got his bag, and waited at the gate when told."* previously passed, but the removal of commas and periods via `re.findall(r"\b\w+\b")` shifted the embedding vector just enough to drop the correct milestone out of the Top-3. This was already a highly decayed edge-case score due to the child's age (60 months) relative to the milestone's age band.

### Persistent Failure Categories

| Category | Count | Status / Notes |
| :--- | :---: | :--- |
| **Hinglish Vocabulary Gap** | 13 | Decreased from 26. These remaining cases require more specific/complex verbs (e.g., *"dekhne"*, *"tootne"*, *"shor"*) or noun translations that are not yet covered. |
| **Communication vs. Social Emotional Confusion** | 3 | Persists. English-language interactions containing both verbal actions and play contexts (e.g., *"played the naming game"*, *"spoke to the visitor... play block game"*) continue to confuse the two domains. |
| **Generic Keyword Collision** | 2 | Persists. Non-specific descriptors (e.g., *"toy receiver"* or *"pressed piano keys"*) map to general play/communication rather than functional use or mechanical toys. |
| **Fine Motor vs. Cognitive Confusion** | 1 | Persists. Double-intent sentences (*"opened the box lid to find the toy inside"*) are dominated by the cognitive search intent over the fine motor lid-opening action. |

### Conclusion on Domain Confusion
Mutual confusion between **Communication** and **Social Emotional** domains persists for English observations and complex Hinglish queries because it is an inherent property of the semantic model's embedding weights (e.g., aligning social play words with communication gestures). Resolving this will require the proposed **Soft Domain Boosting** recommendation rather than glossary expansion.
