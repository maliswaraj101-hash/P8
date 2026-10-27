import asyncio
import concurrent.futures
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import time
import json
import yaml
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from werkzeug.utils import secure_filename
import PyPDF2
import ollama

# Import audit components
from src.document_parser import ScheduleIIIParser
from src.compliance_checker import ComplianceChecker
from src.error_detector import ErrorDetector
from src.report_generator import ReportGenerator
from models.rag_engine import RAGEngine

# Flask app setup
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend at localhost:3000

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache setup with expiration
analysis_cache = {}
CACHE_EXPIRY_SECONDS = 3600  # 1 hour

class EnhancedAuditManagementSystem:
    def __init__(self, config_path="config.yaml"):
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            self.config = {
                'model': {'name': 'mistral', 'temperature': 0.1},
                'audit_rules': {'balance_tolerance': 1.0}
            }
        
        # Initialize components
        self.parser = ScheduleIIIParser()
        self.compliance_checker = ComplianceChecker()
        self.error_detector = ErrorDetector()
        self.report_generator = ReportGenerator()
        
        # Initialize RAG engine with error handling
        try:
            self.rag_engine = RAGEngine()
            self.rag_available = True
            logger.info("RAG engine initialized successfully")
        except Exception as e:
            logger.warning(f"RAG engine initialization failed: {e}")
            self.rag_available = False

    async def analyze_document(self, file_path: str, text: str, tables: List, model_name: str = "mistral") -> Dict:
        """Fast analysis mode with async processing - 5 second response target"""
        start_time = time.time()
        logger.info("Starting FAST analysis mode...")
        
        try:
            if not text or not isinstance(text, str):
                return self._build_error_response("Empty or invalid document text", file_path, model_name, start_time)

            # Parse document
            parse_start = time.time()
            parsed_data = self.parser.parse_schedule3_from_text(text)
            logger.info(f"Document parsing completed in {time.time() - parse_start:.2f} seconds")
            
            company_name = parsed_data.get('company_name', 'Unknown Company')

            # Concurrent compliance and error detection
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                compliance_future = loop.run_in_executor(executor, self.compliance_checker.check_compliance, parsed_data)
                errors_future = loop.run_in_executor(executor, self.error_detector.detect_errors, parsed_data)
                compliance_issues, errors = await asyncio.gather(compliance_future, errors_future)
            
            logger.info(f"Compliance check: {len(compliance_issues)} issues, Error detection: {len(errors)} errors")

            # Basic LLaMA analysis with timeout
            basic_analysis = "Document processed - manual review recommended"
            if len(text) > 100:
                try:
                    basic_analysis_task = asyncio.wait_for(
                        loop.run_in_executor(executor, self.get_basic_llama_analysis, text[:1000], model_name),
                        timeout=2.0  # 2-second timeout for LLaMA
                    )
                    basic_analysis = await basic_analysis_task
                except asyncio.TimeoutError:
                    logger.warning("LLaMA analysis timed out")
                except Exception as e:
                    logger.warning(f"Ollama analysis failed: {e}")

            # RAG analysis (async)
            rag_analyses = {}
            if self.rag_available:
                try:
                    rag_task = asyncio.wait_for(
                        loop.run_in_executor(executor, self.perform_rag_analysis, parsed_data, compliance_issues, errors),
                        timeout=2.0  # 2-second timeout for RAG
                    )
                    rag_analyses = await rag_task
                except asyncio.TimeoutError:
                    logger.warning("RAG analysis timed out")
                    rag_analyses = self._get_fallback_rag_analysis()
                except Exception as e:
                    logger.error(f"RAG analysis failed: {e}")
                    rag_analyses = self._get_fallback_rag_analysis()
            else:
                rag_analyses = self._get_fallback_rag_analysis()

            # Generate enhanced report
            report_start = time.time()
            report = self.report_generator.generate_enhanced_report(parsed_data, compliance_issues, errors, rag_analyses)
            logger.info(f"Report generation completed in {time.time() - report_start:.2f} seconds")

            # Build API response matching the exact structure
            response = self._build_api_response(
                parsed_data=parsed_data,
                compliance_issues=compliance_issues,
                errors=errors,
                rag_analyses=rag_analyses,
                basic_analysis=basic_analysis,
                file_path=file_path,
                text=text,
                tables=tables,
                model_name=model_name,
                start_time=start_time,
                report=report
            )
            
            logger.info(f"Fast analysis completed in {time.time() - start_time:.2f} seconds")
            return response
        
        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            return self._build_error_response(str(e), file_path, model_name, start_time)

    def get_basic_llama_analysis(self, text: str, model_name: str) -> str:
        """Generate basic LLaMA analysis with optimized prompt"""
        prompt = f"Briefly analyze this Schedule III document excerpt (max 500 chars): {text[:500]}"
        try:
            logger.info(f"Calling Ollama with model: {model_name}")
            response = ollama.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.1, 'num_predict': 100, 'timeout': 30}
            )
            logger.info("Ollama response received")
            return response['message']['content'].strip()
        except Exception as e:
            logger.error(f"Ollama analysis failed: {e}")
            return f"Analysis unavailable: {str(e)}"

    def _build_api_response(self, parsed_data: Dict, compliance_issues: List[Dict], errors: List[Dict], 
                           rag_analyses: Dict, basic_analysis: str, file_path: str, text: str, 
                           tables: List, model_name: str, start_time: float, report: Dict) -> Dict:
        """Build API response matching the exact frontend structure"""
        filename = Path(file_path).name
        company_name = parsed_data.get('company_name', 'Unknown Company')
        total_issues = len(compliance_issues) + len(errors)
        summary = (f"Schedule III analysis for {company_name}: {total_issues} issues found"
                  if total_issues > 0 else f"Schedule III analysis for {company_name} shows full compliance")

        # Format inconsistencies for the exact structure
        basic_inconsistencies = self._format_basic_inconsistencies(compliance_issues + errors)
        
        # Use report's recommendations and rag_analysis
        rag_analysis_text = (report['rag_analysis'].get('general_compliance', {}).get('analysis', basic_analysis)
                           if self.rag_available else basic_analysis)
        recommendations = '; '.join(report['recommendations']) if report['recommendations'] else "No specific recommendations"

        analysis_result = {
            "inconsistencies": {
                "basic_inconsistencies": basic_inconsistencies,
                "rag_analysis": rag_analysis_text,
                "recommendations": recommendations,
                "enhanced": self.rag_available,
                "error": ""
            },
            "summary": summary
        }

        response_data = {
            "text": text[:2000],
            "inconsistencies": analysis_result["inconsistencies"].get('basic_inconsistencies', []),
            "rag_analysis": analysis_result["inconsistencies"].get('rag_analysis', ''),
            "recommendations": analysis_result["inconsistencies"].get('recommendations', ''),
            "enhanced": analysis_result["inconsistencies"].get('enhanced', False),
            "error": analysis_result["inconsistencies"].get('error', ''),
            "summary": analysis_result["summary"],
            "filename": filename,
            "status": "success"
        }

        return response_data

    def _build_error_response(self, error_message: str, file_path: str, model_name: str, start_time: float) -> Dict:
        """Build error response matching the exact frontend structure"""
        filename = Path(file_path).name if file_path else "unknown"
        analysis_result = {
            "inconsistencies": {
                "basic_inconsistencies": [],
                "rag_analysis": f"Analysis failed: {error_message}",
                "recommendations": "Please check document format and retry.",
                "enhanced": False,
                "error": error_message
            },
            "summary": "Analysis failed due to error"
        }

        return {
            "text": "",
            "inconsistencies": analysis_result["inconsistencies"].get('basic_inconsistencies', []),
            "rag_analysis": analysis_result["inconsistencies"].get('rag_analysis', ''),
            "recommendations": analysis_result["inconsistencies"].get('recommendations', ''),
            "enhanced": analysis_result["inconsistencies"].get('enhanced', False),
            "error": analysis_result["inconsistencies"].get('error', ''),
            "summary": analysis_result["summary"],
            "filename": filename,
            "status": "error"
        }

    def _format_basic_inconsistencies(self, all_issues: List[Dict]) -> List[Dict]:
        """Format inconsistencies for API response"""
        return [{
            "type": issue.get('type', 'unknown'),
            "severity": issue.get('severity', 'medium'),
            "description": issue.get('description', 'No description'),
            "field": issue.get('field', issue.get('section', 'unknown')),
            "value": str(issue.get('value', 'N/A'))
        } for issue in all_issues]

    def _get_fallback_rag_analysis(self) -> Dict:
        """Fallback RAG analysis"""
        return {
            'general_compliance': {
                'analysis': 'Basic rule-based analysis performed. RAG enhancement unavailable.',
                'sources_used': ['Companies Act 2013 - Schedule III'],
                'context_documents': 0
            }
        }

    async def perform_rag_analysis(self, parsed_data: Dict, compliance_issues: List[Dict], errors: List[Dict]) -> Dict:
        """Perform enhanced RAG analysis with multiple targeted queries"""
        analyses = {}
        queries = [
            (f"Analyze Schedule III compliance for: {json.dumps(parsed_data, indent=2)}", "general_compliance"),
            (f"Evaluate balance sheet equation for: {json.dumps(parsed_data.get('totals', {}), indent=2)}", "balance_equation"),
            (f"Provide resolution suggestions for issues: {json.dumps(compliance_issues + errors, indent=2)}", "issue_resolution"),
            (f"Check Schedule III format compliance for: {json.dumps(parsed_data, indent=2)}", "format_review")
        ]

        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            tasks = [loop.run_in_executor(executor, self.rag_engine.generate_rag_response, query, parsed_data)
                     for query, analysis_type in queries]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        for (query, analysis_type), result in zip(queries, results):
            if isinstance(result, Exception):
                logger.warning(f"RAG analysis for {analysis_type} failed: {result}")
                analyses[analysis_type] = {
                    'analysis': f"RAG analysis unavailable: {str(result)}",
                    'sources_used': [],
                    'context_documents': 0
                }
            else:
                analyses[analysis_type] = result

        return analyses

# Initialize the audit system globally
audit_system = EnhancedAuditManagementSystem()

# Helper functions
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_and_tables(file_path):
    """Extract text and tables from PDF with enhanced error handling"""
    try:
        text = ""
        tables = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    else:
                        logger.warning(f"No text extracted from page {page_num}")
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num}: {e}")
                    text += f"[Page {page_num} extraction failed]\n"
        return text, tables
    except Exception as e:
        logger.error(f"Error reading PDF: {e}")
        return "", []

def generate_cache_key(file_path, model_name):
    """Generate cache key with timestamp"""
    file_stats = os.stat(file_path)
    content = f"{file_path}_{file_stats.st_size}_{file_stats.st_mtime}_{model_name}"
    return hashlib.md5(content.encode()).hexdigest()

# Flask Routes
@app.route('/upload', methods=['POST'])
async def upload_file():
    """Main upload endpoint with async handling"""
    start_time = time.time()
    logger.info("Received file upload request")
    
    try:
        if 'file' not in request.files:
            return jsonify(audit_system._build_error_response("No file provided", "", request.form.get('model', 'mistral'), start_time)), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify(audit_system._build_error_response("No file selected", "", request.form.get('model', 'mistral'), start_time)), 400

        if not allowed_file(file.filename):
            return jsonify(audit_system._build_error_response("File type not allowed. Please upload a PDF file.", file.filename, request.form.get('model', 'mistral'), start_time)), 400

        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        logger.info(f"File saved: {file_path}")

        # Check cache
        model_name = request.form.get('model', 'mistral')
        cache_key = generate_cache_key(file_path, model_name)
        if cache_key in analysis_cache and (time.time() - analysis_cache[cache_key].get('cache_time', 0)) < CACHE_EXPIRY_SECONDS:
            logger.info("Returning cached result")
            cached_result = analysis_cache[cache_key]
            cached_result["cached"] = True
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Could not delete temporary file: {e}")
            return jsonify(cached_result), 200

        # Extract text and tables
        text, tables = extract_text_and_tables(file_path)
        if not text.strip():
            return jsonify(audit_system._build_error_response("Could not extract text from PDF", file_path, model_name, start_time)), 400

        # Perform analysis
        analysis_result = await audit_system.analyze_document(file_path, text, tables, model_name)

        # Cache the result
        analysis_result['cache_time'] = time.time()
        analysis_cache[cache_key] = analysis_result

        # Clean up uploaded file
        try:
            os.remove(file_path)
        except Exception as e:
            logger.warning(f"Could not delete temporary file: {e}")

        logger.info(f"Analysis completed in {time.time() - start_time:.2f} seconds")
        return jsonify(analysis_result), 200

    except Exception as e:
        logger.error(f"Upload endpoint error: {e}")
        return jsonify(audit_system._build_error_response(f"Internal server error: {str(e)}", filename if 'filename' in locals() else "unknown", request.form.get('model', 'mistral'), start_time)), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "rag_available": audit_system.rag_available,
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        "message": "AI Audit Management System API",
        "version": "1.0",
        "endpoints": {
            "upload": "/upload (POST)",
            "health": "/health (GET)"
        }
    }), 200

if __name__ == '__main__':
    logger.info("Starting AI Audit Management System...")
    logger.info(f"RAG Engine Available: {audit_system.rag_available}")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )