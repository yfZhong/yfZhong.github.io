#!/usr/bin/env python3
"""
Advanced Examples for Medical Dialogue Fact-Checking Agent

This file demonstrates various scenarios and edge cases.
"""

from medical_fact_checker import MedicalFactChecker, format_output


def example_1_basic_consistency():
    """Example 1: Summary is fully consistent with dialogue"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Fully Consistent Summary")
    print("="*80)
    
    dialogue = [
        {
            "speaker": "patient",
            "utterance": "I have been experiencing chest pain for 2 days."
        },
        {
            "speaker": "doctor",
            "utterance": "Is the pain sharp or dull? Does it radiate anywhere?"
        },
        {
            "speaker": "patient",
            "utterance": "It's a sharp pain, radiating to my left arm."
        },
        {
            "speaker": "doctor",
            "utterance": "I'm ordering an ECG and prescribing aspirin 81mg daily."
        }
    ]
    
    summary = "Patient has sharp chest pain for 2 days radiating to left arm. Doctor ordered ECG and prescribed aspirin 81mg daily."
    
    checker = MedicalFactChecker()
    result = checker.evaluate_consistency(dialogue, summary)
    print(format_output(result))
    
    return result


def example_2_contradictory_summary():
    """Example 2: Summary contradicts the dialogue"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Summary with Contradictions")
    print("="*80)
    
    dialogue = [
        {
            "speaker": "patient",
            "utterance": "I don't have any fever. Just a cough."
        },
        {
            "speaker": "doctor",
            "utterance": "How long have you had the cough?"
        },
        {
            "speaker": "patient",
            "utterance": "About 5 days now."
        }
    ]
    
    summary = "Patient has fever and cough for 5 days."
    
    checker = MedicalFactChecker()
    result = checker.evaluate_consistency(dialogue, summary)
    print(format_output(result))
    
    return result


def example_3_conflicting_dialogue():
    """Example 3: Dialogue contains contradictions (patient changes answer)"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Conflicting Information in Dialogue")
    print("="*80)
    
    dialogue = [
        {
            "speaker": "doctor",
            "utterance": "Are you allergic to any medications?"
        },
        {
            "speaker": "patient",
            "utterance": "No, I'm not allergic to anything."
        },
        {
            "speaker": "doctor",
            "utterance": "Have you ever had any reactions to penicillin?"
        },
        {
            "speaker": "patient",
            "utterance": "Oh wait, I did have a rash from penicillin before."
        }
    ]
    
    summary = "Patient is allergic to penicillin."
    
    checker = MedicalFactChecker()
    result = checker.evaluate_consistency(dialogue, summary)
    print(format_output(result))
    
    return result


def example_4_hallucinated_facts():
    """Example 4: Summary adds facts not in dialogue"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Summary with Hallucinated Facts (NEI)")
    print("="*80)
    
    dialogue = [
        {
            "speaker": "patient",
            "utterance": "I have been feeling tired lately."
        },
        {
            "speaker": "doctor",
            "utterance": "How long has this been going on?"
        },
        {
            "speaker": "patient",
            "utterance": "About 3 weeks."
        }
    ]
    
    summary = "Patient reports chronic fatigue for 3 weeks and weight loss."
    
    checker = MedicalFactChecker()
    result = checker.evaluate_consistency(dialogue, summary)
    print(format_output(result))
    
    return result


def example_5_medication_dosage():
    """Example 5: Complex medication information"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Medication Dosage Verification")
    print("="*80)
    
    dialogue = [
        {
            "speaker": "patient",
            "utterance": "I'm currently taking metformin 500mg twice daily."
        },
        {
            "speaker": "doctor",
            "utterance": "Good. Let's increase it to 1000mg twice daily."
        },
        {
            "speaker": "patient",
            "utterance": "Should I take it with meals?"
        },
        {
            "speaker": "doctor",
            "utterance": "Yes, take it with breakfast and dinner."
        }
    ]
    
    summary = "Patient was taking metformin 500mg twice daily. Doctor increased dose to 1000mg twice daily with meals."
    
    checker = MedicalFactChecker()
    result = checker.evaluate_consistency(dialogue, summary)
    print(format_output(result))
    
    return result


def example_6_temporal_information():
    """Example 6: Temporal scope (past vs present)"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Temporal Information Handling")
    print("="*80)
    
    dialogue = [
        {
            "speaker": "patient",
            "utterance": "I used to smoke a pack a day, but I quit 5 years ago."
        },
        {
            "speaker": "doctor",
            "utterance": "Excellent. That will significantly reduce your health risks."
        },
        {
            "speaker": "patient",
            "utterance": "I occasionally drink alcohol now, maybe once a week."
        }
    ]
    
    summary = "Patient smokes one pack daily and drinks alcohol weekly."
    
    checker = MedicalFactChecker()
    result = checker.evaluate_consistency(dialogue, summary)
    print(format_output(result))
    
    return result


def example_7_negation_handling():
    """Example 7: Negation detection"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Negation Detection")
    print("="*80)
    
    dialogue = [
        {
            "speaker": "doctor",
            "utterance": "Do you have any chest pain?"
        },
        {
            "speaker": "patient",
            "utterance": "No chest pain. No shortness of breath either."
        },
        {
            "speaker": "doctor",
            "utterance": "Any swelling in your legs?"
        },
        {
            "speaker": "patient",
            "utterance": "No swelling."
        }
    ]
    
    summary = "Patient denies chest pain and shortness of breath. No leg swelling reported."
    
    checker = MedicalFactChecker()
    result = checker.evaluate_consistency(dialogue, summary)
    print(format_output(result))
    
    return result


def example_8_duplicate_facts():
    """Example 8: Patient repeats information (duplication handling)"""
    print("\n" + "="*80)
    print("EXAMPLE 8: Duplicate Fact Consolidation")
    print("="*80)
    
    dialogue = [
        {
            "speaker": "patient",
            "utterance": "I have severe back pain."
        },
        {
            "speaker": "doctor",
            "utterance": "Where exactly is the pain located?"
        },
        {
            "speaker": "patient",
            "utterance": "Lower back. I've had severe lower back pain for a week."
        },
        {
            "speaker": "doctor",
            "utterance": "Any numbness or tingling?"
        },
        {
            "speaker": "patient",
            "utterance": "No, just the severe pain in my lower back."
        }
    ]
    
    summary = "Patient has severe lower back pain for one week without numbness or tingling."
    
    checker = MedicalFactChecker()
    result = checker.evaluate_consistency(dialogue, summary)
    print(format_output(result))
    
    return result


def example_9_complex_medical_scenario():
    """Example 9: Complex realistic medical dialogue"""
    print("\n" + "="*80)
    print("EXAMPLE 9: Complex Medical Scenario")
    print("="*80)
    
    dialogue = [
        {
            "speaker": "patient",
            "utterance": "I've been having trouble sleeping. I wake up multiple times at night."
        },
        {
            "speaker": "doctor",
            "utterance": "How long has this been happening?"
        },
        {
            "speaker": "patient",
            "utterance": "About 2 months. I also feel tired during the day."
        },
        {
            "speaker": "doctor",
            "utterance": "Do you snore? Has anyone told you that you stop breathing while asleep?"
        },
        {
            "speaker": "patient",
            "utterance": "My wife says I snore loudly and sometimes gasp for air."
        },
        {
            "speaker": "doctor",
            "utterance": "This could be sleep apnea. I'm referring you for a sleep study. In the meantime, try sleeping on your side and avoid alcohol before bed."
        }
    ]
    
    summary = "Patient presents with insomnia for 2 months with daytime fatigue. Wife reports loud snoring and breathing pauses. Doctor suspects sleep apnea, ordered sleep study, and recommended positional therapy and alcohol avoidance."
    
    checker = MedicalFactChecker()
    result = checker.evaluate_consistency(dialogue, summary)
    print(format_output(result))
    
    return result


def run_all_examples():
    """Run all examples"""
    examples = [
        example_1_basic_consistency,
        example_2_contradictory_summary,
        example_3_conflicting_dialogue,
        example_4_hallucinated_facts,
        example_5_medication_dosage,
        example_6_temporal_information,
        example_7_negation_handling,
        example_8_duplicate_facts,
        example_9_complex_medical_scenario
    ]
    
    results = []
    for example_func in examples:
        result = example_func()
        results.append(result)
        input("\nPress Enter to continue to next example...")
    
    # Summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS ACROSS ALL EXAMPLES")
    print("="*80)
    
    total_precision = sum(r['metrics'].fact_precision for r in results) / len(results)
    total_recall = sum(r['metrics'].fact_recall for r in results) / len(results)
    
    print(f"\nAverage Precision: {total_precision:.2%}")
    print(f"Average Recall: {total_recall:.2%}")
    
    total_tp = sum(r['metrics'].tp for r in results)
    total_fp = sum(r['metrics'].fp for r in results)
    total_nei = sum(r['metrics'].nei for r in results)
    
    print(f"\nTotal across all examples:")
    print(f"  Supported: {total_tp}")
    print(f"  Rejected: {total_fp}")
    print(f"  NEI: {total_nei}")


if __name__ == "__main__":
    print("Medical Dialogue Fact-Checking Agent - Advanced Examples")
    print("This demo showcases various scenarios and edge cases.\n")
    
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        example_map = {
            '1': example_1_basic_consistency,
            '2': example_2_contradictory_summary,
            '3': example_3_conflicting_dialogue,
            '4': example_4_hallucinated_facts,
            '5': example_5_medication_dosage,
            '6': example_6_temporal_information,
            '7': example_7_negation_handling,
            '8': example_8_duplicate_facts,
            '9': example_9_complex_medical_scenario,
        }
        
        if example_num in example_map:
            example_map[example_num]()
        else:
            print(f"Example {example_num} not found. Use 1-9.")
    else:
        run_all_examples()
