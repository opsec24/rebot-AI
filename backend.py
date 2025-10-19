from fastapi import FastAPI, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
import uuid
from datetime import datetime
import requests
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import uvicorn
import markdown
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import html
import re

# Helper functions for PDF generation
def escape_html(text):
    """Escape HTML special characters for safe PDF generation"""
    if not text:
        return ""
    # First decode any HTML entities, then escape special characters
    text = html.unescape(str(text))
    # Escape characters that could cause issues in PDF
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    return text

def clean_html_content(content):
    """Clean HTML content from Quill editor for PDF generation"""
    if not content:
        return ""
    
    # Convert HTML to plain text with proper line breaks
    content = str(content)
    
    # Remove script and style tags completely
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Convert common HTML tags to line breaks
    content = content.replace('<br>', '\n')
    content = content.replace('<br/>', '\n')
    content = content.replace('<br />', '\n')
    content = content.replace('</p>', '\n\n')
    content = content.replace('<p>', '')
    content = content.replace('</div>', '\n')
    content = content.replace('<div>', '')
    content = content.replace('</li>', '\n')
    content = content.replace('<li>', '• ')
    content = content.replace('</ul>', '\n')
    content = content.replace('<ul>', '')
    content = content.replace('</ol>', '\n')
    content = content.replace('<ol>', '')
    
    # Remove remaining HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    
    # Decode HTML entities
    content = html.unescape(content)
    
    # Clean up extra whitespace
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # Remove excessive line breaks
    content = content.strip()
    
    # Convert line breaks to <br/> for PDF
    content = content.replace('\n', '<br/>')
    
    return content

# Initialize FastAPI app
app = FastAPI(title="Pentest Vulnerability Report Generator", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
os.makedirs("static", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize LLaMA 3B with OLLAMA (optional)
try:
    print("Initializing LLaMA 3.2 3B model...")
    llm = OllamaLLM(model="llama3.2:3b", base_url="http://localhost:11434")
    print("Testing AI connection...")
    # Test the connection
    test_response = llm.invoke("Hello")
    print(f"AI connection successful! Test response: {test_response[:50]}...")
    AI_AVAILABLE = True
except Exception as e:
    print(f"Warning: OLLAMA not available: {e}")
    llm = None
    AI_AVAILABLE = False

# Pydantic models for structured output
class VulnerabilityDetails(BaseModel):
    description: str = Field(description="Detailed description of the vulnerability")
    remediation: str = Field(description="Step-by-step remediation instructions")
    references: List[str] = Field(description="List of reference links (OWASP, CWE, etc.)")
    owasp_category: str = Field(description="OWASP Top 10 category")
    cwe_id: str = Field(description="CWE ID number")
    impact_level: str = Field(description="Impact level: Critical, High, Medium, or Low")
    likelihood_level: str = Field(description="Likelihood level: Critical, High, Medium, or Low")

class VulnerabilityReport(BaseModel):
    id: str
    title: str
    status: str
    description: str
    location: str
    steps_to_reproduce: str
    impact: str
    likelihood: str
    impact_description: str
    likelihood_description: str
    cwe_id: str
    owasp_category: str
    instances: int
    remediation: str
    references: List[str]
    created_date: str

# In-memory storage (no database)
vulnerabilities_db: List[VulnerabilityReport] = []

# LangChain prompt template for vulnerability analysis
vulnerability_prompt = PromptTemplate(
    input_variables=["vulnerability_title"],
    template="""
You are an expert penetration tester and security researcher. Analyze the vulnerability and provide detailed information.

Vulnerability Title: {vulnerability_title}

Based on the vulnerability title, analyze and provide detailed information in this EXACT JSON format (no other text):

{{
    "description": "Detailed technical description explaining how this vulnerability works, what makes it exploitable, and the security impact",
    "remediation": "Specific, actionable remediation steps that developers can implement to fix this vulnerability",
    "references": ["List of relevant OWASP, CWE, and security resource links"],
    "owasp_category": "Appropriate OWASP Top 10 category based on the vulnerability type",
    "cwe_id": "Relevant CWE ID number based on the vulnerability type",
    "impact_level": "Critical, High, Medium, or Low based on the vulnerability severity",
    "likelihood_level": "Critical, High, Medium, or Low based on exploitation difficulty"
}}

IMPORTANT: 
- Analyze the vulnerability title to determine the correct OWASP Top 10 category (A01-A10)
- Use appropriate CWE IDs based on the vulnerability type
- Assess realistic impact and likelihood levels
- Provide specific, actionable remediation steps
- Include relevant reference links
- Return ONLY the JSON, no explanations or additional text
"""
)

# Output parser for structured response
parser = PydanticOutputParser(pydantic_object=VulnerabilityDetails)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    return FileResponse("static/index.html")

@app.post("/api/generate-vulnerability-details")
async def generate_vulnerability_details(title: str = Form(...)):
    """Generate vulnerability details using LLaMA 3B"""
    try:
        if not AI_AVAILABLE or not llm:
            # Return error if AI is not available
            return {
                "success": False,
                "message": "AI service is not available. Please ensure OLLAMA is running with llama3.2:3b model."
            }
        
        # Create the prompt
        prompt = vulnerability_prompt.format(vulnerability_title=title)
        
        # Get response from LLaMA
        response = llm.invoke(prompt)
        
        # Parse the JSON response
        try:
            # Clean the response to extract JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                parsed_data = json.loads(json_str)
                # --- FIX: Ensure remediation is a string, not a list ---
                if isinstance(parsed_data.get("remediation"), list):
                    parsed_data["remediation"] = "\n".join(parsed_data["remediation"])
                # ------------------------------------------------------

                # Convert to VulnerabilityDetails
                vuln_details = VulnerabilityDetails(**parsed_data)
                
                return {
                    "success": True,
                    "data": vuln_details.dict()
                }
            else:
                raise ValueError("No valid JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            # Return error if JSON parsing fails
            return {
                "success": False,
                "message": f"Failed to parse AI response. Please try again or check the AI model. Error: {str(e)}"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating vulnerability details: {str(e)}")


@app.post("/api/save-vulnerability")
async def save_vulnerability(
    title: str = Form(...),
    status: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    steps_to_reproduce: str = Form(...),
    impact: str = Form(...),
    likelihood: str = Form(...),
    impact_description: str = Form(...),
    likelihood_description: str = Form(...),
    cwe_id: str = Form(...),
    owasp_category: str = Form(...),
    instances: int = Form(...),
    remediation: str = Form(...),
    references: str = Form(...)
):
    """Save a vulnerability report"""
    try:
        # Parse references
        references_list = [ref.strip() for ref in references.split('\n') if ref.strip()]
        
        # Create vulnerability report
        vuln_report = VulnerabilityReport(
            id=str(uuid.uuid4()),
            title=title,
            status=status,
            description=description,
            location=location,
            steps_to_reproduce=steps_to_reproduce,
            impact=impact,
            likelihood=likelihood,
            impact_description=impact_description,
            likelihood_description=likelihood_description,
            cwe_id=cwe_id,
            owasp_category=owasp_category,
            instances=instances,
            remediation=remediation,
            references=references_list,
            created_date=datetime.now().isoformat()
        )
        
        # Add to database
        vulnerabilities_db.append(vuln_report)
        
        return {
            "success": True,
            "message": f"Vulnerability '{title}' saved successfully!",
            "id": vuln_report.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving vulnerability: {str(e)}")

@app.get("/api/vulnerabilities")
async def get_vulnerabilities():
    """Get all vulnerabilities"""
    return {
        "success": True,
        "data": [vuln.dict() for vuln in vulnerabilities_db]
    }

@app.delete("/api/vulnerabilities/{vuln_id}")
async def delete_vulnerability(vuln_id: str):
    """Delete a vulnerability"""
    global vulnerabilities_db
    vulnerabilities_db = [vuln for vuln in vulnerabilities_db if vuln.id != vuln_id]
    return {"success": True, "message": "Vulnerability deleted successfully"}

@app.get("/api/export-report")
async def export_report(format: str = "markdown"):
    """Export all vulnerabilities as a combined report"""
    if not vulnerabilities_db:
        raise HTTPException(status_code=404, detail="No vulnerabilities to export")
    
    # Generate markdown report
    report = "# Penetration Testing Vulnerability Report\n\n"
    report += f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    report += f"**Total Vulnerabilities:** {len(vulnerabilities_db)}\n\n"
    report += "---\n\n"
    
    for i, vuln in enumerate(vulnerabilities_db, 1):
        report += f"## {i}. {vuln.title}\n\n"
        report += f"**Status:** {vuln.status}\n\n"
        report += f"**Description:** {vuln.description}\n\n"
        report += f"**Vulnerability Location:** `{vuln.location}`\n\n"
        report += f"**Steps to Reproduce:**\n\n{vuln.steps_to_reproduce}\n\n"
        report += f"**Severity:**\n\n"
        report += f"- **Impact:** {vuln.impact}. {vuln.impact_description}\n"
        report += f"- **Likelihood:** {vuln.likelihood}. {vuln.likelihood_description}\n\n"
        report += f"| **CWE** | **OWASP Category** | **Instances** |\n"
        report += f"|---------|-------------------|---------------|\n"
        report += f"| {vuln.cwe_id} | {vuln.owasp_category} | {vuln.instances} |\n\n"
        report += f"**Remediation:**\n\n{vuln.remediation}\n\n"
        if vuln.references:
            report += f"**References:**\n\n"
            for ref in vuln.references:
                report += f"- {ref}\n"
            report += "\n"
        report += "---\n\n"
    
    if format.lower() == "pdf":
        # Generate PDF using reportlab
        from io import BytesIO
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkred,
            fontName='Helvetica-Bold'
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=15,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.lightgrey,
            borderPadding=8,
            backColor=colors.lightgrey
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            fontName='Helvetica',
            leading=14
        )
        bold_style = ParagraphStyle(
            'BoldStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        # Build PDF content
        story = []
        
        # Title
        story.append(Paragraph("Penetration Testing Vulnerability Report", title_style))
        story.append(Spacer(1, 12))
        
        # Report info
        story.append(Paragraph(f"<b>Generated on:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        story.append(Paragraph(f"<b>Total Vulnerabilities:</b> {len(vulnerabilities_db)}", normal_style))
        story.append(Spacer(1, 20))
        
        # Add each vulnerability
        for i, vuln in enumerate(vulnerabilities_db, 1):
            # Vulnerability title with severity indicator
            severity_color = colors.red if vuln.impact == 'Critical' else colors.orange if vuln.impact == 'High' else colors.yellow if vuln.impact == 'Medium' else colors.green
            story.append(Paragraph(f"{i}. {escape_html(vuln.title)} <font color='{severity_color}'>({vuln.impact})</font>", heading_style))
            
            # Status and basic info
            story.append(Paragraph(f"<b>Status:</b> {escape_html(vuln.status)}", bold_style))
            story.append(Paragraph(f"<b>Description:</b> {escape_html(vuln.description)}", normal_style))
            story.append(Paragraph(f"<b>Location:</b> {escape_html(vuln.location)}", normal_style))
            story.append(Spacer(1, 10))
            
            # Steps to reproduce
            story.append(Paragraph("<b>Steps to Reproduce:</b>", bold_style))
            # Clean HTML from Quill editor and escape special characters
            steps_clean = clean_html_content(vuln.steps_to_reproduce)
            story.append(Paragraph(steps_clean, normal_style))
            story.append(Spacer(1, 10))
            
            # Severity assessment
            story.append(Paragraph("<b>Risk Assessment:</b>", bold_style))
            story.append(Paragraph(f"<b>Impact:</b> {escape_html(vuln.impact)} - {escape_html(vuln.impact_description)}", normal_style))
            story.append(Paragraph(f"<b>Likelihood:</b> {escape_html(vuln.likelihood)} - {escape_html(vuln.likelihood_description)}", normal_style))
            story.append(Spacer(1, 10))
            
            # CWE and OWASP table with better styling
            table_data = [
                ['CWE ID', 'OWASP Category', 'Instances', 'Severity'],
                [escape_html(vuln.cwe_id), escape_html(vuln.owasp_category), str(vuln.instances), escape_html(vuln.impact)]
            ]
            table = Table(table_data, colWidths=[1.5*inch, 2.5*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            story.append(table)
            story.append(Spacer(1, 15))
            
            # Remediation
            story.append(Paragraph("<b>Remediation Steps:</b>", bold_style))
            remediation_clean = clean_html_content(vuln.remediation)
            story.append(Paragraph(remediation_clean, normal_style))
            story.append(Spacer(1, 10))
            
            # References
            if vuln.references:
                story.append(Paragraph("<b>References:</b>", bold_style))
                for ref in vuln.references:
                    story.append(Paragraph(f"• {escape_html(ref)}", normal_style))
            
            story.append(Spacer(1, 25))
        
        # Build PDF with error handling
        try:
            doc.build(story)
            pdf_content = buffer.getvalue()
            
            # Validate PDF content
            if len(pdf_content) < 100:  # PDF should be at least 100 bytes
                raise ValueError("Generated PDF is too small, likely corrupted")
            
            # Check if it starts with PDF header
            if not pdf_content.startswith(b'%PDF-'):
                raise ValueError("Generated content is not a valid PDF")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
        finally:
            buffer.close()
        
        filename = f"pentest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_content))
            }
        )
    else:
        # Return markdown
        filename = f"pentest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        return {
            "success": True,
            "report": report,
            "filename": filename
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
