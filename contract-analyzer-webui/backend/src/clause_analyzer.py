from typing import Dict, List, Optional
from langchain_community.llms import Ollama
from src.rag_pipeline import RAGPipeline
from src.config import TARGET_CLAUSES, RISK_CRITERIA, OLLAMA_MODEL, OLLAMA_BASE_URL


class ClauseAnalyzer:
    
    def __init__(self, rag_pipeline: RAGPipeline, llm_model: str = None):
        self.rag_pipeline = rag_pipeline
        if llm_model is None:
            llm_model = OLLAMA_MODEL
        self.llm = Ollama(
            model=llm_model, 
            base_url=OLLAMA_BASE_URL, 
            temperature=0
        )
    
    def extract_clause(self, clause_type: str) -> Dict:
        # Single optimized query - no reranking for speed
        query = f"Extract the complete text of the '{clause_type}' clause from this contract."
        
        result = self.rag_pipeline.answer_query(query, use_reranking=False)
        
        # More lenient detection - check if we got meaningful content
        answer_lower = result["answer"].lower()
        has_content = len(result["answer"]) > 50 and result["sources"]
        
        # Detect AI refusal or not found responses
        is_negative = any(phrase in answer_lower for phrase in [
            "i don't know", 
            "not found", 
            "does not contain",
            "no information",
            "cannot find",
            "i can't assist",
            "i cannot",
            "feel free to ask",
            "different topic",
            "cannot create",
            "without permission",
            "did not provide sufficient"
        ])
        
        if not has_content or is_negative:
            return {
                "clause_type": clause_type,
                "found": False,
                "content": None,
                "summary": "Clause not found in the contract.",
                "risk_rating": "N/A",
                "risk_explanation": "Cannot assess risk as clause was not found.",
                "citations": []
            }
        
        return {
            "clause_type": clause_type,
            "found": True,
            "content": result["answer"],
            "summary": None,
            "risk_rating": None,
            "risk_explanation": None,
            "citations": result["sources"]
        }
    
    def summarize_clause(self, clause_content: str, clause_type: str) -> str:
        summary_prompt = """You are a legal analyst. Provide a 2-sentence summary of this contract clause:

{content}

Summary:"""
        
        prompt_text = summary_prompt.format(clause_type=clause_type, content=clause_content[:2000])
        response = self.llm.invoke(prompt_text)
        
        return response.strip()
    
    def assess_risk(self, clause_content: str, clause_type: str) -> Dict[str, str]:
        risk_keywords = RISK_CRITERIA.get(clause_type, {})
        high_risk_keywords = risk_keywords.get("high_risk_keywords", [])
        low_risk_keywords = risk_keywords.get("low_risk_keywords", [])
        
        content_lower = clause_content.lower()
        high_risk_count = sum(1 for keyword in high_risk_keywords if keyword.lower() in content_lower)
        low_risk_count = sum(1 for keyword in low_risk_keywords if keyword.lower() in content_lower)
        
        risk_prompt = """Risk level (HIGH/MEDIUM/LOW):

{content}

RISK_LEVEL: 
EXPLANATION: """
        
        prompt_text = risk_prompt.format(clause_type=clause_type, content=clause_content)
        response = self.llm.invoke(prompt_text)
        
        response_text = response.strip()
        
        risk_level = "MEDIUM"
        explanation = "Unable to determine risk level."
        
        if "RISK_LEVEL:" in response_text:
            lines = response_text.split("\n")
            for line in lines:
                if line.startswith("RISK_LEVEL:"):
                    risk_level = line.replace("RISK_LEVEL:", "").strip()
                elif line.startswith("EXPLANATION:"):
                    explanation = line.replace("EXPLANATION:", "").strip()
        
        if high_risk_count > low_risk_count and risk_level == "MEDIUM":
            risk_level = "HIGH"
        elif low_risk_count > high_risk_count and risk_level == "MEDIUM":
            risk_level = "LOW"
        
        return {
            "risk_rating": risk_level,
            "risk_explanation": explanation
        }
    
    def analyze_all_clauses(self) -> List[Dict]:
        results = []
        
        for clause_type in TARGET_CLAUSES:
            print(f"\nAnalyzing: {clause_type}...")
            
            clause_data = self.extract_clause(clause_type)
            
            # Only do expensive LLM calls if clause was found
            if clause_data["found"]:
                print(f"  ✓ Found - summarizing and assessing risk...")
                summary = self.summarize_clause(clause_data["content"], clause_type)
                risk_assessment = self.assess_risk(clause_data["content"], clause_type)
                
                clause_data["summary"] = summary
                clause_data["risk_rating"] = risk_assessment["risk_rating"]
                clause_data["risk_explanation"] = risk_assessment["risk_explanation"]
            else:
                print(f"  ✗ Not found - skipping analysis")
            
            results.append(clause_data)
        
        return results
    
    def generate_redline_suggestion(self, clause_content: str, clause_type: str, risk_rating: str) -> Optional[str]:
        if risk_rating != "HIGH":
            return None
        
        redline_prompt = """You are a legal contract negotiation expert. The following {clause_type} clause has been identified as HIGH RISK.

Original Clause:
{content}

Suggest a more balanced alternative version of this clause that:
1. Maintains the core intent
2. Provides better protection for both parties
3. Reduces one-sided obligations
4. Adds reasonable limitations or safeguards

Provide your suggestion in this format:
SUGGESTED REVISION:
[Your revised clause text]

RATIONALE:
[Brief explanation of changes]"""
        
        prompt_text = redline_prompt.format(clause_type=clause_type, content=clause_content)
        response = self.llm.invoke(prompt_text)
        
        return response.strip()
