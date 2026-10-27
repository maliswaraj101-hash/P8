
import json
import os

from models.rag_engine import RAGEngine


def populate_schedule3_knowledge():
    """Populate the knowledge base with Schedule III regulations and examples"""
    
    rag_engine = RAGEngine()
    
    # Schedule III regulatory documents
    schedule3_docs = [
        {
            'content': '''Schedule III Part I - Balance Sheet Format:
            I. EQUITY AND LIABILITIES
            (1) Shareholders' funds
                (a) Share capital
                (b) Reserves and surplus
            (2) Share application money pending allotment
            (3) Non-current liabilities
                (a) Long-term borrowings
                (b) Deferred tax liabilities (Net)
                (c) Other long-term liabilities
                (d) Long-term provisions
            (4) Current liabilities
                (a) Short-term borrowings
                (b) Trade payables
                (c) Other current liabilities
                (d) Short-term provisions''',
            'source': 'Companies Act 2013 - Schedule III',
            'type': 'regulation',
            'section': 'balance_sheet_format'
        },
        {
            'content': '''Schedule III Part II - Assets Format:
            II. ASSETS
            (1) Non-current assets
                (a) Property, Plant and Equipment
                    (i) Tangible assets
                    (ii) Intangible assets
                    (iii) Capital work-in-progress
                    (iv) Intangible assets under development
                (b) Non-current investments
                (c) Deferred tax assets (net)
                (d) Long-term loans and advances
                (e) Other non-current assets
            (2) Current assets
                (a) Current investments
                (b) Inventories
                (c) Trade receivables
                (d) Cash and cash equivalents
                (e) Short-term loans and advances
                (f) Other current assets''',
            'source': 'Companies Act 2013 - Schedule III',
            'type': 'regulation',
            'section': 'assets_format'
        },
        {
            'content': '''General Instructions for Schedule III:
            1. Figures in the financial statements shall be rounded off to the nearest hundreds, thousands, lakhs or crores as may be considered appropriate
            2. Previous year's figures shall be regrouped/rearranged wherever necessary
            3. Assets and liabilities should be classified as current or non-current as per the operating cycle concept
            4. The Balance Sheet equation must be maintained: Assets = Equity + Liabilities''',
            'source': 'Companies Act 2013 - Schedule III General Instructions',
            'type': 'regulation',
            'section': 'general_instructions'
        }
    ]
    
    # Common audit findings and compliance issues
    audit_cases = [
        {
            'content': '''Common Schedule III Compliance Issue - Balance Sheet Equation:
            Issue: Total Assets not equal to Total Equity + Liabilities
            Root Causes: 
            - Mathematical errors in summation
            - Misclassification of items
            - Omitted line items
            Resolution: Verify all calculations and ensure proper classification''',
            'source': 'Audit Best Practices',
            'type': 'audit_case',
            'section': 'balance_equation'
        },
        {
            'content': '''Schedule III Rounding Compliance:
            Requirement: Amounts should be rounded to nearest hundreds/thousands/lakhs
            Common Violations:
            - Exact figures without rounding
            - Inconsistent rounding across line items
            - Rounding that creates balance mismatches
            Best Practice: Apply consistent rounding methodology''',
            'source': 'Audit Best Practices',
            'type': 'audit_case',
            'section': 'rounding'
        }
    ]
    
    # Add documents to knowledge base
    rag_engine.add_documents_to_knowledge_base(schedule3_docs, "schedule3_knowledge")
    rag_engine.add_documents_to_knowledge_base(audit_cases, "audit_cases")
    
    print("Knowledge base populated successfully!")

if __name__ == "__main__":
    populate_schedule3_knowledge()
