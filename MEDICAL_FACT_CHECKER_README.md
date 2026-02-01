# Medical Dialogue Fact-Checking Agent

An intelligent AI agent using cutting-edge NLP + reasoning to evaluate factual consistency in medical dialogue summarization.

## Overview

This system evaluates whether a summary of a medical dialogue is factually consistent with the source dialogue. It extracts atomic facts from both the dialogue and summary, performs relation-aware consolidation, and computes precision/recall metrics.

**Key Constraint:** No external medical knowledge is used. All verification is grounded purely in the source dialogue.

## Features

### Step 1: Build Source Factlist
- ✅ Extracts atomic facts from multi-turn doctor-patient dialogue
- ✅ Includes provenance tracking (speaker, turn index, sentence index)
- ✅ Detects negation, certainty, time scope, and value-unit pairs
- ✅ Relation checking: Entailment, Contradiction, Complement, Duplication, Neutral
- ✅ Intelligent consolidation with update rules:
  - Duplication → Merge with provenance
  - Entailment → Keep more informative
  - Complement → Enrich with compatible details
  - Contradiction → Keep both, mark conflict
  - Neutral → Add as independent fact

### Step 2: Build Summary Factlist
- ✅ Extracts atomic facts from summary
- ✅ Each fact gets a unique ID

### Step 3: Verify Summary Facts
- ✅ Evidence linking (retrieves top 3-5 relevant source facts)
- ✅ Verification labels:
  - **Supported**: Entailed by source facts
  - **Rejected**: Contradicted by source facts
  - **NEI (Not Enough Information)**: Cannot be verified
- ✅ Conflict-aware handling for contradictory source evidence
- ✅ Justification for each label

### Step 4: Compute Metrics
- ✅ Fact Precision: TP / (TP + FP)
- ✅ Fact Recall: Source facts covered by supported summary facts
- ✅ Detailed breakdown: TP, FP, NEI counts

## Installation

No external dependencies required! Pure Python 3.6+ implementation.

```bash
# Just copy the file
cp medical_fact_checker.py /your/project/
```

## Usage

### Basic Example

```python
from medical_fact_checker import MedicalFactChecker

# Create dialogue
dialogue = [
    {
        "speaker": "patient",
        "utterance": "I have a headache and fever."
    },
    {
        "speaker": "doctor",
        "utterance": "Take acetaminophen 500mg every 6 hours."
    }
]

# Create summary
summary = "Patient has headache. Doctor prescribed acetaminophen 500mg."

# Run fact checker
checker = MedicalFactChecker()
result = checker.evaluate_consistency(dialogue, summary)

# Access results
print(f"Precision: {result['metrics'].fact_precision:.2%}")
print(f"Recall: {result['metrics'].fact_recall:.2%}")
```

### Running the Demo

```bash
python medical_fact_checker.py
```

This runs a complete example with a multi-turn dialogue and summary containing both accurate and inaccurate claims.

## Data Structures

### SourceFact
```python
@dataclass
class SourceFact:
    fact_id: str                    # Unique identifier
    fact_text: str                  # Atomic statement
    speaker: str                    # "doctor" or "patient"
    source_sentence: str            # Verbatim sentence
    turn_index: int                 # Position in dialogue
    sentence_index: int             # Position in turn
    
    # Optional structured fields
    entities: List[str]             # Medical entities
    polarity: str                   # "affirmed" or "negated"
    time_scope: Optional[str]       # "past", "current", "future"
    certainty: str                  # "definite", "probable", "possible"
    value_unit: Optional[Dict]      # {"value": "50", "unit": "mg"}
    
    # Consolidation metadata
    status: str                     # "active", "merged", "conflicting"
    conflict_group_id: Optional[str]
    merged_from: List[str]
    alternative_sources: List[Dict]
```

### SummaryFact
```python
@dataclass
class SummaryFact:
    summary_fact_id: str
    fact_text: str
    
    # Verification results
    evidence_fact_ids: List[str]           # Top supporting/contradicting facts
    verification_label: VerificationLabel  # SUPPORTED, REJECTED, or NEI
    justification: str                     # Explanation
    ambiguity_reason: Optional[str]        # For NEI with conflicts
```

### Metrics
```python
@dataclass
class Metrics:
    fact_precision: float    # TP / (TP + FP)
    fact_recall: float       # src_covered / src_total
    tp: int                  # Supported claims
    fp: int                  # Rejected claims
    nei: int                 # Not enough information
    src_covered: int         # Source facts recalled
    src_total: int          # Total source facts
```

## Example Output

```
================================================================================
MEDICAL DIALOGUE FACT-CHECKING RESULTS
================================================================================

📋 SOURCE FACTS EXTRACTED:
--------------------------------------------------------------------------------

ID: sf_0_0_0
  Speaker: patient
  Fact: I've been having severe headaches for the past week.
  Turn 0, Sentence 0
  Time: past

ID: sf_0_1_0
  Speaker: patient
  Fact: The pain is mostly on the right side.
  Turn 0, Sentence 1

...

📝 SUMMARY FACTS VERIFICATION:
--------------------------------------------------------------------------------

✅ ID: summ_0
  Fact: Patient reports daily severe headaches on the right side for one week.
  Label: Supported
  Evidence: ['sf_0_0_0', 'sf_0_1_0']
  Justification: Supported by source fact (turn 0): I've been having severe...

❌ ID: summ_2
  Fact: Patient experiences light sensitivity.
  Label: Rejected
  Evidence: ['sf_4_1_0']
  Justification: Contradicted by source fact (turn 4): No light sensitivity though.

...

📊 METRICS:
--------------------------------------------------------------------------------
Fact Precision: 75.00% (3 supported / 4 claims)
Fact Recall: 83.33% (5 / 6 source facts covered)

Breakdown:
  ✅ True Positives (Supported): 3
  ❌ False Positives (Rejected): 1
  ❓ Not Enough Info (NEI): 0
```

## Architecture

### Relation-Aware Consolidation

The system intelligently merges duplicate or related facts:

1. **Duplication Detection**: Exact or near-exact matches are merged
2. **Entailment**: More specific facts replace general ones
3. **Complement**: Compatible details are enriched
4. **Contradiction**: Both versions kept with conflict markers
5. **Neutral**: Added as independent facts

### Conflict Handling

When source dialogue contains contradictions (e.g., patient changes their answer):
- Both conflicting facts are retained
- Assigned a `conflict_group_id`
- Marked with `status: "conflicting"`
- Summary facts linking to conflicts are labeled NEI

### Evidence Linking

For each summary fact, the system:
1. Extracts entities and key terms
2. Scores source facts by entity/word overlap
3. Retrieves top 3-5 most relevant facts
4. Uses them for verification

### Verification Logic

- **Supported**: High similarity + matching polarity
- **Rejected**: High similarity + opposite polarity
- **NEI**: Low similarity OR conflicting evidence

## Limitations & Extensions

### Current Implementation
- Rule-based fact extraction (production would use advanced NLP models)
- Simple entity recognition (production would use medical NER models)
- Lexical similarity for matching (production would use semantic embeddings)

### Recommended Extensions
1. **Advanced NLP**: Use transformer models (BioBERT, ClinicalBERT) for fact extraction
2. **Semantic Matching**: Use sentence embeddings for better evidence retrieval
3. **Coreference Resolution**: Link pronouns to entities across turns
4. **Temporal Reasoning**: Better handling of time expressions and sequence
5. **Entity Linking**: Map medical terms to standard ontologies (for display only, not verification)

## Testing

```python
# Test with contradictory dialogue
dialogue = [
    {"speaker": "patient", "utterance": "I have a fever."},
    {"speaker": "patient", "utterance": "Actually, I don't have a fever."}
]
summary = "Patient has a fever."

checker = MedicalFactChecker()
result = checker.evaluate_consistency(dialogue, summary)
# Should mark as NEI due to contradiction
```

## License

MIT License - Feel free to use and modify for your research and applications.

## Citation

If you use this system in your research, please cite:

```bibtex
@software{medical_fact_checker_2026,
  title={Intelligent AI Agent for Medical Dialogue Fact-Checking},
  author={Your Name},
  year={2026},
  url={https://github.com/yfZhong/yfZhong.github.io}
}
```

## Contact

For questions or contributions, please open an issue on GitHub.
