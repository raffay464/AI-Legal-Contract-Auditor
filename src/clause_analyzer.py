from typing import Dict, List, Optional
from langchain_community.llms import Ollama
from src.rag_pipeline import RAGPipeline
from src.config import TARGET_CLAUSES, RISK_CRITERIA, OLLAMA_MODEL, OLLAMA_BASE_URL


class ClauseAnalyzer:
    
    def __init__(self, rag_pipeline: RAGPipeline, llm_model: str = None):
        self.rag_pipeline = rag_pipeline
        if llm_model is None:
            llm_model = OLLAMA_MODEL
        self.llm = Ollama(model=llm_model, base_url=OLLAMA_BASE_URL, temperature=0)
    
    def extract_clause(self, clause_type: str) -> Dict:
        # Try multiple query variations to improve retrieval
        queries = [
            f"Find and extract the complete {clause_type} clause from the contract.",
            f"What does the contract say about {clause_type}?",
            f"Locate any provisions related to {clause_type} in this agreement."
        ]
        
        best_result = None
        best_confidence = "none"
        
        for query in queries:
            result = self.rag_pipeline.answer_query(query, use_reranking=True)
            
            # Check if this result is better
            if result["confidence"] == "high":
                best_result = result
                break
            elif result["confidence"] == "medium" and best_confidence == "none":
                best_result = result
                best_confidence = "medium"
            elif best_result is None:
                best_result = result
        
        # Check if clause was found
        if best_result is None or "I don't know" in best_result["answer"] or not best_result["sources"]:
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
            "content": best_result["answer"],
            "summary": None,
            "risk_rating": None,
            "risk_explanation": None,
            "citations": best_result["sources"]
        }
    
    def summarize_clause(self, clause_content: str, clause_type: str) -> str:
        summary_prompt = """You are a legal expert. Summarize the following {clause_type} clause in plain English that a non-lawyer can understand.

Clause Content:
{content}

Provide a clear, concise summary (2-3 sentences) focusing on:
- What the clause requires
- Who it affects
- Key obligations or restrictions

Summary:"""
        
        prompt_text = summary_prompt.format(clause_type=clause_type, content=clause_content)
        response = self.llm.invoke(prompt_text)
        
        return response.strip()
    
    def assess_risk(self, clause_content: str, clause_type: str) -> Dict[str, str]:
        risk_keywords = RISK_CRITERIA.get(clause_type, {})
        high_risk_keywords = risk_keywords.get("high_risk_keywords", [])
        low_risk_keywords = risk_keywords.get("low_risk_keywords", [])
        
        content_lower = clause_content.lower()
        high_risk_count = sum(1 for keyword in high_risk_keywords if keyword.lower() in content_lower)
        low_risk_count = sum(1 for keyword in low_risk_keywords if keyword.lower() in content_lower)
        
        risk_prompt = """You are a legal risk assessment expert. Analyze the following {clause_type} clause and determine if it is vendor-friendly or customer-friendly.

Clause Content:
{content}

Assess the risk level as:
- HIGH: Very unfavorable terms, one-sided obligations, severe restrictions, or lack of protections
- MEDIUM: Somewhat unbalanced terms, moderate restrictions, or unclear provisions
- LOW: Balanced terms, reasonable restrictions, mutual obligations, or favorable protections

Consider:
1. Balance of obligations between parties
2. Severity of restrictions or penalties
3. Flexibility and termination rights
4. Protection of interests

Respond in this exact format:
RISK_LEVEL: [HIGH/MEDIUM/LOW]
EXPLANATION: [2-3 sentences explaining why]"""
        
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
            
            if clause_data["found"]:
                summary = self.summarize_clause(clause_data["content"], clause_type)
                risk_assessment = self.assess_risk(clause_data["content"], clause_type)
                
                clause_data["summary"] = summary
                clause_data["risk_rating"] = risk_assessment["risk_rating"]
                clause_data["risk_explanation"] = risk_assessment["risk_explanation"]
            
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
