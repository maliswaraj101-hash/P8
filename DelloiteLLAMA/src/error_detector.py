from typing import Dict, List
import re
from datetime import datetime

class ErrorDetector:
    def __init__(self):
        self.error_patterns = {
            'negative_values': r'-\d+',
            'zero_totals': r'Total[:\s]*0',
            'formatting_errors': r'[^\d,\.\s\-]'
        }
        
        # Items that can legitimately be negative
        self.allowed_negative_items = {'reserves', 'accumulated_losses', 'current_year_loss', 'retained_earnings'}
        
        # Critical items that should typically not be zero
        self.critical_non_zero_items = {'share_capital', 'tangible_assets'}
        
        # Reasonable ratio thresholds
        self.ratio_thresholds = {
            'cash_ratio': 0.5,  # Cash to total assets
            'debt_ratio': 0.8,  # Total debt to total assets
            'round_numbers_threshold': 0.7  # Percentage of round numbers allowed
        }
    
    def detect_errors(self, parsed_data: Dict) -> List[Dict]:
        errors = []
        
        # Validate input structure first
        if not self._validate_input_structure(parsed_data):
            errors.append({
                'type': 'invalid_input_structure',
                'severity': 'critical',
                'description': 'Invalid or malformed input data structure'
            })
            return errors
        
        # Check for mathematical errors
        errors.extend(self.check_mathematical_errors(parsed_data))
        
        # Check for data consistency
        errors.extend(self.check_data_consistency(parsed_data))
        
        # Check for formatting issues
        errors.extend(self.check_formatting_issues(parsed_data))
        
        # Check for logical errors
        errors.extend(self.check_logical_errors(parsed_data))
        
        # Add pattern anomaly detection
        errors.extend(self.detect_pattern_anomalies(parsed_data))
        
        return errors
    
    def check_mathematical_errors(self, data: Dict) -> List[Dict]:
        errors = []
        
        try:
            all_sections = {
                'equity_liabilities': data.get('equity_liabilities', {}),
                'assets': data.get('assets', {})
            }
            
            for section_name, section in all_sections.items():
                if not isinstance(section, dict):
                    errors.append({
                        'type': 'invalid_section_type',
                        'severity': 'high',
                        'description': f'Section {section_name} is not a dictionary',
                        'section': section_name,
                        'actual_type': type(section).__name__
                    })
                    continue
                
                for key, value in section.items():
                    # Check if value is numeric
                    if not self._is_numeric(value):
                        errors.append({
                            'type': 'non_numeric_value',
                            'severity': 'medium',
                            'description': f'Non-numeric value found in {section_name}.{key}: {value}',
                            'section': section_name,
                            'field': key,
                            'value': value,
                            'value_type': type(value).__name__
                        })
                        continue
                    
                    numeric_value = float(value)
                    
                    # Check for negative values where they shouldn't be
                    if numeric_value < 0 and key.lower() not in self.allowed_negative_items:
                        errors.append({
                            'type': 'negative_value_error',
                            'severity': 'medium',
                            'description': f'Negative value found in {section_name}.{key}: {numeric_value:,.2f}',
                            'section': section_name,
                            'field': key,
                            'value': numeric_value
                        })
                    
                    # Check for extremely large values (potential data entry errors)
                    if abs(numeric_value) > 1e12:  # 1 trillion
                        errors.append({
                            'type': 'extremely_large_value',
                            'severity': 'medium',
                            'description': f'Extremely large value in {section_name}.{key}: {numeric_value:,.2f}',
                            'section': section_name,
                            'field': key,
                            'value': numeric_value
                        })
                    
                    # Check for precision issues (too many decimal places)
                    if self._has_excessive_decimal_places(numeric_value):
                        errors.append({
                            'type': 'excessive_decimal_precision',
                            'severity': 'low',
                            'description': f'Value has excessive decimal places in {section_name}.{key}: {numeric_value}',
                            'section': section_name,
                            'field': key,
                            'value': numeric_value
                        })
        
        except Exception as e:
            errors.append({
                'type': 'mathematical_check_error',
                'severity': 'high',
                'description': f'Error during mathematical validation: {str(e)}'
            })
        
        return errors
    
    def check_data_consistency(self, data: Dict) -> List[Dict]:
        errors = []
        
        try:
            equity_liabilities = data.get('equity_liabilities', {})
            assets = data.get('assets', {})
            
            # Ensure sections contain only numeric values for calculation
            clean_equity_liabilities = self._get_numeric_values(equity_liabilities)
            clean_assets = self._get_numeric_values(assets)
            
            if not clean_equity_liabilities and not clean_assets:
                errors.append({
                    'type': 'no_valid_numeric_data',
                    'severity': 'critical',
                    'description': 'No valid numeric data found in financial statements'
                })
                return errors
            
            # Calculate expected totals with better error handling
            expected_equity_total = sum(clean_equity_liabilities.values()) if clean_equity_liabilities else 0
            expected_assets_total = sum(clean_assets.values()) if clean_assets else 0
            
            # Check fundamental balance sheet equation
            if abs(expected_equity_total - expected_assets_total) > 1:
                errors.append({
                    'type': 'balance_sheet_imbalance',
                    'severity': 'critical',
                    'description': f'Balance sheet does not balance: Assets ({expected_assets_total:,.2f}) ≠ Equity + Liabilities ({expected_equity_total:,.2f})',
                    'assets_total': expected_assets_total,
                    'equity_liabilities_total': expected_equity_total,
                    'difference': abs(expected_equity_total - expected_assets_total)
                })
            
            # Check if declared totals match calculated totals (if provided)
            totals_section = data.get('totals', {})
            if totals_section:
                declared_assets_total = totals_section.get('total_assets')
                declared_equity_total = totals_section.get('total_equity_liabilities')
                
                if declared_assets_total is not None and self._is_numeric(declared_assets_total):
                    declared_assets_total = float(declared_assets_total)
                    if abs(declared_assets_total - expected_assets_total) > 1:
                        errors.append({
                            'type': 'total_mismatch',
                            'severity': 'high',
                            'description': f'Declared total assets ({declared_assets_total:,.2f}) does not match sum of individual assets ({expected_assets_total:,.2f})',
                            'declared_total': declared_assets_total,
                            'calculated_total': expected_assets_total,
                            'difference': abs(declared_assets_total - expected_assets_total)
                        })
                
                if declared_equity_total is not None and self._is_numeric(declared_equity_total):
                    declared_equity_total = float(declared_equity_total)
                    if abs(declared_equity_total - expected_equity_total) > 1:
                        errors.append({
                            'type': 'equity_total_mismatch',
                            'severity': 'high',
                            'description': f'Declared total equity+liabilities ({declared_equity_total:,.2f}) does not match sum ({expected_equity_total:,.2f})',
                            'declared_total': declared_equity_total,
                            'calculated_total': expected_equity_total,
                            'difference': abs(declared_equity_total - expected_equity_total)
                        })
            
            # Check for missing complementary items
            self._check_complementary_items(clean_assets, clean_equity_liabilities, errors)
            
        except Exception as e:
            errors.append({
                'type': 'consistency_check_error',
                'severity': 'high',
                'description': f'Error during consistency validation: {str(e)}'
            })
        
        return errors
    
    def check_formatting_issues(self, data: Dict) -> List[Dict]:
        errors = []
        
        try:
            # Enhanced date validation
            date_str = data.get('date')
            if date_str:
                date_errors = self._validate_date_format(date_str)
                errors.extend(date_errors)
            
            # Enhanced company name validation
            company_name = data.get('company_name')
            if company_name:
                name_errors = self._validate_company_name(company_name)
                errors.extend(name_errors)
            
            # Check for missing essential formatting elements
            essential_fields = ['company_name', 'date', 'statement_type']
            for field in essential_fields:
                if not data.get(field):
                    errors.append({
                        'type': 'missing_essential_field',
                        'severity': 'medium',
                        'description': f'Missing essential field: {field}',
                        'field': field
                    })
            
            # Check for proper currency specification
            currency = data.get('currency')
            if currency and not self._validate_currency_format(currency):
                errors.append({
                    'type': 'invalid_currency_format',
                    'severity': 'low',
                    'description': f'Currency format may be invalid: {currency}',
                    'field': 'currency',
                    'value': currency
                })
                
        except Exception as e:
            errors.append({
                'type': 'formatting_check_error',
                'severity': 'medium',
                'description': f'Error during formatting validation: {str(e)}'
            })
        
        return errors
    
    def check_logical_errors(self, data: Dict) -> List[Dict]:
        errors = []
        
        try:
            equity_liabilities = self._get_numeric_values(data.get('equity_liabilities', {}))
            assets = self._get_numeric_values(data.get('assets', {}))
            
            if not assets:
                return errors
            
            total_assets = sum(assets.values())
            
            # Enhanced cash ratio check
            cash = assets.get('cash_equivalents', 0)
            if cash > 0 and total_assets > 0:
                cash_ratio = cash / total_assets
                if cash_ratio > self.ratio_thresholds['cash_ratio']:
                    errors.append({
                        'type': 'unusual_cash_ratio',
                        'severity': 'low',
                        'description': f'Cash equivalents represent {cash_ratio*100:.1f}% of total assets, which is unusually high',
                        'ratio': cash_ratio,
                        'cash_amount': cash,
                        'total_assets': total_assets,
                        'threshold': self.ratio_thresholds['cash_ratio']
                    })
            
            # Check for zero values in critical items
            all_items = {**equity_liabilities, **assets}
            for item in self.critical_non_zero_items:
                if item in all_items and all_items[item] == 0:
                    errors.append({
                        'type': 'zero_critical_value',
                        'severity': 'medium',
                        'description': f'Critical item {item} has zero value, which may indicate an error',
                        'field': item,
                        'value': 0
                    })
            
            # Check for logical inconsistencies in related items
            self._check_logical_relationships(assets, equity_liabilities, errors)
            
            # Check for unusual asset composition
            self._check_asset_composition(assets, total_assets, errors)
            
        except Exception as e:
            errors.append({
                'type': 'logical_check_error',
                'severity': 'medium',
                'description': f'Error during logical validation: {str(e)}'
            })
        
        return errors
    
    def detect_pattern_anomalies(self, data: Dict) -> List[Dict]:
        """Detect unusual patterns in the financial data"""
        errors = []
        
        try:
            # Collect all numeric values with context
            all_values = []
            all_sections = {
                'equity_liabilities': data.get('equity_liabilities', {}),
                'assets': data.get('assets', {})
            }
            
            for section_name, section in all_sections.items():
                clean_section = self._get_numeric_values(section)
                for key, value in clean_section.items():
                    if value > 0:  # Only consider positive values
                        all_values.append({
                            'value': value,
                            'section': section_name,
                            'item': key
                        })
            
            if not all_values:
                return errors
            
            # Check for excessive round numbers
            round_numbers = []
            for item in all_values:
                value = item['value']
                # Check multiple levels of roundness
                if value % 10000000 == 0:  # 1 crore
                    round_numbers.append({**item, 'round_level': 'crore'})
                elif value % 1000000 == 0:  # 10 lakhs
                    round_numbers.append({**item, 'round_level': 'lakh'})
                elif value % 100000 == 0:  # 1 lakh
                    round_numbers.append({**item, 'round_level': 'lakh_small'})
            
            if len(all_values) > 0:
                round_ratio = len(round_numbers) / len(all_values)
                if round_ratio > self.ratio_thresholds['round_numbers_threshold']:
                    errors.append({
                        'type': 'excessive_round_numbers',
                        'severity': 'low',
                        'description': f'{len(round_numbers)} out of {len(all_values)} values ({round_ratio*100:.1f}%) are round numbers, which may indicate estimates',
                        'round_count': len(round_numbers),
                        'total_count': len(all_values),
                        'ratio': round_ratio,
                        'threshold': self.ratio_thresholds['round_numbers_threshold'],
                        'round_details': round_numbers[:5]  # Show first 5 examples
                    })
            
            # Check for duplicate values (potential copy-paste errors)
            value_counts = {}
            for item in all_values:
                value = item['value']
                if value not in value_counts:
                    value_counts[value] = []
                value_counts[value].append(item)
            
            duplicates = {v: items for v, items in value_counts.items() if len(items) > 1 and v > 1000}
            if duplicates:
                errors.append({
                    'type': 'duplicate_values_detected',
                    'severity': 'low',
                    'description': f'Found {len(duplicates)} values that appear multiple times, which may indicate copy-paste errors',
                    'duplicate_count': len(duplicates),
                    'examples': list(duplicates.items())[:3]  # Show first 3 examples
                })
                
        except Exception as e:
            errors.append({
                'type': 'pattern_analysis_error',
                'severity': 'low',
                'description': f'Error during pattern analysis: {str(e)}'
            })
        
        return errors
    
    # Helper methods
    def _validate_input_structure(self, data: Dict) -> bool:
        """Validate basic structure of input data"""
        return isinstance(data, dict) and len(data) > 0
    
    def _is_numeric(self, value) -> bool:
        """Check if a value can be converted to float"""
        if value is None:
            return False
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _get_numeric_values(self, section: Dict) -> Dict:
        """Extract only numeric values from a section"""
        return {k: float(v) for k, v in section.items() if self._is_numeric(v)}
    
    def _has_excessive_decimal_places(self, value: float, max_places: int = 2) -> bool:
        """Check if a float has too many decimal places"""
        try:
            decimal_str = f"{value:.10f}".rstrip('0')
            if '.' in decimal_str:
                decimal_places = len(decimal_str.split('.')[1])
                return decimal_places > max_places
        except:
            pass
        return False
    
    def _validate_date_format(self, date_str: str) -> List[Dict]:
        """Enhanced date validation"""
        errors = []
        
        if not isinstance(date_str, str):
            errors.append({
                'type': 'date_type_error',
                'severity': 'medium',
                'description': f'Date should be string, got {type(date_str).__name__}',
                'field': 'date',
                'value': date_str
            })
            return errors
        
        # Try multiple date formats
        date_formats = [
            r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
            r'\d{4}/\d{2}/\d{2}'   # YYYY/MM/DD
        ]
        
        format_matched = any(re.match(pattern, date_str.strip()) for pattern in date_formats)
        
        if not format_matched:
            errors.append({
                'type': 'date_format_error',
                'severity': 'low',
                'description': f'Date format may not be standard: {date_str}',
                'field': 'date',
                'value': date_str,
                'expected_formats': ['DD-MM-YYYY', 'YYYY-MM-DD', 'DD/MM/YYYY', 'YYYY/MM/DD']
            })
        
        return errors
    
    def _validate_company_name(self, company_name: str) -> List[Dict]:
        """Enhanced company name validation"""
        errors = []
        
        if not isinstance(company_name, str):
            errors.append({
                'type': 'company_name_type_error',
                'severity': 'medium',
                'description': f'Company name should be string, got {type(company_name).__name__}',
                'field': 'company_name',
                'value': company_name
            })
            return errors
        
        name = company_name.strip()
        
        if len(name) < 3:
            errors.append({
                'type': 'company_name_error',
                'severity': 'medium',
                'description': f'Company name appears too short: "{name}"',
                'field': 'company_name',
                'value': company_name,
                'length': len(name)
            })
        
        if len(name) > 200:
            errors.append({
                'type': 'company_name_too_long',
                'severity': 'low',
                'description': f'Company name appears unusually long ({len(name)} characters)',
                'field': 'company_name',
                'value': company_name,
                'length': len(name)
            })
        
        return errors
    
    def _validate_currency_format(self, currency: str) -> bool:
        """Validate currency format"""
        if not isinstance(currency, str):
            return False
        
        # Common currency codes
        common_currencies = ['INR', 'USD', 'EUR', 'GBP', 'JPY', 'Rs.', 'Rs', '$', '€', '£']
        currency_upper = currency.strip().upper()
        
        return any(curr.upper() in currency_upper for curr in common_currencies)
    
    def _check_complementary_items(self, assets: Dict, equity_liabilities: Dict, errors: List[Dict]):
        """Check for missing complementary financial items"""
        # If there are current assets, there should typically be current liabilities
        current_assets = assets.get('current_assets', 0) or assets.get('inventories', 0) or assets.get('trade_receivables', 0)
        current_liabilities = equity_liabilities.get('current_liabilities', 0) or equity_liabilities.get('trade_payables', 0)
        
        if current_assets > 0 and current_liabilities == 0:
            errors.append({
                'type': 'missing_current_liabilities',
                'severity': 'low',
                'description': 'Current assets present but no current liabilities found, which is unusual',
                'current_assets': current_assets
            })
    
    def _check_logical_relationships(self, assets: Dict, equity_liabilities: Dict, errors: List[Dict]):
        """Check logical relationships between financial items"""
        # Share capital should not exceed total assets significantly
        share_capital = equity_liabilities.get('share_capital', 0)
        total_assets = sum(assets.values()) if assets else 0
        
        if share_capital > 0 and total_assets > 0 and share_capital > total_assets * 1.5:
            errors.append({
                'type': 'share_capital_exceeds_assets',
                'severity': 'medium',
                'description': f'Share capital ({share_capital:,.2f}) significantly exceeds total assets ({total_assets:,.2f})',
                'share_capital': share_capital,
                'total_assets': total_assets,
                'ratio': share_capital / total_assets
            })
    
    def _check_asset_composition(self, assets: Dict, total_assets: float, errors: List[Dict]):
        """Check for unusual asset composition"""
        if total_assets <= 0:
            return
        
        # Check if any single asset dominates (>90% of total)
        for asset_name, asset_value in assets.items():
            if asset_value > 0:
                ratio = asset_value / total_assets
                if ratio > 0.9:
                    errors.append({
                        'type': 'single_asset_dominance',
                        'severity': 'low',
                        'description': f'{asset_name} represents {ratio*100:.1f}% of total assets, which is unusual',
                        'asset': asset_name,
                        'value': asset_value,
                        'total_assets': total_assets,
                        'ratio': ratio
                    })  