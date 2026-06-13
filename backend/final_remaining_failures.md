# Final Remaining Failures (OIE v1.3)

This document details the final **6 remaining failure cases** out of the 160 benchmark test samples, following the completion of Phase 5A.3. 

---

## Remaining Failures Audit Table

| Case # | Observation Text | Expected Milestone | Predicted Milestone | Failure Category | Root Cause |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **1** | "Chammach uthao aur plate me rakho bola to usne dono kaam kiye." | Follows instructions with two related steps | Uses spoon to feed self partially | Glossary | "uthao" (pick up), "rakho" (place), "dono" (both), "kaam" (work), and "kiye" (did) are missing from the glossary. The sentence is parsed as "spoon ... plate ... said", matching spoon self-feeding. |
| **2** | "Kitab me apple aur car ko dekh kar bolta hai." | Identifies common objects in books | Greets familiar people spontaneously | Domain Confusion | "bolta" translates to "speaks". The strong verb "speaks" steers the embedding towards conversational speech milestones rather than book identification. |
| **3** | "She explained that she played with Eli on the slides in the park." | Recounts a simple story or event | Plays cooperatively taking turns | Domain Confusion | The playground action verbs ("played", "slides", "park") dominate over the communication verb ("explained"), causing a false match with social turn-taking. |
| **4** | "Dabbe ko gadi bana kar chala raha tha." | Engages in simple pretend play scenarios | Draws simple circle closed loop | Glossary | "chala" translates to "walked" (which is incorrect for driving a box-car in this context). "ko", "raha", and "tha" are also missing from the glossary, degrading the sentence representation. |
| **5** | "Ek jaise socks ko laundry basket me sath rakha." | Matches identical items or colors | Balances on one foot briefly for 2s | Ranking | Adding laundry basket examples to the two-step instructions milestone causes this sock-sorting observation to align with instruction-following and motor tasks rather than matching colors. |
| **6** | "Poocha ki inme se kaunsa block sabse alag hai to bataya." | Correctly matches same and different items | Uses sentences of 4 or 5 words | Glossary | "inme", "se", "kaunsa" (which), "sabse" (most), and "to" are missing. The fragmented translation ("asked ... block ... different ... told") matches Communication speech lengths. |
