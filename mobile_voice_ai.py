# mobile_voice_ai.py
# Mobile-accessible AI system with voice capabilities

print("=== MOBILE VOICE AI SYSTEM ===")

import os
import json
import socket
from datetime import datetime
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Environment loaded")
except:
    print("⚠ dotenv not available")

# AI imports with fallbacks
CREWAI_AVAILABLE = False
LANGCHAIN_AVAILABLE = False

try:
    from crewai import Agent, Task, Crew, Process
    print("✓ CrewAI available")
    CREWAI_AVAILABLE = True
except:
    print("⚠ CrewAI not available")

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("✓ LangChain available")
    LANGCHAIN_AVAILABLE = True
except:
    print("⚠ LangChain not available")

class MobileAISystem:
    """Mobile-optimized AI system with voice capabilities"""
    
    def __init__(self):
        print("\n=== MOBILE AI SYSTEM INIT ===")
        
        self.google_key = os.environ.get('GOOGLE_API_KEY')
        print(f"Google API: {'✓' if self.google_key else '❌'}")
        
        self.setup_ai()
        
    def setup_ai(self):
        """Setup AI with mobile-optimized settings"""
        if LANGCHAIN_AVAILABLE and self.google_key:
            try:
                self.gemini = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",  # Fast model for mobile
                    google_api_key=self.google_key,
                    temperature=0.7
                )
                self.ai_available = True
                print("✓ Gemini ready for mobile")
            except Exception as e:
                print(f"❌ Gemini setup failed: {e}")
                self.ai_available = False
        else:
            self.ai_available = False
            print("⚠ Using demo mode")
    
    def get_quick_briefing(self):
        """Mobile-optimized quick briefing"""
        if self.ai_available:
            try:
                prompt = """Provide a concise AI market briefing in exactly this format for mobile reading:

🎯 TOP AI APP /FRAMEWORK DEVELOPMENT:
[Three key developments in AI this week, each in 1-2 sentences]

MOST IMPORTANT AI REGULATORY NEWS:
[One key regulatory update or framework change]
[Share link to learn more if available]
[Give 5 key takeaways from regulatory frameworks]

💼 BUSINESS IMPACT:
[2-3 sentences on business implications]

📈 INVESTMENT ANGLE:
[Key investment opportunity or risk]

⚡ ACTION ITEM:
[One specific action to take]

Keep it under 200 words total. Be conversational and actionable."""

                response = self.gemini.invoke(prompt)
                content = response.content if hasattr(response, 'content') else str(response)
                
                return {
                    'briefing': content,
                    'voice_text': self.prepare_voice_text(content),
                    'method': 'Gemini Mobile',
                    'status': 'success',
                    'timestamp': datetime.now().strftime('%I:%M %p')
                }
            except Exception as e:
                print(f"AI error: {e}")
                return self.get_mobile_demo()
        else:
            return self.get_mobile_demo()
    
    def get_mobile_demo(self):
        """Mobile-optimized demo briefing"""
        current_time = datetime.now()
        
        briefing = f"""🎯 TOP AI DEVELOPMENT:
Enterprise AI adoption hits 78% among Fortune 500 companies this quarter, with deployment time reducing by 65%.

💼 BUSINESS IMPACT:
Companies using AI strategically are seeing 25% faster decision-making and 40% improvement in operational efficiency. The competitive gap is widening quickly.

MOST IMPORTANT AI REGULATORY NEWS:
5 key regulatory updates or framework change


📈 INVESTMENT ANGLE:
AI infrastructure stocks up 32% this quarter. Best opportunities in specialized AI tools and data management platforms.

⚡ ACTION ITEM:
Assess your organization's AI readiness this week. Leaders moving now will dominate their markets by 2026.

Generated at {current_time.strftime('%I:%M %p')} • Demo Mode"""

        return {
            'briefing': briefing,
            'voice_text': self.prepare_voice_text(briefing),
            'method': 'Mobile Demo',
            'status': 'demo',
            'timestamp': current_time.strftime('%I:%M %p')
        }
    
    def prepare_voice_text(self, text):
        """Prepare text for voice reading"""
        # Clean up for voice synthesis
        voice_text = text.replace('🎯', 'Top AI Development: ')
        voice_text = voice_text.replace('💼', 'Business Impact: ')
        voice_text = voice_text.replace('💼', 'Regulatory Change: ')
        voice_text = voice_text.replace('📈', 'Investment Angle: ')
        voice_text = voice_text.replace('⚡', 'Action Item: ')
        voice_text = voice_text.replace('•', '. ')
        voice_text = voice_text.replace('\n\n', '. ')
        voice_text = voice_text.replace('\n', ' ')
        
        return voice_text

# Flask app with mobile optimization
app = Flask(__name__)
CORS(app)  # Enable cross-origin requests for mobile

# Get local IP for mobile access
def get_local_ip():
    try:
        # Connect to a remote address to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

# Mobile-optimized dashboard
MOBILE_DASHBOARD = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Voice Assistant</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <style>
        * { 
            margin: 0; padding: 0; box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', system-ui, sans-serif;
            background: linear-gradient(145deg, #000000 0%, #1a1a2e 30%, #16213e 70%, #0f3460 100%);
            color: #ffffff; min-height: 100vh; overflow-x: hidden;
            padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left);
        }
        
        .container { 
            max-width: 400px; margin: 0 auto; padding: 20px 15px;
            min-height: 100vh; display: flex; flex-direction: column;
        }
        
        .header {
            text-align: center; margin-bottom: 30px; padding: 25px 20px;
            background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(20px);
            border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .header h1 { 
            font-size: 1.8rem; font-weight: 800; margin-bottom: 8px;
            background: linear-gradient(135deg, #60a5fa, #a78bfa, #fb7185);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        
        .header p { 
            font-size: 0.9rem; color: #94a3b8; margin-bottom: 15px;
        }
        
        .status-badge {
            display: inline-block; padding: 6px 12px;
            background: linear-gradient(135deg, #10b981, #059669);
            border-radius: 15px; font-size: 0.75rem; font-weight: 600;
            text-transform: uppercase; letter-spacing: 0.5px;
        }
        
        .action-section {
            flex: 1; display: flex; flex-direction: column; justify-content: center;
            margin: 20px 0;
        }
        
        .main-button { 
            width: 100%; margin-bottom: 15px;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            color: white; padding: 18px 25px; border: none; border-radius: 16px;
            font-size: 1.1rem; font-weight: 700; cursor: pointer;
            transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 0.5px;
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
            touch-action: manipulation;
        }
        
        .main-button:active { 
            transform: scale(0.98); 
            box-shadow: 0 4px 16px rgba(59, 130, 246, 0.5);
        }
        
        .voice-button {
            background: linear-gradient(135deg, #ec4899, #f43f5e);
            box-shadow: 0 8px 32px rgba(236, 72, 153, 0.3);
        }
        
        .voice-button:active {
            box-shadow: 0 4px 16px rgba(236, 72, 153, 0.5);
        }
        
        .quick-actions {
            display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
            margin-bottom: 20px;
        }
        
        .quick-btn {
            background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px;
            color: white; padding: 12px; font-size: 0.9rem; font-weight: 600;
            cursor: pointer; transition: all 0.2s ease; touch-action: manipulation;
        }
        
        .quick-btn:active {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(0.96);
        }
        
        .results { 
            background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(20px);
            border-radius: 16px; padding: 20px; margin-top: 20px; display: none;
            border: 1px solid rgba(255, 255, 255, 0.1);
            animation: slideUp 0.3s ease;
        }
        
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .loading { 
            text-align: center; font-size: 1rem; color: #94a3b8;
            padding: 40px 20px; animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.6; }
            50% { opacity: 1; }
        }
        
        .briefing-content {
            line-height: 1.6; font-size: 0.95rem; color: #e2e8f0;
            white-space: pre-wrap; margin: 15px 0;
        }
        
        .meta-bar {
            display: flex; justify-content: space-between; align-items: center;
            margin-top: 15px; padding-top: 15px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 0.8rem; color: #94a3b8;
        }
        
        .voice-controls {
            display: flex; gap: 10px; margin-top: 15px;
        }
        
        .voice-control-btn {
            flex: 1; background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 8px;
            color: white; padding: 10px; font-size: 0.8rem; font-weight: 600;
            cursor: pointer; transition: all 0.2s; touch-action: manipulation;
        }
        
        .voice-control-btn:active {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .speaking { 
            background: linear-gradient(135deg, #10b981, #059669) !important;
            animation: speaking 1s ease-in-out infinite alternate;
        }
        
        @keyframes speaking {
            from { opacity: 0.7; }
            to { opacity: 1; }
        }
        
        /* iOS Shortcuts hint */
        .shortcuts-hint {
            background: rgba(255, 255, 255, 0.05); border-radius: 12px;
            padding: 15px; margin-top: 20px; font-size: 0.8rem;
            color: #94a3b8; text-align: center; line-height: 1.4;
        }
        
        .shortcuts-hint strong { color: #60a5fa; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Voice Assistant</h1>
            <p>Enterprise AI intelligence on-demand</p>
            <div class="status-badge" id="status">Ready</div>
        </div>
        
        <div class="action-section">
            <div class="quick-actions">
                <button class="quick-btn" onclick="getQuickUpdate()">Quick Update</button>
                <button class="quick-btn" onclick="getFullBriefing()">Full Analysis</button>
            </div>
            
            <button class="main-button" onclick="getAIBriefing()">
                Generate AI Briefing
            </button>
            
            <button class="main-button voice-button" onclick="getVoiceBriefing()">
                Voice Briefing
            </button>
        </div>
        
        <div id="results" class="results">
            <div id="loading" class="loading">AI processing...</div>
            <div id="content" style="display:none;">
                <div id="briefing" class="briefing-content"></div>
                <div class="voice-controls">
                    <button class="voice-control-btn" onclick="speakBriefing()">🔊 Read Aloud</button>
                    <button class="voice-control-btn" onclick="stopSpeaking()">⏹ Stop</button>
                    <button class="voice-control-btn" onclick="copyToClipboard()">📋 Copy</button>
                </div>
                <div class="meta-bar">
                    <span id="method">-</span>
                    <span id="timestamp">-</span>
                </div>
            </div>
        </div>
        
        <div class="shortcuts-hint">
            <strong>iOS Shortcuts:</strong> Add this URL to Shortcuts for voice activation<br>
            <span id="api-url">Loading...</span>
        </div>
    </div>
    
    <script>
        let currentVoiceText = '';
        let speechSynthesis = window.speechSynthesis;
        let currentUtterance = null;
        
        // Set API URL for Shortcuts
        window.onload = function() {
            const apiUrl = window.location.origin + '/api/voice-briefing';
            document.getElementById('api-url').textContent = apiUrl;
        };
        
        function updateStatus(text, isLoading = false) {
            const status = document.getElementById('status');
            status.textContent = text;
            status.className = isLoading ? 'status-badge loading' : 'status-badge';
        }
        
        function showResults(data) {
            document.getElementById('results').style.display = 'block';
            document.getElementById('loading').style.display = 'none';
            document.getElementById('content').style.display = 'block';
            
            document.getElementById('briefing').textContent = data.briefing || 'No briefing available';
            document.getElementById('method').textContent = data.method || 'Unknown';
            document.getElementById('timestamp').textContent = data.timestamp || 'Now';
            
            currentVoiceText = data.voice_text || data.briefing || '';
            updateStatus('Ready');
        }
        
        function showLoading() {
            document.getElementById('results').style.display = 'block';
            document.getElementById('loading').style.display = 'block';
            document.getElementById('content').style.display = 'none';
            updateStatus('Processing...', true);
        }
        
        function getAIBriefing() {
            showLoading();
            fetch('/api/mobile-briefing')
                .then(response => response.json())
                .then(data => showResults(data))
                .catch(error => {
                    console.error('Error:', error);
                    showResults({
                        briefing: 'Connection error. Please check your network.',
                        method: 'Error',
                        timestamp: new Date().toLocaleTimeString()
                    });
                });
        }
        
        function getVoiceBriefing() {
            showLoading();
            fetch('/api/voice-briefing')
                .then(response => response.json())
                .then(data => {
                    showResults(data);
                    // Auto-speak for voice briefing
                    setTimeout(() => speakBriefing(), 500);
                })
                .catch(error => {
                    console.error('Error:', error);
                    showResults({
                        briefing: 'Voice briefing unavailable. Please try again.',
                        method: 'Voice Error',
                        timestamp: new Date().toLocaleTimeString()
                    });
                });
        }
        
        function getQuickUpdate() {
            showLoading();
            fetch('/api/quick-update')
                .then(response => response.json())
                .then(data => showResults(data))
                .catch(error => console.error('Error:', error));
        }
        
        function getFullBriefing() {
            getAIBriefing();
        }
        
        function speakBriefing() {
            if (!currentVoiceText) return;
            
            stopSpeaking();
            
            currentUtterance = new SpeechSynthesisUtterance(currentVoiceText);
            currentUtterance.rate = 0.9;
            currentUtterance.pitch = 1;
            currentUtterance.volume = 1;
            
            currentUtterance.onstart = function() {
                updateStatus('Speaking...', true);
                document.querySelector('.voice-control-btn').classList.add('speaking');
            };
            
            currentUtterance.onend = function() {
                updateStatus('Ready');
                document.querySelector('.voice-control-btn').classList.remove('speaking');
            };
            
            speechSynthesis.speak(currentUtterance);
        }
        
        function stopSpeaking() {
            speechSynthesis.cancel();
            updateStatus('Ready');
            const speakBtn = document.querySelector('.voice-control-btn');
            if (speakBtn) speakBtn.classList.remove('speaking');
        }
        
        function copyToClipboard() {
            if (!currentVoiceText) return;
            
            navigator.clipboard.writeText(currentVoiceText).then(() => {
                updateStatus('Copied!');
                setTimeout(() => updateStatus('Ready'), 2000);
            }).catch(() => {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = currentVoiceText;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                updateStatus('Copied!');
                setTimeout(() => updateStatus('Ready'), 2000);
            });
        }
        
        // Auto-load briefing on page load for quick access
        document.addEventListener('DOMContentLoaded', function() {
            // Uncomment next line for auto-load
            // setTimeout(getAIBriefing, 1000);
        });
    </script>
</body>
</html>
"""

# API endpoints optimized for mobile and Shortcuts
@app.route('/')
def mobile_dashboard():
    return render_template_string(MOBILE_DASHBOARD)

@app.route('/api/mobile-briefing')
def mobile_briefing():
    """Mobile-optimized briefing"""
    try:
        ai_system = MobileAISystem()
        result = ai_system.get_quick_briefing()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'briefing': f'System temporarily unavailable. Error: {str(e)}',
            'voice_text': 'AI system temporarily unavailable',
            'method': 'Error Handler',
            'status': 'error',
            'timestamp': datetime.now().strftime('%I:%M %p')
        })

@app.route('/api/voice-briefing')
def voice_briefing():
    """Voice-optimized briefing for iOS Shortcuts"""
    try:
        ai_system = MobileAISystem()
        result = ai_system.get_quick_briefing()
        
        # Return just the voice text for Shortcuts
        if request.headers.get('User-Agent', '').find('Shortcuts') != -1:
            return result['voice_text']
        
        return jsonify(result)
    except Exception as e:
        error_text = "AI voice briefing temporarily unavailable"
        return jsonify({
            'briefing': error_text,
            'voice_text': error_text,
            'method': 'Voice Error',
            'status': 'error',
            'timestamp': datetime.now().strftime('%I:%M %p')
        })

@app.route('/api/quick-update')
def quick_update():
    """Ultra-quick update for fast access"""
    return jsonify({
        'briefing': f"""🚀 QUICK AI UPDATE ({datetime.now().strftime('%I:%M %p')})

Enterprise AI adoption accelerating globally. Key developments:
• 65% of Fortune 500 now using AI in core operations
• AI infrastructure investments up 40% this quarter  
• Regulatory frameworks advancing rapidly

Action: Assess your AI strategy this week.""",
        'voice_text': 'Quick AI update: Enterprise AI adoption accelerating globally. 65% of Fortune 500 now using AI in core operations. Infrastructure investments up 40% this quarter. Action item: assess your AI strategy this week.',
        'method': 'Quick Update',
        'status': 'success',
        'timestamp': datetime.now().strftime('%I:%M %p')
    })

# iOS Shortcuts compatible endpoint
@app.route('/api/shortcuts/voice', methods=['GET', 'POST'])
def shortcuts_voice():
    """iOS Shortcuts compatible voice endpoint"""
    try:
        ai_system = MobileAISystem()
        result = ai_system.get_quick_briefing()
        
        # Return plain text for Shortcuts text-to-speech
        return result['voice_text'], 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        return "AI briefing temporarily unavailable", 500, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    local_ip = get_local_ip()
    port = 5005
    
    print(f"\n=== MOBILE AI VOICE SYSTEM ===")
    print(f"Local access: http://localhost:{port}")
    print(f"Mobile access: http://{local_ip}:{port}")
    print(f"iOS Shortcuts URL: http://{local_ip}:{port}/api/shortcuts/voice")
    print("=" * 50)
    print("📱 Open the mobile URL on your phone")
    print("🔊 Add Shortcuts URL to iOS Shortcuts for voice activation")
    print("=" * 50)
    
    # Run on all interfaces so mobile can access
    app.run(host='0.0.0.0', port=port, debug=False)  # debug=False for mobile stability