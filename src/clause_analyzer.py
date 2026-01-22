from typing import Dict, List, Optional
from langchain_community.llms import Ollama
from src.rag_pipeline import RAGPipeline
from src.config import TARGET_CLAUSES, RISK_CRITERIA, OLLAMA_MODEL, OLLAMA_BASE_URL

##  Class for analyzing contract clauses
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
        
##   Extract clause from contract
    def extract_clause(self, clause_type: str) -> Dict:
        query = f"""
        Locate and extract the full contract language related to {clause_type}.
        If present, return the exact clause text.
        """

        result = self.rag_pipeline.answer_query(
            query,
            use_reranking=True
        )

        answer_text = result.get("answer", "").strip()
        answer_lower = answer_text.lower()

        not_found_phrases = [
            "not found",
            "does not contain",
            "no mention",
            "not explicitly stated",
            "cannot find",
            "no relevant clause",
            "not present in the contract"
        ]
        ## Check if clause is found
        if not answer_text or any(phrase in answer_lower for phrase in not_found_phrases):
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
            "content": answer_text,
            "summary": None,
            "risk_rating": None,
            "risk_explanation": None,
            "citations": result.get("sources", [])
        }
        
    ## Summarize clause in plain English
    def summarize_clause(self, clause_content: str, clause_type: str) -> str:
        summary_prompt = f"""
        You are a legal expert. Summarize the following {clause_type} clause in plain English
        that a non-lawyer can understand.

        Clause Content:
        {clause_content}

        Provide a clear, concise summary (2–3 sentences) focusing on:
        - What the clause requires
        - Who it affects
        - Key obligations or restrictions

        Summary:
        """

        response = self.llm.invoke(summary_prompt)
        return response.strip()
    
    ## Assess risk level of clause
    def assess_risk(self, clause_content: str, clause_type: str) -> Dict[str, str]:
        risk_keywords = RISK_CRITERIA.get(clause_type, {})
        high_risk_keywords = risk_keywords.get("high_risk_keywords", [])
        low_risk_keywords = risk_keywords.get("low_risk_keywords", [])

        content_lower = clause_content.lower()
        high_risk_count = sum(1 for kw in high_risk_keywords if kw.lower() in content_lower)
        low_risk_count = sum(1 for kw in low_risk_keywords if kw.lower() in content_lower)

        risk_prompt = f"""
        You are a legal risk assessment expert.

        Analyze the following {clause_type} clause and determine its risk level.

        Clause Content:
        {clause_content}

        Risk Levels:
        - HIGH: Very one-sided or restrictive
        - MEDIUM: Some imbalance or ambiguity
        - LOW: Balanced and reasonable

        Respond in this format:
        RISK_LEVEL: HIGH / MEDIUM / LOW
        EXPLANATION: 2–3 sentence justification
        """

        response = self.llm.invoke(risk_prompt)
        response_text = response.strip()

        risk_level = "MEDIUM"
        explanation = "Risk level could not be clearly determined."

        for line in response_text.splitlines():
            if line.startswith("RISK_LEVEL:"):
                risk_level = line.replace("RISK_LEVEL:", "").strip()
            elif line.startswith("EXPLANATION:"):
                explanation = line.replace("EXPLANATION:", "").strip()

        # Keyword-based adjustment (safe fallback)
        if high_risk_count > low_risk_count and risk_level == "MEDIUM":
            risk_level = "HIGH"
        elif low_risk_count > high_risk_count and risk_level == "MEDIUM":
            risk_level = "LOW"

        return {
            "risk_rating": risk_level,
            "risk_explanation": explanation
        }
        
    ## Analyze all target clauses in the contract
    def analyze_all_clauses(self) -> List[Dict]:
        results = []

        for clause_type in TARGET_CLAUSES:
            print(f"\nAnalyzing: {clause_type}...")

            clause_data = self.extract_clause(clause_type)

            if clause_data["found"]:
                summary = self.summarize_clause(
                    clause_data["content"],
                    clause_type
                )
                risk = self.assess_risk(
                    clause_data["content"],
                    clause_type
                )

                clause_data["summary"] = summary
                clause_data["risk_rating"] = risk["risk_rating"]
                clause_data["risk_explanation"] = risk["risk_explanation"]

            results.append(clause_data)

        return results
    
    ## Generate redline suggestion for high-risk clauses
    def generate_redline_suggestion(
        self,
        clause_content: str,
        clause_type: str,
        risk_rating: str
    ) -> Optional[str]:

        if risk_rating != "HIGH":
            return None

        redline_prompt = f"""
        You are a legal contract negotiation expert.

        The following {clause_type} clause is HIGH RISK.

        Original Clause:
        {clause_content}

        Suggest a more balanced revision that:
        - Keeps original intent
        - Reduces one-sided risk
        - Adds reasonable safeguards

        Format:
        SUGGESTED REVISION:
        [Revised clause]

        RATIONALE:
        [Brief explanation]
        """

        response = self.llm.invoke(redline_prompt)
        return response.strip()
