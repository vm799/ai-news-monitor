# step2_diagnostic.py
# Let's find exactly what's breaking in the advanced version

print("=== ADVANCED AI SYSTEM DIAGNOSTIC ===")

# Test basic imports first
try:
    import os
    import json
    from datetime import datetime
    from flask import Flask, jsonify, render_template_string
    print("✓ Basic imports successful")
except Exception as e:
    print(f"❌ Basic imports failed: {e}")
    exit(1)

# Test dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ dotenv imported and loaded")
except Exception as e:
    print(f"⚠ dotenv issue: {e}")

# Test each advanced import one by one
print("\n=== TESTING ADVANCED IMPORTS ===")

# Test CrewAI
try:
    from crewai import Agent, Task, Crew, Process
    print("✓ CrewAI imported successfully")
    CREWAI_AVAILABLE = True
except ImportError as e:
    print(f"❌ CrewAI not available: {e}")
    print("   Install with: pip install crewai")
    CREWAI_AVAILABLE = False
except Exception as e:
    print(f"❌ CrewAI error: {e}")
    CREWAI_AVAILABLE = False

# Test LangChain
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_community.tools import DuckDuckGoSearchRun
    from langchain.memory import ConversationBufferMemory
    print("✓ LangChain imported successfully")
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"❌ LangChain not available: {e}")
    print("   Install with: pip install langchain-google-genai langchain-community")
    LANGCHAIN_AVAILABLE = False
except Exception as e:
    print(f"❌ LangChain error: {e}")
    LANGCHAIN_AVAILABLE = False

# Test Transformers
try:
    from transformers import pipeline
    print("✓ Transformers imported successfully")
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    print(f"❌ Transformers not available: {e}")
    print("   Install with: pip install transformers torch")
    TRANSFORMERS_AVAILABLE = False
except Exception as e:
    print(f"❌ Transformers error: {e}")
    TRANSFORMERS_AVAILABLE = False

print(f"\n=== AVAILABILITY SUMMARY ===")
print(f"CrewAI: {'✓' if CREWAI_AVAILABLE else '❌'}")
print(f"LangChain: {'✓' if LANGCHAIN_AVAILABLE else '❌'}")
print(f"Transformers: {'✓' if TRANSFORMERS_AVAILABLE else '❌'}")

# Now let's create a version that works with what we have
class FlexibleAISystem:
    """AI system that adapts to available frameworks"""
    
    def __init__(self):
        print("\n=== INITIALIZING FLEXIBLE AI SYSTEM ===")
        
        # Check API keys
        self.google_key = os.environ.get('GOOGLE_API_KEY')
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        
        print(f"Google API Key: {'✓ Found' if self.google_key else '❌ Missing'}")
        print(f"OpenAI API Key: {'✓ Found' if self.openai_key else '❌ Missing'}")
        
        # Initialize what we can
        self.setup_available_frameworks()
        
    def setup_available_frameworks(self):
        """Setup frameworks that are available"""
        
        # Try to setup Gemini
        if LANGCHAIN_AVAILABLE and self.google_key:
            try:
                self.gemini = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=self.google_key,
                    temperature=0.7
                )
                print("✓ Gemini initialized")
                self.gemini_available = True
            except Exception as e:
                print(f"❌ Gemini setup failed: {e}")
                self.gemini_available = False
        else:
            print("⚠ Gemini not available (missing LangChain or API key)")
            self.gemini_available = False
        
        # Try to setup search
        if LANGCHAIN_AVAILABLE:
            try:
                self.search_tool = DuckDuckGoSearchRun()
                print("✓ Search tool initialized")
                self.search_available = True
            except Exception as e:
                print(f"❌ Search setup failed: {e}")
                self.search_available = False
        else:
            print("⚠ Search not available (missing LangChain)")
            self.search_available = False
        
        # Try to setup sentiment analysis
        if TRANSFORMERS_AVAILABLE:
            try:
                self.sentiment_analyzer = pipeline("sentiment-analysis")
                print("✓ Sentiment analyzer initialized")
                self.sentiment_available = True
            except Exception as e:
                print(f"❌ Sentiment setup failed: {e}")
                self.sentiment_available = False
        else:
            print("⚠ Sentiment analysis not available (missing transformers)")
            self.sentiment_available = False
        
        # Try to setup CrewAI
        if CREWAI_AVAILABLE and self.gemini_available:
            try:
                self.setup_crew()
                print("✓ CrewAI agents initialized")
                self.crew_available = True
            except Exception as e:
                print(f"❌ CrewAI setup failed: {e}")
                self.crew_available = False
        else:
            print("⚠ CrewAI not available (missing CrewAI or Gemini)")
            self.crew_available = False
    
    def setup_crew(self):
        """Setup CrewAI if available"""
        self.researcher = Agent(
            role='AI Researcher',
            goal='Research AI developments',
            backstory='You research AI news and developments.',
            verbose=False,
            allow_delegation=False,
            tools=[self.search_tool] if self.search_available else [],
            llm=self.gemini
        )
    
    def generate_analysis(self):
        """Generate analysis using best available method"""
        
        print("\n=== GENERATING ANALYSIS ===")
        
        # Try CrewAI first (most advanced)
        if self.crew_available:
            print("Using CrewAI multi-agent approach...")
            return self.crew_analysis()
        
        # Try Gemini direct
        elif self.gemini_available:
            print("Using Gemini direct approach...")
            return self.gemini_analysis()
        
        # Fallback to demo
        else:
            print("Using demo mode...")
            return self.demo_analysis()
    
    def crew_analysis(self):
        """CrewAI analysis"""
        try:
            task = Task(
                description="Provide a comprehensive AI market analysis",
                agent=self.researcher,
                expected_output="AI market analysis"
            )
            
            crew = Crew(
                agents=[self.researcher],
                tasks=[task],
                verbose=False,
                process=Process.sequential
            )
            
            result = crew.kickoff()
            
            return {
                'analysis': str(result),
                'method': 'CrewAI Multi-Agent',
                'frameworks': ['CrewAI', 'LangChain', 'Gemini'],
                'status': 'success',
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"CrewAI execution failed: {e}")
            return self.gemini_analysis()
    
    def gemini_analysis(self):
        """Direct Gemini analysis"""
        try:
            prompt = """Provide a comprehensive AI market analysis covering:
            1. Recent developments
            2. Business implications
            3. Investment opportunities
            4. Strategic recommendations
            
            Focus on enterprise applications and actionable insights."""
            
            response = self.gemini.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            return {
                'analysis': content,
                'method': 'Gemini Direct',
                'frameworks': ['LangChain', 'Gemini'],
                'status': 'success',
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Gemini analysis failed: {e}")
            return self.demo_analysis()
    
    def demo_analysis(self):
        """High-quality demo analysis"""
        return {
            'analysis': """AI ENTERPRISE INTELLIGENCE BRIEFING

MARKET LANDSCAPE ANALYSIS:
• Enterprise AI adoption accelerating across all sectors
• Large language models becoming infrastructure layer
• Shift from general AI to specialized business applications
• Regulatory frameworks emerging globally

BUSINESS IMPACT ASSESSMENT: 9/10 - Critical Strategic Priority

INVESTMENT OPPORTUNITIES:
• AI infrastructure and model serving platforms
• Specialized AI applications for vertical markets
• Data quality and preparation technologies
• AI governance and compliance solutions

STRATEGIC RECOMMENDATIONS:
1. IMMEDIATE: Conduct AI readiness assessment
2. SHORT-TERM: Identify high-value AI use cases
3. MEDIUM-TERM: Build AI expertise and governance
4. LONG-TERM: Develop AI-competitive advantages

RISK MITIGATION:
• Establish AI governance framework
• Invest in AI talent and training
• Monitor regulatory developments
• Plan for technology evolution

EXECUTIVE SUMMARY:
AI is transitioning from experimental to essential business infrastructure. 
Organizations must act strategically to harness AI's potential while managing risks.
Success requires focused implementation, strong governance, and continuous adaptation.

FRAMEWORK STATUS: Demo mode operational""",
            'method': 'Demo Analysis Engine',
            'frameworks': ['Built-in Intelligence'],
            'status': 'demo',
            'generated_at': datetime.now().isoformat()
        }

# Flask app
app = Flask(__name__)

# Dashboard that shows what's working
DIAGNOSTIC_DASHBOARD = """
<!DOCTYPE html>
<html>
<head>
    <title>AI System Diagnostic</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e40af 0%, #7c3aed 50%, #db2777 100%);
            color: white; min-height: 100vh; padding: 20px;
        }
        
        .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
        
        .header {
            text-align: center; margin-bottom: 40px;
            background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
            padding: 30px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.2);
        }
        
        .header h1 { 
            font-size: 2.3rem; font-weight: 700; margin-bottom: 10px;
            background: linear-gradient(45deg, #60a5fa, #a78bfa, #fb7185);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        
        .status-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px; margin-bottom: 30px;
        }
        
        .status-item {
            background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;
            text-align: center; border: 1px solid rgba(255,255,255,0.2);
        }
        
        .available { border-color: #10b981; background: rgba(16, 185, 129, 0.1); }
        .missing { border-color: #ef4444; background: rgba(239, 68, 68, 0.1); }
        
        .button { 
            display: block; width: 100%; max-width: 350px; margin: 0 auto 30px;
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
            border-radius: 15px; padding: 25px; margin-top: 30px; display: none;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .analysis { 
            white-space: pre-wrap; line-height: 1.7; font-size: 0.9rem;
            background: rgba(0,0,0,0.3); padding: 20px; border-radius: 10px;
            font-family: 'Courier New', monospace; margin: 15px 0;
        }
        
        .meta { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px; margin-top: 20px; padding-top: 20px; 
            border-top: 1px solid rgba(255,255,255,0.2);
        }
        
        .meta-item { text-align: center; font-size: 0.9rem; }
        .meta-label { opacity: 0.7; margin-bottom: 5px; }
        .meta-value { font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI System Diagnostic</h1>
            <p>Testing which AI frameworks are available and working</p>
        </div>
        
        <div class="status-grid">
            <div class="status-item" id="crewai-status">
                <div>CrewAI</div>
                <div id="crewai-text">Checking...</div>
            </div>
            <div class="status-item" id="langchain-status">
                <div>LangChain</div>
                <div id="langchain-text">Checking...</div>
            </div>
            <div class="status-item" id="gemini-status">
                <div>Gemini</div>
                <div id="gemini-text">Checking...</div>
            </div>
            <div class="status-item" id="transformers-status">
                <div>Transformers</div>
                <div id="transformers-text">Checking...</div>
            </div>
        </div>
        
        <button class="button" onclick="runDiagnostic()">
            Run AI Analysis
        </button>
        
        <div id="result" class="result">
            <h3>Analysis Results</h3>
            <div id="analysis" class="analysis"></div>
            <div class="meta">
                <div class="meta-item">
                    <div class="meta-label">Method</div>
                    <div class="meta-value" id="method">-</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Frameworks</div>
                    <div class="meta-value" id="frameworks">-</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Status</div>
                    <div class="meta-value" id="status">-</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Generated</div>
                    <div class="meta-value" id="timestamp">-</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function runDiagnostic() {
            document.getElementById('result').style.display = 'block';
            
            fetch('/api/diagnostic')
                .then(response => response.json())
                .then(data => {
                    console.log('Diagnostic Response:', data);
                    
                    document.getElementById('analysis').textContent = data.analysis || 'No analysis available';
                    document.getElementById('method').textContent = data.method || 'Unknown';
                    document.getElementById('frameworks').textContent = 
                        data.frameworks ? data.frameworks.join(', ') : 'None';
                    document.getElementById('status').textContent = data.status || 'Complete';
                    document.getElementById('timestamp').textContent = 
                        data.generated_at ? new Date(data.generated_at).toLocaleString() : 'Now';
                    
                    // Update status indicators based on response
                    updateStatusIndicators(data);
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('analysis').textContent = 'Error: ' + error.message;
                });
        }
        
        function updateStatusIndicators(data) {
            // This would be updated based on the actual capabilities detected
            const frameworks = data.frameworks || [];
            
            updateStatus('crewai', frameworks.includes('CrewAI'));
            updateStatus('langchain', frameworks.includes('LangChain'));
            updateStatus('gemini', frameworks.includes('Gemini'));
            updateStatus('transformers', frameworks.includes('HuggingFace'));
        }
        
        function updateStatus(framework, available) {
            const element = document.getElementById(framework + '-status');
            const textElement = document.getElementById(framework + '-text');
            
            if (available) {
                element.className = 'status-item available';
                textElement.textContent = 'Available';
            } else {
                element.className = 'status-item missing';
                textElement.textContent = 'Missing';
            }
        }
        
        // Run status check on page load
        window.onload = function() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => updateStatusIndicators(data))
                .catch(error => console.error('Status check failed:', error));
        };
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DIAGNOSTIC_DASHBOARD)

@app.route('/api/status')
def status():
    """Return status of available frameworks"""
    frameworks = []
    if CREWAI_AVAILABLE: frameworks.append('CrewAI')
    if LANGCHAIN_AVAILABLE: frameworks.append('LangChain')
    if TRANSFORMERS_AVAILABLE: frameworks.append('HuggingFace')
    
    google_key = os.environ.get('GOOGLE_API_KEY')
    if LANGCHAIN_AVAILABLE and google_key: frameworks.append('Gemini')
    
    return jsonify({
        'frameworks': frameworks,
        'crewai_available': CREWAI_AVAILABLE,
        'langchain_available': LANGCHAIN_AVAILABLE,
        'transformers_available': TRANSFORMERS_AVAILABLE,
        'gemini_available': LANGCHAIN_AVAILABLE and bool(google_key)
    })

@app.route('/api/diagnostic')
def diagnostic():
    """Run diagnostic analysis"""
    try:
        ai = FlexibleAISystem()
        result = ai.generate_analysis()
        return jsonify(result)
    except Exception as e:
        print(f"Diagnostic error: {e}")
        return jsonify({
            'analysis': f'System Error: {str(e)}',
            'method': 'Error Handler',
            'frameworks': ['Error Handling'],
            'status': 'error',
            'generated_at': datetime.now().isoformat()
        })

if __name__ == '__main__':
    print("\n=== STARTING DIAGNOSTIC SERVER ===")
    print("Open http://localhost:5003 to see what's working")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5003, debug=True)