# Phase 6B Explainability Design: Neurolens Suggestion Contextualization

This document details the explainability mechanism designed for Phase 6B, outlining how Neurolens will present context for each AI suggestion truthfully and consistently with the underlying multilingual embedding model.

---

## 1. Information Sources for Explainability

To explain *why* a milestone was suggested without fabricating keyword matches (since retrieval is embedding-based), the backend will rely on:
1.  **Transliterations Mapping**: The transliteration glossary (`ai_engine.transliteration_glossary`) mapping Hinglish terms (e.g., *"ungli"*, *"gudiya"*) to English equivalents (e.g., *"finger"*, *"doll"*). If the caregiver's text includes glossary keys, we can safely report that translation maps were used.
2.  **Milestone Metadata**: The milestone title, description, domain, and age-band parameters (`age_range_low`, `age_range_high`).
3.  **Domain Mapping**: The classification matching the developmental domain.
4.  **Age Suitability**: Evaluating child age against milestone expected boundaries.

---

## 2. Explainability Metadata Schema

For each suggestion, we will calculate and return the following structured metadata in `ObservationSuggestion`:

```json
{
  "milestone_id": "uuid",
  "title": "Uses items for intended purpose",
  "relevance_score": 0.85,
  "relevance_label": "Strong relevance",
  "domain_name": "Cognitive",
  "translated_terms": [{"raw": "gudiya", "translated": "doll"}],
  "age_band_relevance": "Within typical range (12-18 months)",
  "explanation_text": "Observation contains semantic patterns matching developmental milestones in Cognitive domain. The observation includes local phrasing translated from Hinglish: 'gudiya' (doll). Child is 15 months, which is within the typical age range of 12-18 months."
}
```

---

## 3. Explainability Logic & Algorithm

When compiling suggestions for a given input `observation_text` and `child_age_months`:

### Step A: Identify Translated Terms
*   Tokenize the raw observation text into lowercase words.
*   Compare each word against `ai_engine.transliteration_glossary`. If a word matches, store its raw key and its English translation in `translated_terms`.

### Step B: Evaluate Age-Band Relevance
Compare `child_age_months` against the milestone's `age_range_low` and `age_range_high`:
1.  **On-Track (Within Range)**: `age_range_low <= child_age_months <= age_range_high`
    *   *Text*: `"On-Track: Child is [age] months, matching the typical age range of [low]-[high] months for this milestone."`
2.  **Delayed Skill Check (Above Range)**: `child_age_months > age_range_high`
    *   *Text*: `"Developmental Screening: Child is [age] months. This milestone is typically achieved by [high] months, tracking for developmental delay."`
3.  **Emerging Skill Check (Below Range)**: `child_age_months < age_range_low`
    *   *Text*: `"Emerging Skill Check: Child is [age] months. This milestone is typically expected at [low]-[high] months."`

### Step C: Generate Natural Language Explanation Text
Assemble a user-friendly, truthful statement:
*   State the developmental domain match.
*   Add the age-band relevance description.
*   If Hinglish transliterations occurred, append: `"Caregiver terminology matched: '[raw]' translated to '[translated]'."`
*   *Template*: 
    `"This observation was retrieved based on semantic similarity to behavioral patterns in the [domain] domain. [Age-band explanation]. [Transliteration notes]"`

---

## 4. Implementation Boundaries
*   All calculations are performed post-retrieval.
*   No database changes are required for existing milestones; all logic uses cached `milestone_metadata`.
*   Explainability metadata is stored directly inside the existing `JSON` column `suggested_milestones` of `ai_suggestion_events`.
