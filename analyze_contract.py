#!/usr/bin/env python3
"""
AI Legal Contract Auditor - PDF Analysis Script

This script analyzes a legal contract PDF and generates a comprehensive PDF report
containing all extracted clauses, risk assessments, summaries, and citations.

Usage:
    python analyze_contract.py <contract.pdf> [--output report.pdf] [--redline] [--qa]

Example:
    python analyze_contract.py contract.pdf --output analysis_report.pdf --redline --qa
"""

import sys
import os
import argparse
from pathlib import Path
from src.main import LegalContractAuditor
from src.pdf_report_generator import LegalContractPDFReport

## Main function to parse arguments and run analysis
def main():
    parser = argparse.ArgumentParser(
        description='Analyze legal contracts and generate comprehensive PDF reports'
    )
    parser.add_argument(
        'contract',
        type=str,
        help='Path to the contract PDF file to analyze'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output PDF report path (default: <contract_name>_analysis_report.pdf)'
    )
    parser.add_argument(
        '--redline',
        action='store_true',
        help='Include redline suggestions for high-risk clauses'
    )
    parser.add_argument(
        '--qa',
        action='store_true',
        help='Include Q&A section with common contract questions'
    )
    parser.add_argument(
        '--rebuild',
        action='store_true',
        help='Rebuild vector database (use for first analysis or when changing contracts)'
    )
    
    args = parser.parse_args()
    
    # Validate contract path
    contract_path = Path(args.contract)
    if not contract_path.exists():
        print(f"❌ Error: Contract file not found: {args.contract}")
        sys.exit(1)
    
    if not contract_path.suffix.lower() == '.pdf':
        print(f"❌ Error: File must be a PDF: {args.contract}")
        sys.exit(1)
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = contract_path.stem + "_analysis_report.pdf"
    
    print("="*80)
    print("AI LEGAL CONTRACT AUDITOR")
    print("="*80)
    print(f"\n📄 Contract: {contract_path.name}")
    print(f"📊 Output Report: {output_path}")
    print(f"🔍 Include Redlines: {'Yes' if args.redline else 'No'}")
    print(f"❓ Include Q&A: {'Yes' if args.qa else 'No'}")
    print("\n" + "="*80)
    
    # Initialize auditor
    print("\n🚀 Initializing AI Legal Contract Auditor...")
    auditor = LegalContractAuditor()
    
    # Process contract
    print(f"\n📖 Processing contract{'(rebuilding index)' if args.rebuild else ''}...")
    auditor.process_contracts([str(contract_path)], rebuild_index=args.rebuild)
    
    # Analyze clauses
    print("\n🔍 Analyzing contract clauses...")
    print("   - IP Ownership Assignment")
    print("   - Price Restrictions")
    print("   - Non-compete, Exclusivity, No-solicit of Customers")
    print("   - Termination for Convenience")
    print("   - Governing Law")
    
    results = auditor.analyze_contract(include_redline=args.redline)
    
    # Generate PDF report
    print(f"\n📝 Generating PDF report: {output_path}")
    report = LegalContractPDFReport(output_path)
    
    # Add title page
    report.add_title_page(contract_path.name)
    
    # Add executive summary
    report.add_executive_summary(results)
    
    # Add each clause analysis
    for result in results:
        report.add_clause_analysis(result, include_redline=args.redline)
    
    # Add Q&A section if requested
    if args.qa:
        print("\n❓ Running Q&A analysis...")
        qa_questions = [
            "What is the governing law for this contract?",
            "What are the termination conditions?",
            "Who owns the intellectual property?",
            "Are there any price restrictions or limitations?",
            "What are the non-compete or exclusivity requirements?"
        ]
        
        qa_results = []
        for question in qa_questions:
            result = auditor.query_contract(question)
            qa_results.append({
                'question': question,
                'answer': result['answer'],
                'confidence': result['confidence']
            })
        
        report.add_qa_section(qa_results)
    
    # Generate final PDF
    report.generate()
    
    # Print summary
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    
    found_count = sum(1 for r in results if r['found'])
    high_risk = sum(1 for r in results if r.get('risk_rating') == 'HIGH')
    medium_risk = sum(1 for r in results if r.get('risk_rating') == 'MEDIUM')
    low_risk = sum(1 for r in results if r.get('risk_rating') == 'LOW')
    
    print(f"\n📊 Summary:")
    print(f"   ✓ Clauses Found: {found_count}/{len(results)}")
    print(f"   🔴 High Risk: {high_risk}")
    print(f"   🟡 Medium Risk: {medium_risk}")
    print(f"   🟢 Low Risk: {low_risk}")
    
    if high_risk > 0:
        print(f"\n⚠️  WARNING: {high_risk} HIGH RISK clause(s) require immediate attention!")
    
    print(f"\n✅ Full analysis report saved to: {output_path}")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
