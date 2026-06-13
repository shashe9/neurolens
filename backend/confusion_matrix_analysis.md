# Domain-Level Confusion Matrix Analysis

This document provides a detailed breakdown of the domain-level confusion pairs identified during the live evaluation of the Neurolens Observation Intelligence Engine (OIE).

The evaluation dataset consists of **160 samples** distributed as follows:
*   **Communication**: 40 samples
*   **Social Emotional**: 30 samples
*   **Cognitive**: 30 samples
*   **Gross Motor**: 30 samples
*   **Fine Motor**: 30 samples

## Confusion Matrix Summary

| Actual \ Predicted | Communication | Social Emotional | Cognitive | Gross Motor | Fine Motor | Total Samples | Domain Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Communication** | 28 | 5 | 3 | 0 | 4 | 40 | **70.00%** |
| **Social Emotional** | 7 | 17 | 2 | 1 | 3 | 30 | **56.67%** |
| **Cognitive** | 3 | 2 | 24 | 0 | 1 | 30 | **80.00%** |
| **Gross Motor** | 0 | 0 | 4 | 26 | 0 | 30 | **86.67%** |
| **Fine Motor** | 1 | 0 | 3 | 0 | 26 | 30 | **86.67%** |

---

## 1. Dominant Confusion Pairs

### Pair A: Social Emotional vs. Communication (Mutual Confusion)
*   **Quantification**:
    *   **7 out of 30** Ground Truth Social Emotional samples (23.33%) were misclassified as Communication.
    *   **5 out of 40** Ground Truth Communication samples (12.50%) were misclassified as Social Emotional.
    *   This represents **12 out of 39 total misclassifications (30.77%)**, making it the single largest inter-domain confusion vector.
*   **Likely Causes**:
    *   **Shared Interactive Context**: Social Emotional observations often describe verbal actions (e.g. talking, greeting, playing together), which contain high semantic overlap with Communication milestones.
    *   **Keyword Collisions in English**: Sentences like *"spoke to the visitor"* or *"played the naming game"* trigger both speech (Communication) and interactive play (Social Emotional) tokens.
    *   **Hinglish Phrase Ambiguity**: Transliterated terms like *"bina baat kiye"* (without talking) or *"bina bole"* (without speaking) contain negation, which multilingual embedding models struggle to interpret correctly, thereby matching communication keywords.
*   **Failure Case References**:
    *   **Failure Case 5**: *"She touched her nose and eyes when we played the naming game."* (Actual: Communication $\rightarrow$ Predicted: Social Emotional due to "played ... game").
    *   **Failure Case 9**: *"She spoke to the visitor saying: 'I want to play block game'."* (Actual: Communication $\rightarrow$ Predicted: Social Emotional due to "play block game" overriding sentence length markers).
    *   **Failure Case 16**: *"Sandbox me dusre bacche ke paas khel raha tha bina baat kiye."* (Actual: Social Emotional $\rightarrow$ Predicted: Communication due to "bina baat kiye" triggering speech detection).
    *   **Failure Case 18**: *"Dada ko dekhkar unke paas bhag gaya bina bole."* (Actual: Social Emotional $\rightarrow$ Predicted: Communication due to "bina bole").

### Pair B: Motor Domains (Gross/Fine) vs. Cognitive
*   **Quantification**:
    *   **4 out of 30** Gross Motor samples (13.33%) were misclassified as Cognitive.
    *   **3 out of 30** Fine Motor samples (10.00%) were misclassified as Cognitive.
    *   This represents **7 out of 39 total misclassifications (17.95%)**.
*   **Likely Causes**:
    *   **Verb-Object Associations**: Physical milestones (climbing stairs, opening lids) share heavy vocabulary overlaps with Cognitive milestones (hiding objects, exploring objects, sorting shapes). The semantic embedding focuses on the action target (e.g., "lid", "stairs", "socks") rather than the motor execution itself.
    *   **Hinglish Transliteration Degradation**: When Hindi words like *"seedhiyon"* (stairs), *"daudta"* (runs), or *"socks"* are used in Hinglish, the multilingual model fails to align the actions, resulting in default Cognitive categorizations like *"explores objects"* or *"matching same and different"*.
*   **Failure Case References**:
    *   **Failure Case 32**: *"She opened the box lid to find the toy inside."* (Actual: Fine Motor $\rightarrow$ Predicted: Cognitive. The cognitive search "find the toy" overrides the fine motor action of "opened the box lid").
    *   **Failure Case 30**: *"Adults ki tarah seedhiyon par bari-bari se pair rakh kar chadha."* (Actual: Gross Motor $\rightarrow$ Predicted: Cognitive. Fails to parse "seedhiyon" and "chadha", mapping to Cognitive drawing instead).
    *   **Failure Case 26**: *"Ek jaise socks ko laundry basket me sath rakha."* (Actual: Cognitive $\rightarrow$ Predicted: Fine Motor. Fails to map sorting, matching with "jar lids" instead).

### Pair C: Communication vs. Fine Motor (Hinglish Noise)
*   **Quantification**:
    *   **4 out of 40** Communication samples (10.00%) were misclassified as Fine Motor.
    *   **1 out of 30** Fine Motor samples (3.33%) was misclassified as Communication.
    *   This represents **5 out of 39 total misclassifications (12.82%)**.
*   **Likely Causes**:
    *   **Vocabulary Mismatch**: Fine Motor tasks like pincer grasp and Communication gestures (pointing, waving) both involve hands/fingers. In English, these are separate. In Hinglish, words like *"ungli"* (finger) or *"anguthe"* (thumb) are not mapped properly in the current hardcoded glossary, leading to wild semantic associations.
*   **Failure Case References**:
    *   **Failure Case 3**: *"Paas aao bolne par turant chal kar aa gaya."* (Actual: Communication $\rightarrow$ Predicted: Fine Motor due to multilingual embedding alignment failure).
    *   **Failure Case 31**: *"Ungli aur anguthe se chote daane utha leta hai."* (Actual: Fine Motor $\rightarrow$ Predicted: Communication due to "Ungli" mapping to gestures).

---

## 2. Quantitative Summary of Inter-Domain Confusion

*   **Overall Domain Accuracy**: **75.62%** (121 out of 160 correct)
*   **Total Domain Misclassifications**: **39 cases** (24.38%)
    *   *Communication vs Social Emotional*: 12 cases (30.77% of all misclassifications)
    *   *Gross/Fine Motor vs Cognitive*: 7 cases (17.95% of all misclassifications)
    *   *Communication vs Fine Motor*: 5 cases (12.82% of all misclassifications)
    *   *Other minor misclassifications*: 15 cases (38.46% of all misclassifications)
