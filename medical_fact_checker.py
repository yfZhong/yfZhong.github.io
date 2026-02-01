#!/usr/bin/env python3
"""
Intelligent AI Agent for Evaluating Factual Consistency in Medical Dialogue Summarization

This module implements a complete pipeline for extracting, consolidating, and verifying
atomic facts from medical dialogues and their summaries, using cutting-edge NLP techniques.

No external medical knowledge is used - all verification is grounded in the source dialogue.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum
import re
from collections import defaultdict


class RelationType(Enum):
    """Types of relations between facts"""
    ENTAILMENT = "entailment"
    CONTRADICTION = "contradiction"
    COMPLEMENT = "complement"
    DUPLICATION = "duplication"
    NEUTRAL = "neutral"


class VerificationLabel(Enum):
    """Verification labels for summary facts"""
    SUPPORTED = "Supported"
    REJECTED = "Rejected"
    NEI = "Not Enough Information"


@dataclass
class SourceFact:
    """Structured representation of an atomic fact from source dialogue"""
    fact_id: str
    fact_text: str
    speaker: str  # "doctor" or "patient"
    source_sentence: str
    turn_index: int
    sentence_index: int
    
    # Optional structured fields
    entities: List[str] = field(default_factory=list)
    polarity: str = "affirmed"  # "affirmed" or "negated"
    time_scope: Optional[str] = None
    certainty: str = "definite"  # "definite", "probable", "possible"
    value_unit: Optional[Dict[str, str]] = None
    
    # For handling duplications and conflicts
    status: str = "active"  # "active", "merged", "conflicting"
    conflict_group_id: Optional[str] = None
    merged_from: List[str] = field(default_factory=list)
    alternative_sources: List[Dict] = field(default_factory=list)


@dataclass
class SummaryFact:
    """Structured representation of an atomic fact from summary"""
    summary_fact_id: str
    fact_text: str
    
    # Verification results
    evidence_fact_ids: List[str] = field(default_factory=list)
    verification_label: Optional[VerificationLabel] = None
    justification: str = ""
    ambiguity_reason: Optional[str] = None


@dataclass
class Metrics:
    """Fact-level precision and recall metrics"""
    fact_precision: float
    fact_recall: float
    tp: int  # True Positives (Supported)
    fp: int  # False Positives (Rejected)
    nei: int  # Not Enough Information
    src_covered: int  # Source facts recalled
    src_total: int  # Total source facts


class MedicalFactChecker:
    """
    Main class implementing the intelligent AI agent for medical fact-checking
    """
    
    def __init__(self):
        self.source_factlist: List[SourceFact] = []
        self.summary_factlist: List[SummaryFact] = []
        self.conflict_counter = 0
    
    # ==================== STEP 1: Build source_factlist ====================
    
    def build_source_factlist(self, source_dialogue: List[Dict]) -> List[SourceFact]:
        """
        Extract and consolidate atomic facts from source dialogue.
        
        Args:
            source_dialogue: List of turns, each with 'speaker' and 'utterance'
            
        Returns:
            Consolidated list of source facts
        """
        self.source_factlist = []
        
        for turn_idx, turn in enumerate(source_dialogue):
            speaker = turn.get('speaker', 'unknown').lower()
            utterance = turn.get('utterance', '')
            
            # Split utterance into sentences
            sentences = self._split_sentences(utterance)
            
            for sent_idx, sentence in enumerate(sentences):
                # Extract candidate facts from this sentence
                candidate_facts = self._extract_facts_from_sentence(
                    sentence, speaker, turn_idx, sent_idx
                )
                
                # For each candidate fact, check relation to existing facts
                for candidate in candidate_facts:
                    self._process_candidate_fact(candidate)
        
        return self.source_factlist
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences using simple rules"""
        # Simple sentence splitting - handles periods, question marks, exclamation
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_facts_from_sentence(
        self, 
        sentence: str, 
        speaker: str, 
        turn_idx: int, 
        sent_idx: int
    ) -> List[SourceFact]:
        """
        Extract atomic facts from a single sentence.
        
        This is a rule-based approach that identifies factual claims.
        In a production system, this would use advanced NLP models.
        """
        facts = []
        
        # Clean the sentence
        sentence = sentence.strip()
        if not sentence:
            return facts
        
        # Generate a fact ID
        fact_id = f"sf_{turn_idx}_{sent_idx}_0"
        
        # Detect polarity (negation)
        polarity = "affirmed"
        negation_words = ['no', 'not', 'never', 'none', 'nothing', "n't", 'without']
        sentence_lower = sentence.lower()
        if any(neg in sentence_lower for neg in negation_words):
            polarity = "negated"
        
        # Detect certainty markers
        certainty = "definite"
        if any(word in sentence_lower for word in ['maybe', 'possibly', 'might', 'could']):
            certainty = "possible"
        elif any(word in sentence_lower for word in ['probably', 'likely']):
            certainty = "probable"
        
        # Detect time scope indicators
        time_scope = None
        if any(word in sentence_lower for word in ['currently', 'now', 'today', 'this week']):
            time_scope = "current"
        elif any(word in sentence_lower for word in ['previously', 'before', 'past', 'earlier', 'used to']):
            time_scope = "past"
        elif any(word in sentence_lower for word in ['will', 'going to', 'next', 'future']):
            time_scope = "future"
        
        # Extract entities (simple noun phrase extraction)
        entities = self._extract_entities(sentence)
        
        # Extract value-unit pairs (e.g., "50mg", "twice daily")
        value_unit = self._extract_value_unit(sentence)
        
        # Create the fact
        fact = SourceFact(
            fact_id=fact_id,
            fact_text=sentence,
            speaker=speaker,
            source_sentence=sentence,
            turn_index=turn_idx,
            sentence_index=sent_idx,
            entities=entities,
            polarity=polarity,
            time_scope=time_scope,
            certainty=certainty,
            value_unit=value_unit
        )
        
        facts.append(fact)
        return facts
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract medical entities (simplified)"""
        entities = []
        
        # Medical terms patterns (simplified)
        medical_patterns = [
            r'\b(?:pain|fever|cough|headache|nausea|vomiting|dizziness)\b',
            r'\b(?:mg|ml|tablets?|capsules?|pills?)\b',
            r'\b(?:blood pressure|heart rate|temperature)\b',
            r'\b(?:aspirin|ibuprofen|acetaminophen|antibiotic|medication)\b',
        ]
        
        for pattern in medical_patterns:
            matches = re.finditer(pattern, text.lower())
            entities.extend([m.group() for m in matches])
        
        return list(set(entities))
    
    def _extract_value_unit(self, text: str) -> Optional[Dict[str, str]]:
        """Extract value-unit pairs like '50mg', 'twice daily'"""
        # Pattern for dosages: number + unit
        pattern = r'(\d+\.?\d*)\s*(mg|ml|tablets?|times?|daily|hourly|weekly)'
        match = re.search(pattern, text.lower())
        
        if match:
            return {
                'value': match.group(1),
                'unit': match.group(2)
            }
        return None
    
    def _process_candidate_fact(self, candidate: SourceFact):
        """
        Process a candidate fact by checking relations to existing facts
        and applying update rules.
        """
        # Find relevant existing facts (those with overlapping entities or context)
        relevant_facts = self._find_relevant_facts(candidate)
        
        if not relevant_facts:
            # No relevant facts - add as new
            self.source_factlist.append(candidate)
            return
        
        # Check relation with each relevant fact
        best_relation = None
        best_match = None
        best_score = 0
        
        for existing_fact in relevant_facts:
            relation, score = self._determine_relation(candidate, existing_fact)
            if score > best_score:
                best_score = score
                best_relation = relation
                best_match = existing_fact
        
        # Apply update rules based on the best relation
        if best_match and best_relation:
            self._apply_update_rule(candidate, best_match, best_relation)
        else:
            # Neutral or no strong relation - add as new
            self.source_factlist.append(candidate)
    
    def _find_relevant_facts(self, candidate: SourceFact) -> List[SourceFact]:
        """Find existing facts that might relate to the candidate"""
        relevant = []
        
        candidate_entities = set(candidate.entities)
        candidate_words = set(candidate.fact_text.lower().split())
        
        for existing_fact in self.source_factlist:
            # Skip merged facts
            if existing_fact.status == "merged":
                continue
            
            # Check for entity overlap
            existing_entities = set(existing_fact.entities)
            entity_overlap = len(candidate_entities & existing_entities)
            
            # Check for word overlap
            existing_words = set(existing_fact.fact_text.lower().split())
            word_overlap = len(candidate_words & existing_words)
            
            # Consider relevant if significant overlap
            if entity_overlap > 0 or word_overlap >= 3:
                relevant.append(existing_fact)
        
        return relevant
    
    def _determine_relation(
        self, 
        fact1: SourceFact, 
        fact2: SourceFact
    ) -> Tuple[RelationType, float]:
        """
        Determine the relation between two facts.
        
        Returns:
            (RelationType, confidence_score)
        """
        text1 = fact1.fact_text.lower()
        text2 = fact2.fact_text.lower()
        
        # Exact match -> Duplication
        if text1 == text2:
            return (RelationType.DUPLICATION, 1.0)
        
        # Very high similarity -> Duplication
        words1 = set(text1.split())
        words2 = set(text2.split())
        overlap = len(words1 & words2)
        union = len(words1 | words2)
        similarity = overlap / union if union > 0 else 0
        
        if similarity > 0.85:
            return (RelationType.DUPLICATION, similarity)
        
        # Opposite polarity with same entities -> Contradiction
        if (fact1.polarity != fact2.polarity and 
            len(set(fact1.entities) & set(fact2.entities)) > 0):
            return (RelationType.CONTRADICTION, 0.8)
        
        # Same entities but different details -> Complement or Entailment
        entity_overlap = len(set(fact1.entities) & set(fact2.entities))
        if entity_overlap > 0 and similarity > 0.5:
            # One is more specific -> Entailment
            if len(words1) > len(words2) * 1.3:
                return (RelationType.ENTAILMENT, 0.7)
            elif len(words2) > len(words1) * 1.3:
                return (RelationType.ENTAILMENT, 0.7)
            else:
                # Similar length with overlap -> Complement
                return (RelationType.COMPLEMENT, 0.6)
        
        # Default to neutral
        return (RelationType.NEUTRAL, 0.3)
    
    def _apply_update_rule(
        self, 
        candidate: SourceFact, 
        existing: SourceFact, 
        relation: RelationType
    ):
        """Apply update rules based on the relation type"""
        
        if relation == RelationType.DUPLICATION:
            # Merge: keep existing, add provenance
            existing.alternative_sources.append({
                'turn_index': candidate.turn_index,
                'sentence_index': candidate.sentence_index,
                'source_sentence': candidate.source_sentence
            })
            existing.merged_from.append(candidate.fact_id)
            # Don't add candidate to the list
        
        elif relation == RelationType.ENTAILMENT:
            # Keep more informative (longer/more specific)
            if len(candidate.fact_text) > len(existing.fact_text):
                # Candidate is more informative
                candidate.merged_from = existing.merged_from + [existing.fact_id]
                candidate.alternative_sources = existing.alternative_sources
                # Replace existing with candidate
                idx = self.source_factlist.index(existing)
                self.source_factlist[idx] = candidate
                existing.status = "merged"
            else:
                # Existing is more informative, just add provenance
                existing.alternative_sources.append({
                    'turn_index': candidate.turn_index,
                    'sentence_index': candidate.sentence_index,
                    'source_sentence': candidate.source_sentence
                })
        
        elif relation == RelationType.COMPLEMENT:
            # Enrich: merge compatible details
            # Combine entities
            existing.entities = list(set(existing.entities + candidate.entities))
            
            # Update time scope if one has it and the other doesn't
            if candidate.time_scope and not existing.time_scope:
                existing.time_scope = candidate.time_scope
            
            # Update value_unit if one has it and the other doesn't
            if candidate.value_unit and not existing.value_unit:
                existing.value_unit = candidate.value_unit
            
            # Keep more specific fact text if one is clearly more detailed
            if len(candidate.fact_text) > len(existing.fact_text) * 1.2:
                existing.fact_text = candidate.fact_text
                existing.source_sentence = candidate.source_sentence
            
            # Add provenance
            existing.alternative_sources.append({
                'turn_index': candidate.turn_index,
                'sentence_index': candidate.sentence_index,
                'source_sentence': candidate.source_sentence
            })
        
        elif relation == RelationType.CONTRADICTION:
            # Keep both, mark conflict
            self.conflict_counter += 1
            conflict_id = f"conflict_{self.conflict_counter}"
            
            existing.status = "conflicting"
            existing.conflict_group_id = conflict_id
            
            candidate.status = "conflicting"
            candidate.conflict_group_id = conflict_id
            
            # Add the candidate as a separate fact
            self.source_factlist.append(candidate)
        
        else:  # NEUTRAL
            # Add as new independent fact
            self.source_factlist.append(candidate)
    
    # ==================== STEP 2: Build summary_factlist ====================
    
    def build_summary_factlist(self, summary: str) -> List[SummaryFact]:
        """
        Extract atomic facts from the summary.
        
        Args:
            summary: The summary text
            
        Returns:
            List of summary facts
        """
        self.summary_factlist = []
        
        # Split summary into sentences
        sentences = self._split_sentences(summary)
        
        for idx, sentence in enumerate(sentences):
            # Each sentence is treated as an atomic fact
            fact = SummaryFact(
                summary_fact_id=f"summ_{idx}",
                fact_text=sentence
            )
            self.summary_factlist.append(fact)
        
        return self.summary_factlist
    
    # ==================== STEP 3: Verify summary facts ====================
    
    def verify_summary_facts(self) -> List[SummaryFact]:
        """
        Verify each summary fact against source facts.
        
        Returns:
            Updated summary_factlist with verification results
        """
        for summary_fact in self.summary_factlist:
            self._verify_single_fact(summary_fact)
        
        return self.summary_factlist
    
    def _verify_single_fact(self, summary_fact: SummaryFact):
        """Verify a single summary fact against source facts"""
        
        # 3.1 Evidence linking
        evidence_facts = self._retrieve_evidence(summary_fact)
        summary_fact.evidence_fact_ids = [f.fact_id for f in evidence_facts[:5]]
        
        # 3.2 Decide verification label
        if not evidence_facts:
            summary_fact.verification_label = VerificationLabel.NEI
            summary_fact.justification = "No relevant source facts found"
            return
        
        # Check for conflicts in evidence
        conflict_groups = set()
        for ef in evidence_facts:
            if ef.conflict_group_id:
                conflict_groups.add(ef.conflict_group_id)
        
        # 3.3 Conflict-aware handling
        if conflict_groups:
            summary_fact.verification_label = VerificationLabel.NEI
            summary_fact.justification = "Source facts contain contradictory information"
            summary_fact.ambiguity_reason = f"Conflicting evidence in groups: {conflict_groups}"
            return
        
        # Check if summary fact is supported, rejected, or NEI
        label, justification = self._determine_verification_label(
            summary_fact, evidence_facts
        )
        
        summary_fact.verification_label = label
        summary_fact.justification = justification
    
    def _retrieve_evidence(self, summary_fact: SummaryFact) -> List[SourceFact]:
        """Retrieve relevant source facts as evidence"""
        
        summary_text = summary_fact.fact_text.lower()
        summary_words = set(summary_text.split())
        
        # Extract entities from summary fact
        summary_entities = self._extract_entities(summary_fact.fact_text)
        
        # Score each source fact
        scored_facts = []
        for source_fact in self.source_factlist:
            if source_fact.status == "merged":
                continue
            
            source_text = source_fact.fact_text.lower()
            source_words = set(source_text.split())
            
            # Calculate overlap
            word_overlap = len(summary_words & source_words)
            entity_overlap = len(set(summary_entities) & set(source_fact.entities))
            
            # Combined score
            score = word_overlap * 1.0 + entity_overlap * 2.0
            
            if score > 0:
                scored_facts.append((score, source_fact))
        
        # Sort by score and return top matches
        scored_facts.sort(reverse=True, key=lambda x: x[0])
        return [f for _, f in scored_facts[:5]]
    
    def _normalize_text(self, text: str) -> Set[str]:
        """Normalize text for comparison: lowercase, remove punctuation, split into words"""
        # Remove punctuation
        import string
        text_clean = text.lower().translate(str.maketrans('', '', string.punctuation))
        return set(text_clean.split())
    
    def _determine_verification_label(
        self, 
        summary_fact: SummaryFact, 
        evidence_facts: List[SourceFact]
    ) -> Tuple[VerificationLabel, str]:
        """
        Determine if summary fact is Supported, Rejected, or NEI.
        
        Returns:
            (label, justification)
        """
        summary_text = summary_fact.fact_text.lower()
        summary_words = self._normalize_text(summary_fact.fact_text)
        
        # Detect polarity in summary (negation patterns)
        negation_patterns = ['no ', 'not ', 'never ', 'none ', "n't ", 'without ', 
                            'denies ', 'denied ', 'deny ']
        summary_negation = any(neg in summary_text + ' ' for neg in negation_patterns)
        
        # Check each evidence fact
        support_scores = []
        reject_scores = []
        
        for evidence in evidence_facts:
            evidence_text = evidence.fact_text.lower()
            evidence_words = self._normalize_text(evidence.fact_text)
            
            # Calculate multiple similarity metrics
            overlap = len(summary_words & evidence_words)
            
            # Jaccard similarity
            union = len(summary_words | evidence_words)
            jaccard = overlap / union if union > 0 else 0
            
            # Overlap ratio (what portion of summary is in evidence)
            overlap_ratio = overlap / len(summary_words) if len(summary_words) > 0 else 0
            
            # Combined similarity score
            similarity = max(jaccard, overlap_ratio * 0.7)
            
            # Check polarity match
            evidence_negation = (evidence.polarity == "negated")
            polarity_match = (summary_negation == evidence_negation)
            
            # Boost similarity if key entities/numbers match
            summary_entities = set(self._extract_entities(summary_fact.fact_text))
            if summary_entities and set(evidence.entities) & summary_entities:
                similarity += 0.1
            
            # Check for specific medical terms
            medical_overlap = len(summary_entities & set(evidence.entities))
            if medical_overlap > 0:
                similarity += medical_overlap * 0.05
            
            # Support: good similarity and matching polarity
            if similarity > 0.25 and polarity_match:
                support_scores.append((similarity, evidence))
            
            # Rejection: good similarity but opposite polarity
            elif similarity > 0.25 and not polarity_match:
                reject_scores.append((similarity, evidence))
        
        # Sort by score
        support_scores.sort(reverse=True, key=lambda x: x[0])
        reject_scores.sort(reverse=True, key=lambda x: x[0])
        
        # Make decision
        # Prioritize rejection over support when there's a contradiction
        if reject_scores:
            best_reject_score, best_reject_evidence = reject_scores[0]
            # If there's evidence with opposite polarity and reasonable similarity, it's a rejection
            if best_reject_score > 0.25:
                return (
                    VerificationLabel.REJECTED,
                    f"Contradicted by source fact (turn {best_reject_evidence.turn_index}): {best_reject_evidence.fact_text}"
                )
        
        if support_scores:
            # Supported by evidence
            best_support_score, best_support_evidence = support_scores[0]
            if best_support_score > 0.3:
                return (
                    VerificationLabel.SUPPORTED,
                    f"Supported by source fact (turn {best_support_evidence.turn_index}): {best_support_evidence.fact_text}"
                )
        
        # Not enough information
        return (
            VerificationLabel.NEI,
            "Cannot be verified from available source facts"
        )
    
    # ==================== STEP 4: Compute metrics ====================
    
    def compute_metrics(self) -> Metrics:
        """
        Compute fact-level precision and recall metrics.
        
        Returns:
            Metrics object with precision, recall, and counts
        """
        # Count summary fact labels
        tp = sum(1 for f in self.summary_factlist 
                if f.verification_label == VerificationLabel.SUPPORTED)
        fp = sum(1 for f in self.summary_factlist 
                if f.verification_label == VerificationLabel.REJECTED)
        nei = sum(1 for f in self.summary_factlist 
                 if f.verification_label == VerificationLabel.NEI)
        
        # Compute precision
        denominator = tp + fp
        fact_precision = tp / denominator if denominator > 0 else 0.0
        
        # Compute recall
        # Find which source facts are "recalled" (covered by supported summary facts)
        covered_source_ids = set()
        for summary_fact in self.summary_factlist:
            if summary_fact.verification_label == VerificationLabel.SUPPORTED:
                covered_source_ids.update(summary_fact.evidence_fact_ids)
        
        # Count active source facts (exclude merged ones)
        active_source_facts = [f for f in self.source_factlist 
                              if f.status != "merged"]
        
        src_covered = len(covered_source_ids)
        src_total = len(active_source_facts)
        
        fact_recall = src_covered / src_total if src_total > 0 else 0.0
        
        return Metrics(
            fact_precision=fact_precision,
            fact_recall=fact_recall,
            tp=tp,
            fp=fp,
            nei=nei,
            src_covered=src_covered,
            src_total=src_total
        )
    
    # ==================== Main Pipeline ====================
    
    def evaluate_consistency(
        self, 
        source_dialogue: List[Dict], 
        summary: str
    ) -> Dict:
        """
        Complete pipeline: evaluate factual consistency of summary against dialogue.
        
        Args:
            source_dialogue: List of dialogue turns
            summary: Summary text
            
        Returns:
            Dictionary with source_factlist, summary_factlist, and metrics
        """
        # Step 1: Build source factlist
        source_factlist = self.build_source_factlist(source_dialogue)
        
        # Step 2: Build summary factlist
        summary_factlist = self.build_summary_factlist(summary)
        
        # Step 3: Verify summary facts
        verified_summary = self.verify_summary_facts()
        
        # Step 4: Compute metrics
        metrics = self.compute_metrics()
        
        return {
            'source_factlist': source_factlist,
            'summary_factlist': verified_summary,
            'metrics': metrics
        }


def format_output(result: Dict) -> str:
    """Format the evaluation results for display"""
    output = []
    
    output.append("=" * 80)
    output.append("MEDICAL DIALOGUE FACT-CHECKING RESULTS")
    output.append("=" * 80)
    
    # Source Facts
    output.append("\n📋 SOURCE FACTS EXTRACTED:")
    output.append("-" * 80)
    for fact in result['source_factlist']:
        if fact.status != "merged":
            status_marker = "⚠️ " if fact.status == "conflicting" else ""
            output.append(f"\n{status_marker}ID: {fact.fact_id}")
            output.append(f"  Speaker: {fact.speaker}")
            output.append(f"  Fact: {fact.fact_text}")
            output.append(f"  Turn {fact.turn_index}, Sentence {fact.sentence_index}")
            if fact.polarity == "negated":
                output.append(f"  Polarity: NEGATED")
            if fact.time_scope:
                output.append(f"  Time: {fact.time_scope}")
            if fact.conflict_group_id:
                output.append(f"  ⚠️ Conflict Group: {fact.conflict_group_id}")
    
    # Summary Facts
    output.append("\n\n📝 SUMMARY FACTS VERIFICATION:")
    output.append("-" * 80)
    for fact in result['summary_factlist']:
        label = fact.verification_label.value if fact.verification_label else "Unknown"
        icon = "✅" if label == "Supported" else ("❌" if label == "Rejected" else "❓")
        
        output.append(f"\n{icon} ID: {fact.summary_fact_id}")
        output.append(f"  Fact: {fact.fact_text}")
        output.append(f"  Label: {label}")
        output.append(f"  Evidence: {fact.evidence_fact_ids}")
        output.append(f"  Justification: {fact.justification}")
        if fact.ambiguity_reason:
            output.append(f"  Ambiguity: {fact.ambiguity_reason}")
    
    # Metrics
    output.append("\n\n📊 METRICS:")
    output.append("-" * 80)
    metrics = result['metrics']
    output.append(f"Fact Precision: {metrics.fact_precision:.2%} ({metrics.tp} supported / {metrics.tp + metrics.fp} claims)")
    output.append(f"Fact Recall: {metrics.fact_recall:.2%} ({metrics.src_covered} / {metrics.src_total} source facts covered)")
    output.append(f"\nBreakdown:")
    output.append(f"  ✅ True Positives (Supported): {metrics.tp}")
    output.append(f"  ❌ False Positives (Rejected): {metrics.fp}")
    output.append(f"  ❓ Not Enough Info (NEI): {metrics.nei}")
    
    output.append("\n" + "=" * 80)
    
    return "\n".join(output)


if __name__ == "__main__":
    # Example usage
    print("Medical Dialogue Fact-Checking Agent\n")
    
    # Example medical dialogue
    dialogue = [
        {
            "speaker": "patient",
            "utterance": "I've been having severe headaches for the past week. The pain is mostly on the right side."
        },
        {
            "speaker": "doctor",
            "utterance": "How often do you get these headaches? Are you taking any medication currently?"
        },
        {
            "speaker": "patient",
            "utterance": "Almost daily. I'm taking ibuprofen 400mg twice a day, but it doesn't help much."
        },
        {
            "speaker": "doctor",
            "utterance": "I see. Do you have any nausea or sensitivity to light with these headaches?"
        },
        {
            "speaker": "patient",
            "utterance": "Yes, sometimes I feel nauseous. No light sensitivity though."
        },
        {
            "speaker": "doctor",
            "utterance": "Based on your symptoms, this could be migraine. I recommend trying sumatriptan 50mg. Take it at the onset of headache."
        }
    ]
    
    # Example summary (with some inaccuracies for testing)
    summary = """Patient reports daily severe headaches on the right side for one week. 
    Currently taking ibuprofen 400mg without relief. Patient experiences light sensitivity. 
    Doctor diagnosed migraine and prescribed sumatriptan 50mg."""
    
    # Run the fact checker
    checker = MedicalFactChecker()
    result = checker.evaluate_consistency(dialogue, summary)
    
    # Print formatted results
    print(format_output(result))
