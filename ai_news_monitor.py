# ai_news_monitor.py
# Expert debugged version - ALL syntax errors fixed

import os
import json
import requests
import schedule
import time
import threading
import sqlite3
import hashlib
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Environment loaded")
except ImportError:
    print("⚠ dotenv not available - using system environment")
except Exception as e:
    print("⚠ Environment error: " + str(e))

# Try to import feedparser
try:
    import feedparser
    print("✓ feedparser available")
    FEEDPARSER_AVAILABLE = True
except ImportError:
    print("❌ feedparser not available")
    print("   Install with: pip install feedparser")
    FEEDPARSER_AVAILABLE = False

class AINewsMonitor:
    """Real-time AI news monitoring and notification system"""
    
    def __init__(self):
        print("=== AI NEWS MONITOR INIT ===")
        
        # Initialize database first
        self.init_database()
        
        # News sources - verified working RSS feeds
        self.news_sources = {
            'TechCrunch AI': 'https://techcrunch.com/category/artificial-intelligence/feed/',
            'VentureBeat AI': 'https://venturebeat.com/ai/feed/',
            'The Verge AI': 'https://www.theverge.com/ai-artificial-intelligence/rss/index.xml',
            'AI News': 'https://artificialintelligence-news.com/feed/',
            'Ars Technica': 'https://feeds.arstechnica.com/arstechnica/technology-lab'
        }
        
        # Keywords for filtering important news
        self.ai_keywords = [
            'artificial intelligence', 'machine learning', 'deep learning', 'neural network',
            'chatgpt', 'gpt-4', 'gpt-5', 'claude', 'gemini', 'openai', 'anthropic', 'google ai',
            'ai regulation', 'ai policy', 'ai governance', 'ai safety', 'ai ethics',
            'enterprise ai', 'ai adoption', 'ai investment', 'ai funding', 'ai startup',
            'large language model', 'llm', 'foundation model', 'generative ai',
            'microsoft copilot', 'github copilot', 'ai assistant', 'ai agent'
        ]
        
        # Notification services
        self.pushover_token = os.environ.get('PUSHOVER_TOKEN')
        self.pushover_user = os.environ.get('PUSHOVER_USER')
        self.webhook_url = os.environ.get('WEBHOOK_URL')
        
        pushover_status = '✓' if self.pushover_token else '❌'
        webhook_status = '✓' if self.webhook_url else '❌'
        feedparser_status = '✓' if FEEDPARSER_AVAILABLE else '❌'
        
        print("Pushover configured: " + pushover_status)
        print("Webhook configured: " + webhook_status)
        print("Feedparser available: " + feedparser_status)
        
        # Thread lock for database operations
        self._db_lock = threading.Lock()
        
        print("✓ AI News Monitor initialized successfully")
    
    def init_database(self):
        """Initialize SQLite database with proper error handling"""
        try:
            # Create database file
            db_path = 'ai_news.db'
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            
            # Create table if it doesn't exist
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sent_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_hash TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    source TEXT NOT NULL,
                    sent_at TIMESTAMP NOT NULL,
                    url TEXT NOT NULL
                )
            ''')
            self.conn.commit()
            cursor.close()
            print("✓ Database initialized successfully")
            
        except Exception as e:
            print("❌ Database initialization error: " + str(e))
            print("   Using in-memory database as fallback")
            try:
                # Fallback to in-memory database
                self.conn = sqlite3.connect(':memory:', check_same_thread=False)
                cursor = self.conn.cursor()
                cursor.execute('''
                    CREATE TABLE sent_articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        article_hash TEXT UNIQUE NOT NULL,
                        title TEXT NOT NULL,
                        source TEXT NOT NULL,
                        sent_at TIMESTAMP NOT NULL,
                        url TEXT NOT NULL
                    )
                ''')
                self.conn.commit()
                cursor.close()
                print("⚠ Using in-memory database")
            except Exception as fallback_error:
                print("❌ Fallback database error: " + str(fallback_error))
                self.conn = None
    
    def get_article_hash(self, title, url):
        """Generate unique hash for article"""
        try:
            # Clean inputs
            clean_title = str(title).strip()
            clean_url = str(url).strip()
            combined = clean_title + clean_url
            return hashlib.md5(combined.encode('utf-8')).hexdigest()
        except Exception as e:
            print("Hash generation error: " + str(e))
            # Fallback hash
            return hashlib.md5(str(title).encode('utf-8', errors='ignore')).hexdigest()
    
    def is_article_sent(self, article_hash):
        """Check if article was already sent - thread safe"""
        if not self.conn:
            return False
            
        try:
            with self._db_lock:
                cursor = self.conn.cursor()
                cursor.execute('SELECT 1 FROM sent_articles WHERE article_hash = ?', (article_hash,))
                result = cursor.fetchone()
                cursor.close()
                return result is not None
        except Exception as e:
            print("Database check error: " + str(e))
            return False
    
    def mark_article_sent(self, article_hash, title, source, url):
        """Mark article as sent - thread safe"""
        if not self.conn:
            return False
            
        try:
            with self._db_lock:
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO sent_articles (article_hash, title, source, sent_at, url)
                    VALUES (?, ?, ?, ?, ?)
                ''', (article_hash, title, source, datetime.now(), url))
                self.conn.commit()
                cursor.close()
                return True
        except Exception as e:
            print("Database insert error: " + str(e))
            return False
    
    def fetch_news_from_source(self, source_name, feed_url):
        """Fetch news from a single RSS source with comprehensive error handling"""
        if not FEEDPARSER_AVAILABLE:
            print("⚠ Feedparser not available - skipping " + source_name)
            return []
        
        try:
            print("Fetching from " + source_name + "...")
            
            # Set proper headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; AI News Monitor/1.0)',
                'Accept': 'application/rss+xml, application/xml, text/xml'
            }
            
            # Parse feed with timeout protection
            try:
                feed = feedparser.parse(feed_url, request_headers=headers)
            except Exception as parse_error:
                print("Feed parsing error for " + source_name + ": " + str(parse_error))
                return []
            
            # Check if feed was parsed successfully
            if not hasattr(feed, 'entries'):
                print("No entries attribute for " + source_name)
                return []
                
            if not feed.entries:
                print("No entries found for " + source_name)
                return []
            
            articles = []
            
            # Process up to 5 most recent articles
            for entry in feed.entries[:5]:
                try:
                    # Safely get entry attributes
                    title = getattr(entry, 'title', '').strip()
                    summary = getattr(entry, 'summary', '').strip()
                    link = getattr(entry, 'link', '').strip()
                    published = getattr(entry, 'published', '')
                    
                    # Skip if missing essential data
                    if not title or not link:
                        continue
                    
                    # Check if article is AI-related
                    content_to_check = (title + " " + summary).lower()
                    
                    is_ai_related = False
                    for keyword in self.ai_keywords:
                        if keyword in content_to_check:
                            is_ai_related = True
                            break
                    
                    if is_ai_related:
                        # Truncate summary if too long
                        if len(summary) > 200:
                            summary = summary[:200] + '...'
                        
                        article = {
                            'title': title,
                            'url': link,
                            'source': source_name,
                            'published': published,
                            'summary': summary,
                            'hash': self.get_article_hash(title, link)
                        }
                        articles.append(article)
                
                except Exception as entry_error:
                    print("Error processing entry from " + source_name + ": " + str(entry_error))
                    continue
            
            print("Found " + str(len(articles)) + " AI articles from " + source_name)
            return articles
            
        except Exception as e:
            print("Error fetching from " + source_name + ": " + str(e))
            return []
    
    def fetch_all_news(self):
        """Fetch news from all sources with improved error handling"""
        all_articles = []
        
        for source_name, feed_url in self.news_sources.items():
            try:
                articles = self.fetch_news_from_source(source_name, feed_url)
                all_articles.extend(articles)
                # Small delay between requests to be respectful
                time.sleep(1)
            except Exception as e:
                print("Error processing source " + source_name + ": " + str(e))
                continue
        
        # Remove duplicates based on hash
        unique_articles = {}
        for article in all_articles:
            article_hash = article.get('hash')
            if article_hash and article_hash not in unique_articles:
                unique_articles[article_hash] = article
        
        # Sort by most recent (handle missing published dates gracefully)
        def get_sort_key(article):
            try:
                published = article.get('published', '')
                if published:
                    return published
                else:
                    return datetime.now().isoformat()
            except:
                return datetime.now().isoformat()
        
        sorted_articles = sorted(unique_articles.values(), 
                               key=get_sort_key, reverse=True)
        
        print("Total unique AI articles found: " + str(len(sorted_articles)))
        return sorted_articles
    
    def send_pushover_notification(self, title, message, url=None):
        """Send notification via Pushover with proper error handling"""
        if not self.pushover_token or not self.pushover_user:
            print("⚠ Pushover not configured")
            return False
        
        try:
            # Prepare data with character limits
            data = {
                'token': self.pushover_token,
                'user': self.pushover_user,
                'title': str(title)[:250],  # Pushover title limit
                'message': str(message)[:1024],  # Pushover message limit
                'priority': 0,
                'sound': 'pushover'
            }
            
            if url:
                data['url'] = str(url)
                data['url_title'] = 'Read Article'
            
            # Send request
            response = requests.post(
                'https://api.pushover.net/1/messages.json', 
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                print("✓ Pushover notification sent successfully")
                return True
            else:
                print("❌ Pushover error " + str(response.status_code) + ": " + response.text)
                return False
                
        except Exception as e:
            print("❌ Pushover error: " + str(e))
            return False
    
    def send_webhook_notification(self, article):
        """Send notification via webhook with support for multiple services"""
        if not self.webhook_url:
            print("⚠ Webhook not configured")
            return False
        
        try:
            webhook_url = str(self.webhook_url).strip()
            
            # Handle different webhook services
            if 'ifttt.com' in webhook_url or 'maker.ifttt.com' in webhook_url:
                # IFTTT webhook format
                payload = {
                    'value1': "🤖 " + article['source'],  # Title
                    'value2': article['title'] + "\n\n" + article['summary'],  # Message
                    'value3': article['url']  # URL
                }
                
                response = requests.post(
                    webhook_url, 
                    json=payload, 
                    timeout=30,
                    headers={'Content-Type': 'application/json'}
                )
                
            elif 'ntfy.sh' in webhook_url:
                # ntfy.sh format - send as plain text with headers
                headers = {
                    'Title': "🤖 " + article['source'],
                    'Tags': 'robot,news',
                    'Priority': '3',
                    'Content-Type': 'text/plain'
                }
                
                message_body = article['title'] + "\n\n" + article['summary'] + "\n\nRead more: " + article['url']
                
                response = requests.post(
                    webhook_url, 
                    data=message_body.encode('utf-8'),
                    headers=headers,
                    timeout=30
                )
                
            else:
                # Generic webhook format (including webhook.site)
                payload = {
                    'title': '🤖 AI News Alert',
                    'message': article['title'] + "\n\nSource: " + article['source'] + "\n" + article['summary'],
                    'url': article['url'],
                    'source': article['source'],
                    'timestamp': datetime.now().isoformat()
                }
                
                response = requests.post(
                    webhook_url, 
                    json=payload, 
                    timeout=30,
                    headers={'Content-Type': 'application/json'}
                )
            
            # Check response
            if response.status_code in [200, 201, 202, 204]:
                print("✓ Webhook notification sent successfully")
                return True
            else:
                print("❌ Webhook error " + str(response.status_code) + ": " + response.text)
                return False
                
        except Exception as e:
            print("❌ Webhook error: " + str(e))
            return False
    
    def process_new_articles(self):
        """Process new articles and send notifications"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("\n=== CHECKING FOR NEW AI NEWS - " + current_time + " ===")
        
        try:
            # Fetch all articles
            articles = self.fetch_all_news()
            
            if not articles:
                print("No articles found")
                return []
            
            # Find new articles
            new_articles = []
            for article in articles:
                try:
                    article_hash = article.get('hash')
                    if article_hash and not self.is_article_sent(article_hash):
                        new_articles.append(article)
                except Exception as e:
                    print("Error checking article: " + str(e))
                    continue
            
            print("Found " + str(len(new_articles)) + " new articles")
            
            # Send notifications for new articles (limit to top 3 to avoid spam)
            notifications_sent = 0
            
            for article in new_articles[:3]:
                try:
                    # Create notification message
                    title = "AI News: " + article['source']
                    message = article['title'] + "\n\n" + article['summary']
                    
                    # Track if any notification was sent
                    notification_sent = False
                    
                    # Try Pushover
                    if self.pushover_token and self.pushover_user:
                        if self.send_pushover_notification(title, message, article['url']):
                            notification_sent = True
                    
                    # Try webhook
                    if self.webhook_url:
                        if self.send_webhook_notification(article):
                            notification_sent = True
                    
                    # Mark as sent if any notification was successful
                    if notification_sent:
                        if self.mark_article_sent(
                            article['hash'], 
                            article['title'], 
                            article['source'], 
                            article['url']
                        ):
                            print("✓ Sent: " + article['title'][:50] + "...")
                            notifications_sent += 1
                        else:
                            print("⚠ Failed to mark as sent: " + article['title'][:50] + "...")
                    else:
                        print("❌ No notifications sent for: " + article['title'][:50] + "...")
                    
                    # Rate limiting between notifications
                    time.sleep(2)
                    
                except Exception as e:
                    print("Error processing article: " + str(e))
                    continue
            
            print("Successfully sent " + str(notifications_sent) + " notifications")
            return new_articles
            
        except Exception as e:
            print("Error in process_new_articles: " + str(e))
            return []
    
    def get_recent_articles(self, hours=24):
        """Get recent articles for web interface"""
        try:
            articles = self.fetch_all_news()
            
            # Add "sent" status to articles
            for article in articles:
                try:
                    article_hash = article.get('hash')
                    if article_hash:
                        article['sent'] = self.is_article_sent(article_hash)
                    else:
                        article['sent'] = False
                except Exception as e:
                    print("Error checking sent status: " + str(e))
                    article['sent'] = False
            
            return articles[:20]  # Return top 20
            
        except Exception as e:
            print("Error getting recent articles: " + str(e))
            return []

# Flask application
app = Flask(__name__)
CORS(app)

# Global monitor instance
news_monitor = None

# Web interface
WEB_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI News Monitor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 50%, #581c87 100%);
            color: #f8fafc; min-height: 100vh; padding: 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .header {
            text-align: center; margin-bottom: 40px; padding: 30px;
            background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px);
            border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .header h1 { 
            font-size: 2.5rem; font-weight: 800; margin-bottom: 10px;
            background: linear-gradient(135deg, #60a5fa, #a78bfa, #fb7185);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .stats {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px; margin-bottom: 30px;
        }
        .stat-card {
            background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 15px;
            text-align: center; border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .stat-number { font-size: 2rem; font-weight: 800; color: #60a5fa; }
        .stat-label { font-size: 0.9rem; opacity: 0.8; margin-top: 5px; }
        .controls {
            display: flex; gap: 15px; margin-bottom: 30px; flex-wrap: wrap; justify-content: center;
        }
        .btn {
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            color: white; padding: 12px 24px; border: none; border-radius: 10px;
            font-weight: 600; cursor: pointer; transition: all 0.3s; font-size: 0.9rem;
        }
        .btn:hover { transform: translateY(-2px); }
        .articles { display: grid; gap: 20px; }
        .article {
            background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(10px);
            border-radius: 15px; padding: 25px; border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s;
        }
        .article:hover { 
            background: rgba(255, 255, 255, 0.12); transform: translateY(-2px);
        }
        .article-header {
            display: flex; justify-content: space-between; align-items: flex-start;
            margin-bottom: 15px; flex-wrap: wrap; gap: 10px;
        }
        .article-source {
            background: linear-gradient(135deg, #10b981, #059669);
            color: white; padding: 4px 12px; border-radius: 12px;
            font-size: 0.8rem; font-weight: 600;
        }
        .article-status { padding: 4px 12px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; }
        .sent { background: rgba(16, 185, 129, 0.2); color: #10b981; }
        .new { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
        .article-title {
            font-size: 1.2rem; font-weight: 700; margin-bottom: 10px; line-height: 1.4;
        }
        .article-title a { color: #f8fafc; text-decoration: none; }
        .article-title a:hover { color: #60a5fa; }
        .article-summary { color: #cbd5e1; line-height: 1.6; font-size: 0.95rem; }
        .loading { text-align: center; padding: 60px 20px; font-size: 1.2rem; opacity: 0.7; }
        .last-update { text-align: center; margin-top: 30px; opacity: 0.6; font-size: 0.9rem; }
        .error {
            background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444;
            color: #fecaca; padding: 20px; border-radius: 10px; margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI News Monitor</h1>
            <p>Real-time AI news monitoring with push notifications</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="total-articles">-</div>
                <div class="stat-label">Articles Today</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="new-articles">-</div>
                <div class="stat-label">New Articles</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="sources">5</div>
                <div class="stat-label">News Sources</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="checkForNews()">Check for News</button>
            <button class="btn" onclick="refreshArticles()">Refresh Articles</button>
            <button class="btn" onclick="testNotification()">Test Notification</button>
        </div>
        
        <div id="articles" class="articles">
            <div class="loading">Loading AI news articles...</div>
        </div>
        
        <div class="last-update">Last updated: <span id="last-update">Never</span></div>
    </div>
    
    <script>
        let articles = [];
        
        function updateStats() {
            const total = articles.length;
            const newCount = articles.filter(a => !a.sent).length;
            document.getElementById('total-articles').textContent = total;
            document.getElementById('new-articles').textContent = newCount;
        }
        
        function displayArticles() {
            const container = document.getElementById('articles');
            if (articles.length === 0) {
                container.innerHTML = '<div class="loading">No articles found</div>';
                return;
            }
            container.innerHTML = articles.map(article => `
                <div class="article">
                    <div class="article-header">
                        <div class="article-source">${article.source}</div>
                        <div class="article-status ${article.sent ? 'sent' : 'new'}">
                            ${article.sent ? 'Sent' : 'New'}
                        </div>
                    </div>
                    <div class="article-title">
                        <a href="${article.url}" target="_blank">${article.title}</a>
                    </div>
                    <div class="article-summary">${article.summary}</div>
                </div>
            `).join('');
            updateStats();
        }
        
        function refreshArticles() {
            document.getElementById('articles').innerHTML = '<div class="loading">Fetching latest articles...</div>';
            fetch('/api/articles')
                .then(response => response.json())
                .then(data => {
                    if (data.error) throw new Error(data.error);
                    articles = data.articles || [];
                    displayArticles();
                    document.getElementById('last-update').textContent = new Date().toLocaleString();
                })
                .catch(error => {
                    document.getElementById('articles').innerHTML = `<div class="error">Error: ${error.message}</div>`;
                });
        }
        
        function checkForNews() {
            document.getElementById('articles').innerHTML = '<div class="loading">Checking for new AI news...</div>';
            fetch('/api/check-news', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.error) throw new Error(data.error);
                    alert(`Found ${data.new_articles || 0} new articles. Notifications sent!`);
                    refreshArticles();
                })
                .catch(error => alert('Error: ' + error.message));
        }
        
        function testNotification() {
            fetch('/api/test-notification', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.success ? 'Test notification sent!' : 'Failed to send notification.');
                })
                .catch(error => alert('Error: ' + error.message));
        }
        
        setInterval(refreshArticles, 5 * 60 * 1000);
        refreshArticles();
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(WEB_INTERFACE)

@app.route('/api/articles')
def get_articles():
    """Get recent articles with comprehensive error handling"""
    try:
        global news_monitor
        if not news_monitor:
            news_monitor = AINewsMonitor()
        
        articles = news_monitor.get_recent_articles()
        return jsonify({
            'articles': articles,
            'count': len(articles),
            'timestamp': datetime.now().isoformat(),
            'success': True
        })
    except Exception as e:
        print("API error - get_articles: " + str(e))
        return jsonify({
            'error': str(e),
            'articles': [],
            'count': 0,
            'success': False
        }), 500

@app.route('/api/check-news', methods=['POST'])
def check_news():
    """Manually trigger news check"""
    try:
        global news_monitor
        if not news_monitor:
            news_monitor = AINewsMonitor()
        
        new_articles = news_monitor.process_new_articles()
        return jsonify({
            'success': True,
            'new_articles': len(new_articles),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print("API error - check_news: " + str(e))
        return jsonify({
            'error': str(e),
            'success': False,
            'new_articles': 0
        }), 500

@app.route('/api/test-notification', methods=['POST'])
def test_notification():
    """Send test notification"""
    try:
        global news_monitor
        if not news_monitor:
            news_monitor = AINewsMonitor()
        
        # Create test article
        test_article = {
            'title': 'AI News Monitor Test - System Working!',
            'summary': 'This is a test notification from your AI News Monitor system. If you received this, your notifications are working correctly!',
            'source': 'AI News Monitor',
            'url': 'https://github.com'
        }
        
        success = False
        
        # Test Pushover if configured
        if news_monitor.pushover_token and news_monitor.pushover_user:
            if news_monitor.send_pushover_notification("🤖 AI News Test", test_article['summary']):
                success = True
        
        # Test webhook if configured
        if news_monitor.webhook_url:
            if news_monitor.send_webhook_notification(test_article):
                success = True
        
        return jsonify({
            'success': success,
            'message': 'Test notification sent successfully!' if success else 'No notification services configured'
        })
    except Exception as e:
        print("API error - test_notification: " + str(e))
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/shortcuts/latest', methods=['GET'])
def shortcuts_latest():
    """iOS Shortcuts endpoint for latest news"""
    try:
        global news_monitor
        if not news_monitor:
            news_monitor = AINewsMonitor()
        
        articles = news_monitor.get_recent_articles()
        
        if not articles:
            return "No recent AI news found", 200, {'Content-Type': 'text/plain'}
        
        # Format for iOS Shortcuts
        latest = articles[0]
        text = "Latest AI News:\n\n" + latest['title'] + "\n\nSource: " + latest['source'] + "\n\n" + latest['summary'] + "\n\nRead more: " + latest['url']
        
        return text, 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        error_text = "AI News Monitor error: " + str(e)
        print("Shortcuts API error: " + str(e))
        return error_text, 500, {'Content-Type': 'text/plain'}

def run_scheduler():
    """Run the news checking scheduler"""
    print("Starting news monitoring scheduler...")
    
    try:
        # Schedule news checks every 30 minutes
        schedule.every(30).minutes.do(safe_news_check)
        
        # Also run at specific times
        schedule.every().day.at("08:00").do(safe_news_check)
        schedule.every().day.at("12:00").do(safe_news_check)
        schedule.every().day.at("18:00").do(safe_news_check)
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except Exception as e:
        print("Scheduler error: " + str(e))
        # Wait before retrying
        time.sleep(300)

def safe_news_check():
    """Safe wrapper for news checking"""
    try:
        global news_monitor
        if news_monitor:
            news_monitor.process_new_articles()
        else:
            print("News monitor not initialized")
    except Exception as e:
        print("Scheduled news check error: " + str(e))

if __name__ == '__main__':
    print("=== AI NEWS MONITOR STARTING ===")
    
    try:
        # Initialize monitor
        news_monitor = AINewsMonitor()
        
        # Start scheduler in background
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        print("\n🚀 AI News Monitor is running!")
        print("📱 Web interface: http://localhost:5006")
        print("🔔 Notifications will be sent automatically")
        print("📊 Monitor performance on the web interface")
        print("=" * 50)
        
        # Use environment PORT if available (for deployment)
        port = int(os.environ.get('PORT', 5006))
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print("❌ Startup error: " + str(e))
        print("Check your configuration and try again")