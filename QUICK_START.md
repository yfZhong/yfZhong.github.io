# Medical Dialogue Fact-Checking Agent - Quick Start Guide

## Installation

No dependencies required! Just Python 3.6+

```bash
# Download the files
# - medical_fact_checker.py (main system)
# - examples.py (demonstrations)
# - MEDICAL_FACT_CHECKER_README.md (detailed documentation)

python3 medical_fact_checker.py  # Run basic demo
python3 examples.py              # Run all 9 examples
python3 examples.py 1            # Run specific example (1-9)
```

## Basic Usage

```python
from medical_fact_checker import MedicalFactChecker

# 1. Prepare your dialogue
dialogue = [
    {
        "speaker": "patient",
        "utterance": "I have been experiencing chest pain for 2 days."
    },
    {
        "speaker": "doctor",
        "utterance": "I'm prescribing aspirin 81mg daily."
    }
]

# 2. Prepare summary to verify
summary = "Patient has chest pain for 2 days. Doctor prescribed aspirin 81mg daily."

# 3. Run fact-checking
checker = MedicalFactChecker()
result = checker.evaluate_consistency(dialogue, summary)

# 4. Access results
print(f"Precision: {result['metrics'].fact_precision:.2%}")
print(f"Recall: {result['metrics'].fact_recall:.2%}")

for fact in result['summary_factlist']:
    print(f"{fact.verification_label.value}: {fact.fact_text}")
```

## Output Structure

### result['source_factlist']
List of atomic facts extracted from dialogue:
- `fact_id`: Unique identifier
- `fact_text`: The atomic claim
- `speaker`: "doctor" or "patient"
- `polarity`: "affirmed" or "negated"
- `status`: "active", "merged", or "conflicting"

### result['summary_factlist']
List of atomic facts from summary with verification:
- `fact_text`: The claim
- `verification_label`: SUPPORTED, REJECTED, or NEI
- `evidence_fact_ids`: Source facts used for verification
- `justification`: Explanation

### result['metrics']
Performance metrics:
- `fact_precision`: TP / (TP + FP)
- `fact_recall`: Coverage of source facts
- `tp`, `fp`, `nei`: Count breakdowns

## Key Features

### 1. Fact Consolidation
```python
# Handles duplicate/related facts automatically
dialogue = [
    {"speaker": "patient", "utterance": "I have pain."},
    {"speaker": "patient", "utterance": "I have severe pain in my back."}
]
# Second fact enriches the first (more specific)
```

### 2. Negation Detection
```python
dialogue = [
    {"speaker": "patient", "utterance": "I don't have any fever."}
]
summary = "Patient has fever."
# Result: REJECTED (contradiction detected)
```

### 3. Compound Sentence Splitting
```python
summary = "Patient has fever and cough."
# Automatically splits into:
# - "Patient has fever"
# - "Patient has cough"
# Each verified independently
```

### 4. Conflict Handling
```python
dialogue = [
    {"speaker": "patient", "utterance": "I'm not allergic."},
    {"speaker": "patient", "utterance": "Actually, I'm allergic to penicillin."}
]
# Both facts retained with conflict_group_id
# Summary facts linking to conflicts marked NEI
```

## Example Scenarios

### Scenario 1: Fully Accurate Summary
```python
dialogue = [
    {"speaker": "patient", "utterance": "I have chest pain for 2 days."}
]
summary = "Patient has chest pain for 2 days."
# Result: SUPPORTED (100% precision, 100% recall)
```

### Scenario 2: Hallucinated Information
```python
dialogue = [
    {"speaker": "patient", "utterance": "I feel tired."}
]
summary = "Patient has fatigue and weight loss."
# Result:
# - "Patient has fatigue" -> SUPPORTED
# - "Patient has weight loss" -> NEI (not mentioned in dialogue)
```

### Scenario 3: Contradictory Summary
```python
dialogue = [
    {"speaker": "patient", "utterance": "I don't have fever."}
]
summary = "Patient has fever."
# Result: REJECTED (contradiction)
```

## Understanding Metrics

### Precision
Measures how many summary claims are correct:
- **High precision** (>80%): Summary is mostly accurate
- **Medium precision** (50-80%): Some inaccuracies present
- **Low precision** (<50%): Summary has many errors

### Recall
Measures how much of the source is covered:
- **High recall** (>80%): Summary captures most information
- **Medium recall** (50-80%): Summary is selective
- **Low recall** (<50%): Summary misses key information

### Interpretation Examples

```
Precision: 100%, Recall: 60%
→ Everything in summary is correct, but it's incomplete

Precision: 70%, Recall: 90%
→ Summary is comprehensive but includes some errors

Precision: 50%, Recall: 100%
→ Summary covers everything but has many inaccuracies
```

## Advanced Usage

### Custom Formatting
```python
from medical_fact_checker import format_output

result = checker.evaluate_consistency(dialogue, summary)
formatted = format_output(result)
print(formatted)  # Pretty-printed results
```

### Accessing Raw Data
```python
# Examine individual source facts
for fact in result['source_factlist']:
    if fact.status == "conflicting":
        print(f"Conflict: {fact.fact_text}")
        print(f"Group: {fact.conflict_group_id}")

# Check verification justifications
for fact in result['summary_factlist']:
    if fact.verification_label.value == "Rejected":
        print(f"Error: {fact.fact_text}")
        print(f"Reason: {fact.justification}")
```

### Analyzing Specific Claims
```python
# Find which summary facts cover a specific topic
topic = "medication"
relevant_facts = [
    f for f in result['summary_factlist']
    if topic in f.fact_text.lower()
]

for fact in relevant_facts:
    print(f"{fact.verification_label.value}: {fact.fact_text}")
```

## Common Pitfalls

### ❌ Long Complex Sentences
```python
# BAD: Hard to verify as single fact
summary = "Patient reports severe chest pain radiating to left arm with associated dyspnea and diaphoresis for 2 days."

# GOOD: Split into atomic facts (done automatically)
summary = "Patient has severe chest pain. Pain radiates to left arm. Patient has dyspnea and diaphoresis. Duration is 2 days."
```

### ❌ Ambiguous References
```python
# BAD: Unclear what "it" refers to
dialogue = [
    {"speaker": "patient", "utterance": "I have pain and fever."},
    {"speaker": "doctor", "utterance": "When did it start?"}
]
# System may not resolve "it"

# GOOD: Explicit references
dialogue = [
    {"speaker": "patient", "utterance": "I have pain and fever."},
    {"speaker": "doctor", "utterance": "When did the fever start?"}
]
```

### ❌ Implicit Information
```python
# BAD: Inferring beyond dialogue
dialogue = [
    {"speaker": "patient", "utterance": "I have chest pain."}
]
summary = "Patient has cardiac symptoms."
# Result: NEI (cardiac is interpretation, not stated)

# GOOD: Use exact terminology
summary = "Patient has chest pain."
# Result: SUPPORTED
```

## Troubleshooting

### Low Precision
**Symptoms:** Many REJECTED facts
**Causes:**
1. Summary adds information not in dialogue
2. Summary contradicts dialogue
3. Wrong negation (affirmed vs. negated)

**Solutions:**
- Review REJECTED facts and their justifications
- Check if summary introduces external knowledge
- Verify negation handling

### Low Recall
**Symptoms:** Few source facts covered
**Causes:**
1. Summary is too brief
2. Summary uses different terminology
3. Summary focuses on subset of dialogue

**Solutions:**
- Review which source facts are uncovered
- Check if summary paraphrases too much
- Consider if summary is intentionally selective

### Many NEI Results
**Symptoms:** High NEI count
**Causes:**
1. Summary too vague or general
2. Conflicting information in dialogue
3. Poor lexical overlap

**Solutions:**
- Check ambiguity_reason for conflicts
- Review evidence_fact_ids to see what matched
- Consider rewording for better overlap

## Best Practices

1. **Use complete utterances**: Include full patient/doctor statements
2. **Maintain speaker labels**: Critical for attribution
3. **Keep atomic summaries**: One claim per sentence when possible
4. **Check metrics together**: Don't optimize one at expense of other
5. **Review justifications**: Understand why facts are verified as they are

## Limitations

This is a rule-based prototype. Production systems should use:
- Advanced NLP models (BERT, BioBERT) for extraction
- Semantic similarity (sentence embeddings) instead of lexical
- Coreference resolution for pronoun handling
- Medical entity recognition (NER) for better entity matching
- Dependency parsing for complex sentence structure

## Support

See `MEDICAL_FACT_CHECKER_README.md` for comprehensive documentation.

For issues or questions, please open a GitHub issue.
