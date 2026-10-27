from typing import Dict,List
import re
from datetime import datetime

class ComplianceChecker:
    def __init__(self):
        # Schedule III mandatory requirements based on the PDF[1]
        self.mandatory_items = {
            'equity_liabilities': [
                'share_capital',
                'reserves'
            ],
            'assets': [
                'tangible_assets',
                'current_investments',
                'inventories',
                'trade_receivables',
                'cash_equivalents'
            ]
        }
        
        # Tolerance for balance sheet equation (can be configurable)
        self.balance_tolerance = 1.0
        
        # Minimum threshold for rounding checks
        self.rounding_threshold = 100000

    def check_compliance(self, parsed_data: Dict) -> List[Dict]:
        issues = []
        
        # Validate input data structure first
        if not self._validate_input_structure(parsed_data):
            issues.append({
                'type': 'invalid_data_structure',
                'severity': 'critical',
                'description': 'Invalid or malformed input data structure'
            })
            return issues
        
        # Check balance sheet equation
        issues.extend(self.check_balance_equation(parsed_data))
        
        # Check mandatory disclosures
        issues.extend(self.check_mandatory_items(parsed_data))
        
        # Check formatting compliance
        issues.extend(self.check_formatting(parsed_data))
        
        # Check rounding requirements
        issues.extend(self.check_rounding(parsed_data))
        
        return issues

    def check_balance_equation(self, data: Dict) -> List[Dict]:
        issues = []
        
        try:
            # Get equity and liabilities data with better error handling
            equity_liabilities = data.get('equity_liabilities', {})
            assets = data.get('assets', {})
            
            # Calculate totals with validation for numeric values
            equity_total = self._calculate_section_total(equity_liabilities, 'equity_liabilities')
            assets_total = self._calculate_section_total(assets, 'assets')
            
            # Handle cases where totals couldn't be calculated
            if equity_total is None or assets_total is None:
                issues.append({
                    'type': 'balance_calculation_error',
                    'severity': 'high',
                    'description': 'Unable to calculate balance sheet totals due to invalid numeric values'
                })
                return issues
            
            difference = abs(equity_total - assets_total)
            
            if difference > self.balance_tolerance:
                issues.append({
                    'type': 'balance_equation_violation',
                    'severity': 'high',
                    'description': f'Balance sheet equation violated. Assets: {assets_total:,.2f}, Equity+Liabilities: {equity_total:,.2f}',
                    'difference': difference,
                    'assets_total': assets_total,
                    'equity_liabilities_total': equity_total
                })
            
            # Check for negative totals which shouldn't normally occur
            if equity_total < 0:
                issues.append({
                    'type': 'negative_equity_liabilities',
                    'severity': 'medium',
                    'description': f'Negative total equity and liabilities: {equity_total:,.2f}'
                })
            
            if assets_total < 0:
                issues.append({
                    'type': 'negative_assets',
                    'severity': 'medium',
                    'description': f'Negative total assets: {assets_total:,.2f}'
                })
                
        except Exception as e:
            issues.append({
                'type': 'balance_equation_error',
                'severity': 'high',
                'description': f'Error checking balance equation: {str(e)}'
            })
        
        return issues

    def check_mandatory_items(self, data: Dict) -> List[Dict]:
        issues = []
        
        for section, items in self.mandatory_items.items():
            section_data = data.get(section, {})
            
            # Check if section exists
            if not section_data:
                issues.append({
                    'type': 'missing_section',
                    'severity': 'high',
                    'description': f'Required section "{section}" is completely missing',
                    'section': section
                })
                continue
            
            for item in items:
                if item not in section_data:
                    issues.append({
                        'type': 'missing_mandatory_item',
                        'severity': 'medium',
                        'description': f'Missing mandatory item: {item} in {section}',
                        'section': section,
                        'item': item
                    })
                else:
                    # Check if the item has a valid value
                    value = section_data[item]
                    if value is None:
                        issues.append({
                            'type': 'null_mandatory_item',
                            'severity': 'medium',
                            'description': f'Mandatory item "{item}" in "{section}" has null value',
                            'section': section,
                            'item': item
                        })
                    elif not self._is_valid_numeric(value):
                        issues.append({
                            'type': 'invalid_mandatory_item_value',
                            'severity': 'medium',
                            'description': f'Mandatory item "{item}" in "{section}" has invalid numeric value: {value}',
                            'section': section,
                            'item': item,
                            'value': value
                        })
        
        return issues

    def check_formatting(self, data: Dict) -> List[Dict]:
        issues = []
        
        # Check company name
        company_name = data.get('company_name')
        if not company_name:
            issues.append({
                'type': 'missing_company_name',
                'severity': 'high',
                'description': 'Company name is missing from the document'
            })
        elif not isinstance(company_name, str) or len(company_name.strip()) == 0:
            issues.append({
                'type': 'invalid_company_name',
                'severity': 'high',
                'description': 'Company name is empty or invalid',
                'value': company_name
            })
        elif len(company_name.strip()) < 2:
            issues.append({
                'type': 'company_name_too_short',
                'severity': 'medium',
                'description': 'Company name appears to be too short',
                'value': company_name
            })
        
        # Check date with better validation
        date = data.get('date')
        if not date:
            issues.append({
                'type': 'missing_date',
                'severity': 'high',
                'description': 'Balance sheet date is missing'
            })
        else:
            date_issues = self._validate_date(date)
            issues.extend(date_issues)
        
        # Check for required financial statement headers/titles
        if not data.get('statement_type'):
            issues.append({
                'type': 'missing_statement_type',
                'severity': 'medium',
                'description': 'Financial statement type is not specified'
            })
        
        return issues

    def check_rounding(self, data: Dict) -> List[Dict]:
        issues = []
        
        try:
            # Collect all amounts with their context
            all_amounts = []
            
            # Add amounts from equity_liabilities with context
            for item, value in data.get('equity_liabilities', {}).items():
                if self._is_valid_numeric(value):
                    all_amounts.append({
                        'value': float(value),
                        'item': item,
                        'section': 'equity_liabilities'
                    })
            
            # Add amounts from assets with context
            for item, value in data.get('assets', {}).items():
                if self._is_valid_numeric(value):
                    all_amounts.append({
                        'value': float(value),
                        'item': item,
                        'section': 'assets'
                    })
            
            for amount_info in all_amounts:
                amount = amount_info['value']
                
                # Check rounding for large amounts
                if abs(amount) > self.rounding_threshold:
                    # Check if rounded to nearest hundred
                    if amount % 100 != 0:
                        issues.append({
                            'type': 'rounding_issue',
                            'severity': 'low',
                            'description': f'Amount {amount:,.2f} in {amount_info["section"]}.{amount_info["item"]} may need rounding to hundreds as per Schedule III',
                            'amount': amount,
                            'item': amount_info['item'],
                            'section': amount_info['section'],
                            'suggested_value': round(amount / 100) * 100
                        })
                
                # Check for unusual precision (too many decimal places)
                if self._has_excessive_precision(amount):
                    issues.append({
                        'type': 'excessive_precision',
                        'severity': 'low',
                        'description': f'Amount {amount} has excessive decimal precision',
                        'amount': amount,
                        'item': amount_info['item'],
                        'section': amount_info['section']
                    })
                    
        except Exception as e:
            issues.append({
                'type': 'rounding_check_error',
                'severity': 'low',
                'description': f'Error checking rounding requirements: {str(e)}'
            })
        
        return issues

    def _validate_input_structure(self, data: Dict) -> bool:
        """Validate basic structure of input data"""
        if not isinstance(data, dict):
            return False
        
        # Check for required top-level keys
        required_sections = ['equity_liabilities', 'assets']
        for section in required_sections:
            if section in data and not isinstance(data[section], dict):
                return False
        
        return True

    def _calculate_section_total(self, section_data: Dict, section_name: str) -> float:
        """Calculate total for a section with proper error handling"""
        try:
            total = 0.0
            for key, value in section_data.items():
                if self._is_valid_numeric(value):
                    total += float(value)
                elif value is not None:
                    # Log problematic values but continue calculation
                    continue
            return total
        except Exception:
            return None

    def _is_valid_numeric(self, value) -> bool:
        """Check if a value is a valid numeric value"""
        if value is None:
            return False
        
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    def _validate_date(self, date) -> List[Dict]:
        """Validate date format and reasonableness"""
        issues = []
        
        if not isinstance(date, str):
            issues.append({
                'type': 'invalid_date_format',
                'severity': 'medium',
                'description': f'Date should be a string, got {type(date).__name__}',
                'value': date
            })
            return issues
        
        # Try to parse common date formats
        date_formats = ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d', '%d-%b-%Y']
        parsed_date = None
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date.strip(), fmt)
                break
            except ValueError:
                continue
        
        if parsed_date is None:
            issues.append({
                'type': 'unparseable_date',
                'severity': 'medium',
                'description': f'Date format not recognized: {date}',
                'value': date
            })
        else:
            # Check if date is reasonable (not too far in future or past)
            current_year = datetime.now().year
            if parsed_date.year > current_year + 1:
                issues.append({
                    'type': 'future_date',
                    'severity': 'medium',
                    'description': f'Balance sheet date appears to be in the future: {date}',
                    'value': date
                })
            elif parsed_date.year < current_year - 10:
                issues.append({
                    'type': 'very_old_date',
                    'severity': 'low',
                    'description': f'Balance sheet date is more than 10 years old: {date}',
                    'value': date
                })
        
        return issues

    def _has_excessive_precision(self, amount: float) -> bool:
        """Check if amount has too many decimal places"""
        # Convert to string to check decimal places
        amount_str = f"{amount:.10f}".rstrip('0')
        if '.' in amount_str:
            decimal_places = len(amount_str.split('.')[1])
            return decimal_places > 2
        return False