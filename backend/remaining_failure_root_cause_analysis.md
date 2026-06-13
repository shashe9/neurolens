# Remaining Failure Root-Cause Analysis (Phase 5A.2B)

This document contains a detailed root-cause audit of the remaining **12 retrieval failure cases** in the Neurolens Observation Intelligence Engine (OIE) following the milestone semantic enrichment phase.

---

## Failure Analysis Summary

| Case # | Observation Text | Expected Milestone | Predicted Milestone | Failure Classification | Fixed Without Logic Change? |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **1** | "He picked up the socks and put them in the laundry bin when asked." | Follows instructions with two related steps | Screws and unscrews jar lids | Missing milestone example | **Yes** (Add socks/laundry bin example) |
| **2** | "Kitab me apple aur car ko dekh kar bolta hai." | Identifies common objects in books | Greets familiar people spontaneously | Genuine domain confusion | **Yes** (Map "bolta" to "says" or add "says" to milestone) |
| **3** | "She explained that she played with Eli on the slides in the park." | Recounts a simple story or event | Plays cooperatively taking turns | Genuine domain confusion | **No** (Activity words dominate; needs domain boost) |
| **4** | "Bina kisi atkan ke bolta hai: 'hume park chalna chahiye'." | Speaks clearly in full sentences | Swings and climbs on play structures | Missing glossary term | **Yes** (Translate "bina" and "atkan") |
| **5** | "Mera chehra dekhta hai jab hum chidiya ki taraf dekhte hain." | Looks at caregiver for joint attention | Uses several single words besides mama or dada | Missing glossary term | **Yes** (Translate "dekhta" and "dekhte") |
| **6** | "Mummy ki taraf dekha jab koi anjaan ghar aaya." | Looks at parent face for reaction | Uses several single words besides mama or dada | Missing glossary term | **Yes** (Translate "dekha", "anjaan", "aaya") |
| **7** | "Usko pata hai ki kahani ka dragon sach me nahi hota." | Distinguishes real vs make-believe accurately | Speaks clearly in full sentences | Missing glossary term | **Yes** (Translate "pata", "kahani", "sach", "nahi", "hota") |
| **8** | "She put the toy receiver to her ear pretending to talk." | Tries to use items for their intended purpose | Plays simple interactive games | Ranking issue | **Yes** (Boost "receiver" and "talk" keywords) |
| **9** | "Round rings ko round slot me daal kar match kiya." | Sorts objects by shapes or colors | Plays simple interactive games | Missing glossary term | **Yes** (Translate "daal", "kiya") |
| **10** | "Dabbe ko gadi bana kar chala raha tha." | Engages in simple pretend play scenarios | Says sentences of 3 or 4 words | Ranking issue | **Yes** (Contextualize "chala" translation) |
| **11** | "Ek jaise socks ko laundry basket me sath rakha." | Matches identical items or colors | Balances on one foot briefly for 2s | Missing glossary term | **Yes** (Translate "jaise", "sath", "rakha") |
| **12** | "Poocha ki inme se kaunsa block sabse alag hai to bataya." | Correctly matches same and different items | Hops on one foot a few times | Missing glossary term | **Yes** (Translate "alag", "bataya") |

---

## Detailed Case Audits

### Case 1: "He picked up the socks and put them in the laundry bin when asked."
*   **GT Domain / Milestone**: Communication / *Follows instructions with two related steps*
*   **Predicted Domain / Milestone**: Fine Motor / *Screws and unscrews jar lids*
*   **Root Cause**: The two-step action of picking up socks and putting them in a laundry bin is not matched. The generic verbs "picked up" and "put" map to Fine Motor tasks, and the milestone lacks examples for socks and laundry bins.
*   **Classification**: **Missing milestone example**
*   **Fixable without logic change**: **Yes**. Adding "laundry bin" and "socks" to the milestone examples will pull the semantic embedding closer.

### Case 2: "Kitab me apple aur car ko dekh kar bolta hai."
*   **GT Domain / Milestone**: Communication / *Identifies common objects in books*
*   **Predicted Domain / Milestone**: Social Emotional / *Greets familiar people spontaneously*
*   **Root Cause**: The word "bolta" translates to "speaks". The presence of the strong communication verb "speaks" steers the embedding model towards conversational/greeting speech milestones, rather than pointing/naming items in books.
*   **Classification**: **Genuine domain confusion**
*   **Fixable without logic change**: **Yes**. We can translate "bolta" to "says/speaks" or add "says" to the milestone description.

### Case 3: "She explained that she played with Eli on the slides in the park."
*   **GT Domain / Milestone**: Communication / *Recounts a simple story or event*
*   **Predicted Domain / Milestone**: Social Emotional / *Plays cooperatively taking turns*
*   **Root Cause**: The physical activity terms ("played", "slides", "park") overwhelm the conversational context ("explained"), matching it to playground social play instead of linguistic recounting.
*   **Classification**: **Genuine domain confusion**
*   **Fixable without logic change**: **No**. The activity vocabulary is inherently closer to the Social Emotional domain; this requires retrieval logic updates like Soft Domain Boosting.

### Case 4: "Bina kisi atkan ke bolta hai: 'hume park chalna chahiye'."
*   **GT Domain / Milestone**: Communication / *Speaks clearly in full sentences*
*   **Predicted Domain / Milestone**: Gross Motor / *Swings and climbs on play structures*
*   **Root Cause**: "bolta" $\rightarrow$ "speaks" and "chalna" $\rightarrow$ "walking" are translated, but "bina" (without) and "atkan" (stuttering) are not in the glossary. The model matches "speaks park walking" to playground movement, missing the speech-clarity context entirely.
*   **Classification**: **Missing glossary term**
*   **Fixable without logic change**: **Yes**. Adding "bina" $\rightarrow$ "without" and "atkan" $\rightarrow$ "stuttering" to the transliteration glossary.

### Case 5: "Mera chehra dekhta hai jab hum chidiya ki taraf dekhte hain."
*   **GT Domain / Milestone**: Social Emotional / *Looks at caregiver for joint attention*
*   **Predicted Domain / Milestone**: Communication / *Uses several single words besides mama or dada*
*   **Root Cause**: The critical looking verbs "dekhta" (looks) and "dekhte" (look) are missing from the glossary, leaving the sentence meaning fragmented.
*   **Classification**: **Missing glossary term**
*   **Fixable without logic change**: **Yes**. Adding "dekhta" $\rightarrow$ "looks" and "dekhte" $\rightarrow$ "look".

### Case 6: "Mummy ki taraf dekha jab koi anjaan ghar aaya."
*   **GT Domain / Milestone**: Social Emotional / *Looks at parent face for reaction*
*   **Predicted Domain / Milestone**: Communication / *Uses several single words besides mama or dada*
*   **Root Cause**: The terms "dekha" (looked), "anjaan" (stranger), and "aaya" (came) are missing from the glossary, disabling the core scenario meaning (looking at parent when a stranger comes).
*   **Classification**: **Missing glossary term**
*   **Fixable without logic change**: **Yes**. Adding "dekha" $\rightarrow$ "looked", "anjaan" $\rightarrow$ "stranger", and "aaya" $\rightarrow$ "came".

### Case 7: "Usko pata hai ki kahani ka dragon sach me nahi hota."
*   **GT Domain / Milestone**: Social Emotional / *Distinguishes real vs make-believe accurately*
*   **Predicted Domain / Milestone**: Communication / *Speaks clearly in full sentences*
*   **Root Cause**: The words "pata" (knows), "kahani" (story), "sach" (real), "nahi" (not), and "hota" (exists/happen) are untranslated. Only "dragon" is recognized, leading to generic communication speech matching.
*   **Classification**: **Missing glossary term**
*   **Fixable without logic change**: **Yes**. Add the missing translations to the glossary.

### Case 8: "She put the toy receiver to her ear pretending to talk."
*   **GT Domain / Milestone**: Cognitive / *Tries to use items for their intended purpose*
*   **Predicted Domain / Milestone**: Social Emotional / *Plays simple interactive games*
*   **Root Cause**: While we enriched the milestone description, "pretending to talk" and "receiver" still yield a slightly higher score for interactive play due to the embedding model's innate weights.
*   **Classification**: **Ranking issue**
*   **Fixable without logic change**: **Yes**. Explicitly add "receiver" and "talk" as keyword tokens to the milestone metadata to boost the score.

### Case 9: "Round rings ko round slot me daal kar match kiya."
*   **GT Domain / Milestone**: Cognitive / *Sorts objects by shapes or colors*
*   **Predicted Domain / Milestone**: Social Emotional / *Plays simple interactive games*
*   **Root Cause**: The action word "daal" (put/insert) and "kiya" (did) are missing from the glossary, leaving the sentence context incomplete.
*   **Classification**: **Missing glossary term**
*   **Fixable without logic change**: **Yes**. Add "daal" $\rightarrow$ "put" and "kiya" $\rightarrow$ "did" to the glossary.

### Case 10: "Dabbe ko gadi bana kar chala raha tha."
*   **GT Domain / Milestone**: Cognitive / *Engages in simple pretend play scenarios*
*   **Predicted Domain / Milestone**: Communication / *Says sentences of 3 or 4 words*
*   **Root Cause**: "bana" (make) is untranslated, and "chala" translates strictly to "walked", which is incorrect in this context (where it means "driving/running").
*   **Classification**: **Ranking issue** / **Missing glossary term**
*   **Fixable without logic change**: **Yes**. Update "chala" to "walked/drove" or adjust pretend play to include "chala raha" / "driving".

### Case 11: "Ek jaise socks ko laundry basket me sath rakha."
*   **GT Domain / Milestone**: Cognitive / *Matches identical items or colors*
*   **Predicted Domain / Milestone**: Gross Motor / *Balances on one foot briefly for 2s*
*   **Root Cause**: The sorting words "jaise" (like/similar), "sath" (together), and "rakha" (kept) are not in the glossary. Only "socks" and "basket" are read, leading to random motor matching.
*   **Classification**: **Missing glossary term**
*   **Fixable without logic change**: **Yes**. Translate "jaise" $\rightarrow$ "similar", "sath" $\rightarrow$ "together", and "rakha" $\rightarrow$ "kept".

### Case 12: "Poocha ki inme se kaunsa block sabse alag hai to bataya."
*   **GT Domain / Milestone**: Cognitive / *Correctly matches same and different items*
*   **Predicted Domain / Milestone**: Gross Motor / *Hops on one foot a few times*
*   **Root Cause**: The key comparative word "alag" (different) and action "bataya" (pointed/told) are not translated, losing the "different item" concept.
*   **Classification**: **Missing glossary term**
*   **Fixable without logic change**: **Yes**. Translate "alag" $\rightarrow$ "different" and "bataya" $\rightarrow$ "pointed/told".
