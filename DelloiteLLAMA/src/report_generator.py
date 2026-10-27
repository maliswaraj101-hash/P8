import json
from datetime import datetime
from typing import Dict, List

class ReportGenerator:
    def __init__(self):
        self.report_template = {
            'timestamp': None,
            'document_info': {},
            'compliance_summary': {},
            'error_summary': {},
            'detailed_findings': {},
            'recommendations': [],
            'llama_analysis': None,
            'rag_analysis': None
        }
    
    def generate_report(self, parsed_data: Dict, compliance_issues: List[Dict], 
                       errors: List[Dict], llama_analysis: str) -> Dict:
        """Generate base report with improved error handling"""
        if not parsed_data or not isinstance(parsed_data, dict):
            parsed_data = {}
        if not compliance_issues or not isinstance(compliance_issues, list):
            compliance_issues = []
        if not errors or not isinstance(errors, list):
            errors = []
        if not llama_analysis or not isinstance(llama_analysis, str):
            llama_analysis = ""
        return self._generate_base_report(parsed_data, compliance_issues, errors, llama_analysis)
    
    def generate_enhanced_report(self, parsed_data: Dict, compliance_issues: List[Dict], 
                               errors: List[Dict], rag_analyses: Dict) -> Dict:
        """Generate enhanced report with robust RAG integration"""
        if not parsed_data or not isinstance(parsed_data, dict):
            parsed_data = {}
        if not compliance_issues or not isinstance(compliance_issues, list):
            compliance_issues = []
        if not errors or not isinstance(errors, list):
            errors = []
        if not rag_analyses or not isinstance(rag_analyses, dict):
            rag_analyses = {}
        
        report = self.report_template.copy()
        
        report['timestamp'] = datetime.now().isoformat()
        report['document_info'] = {
            'company_name': parsed_data.get('company_name', 'Unknown'),
            'date': parsed_data.get('date', 'Not Specified'),
            'total_assets': sum(parsed_data.get('assets', {}).values()) or 0.0,
            'total_equity_liabilities': sum(parsed_data.get('equity_liabilities', {}).values()) or 0.0
        }
        
        report['compliance_summary'] = self.summarize_compliance(compliance_issues)
        report['error_summary'] = self.summarize_errors(errors)
        report['detailed_findings'] = {
            'compliance_issues': compliance_issues,
            'detected_errors': errors
        }
        report['recommendations'] = self.generate_enhanced_recommendations(compliance_issues, errors, rag_analyses)
        report['rag_analysis'] = {
            'general_compliance': rag_analyses.get('general_compliance', {}),
            'balance_equation': rag_analyses.get('balance_equation', {}),
            'issue_resolution': rag_analyses.get('issue_resolution', {}),
            'format_review': rag_analyses.get('format_review', {}),
            'sources_consulted': self._extract_all_sources(rag_analyses)
        }
        report['overall_assessment'] = self._generate_overall_assessment(compliance_issues, errors, rag_analyses)
        
        return report
    
    def _generate_base_report(self, parsed_data: Dict, compliance_issues: List[Dict], 
                            errors: List[Dict], llama_analysis: str) -> Dict:
        """Base report generation with improved validation"""
        report = self.report_template.copy()
        
        report['timestamp'] = datetime.now().isoformat()
        report['document_info'] = {
            'company_name': parsed_data.get('company_name', 'Unknown'),
            'date': parsed_data.get('date', 'Not Specified'),
            'total_assets': sum(parsed_data.get('assets', {}).values()) or 0.0,
            'total_equity_liabilities': sum(parsed_data.get('equity_liabilities', {}).values()) or 0.0
        }
        
        report['compliance_summary'] = self.summarize_compliance(compliance_issues)
        report['error_summary'] = self.summarize_errors(errors)
        report['detailed_findings'] = {
            'compliance_issues': compliance_issues,
            'detected_errors': errors
        }
        report['recommendations'] = self.generate_recommendations(compliance_issues , errors)
        report['llama_analysis'] = llama_analysis or "No LLaMA analysis provided"
        
        return report
    
    def summarize_compliance(self, issues: List[Dict]) -> Dict:
        """Enhanced compliance summary with detailed metrics"""
        if not issues:
            return {
                'total_issues': 0,
                'high_severity': 0,
                'medium_severity': 0,
                'low_severity': 0,
                'status': 'COMPLIANT',
                'issue_categories': [],
                'most_common_issue': None
            }
        
        issue_types = [issue.get('type', 'unknown') for issue in issues]
        summary = {
            'total_issues': len(issues),
            'high_severity': len([i for i in issues if i.get('severity') == 'high']),
            'medium_severity': len([i for i in issues if i.get('severity') == 'medium']),
            'low_severity': len([i for i in issues if i.get('severity') == 'low']),
            'status': 'COMPLIANT' if len(issues) == 0 else 'NON_COMPLIANT',
            'issue_categories': list(set(issue_types)),
            'most_common_issue': max(set(issue_types), key=issue_types.count, default=None)
        }
        return summary
    
    def summarize_errors(self, errors: List[Dict]) -> Dict:
        """Enhanced error summary with impact assessment"""
        if not errors:
            return {
                'total_errors': 0,
                'high_severity': 0,
                'medium_severity': 0,
                'low_severity': 0,
                'error_types': [],
                'critical_error_types': [],
                'error_impact': 'NONE'
            }
        
        error_types = [e.get('type', 'unknown') for e in errors]
        high_severity_errors = [e for e in errors if e.get('severity') == 'high']
        impact = 'HIGH' if high_severity_errors else 'MEDIUM' if len(errors) > 3 else 'LOW'
        
        summary = {
            'total_errors': len(errors),
            'high_severity': len(high_severity_errors),
            'medium_severity': len([e for e in errors if e.get('severity') == 'medium']),
            'low_severity': len([e for e in errors if e.get('severity') == 'low']),
            'error_types': list(set(error_types)),
            'critical_error_types': list(set([e.get('type') for e in high_severity_errors])),
            'error_impact': impact
        }
        return summary
    
    def generate_recommendations(self, compliance_issues: List[Dict], errors: List[Dict]) -> List[str]:
        """Improved recommendations with prioritized actions"""
        recommendations = []
        
        # High-severity issues
        high_severity_items = [item for item in compliance_issues + errors if item.get('severity') == 'high']
        if high_severity_items:
            recommendations.append("Address high-severity issues immediately to mitigate significant compliance risks.")
            for item in high_severity_items[:3]:  # Limit to top 3 for brevity
                recommendations.append(f"Resolve {item.get('type', 'issue')}: {item.get('description', 'No description')}")
        
        # Balance sheet equation issues
        balance_issues = [item for item in compliance_issues if item.get('type') == 'balance_equation_violation']
        if balance_issues:
            diff = balance_issues[0].get('difference', 0)
            recommendations.append(f"Correct balance sheet discrepancy (difference: {diff:.2f}) to ensure Assets = Equity + Liabilities.")
        
        # Missing mandatory items
        missing_items = [item for item in compliance_issues if item.get('type') == 'missing_mandatory_item']
        if missing_items:
            missing_fields = [item.get('field', 'unknown') for item in missing_items]
            recommendations.append(f"Add missing mandatory fields ({', '.join(missing_fields[:3])}) as per Schedule III requirements.")
        
        # Mathematical errors
        math_errors = [item for item in errors if 'mathematical' in item.get('type', '').lower()]
        if math_errors:
            recommendations.append("Perform thorough review of financial calculations to correct mathematical errors.")
        
        # Data completeness
        if not compliance_issues and not errors:
            recommendations.append("Document complies with Schedule III; continue maintaining accurate reporting.")
        elif len(compliance_issues) + len(errors) < 3:
            recommendations.append("Minor issues detected; implement targeted corrections for full compliance.")
        
        return recommendations[:5]  # Limit to top 5 recommendations for clarity
    
    def generate_enhanced_recommendations(self, compliance_issues: List[Dict], 
                                        errors: List[Dict], rag_analyses: Dict) -> List[str]:
        """Enhanced recommendations with prioritized RAG insights"""
        recommendations = self.generate_recommendations(compliance_issues, errors)
        rag_recommendations = self._extract_rag_recommendations(rag_analyses)
        
        # Prioritize recommendations based on severity and source
        prioritized = []
        for rec in rag_recommendations:
            if 'high priority' in rec.lower() or 'urgent' in rec.lower():
                prioritized.append(rec)
        prioritized.extend([r for r in rag_recommendations if r not in prioritized])
        recommendations.extend(prioritized)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = [rec for rec in recommendations if not (rec in seen or seen.add(rec))]
        
        return unique_recommendations[:6]  # Limit to top 6 for enhanced report
    
    def _extract_rag_recommendations(self, rag_analyses: Dict) -> List[str]:
        """Extract prioritized RAG-based recommendations"""
        recommendations = []
        
        for analysis_type, analysis_data in rag_analyses.items():
            if not isinstance(analysis_data, dict) or 'analysis' not in analysis_data:
                continue
                
            analysis_text = analysis_data.get('analysis', '')
            if not analysis_text or not isinstance(analysis_text, str):
                continue
                
            sentences = analysis_text.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence or len(sentence) < 20:
                    continue
                    
                # Prioritize recommendations with actionable keywords
                if any(keyword in sentence.lower() for keyword in 
                      ['recommend', 'should', 'must', 'ensure', 'verify', 'correct', 'address']):
                    # Add context from analysis type
                    context = {
                        'general_compliance': 'Compliance',
                        'balance_equation': 'Balance Equation',
                        'issue_resolution': 'Issue Resolution',
 'format_review': 'Format'
                    }.get(analysis_type, 'General')
                    recommendations.append(f"RAG ({context}): {sentence}")
        
        # Sort by relevance (prioritize sentences with stronger action verbs)
        action_strength = {'must': 3, 'should': 2, 'recommend': 1, 'ensure': 2, 'verify': 2, 'correct': 3, 'address': 3}
        def score_recommendation(rec):
            score = sum(action_strength.get(word, 0) for word in rec.lower().split())
            return score
        
        recommendations.sort(key=score_recommendation, reverse=True)
        return recommendations[:4]  # Limit to top 4 RAG recommendations
    
    def _extract_all_sources(self, rag_analyses: Dict) -> List[str]:
        """Extract and validate all RAG sources"""
        all_sources = set()
        
        for analysis_data in rag_analyses.values():
            if isinstance(analysis_data, dict) and 'sources_used' in analysis_data:
                sources = analysis_data.get('sources_used', [])
                if isinstance(sources, (list, set)):
                    all_sources.update(str(source) for source in sources if source)
        
        return sorted(list(all_sources))[:10]  # Limit to top 10 sources for brevity
    
    def _generate_overall_assessment(self, compliance_issues: List[Dict], 
                                   errors: List[Dict], rag_analyses: Dict) -> Dict:
        """Improved overall assessment with weighted scoring"""
        total_issues = len(compliance_issues) + len(errors)
        high_severity_count = len([item for item in compliance_issues + errors 
                                  if item.get('severity') == 'high'])
        medium_severity_count = len([item for item in compliance_issues + errors 
                                    if item.get('severity') == 'medium'])
        
        # Weighted risk scoring
        risk_score = (high_severity_count * 5) + (medium_severity_count * 2) + (total_issues - high_severity_count - medium_severity_count)
        if risk_score > 10:
            risk_level = "HIGH"
        elif risk_score > 4:
            risk_level = "MEDIUM"
        elif risk_score > 0:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        # Enhanced RAG confidence scoring
        total_sources = len(self._extract_all_sources(rag_analyses))
        rag_confidence = (
            'HIGH' if total_sources >= 5 else
            'MEDIUM' if total_sources >= 2 else
            'LOW' if total_sources > 0 else
            'NONE'
        )
        
        return {
            'risk_level': risk_level,
            'total_findings': total_issues,
            'high_severity_findings': high_severity_count,
            'rag_sources_consulted': total_sources,
            'analysis_confidence': rag_confidence,
            'requires_immediate_action': high_severity_count > 0 or risk_score > 8,
            'compliance_status': 'COMPLIANT' if total_issues == 0 else 'NON_COMPLIANT'
        }