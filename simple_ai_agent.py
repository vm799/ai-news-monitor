# simple_ai_agent.py
# Let's start with something that definitely works

print("=== AI AGENT STARTING ===")

try:
    import os
    print("✓ os imported")
    
    import json
    print("✓ json imported")
    
    import requests
    print("✓ requests imported")
    
    from datetime import datetime
    print("✓ datetime imported")
    
    from flask import Flask, jsonify, render_template_string
    print("✓ flask imported")
    
    # Try dotenv
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ dotenv loaded")
    except ImportError:
        print("⚠ dotenv not available")
    
    print("=== ALL BASIC IMPORTS SUCCESSFUL ===")
    
except Exception as e:
    print(f"❌ IMPORT ERROR: {e}")
    exit(1)

# Simple working AI system
class SimpleWorkingAI:
    def __init__(self):
        print("Initializing Simple AI System...")
        self.google_key = os.environ.get('GOOGLE_API_KEY')
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        
        print(f"Google API Key: {'Found' if self.google_key else 'Not found'}")
        print(f"OpenAI API Key: {'Found' if self.openai_key else 'Not found'}")
    
    def analyze_with_gemini(self):
        """Try Gemini analysis"""
        if not self.google_key:
            return self.get_demo_analysis()
        
        try:
            # Simple Gemini API call
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.google_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": "You are a senior AI analyst. Provide a brief analysis of current AI developments and their business impact. Focus on enterprise applications and investment implications. Keep it concise but insightful."
                    }]
                }]
            }
            
            print("Making Gemini API call...")
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    return {
                        'analysis': content,
                        'source': 'Gemini AI',
                        'status': 'success',
                        'generated_at': datetime.now().isoformat()
                    }
            
            print(f"Gemini API Error: {response.status_code}")
            return self.get_demo_analysis()
            
        except Exception as e:
            print(f"Gemini error: {e}")
            return self.get_demo_analysis()
    
    def get_demo_analysis(self):
        """High-quality demo analysis"""
        return {
            'analysis': """AI MARKET INTELLIGENCE BRIEFING

CURRENT LANDSCAPE:
• Enterprise AI adoption accelerating at 40% year-over-year growth
• Large language models becoming commodity infrastructure
• Focus shifting from general AI to specialized business applications
• Regulatory frameworks emerging in EU and US markets

BUSINESS IMPACT ASSESSMENT: 8/10 - High Strategic Priority

KEY INVESTMENT THEMES:
• AI infrastructure and model serving platforms
• Data preparation and quality management tools
• AI-powered vertical software solutions
• Governance and compliance tooling

STRATEGIC RECOMMENDATIONS:
1. Immediate: Audit current AI capabilities across business units
2. Short-term: Identify high-ROI AI implementation opportunities  
3. Medium-term: Build internal AI expertise and governance
4. Long-term: Develop AI-differentiated competitive advantages

RISK FACTORS:
• Rapid technology evolution requiring continuous adaptation
• Skills shortage in AI implementation and management
• Regulatory compliance requirements increasing
• Integration complexity with existing enterprise systems

EXECUTIVE SUMMARY:
AI is transitioning from experimental to essential business infrastructure. 
Organizations that act strategically now will gain significant competitive advantages. 
Key success factors: focused implementation, strong governance, and continuous learning.

This analysis demonstrates enterprise AI capabilities.""",
            'source': 'Demo Analysis Engine',
            'status': 'demo',
            'generated_at': datetime.now().isoformat()
        }

# Flask app
app = Flask(__name__)

# Clean, working dashboard
WORKING_DASHBOARD = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Analysis System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 50%, #581c87 100%);
            color: white; min-height: 100vh; padding: 20px;
        }
        
        .container { 
            max-width: 900px; margin: 0 auto; padding: 40px 20px;
        }
        
        .header {
            text-align: center; margin-bottom: 50px;
            background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
            padding: 40px; border-radius: 20px;
        }
        
        .header h1 { 
            font-size: 2.5rem; font-weight: 700; margin-bottom: 15px;
            background: linear-gradient(45deg, #60a5fa, #a78bfa, #fb7185);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        
        .header p { font-size: 1.1rem; opacity: 0.9; }
        
        .button { 
            display: block; width: 100%; max-width: 350px; margin: 0 auto 40px;
            background: linear-gradient(45deg, #3b82f6, #8b5cf6, #ec4899);
            color: white; padding: 18px 30px; border: none; border-radius: 12px;
            font-size: 1.1rem; font-weight: 600; cursor: pointer;
            transition: all 0.3s; text-transform: uppercase; letter-spacing: 0.5px;
        }
        
        .button:hover { 
            transform: translateY(-3px); 
            box-shadow: 0 10px 30px rgba(59, 130, 246, 0.4);
        }
        
        .result { 
            background: rgba(255,255,255,0.1); backdrop-filter: blur(15px);
            border-radius: 15px; padding: 30px; margin-top: 30px; display: none;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .result h3 { 
            font-size: 1.3rem; font-weight: 600; margin-bottom: 20px;
            padding-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.2);
        }
        
        .loading { 
            text-align: center; font-size: 1.2rem; padding: 40px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
        
        .analysis { 
            white-space: pre-wrap; line-height: 1.7; font-size: 0.95rem;
            background: rgba(0,0,0,0.3); padding: 20px; border-radius: 10px;
            font-family: 'Courier New', monospace; margin: 20px 0;
        }
        
        .meta { 
            display: flex; justify-content: space-between; align-items: center;
            margin-top: 20px; padding-top: 20px; 
            border-top: 1px solid rgba(255,255,255,0.2);
            font-size: 0.9rem; opacity: 0.8;
        }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 2rem; }
            .meta { flex-direction: column; gap: 10px; text-align: center; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Analysis System</h1>
            <p>Enterprise AI intelligence and strategic analysis</p>
        </div>
        
        <button class="button" onclick="runAnalysis()">
            Generate AI Analysis
        </button>
        
        <div id="result" class="result">
            <div id="loading" class="loading">AI system processing...</div>
            <div id="content" style="display:none;">
                <h3>Analysis Results</h3>
                <div id="analysis" class="analysis"></div>
                <div class="meta">
                    <span>Source: <span id="source">-</span></span>
                    <span>Status: <span id="status">-</span></span>
                    <span>Generated: <span id="timestamp">-</span></span>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function runAnalysis() {
            document.getElementById('result').style.display = 'block';
            document.getElementById('loading').style.display = 'block';
            document.getElementById('content').style.display = 'none';
            
            fetch('/api/analyze')
                .then(response => response.json())
                .then(data => {
                    console.log('Response:', data);
                    
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('content').style.display = 'block';
                    
                    document.getElementById('analysis').textContent = data.analysis || 'No analysis available';
                    document.getElementById('source').textContent = data.source || 'Unknown';
                    document.getElementById('status').textContent = data.status || 'Complete';
                    document.getElementById('timestamp').textContent = 
                        data.generated_at ? new Date(data.generated_at).toLocaleString() : 'Now';
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('content').style.display = 'block';
                    document.getElementById('analysis').textContent = 'Error: ' + error.message;
                });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    print("Dashboard route accessed")
    return render_template_string(WORKING_DASHBOARD)

@app.route('/api/analyze')
def analyze():
    print("Analysis API called")
    try:
        ai = SimpleWorkingAI()
        result = ai.analyze_with_gemini()
        print(f"Analysis result: {result['status']}")
        return jsonify(result)
    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({
            'analysis': f'System Error: {str(e)}',
            'source': 'Error Handler',
            'status': 'error',
            'generated_at': datetime.now().isoformat()
        })

if __name__ == '__main__':
    print("=== STARTING FLASK APP ===")
    
    try:
        print("Flask app configuration...")
        print("Server will start on http://localhost:5002")
        print("=" * 50)
        
        app.run(host='0.0.0.0', port=5002, debug=True)
        
    except Exception as e:
        print(f"❌ FLASK ERROR: {e}")

print("=== SCRIPT COMPLETED ===")

# TO RUN:
# 1. Save as simple_ai_agent.py
# 2. python simple_ai_agent.py
# 3. You should see detailed output about what's happening
# 4. Open http://localhost:5002