"""
DuckDuckGo search module with persona-driven responses
"""
import asyncio
import aiohttp
import random
import re
from urllib.parse import quote_plus, unquote
from bs4 import BeautifulSoup
from .persona_manager import PersonaManager

# Constants
DUCKDUCKGO_API_URL = "https://api.duckduckgo.com/"
DUCKDUCKGO_HTML_URL = "https://html.duckduckgo.com/html/"
DEFAULT_TIMEOUT = 10
WEB_SEARCH_TIMEOUT = 15
MAX_ABSTRACT_LENGTH = 800
MAX_SNIPPET_LENGTH = 150
MAX_DESCRIPTION_LENGTH = 200
MAX_AI_RESPONSE_LENGTH = 1500

# HTTP Headers for web requests
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

class TsundereSearch:
    def __init__(self, gemini_model, persona_file="persona_card.json"):
        self.model = gemini_model
        self.persona_manager = PersonaManager(persona_file)
        self.session = None
    
    def _get_persona_response(self, category, subcategory, format_kwargs=None):
        """Helper method to safely get persona responses from nested dictionaries"""
        try:
            responses = self.persona_manager.persona.get("activity_responses", {}).get(category, {}).get(subcategory, [])
            if responses:
                selected = random.choice(responses)
                return selected.format(**format_kwargs) if format_kwargs else selected
        except (KeyError, TypeError, ValueError) as e:
            print(f"⚠️ Error retrieving persona response: {e}")
        return None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    def _clean_url(self, url):
        """Clean and decode URLs from DuckDuckGo redirects"""
        try:
            # Handle DuckDuckGo redirect URLs
            if url.startswith('/l/?uddg='):
                url_match = re.search(r'uddg=([^&]+)', url)
                if url_match:
                    url = unquote(url_match.group(1))
            
            # Handle relative URLs
            elif url.startswith('/'):
                url = f"https://duckduckgo.com{url}"
            
            # Ensure URL has protocol
            elif not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            return url
        except Exception:
            return url
    
    def _validate_query(self, query):
        """Validate and sanitize search query"""
        if not query or not isinstance(query, str):
            return None
        
        query = query.strip()
        if len(query) == 0 or len(query) > 500:
            return None
        
        return query
    
    def _validate_query(self, query):
        """Validate and sanitize search query"""
        if not query or not isinstance(query, str):
            return None
        
        query = query.strip()
        if len(query) == 0 or len(query) > 500:
            return None
        
        return query
    
    async def _get_ai_search_analysis(self, query, search_results):
        """Get AI analysis of search results with tsundere personality"""
        try:
            from .api_manager import GeminiAPIManager
            
            # Create a prompt for AI analysis
            analysis_prompt = f"""You are Coffee, a tsundere AI assistant. A user searched for "{query}" and I found these search results:

{search_results}

Your task:
1. Analyze these search results and provide a helpful summary
2. Answer what the user was likely looking for based on "{query}"
3. Maintain your tsundere personality (reluctant to help but actually helpful)
4. Use your speech patterns: "Ugh", "baka", "It's not like...", etc.
5. Keep the response under {MAX_AI_RESPONSE_LENGTH} characters for Discord

Be informative but act annoyed about having to explain it. Include the most relevant information from the search results."""

            # Try to get the API manager from the bot's globals or create a new one
            import sys
            api_manager = None
            
            # First try to get from main module
            if hasattr(sys.modules.get('__main__'), 'api_manager'):
                api_manager = sys.modules['__main__'].api_manager
            else:
                # Create a new API manager instance if not available
                print("🔧 Creating new API manager for search analysis...")
                api_manager = GeminiAPIManager()
            
            if api_manager:
                ai_response = await api_manager.generate_content(analysis_prompt)
                
                if ai_response:
                    print(f"🤖 AI analysis generated: {ai_response[:100]}...")
                    return ai_response
            
            # Fallback if AI is not available
            print("⚠️ AI analysis not available, using fallback")
            return f"Here's what I found about **{query}**:\n\n{search_results}"
            
        except Exception as e:
            print(f"💥 AI analysis error: {e}")
            return f"Here's what I found about **{query}**:\n\n{search_results}"
    
    async def search_duckduckgo(self, query, max_results=5, use_ai_analysis=True):
        """
        Unified search function that can return either AI analysis or formatted links
        
        Args:
            query: Search query string (max 500 characters)
            max_results: Maximum number of results to return (default: 5)
            use_ai_analysis: If True, returns AI-powered analysis with persona flair.
                           If False, returns formatted links with snippets (default: True)
        
        Returns:
            str: Search results either as AI analysis or formatted links
        """
        # Validate query
        query = self._validate_query(query)
        if not query:
            return self._get_error_response(None, "Invalid or empty search query")
        
        try:
            print(f"🔍 Starting search for: {query} (AI: {use_ai_analysis})")
            session = await self._get_session()
            
            # Try DuckDuckGo Instant Answer API first
            encoded_query = quote_plus(query)
            url = f"{DUCKDUCKGO_API_URL}?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
            print(f"🌐 Requesting: {url}")
            
            async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
                print(f"📡 Response status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"📊 Response keys: {list(data.keys())}")
                    
                    # Check for instant answer (highest priority)
                    if data.get('Answer'):
                        print("✅ Found instant answer")
                        return self._format_instant_answer(query, data)
                    
                    # Check for abstract (Wikipedia-like results)
                    elif data.get('Abstract'):
                        print("✅ Found abstract")
                        return self._format_abstract(query, data)
                    
                    # Check for definition
                    elif data.get('Definition'):
                        print("✅ Found definition")
                        return self._format_definition(query, data)
                    
                    # Check for related topics
                    elif data.get('RelatedTopics'):
                        print(f"✅ Found {len(data['RelatedTopics'])} related topics")
                        return self._format_related_topics(query, data, max_results)
                    
                    else:
                        # No instant results - fall through to web search
                        print("❌ No instant results, trying web search...")
                
                # If no instant results or API failed, try web search
                print("🌐 Performing web search with HTML parsing...")
                web_results = await self._perform_web_search(query, max_results)
                
                if web_results:
                    if use_ai_analysis:
                        print("🤖 Getting AI analysis of search results...")
                        ai_analysis = await self._get_ai_search_analysis(query, web_results['raw'])
                        return ai_analysis
                    else:
                        print("📋 Returning formatted web links...")
                        return web_results['formatted']
                else:
                    return self._get_no_results_response(query)
                    
        except asyncio.TimeoutError:
            print("⏰ Search timed out")
            return self._get_timeout_response(query)
        except Exception as e:
            print(f"💥 Search error: {str(e)}")
            return self._get_error_response(query, str(e))
    
    def _format_instant_answer(self, query, data):
        """Format instant answer results"""
        answer = data['Answer']
        answer_type = data.get('AnswerType', 'calculation')
        
        # Use answer_type for context-specific responses
        if answer_type in ['calculation', 'math']:
            # Get calculation-specific response from persona
            response = self._get_persona_response('calculation', 'success',
                {'result': answer, 'answer_type': answer_type, 'expression': query})
            if not response:
                response = f"**{answer}**"
        else:
            response = self._get_persona_response('search', 'instant_answer',
                {'answer': answer, 'query': query, 'answer_type': answer_type})
            if not response:
                response = f"**{answer}**"
        
        return response
    
    def _format_abstract(self, query, data):
        """Format abstract/Wikipedia-like results"""
        abstract = data['Abstract']
        source = data.get('AbstractSource', 'Unknown')
        url = data.get('AbstractURL', '')
        
        # Truncate if too long
        if len(abstract) > MAX_ABSTRACT_LENGTH:
            abstract = abstract[:MAX_ABSTRACT_LENGTH] + "..."
        
        response = self._get_persona_response('search', 'abstract',
            {'query': query, 'abstract': abstract, 'source': source})
        
        if not response:
            response = f"**{query}**:\n\n{abstract}\n\n*Source: {source}*"
        
        if url:
            response += f"\n🔗 {url}"
        
        return response
    
    def _format_related_topics(self, query, data, max_results):
        """Format related topics results"""
        topics = data['RelatedTopics'][:max_results]
        
        if not topics:
            return self._get_no_results_response(query)
        
        results = []
        for topic in topics:
            if isinstance(topic, dict) and 'Text' in topic:
                text = topic['Text']
                url = topic.get('FirstURL', '')
                
                # Truncate long descriptions
                if len(text) > MAX_DESCRIPTION_LENGTH:
                    text = text[:MAX_DESCRIPTION_LENGTH] + "..."
                
                result_item = f"• {text}"
                if url:
                    result_item += f"\n  🔗 {url}"
                
                results.append(result_item)
        
        if results:
            results_text = "\n\n".join(results)
            response = self._get_persona_response('search', 'related_topics',
                {'query': query, 'results': results_text})
            return response if response else f"**{query}**:\n\n{results_text}"
        
        return self._get_no_results_response(query)
    
    def _format_definition(self, query, data):
        """Format definition results"""
        definition = data['Definition']
        source = data.get('DefinitionSource', 'Dictionary')
        
        success_responses = self.persona_manager.persona.get("activity_responses", {}).get("search", {}).get("definition", [])
        
        if success_responses:
            return random.choice(success_responses).format(
                query=query, definition=definition, source=source
            )
        else:
            return f"**{query}**:\n\n{definition}\n\n*Source: {source}*"
    
    def _get_no_results_response(self, query):
        """Get response when no results found"""
        no_results_responses = self.persona_manager.persona.get("activity_responses", {}).get("search", {}).get("no_results", [])
        
        if no_results_responses:
            return random.choice(no_results_responses).format(query=query)
        else:
            return f"No results found for **{query}**"
    
    def _get_error_response(self, query, error=None):
        """Get response when search fails"""
        error_responses = self.persona_manager.persona.get("activity_responses", {}).get("search", {}).get("error", [])
        
        if error_responses:
            return random.choice(error_responses)
        else:
            return "Search error occurred"
    
    def _get_timeout_response(self, query):
        """Get response when search times out"""
        timeout_responses = self.persona_manager.persona.get("activity_responses", {}).get("search", {}).get("timeout", [])
        
        if timeout_responses:
            return random.choice(timeout_responses).format(query=query)
        else:
            return f"Search timed out for **{query}**"
    
    async def web_search(self, query, max_results=3):
        """
        Web search returning formatted links with snippets (backward compatible)
        This is a convenience method that calls search_duckduckgo with use_ai_analysis=False
        """
        return await self.search_duckduckgo(query, max_results, use_ai_analysis=False)
    
    async def _perform_web_search(self, query, max_results=3):
        """
        Unified web search that returns both raw and formatted results
        Returns dict with 'raw' and 'formatted' keys for flexibility
        """
        try:
            print(f"🌐 Starting web search for: {query}")
            session = await self._get_session()
            
            # DuckDuckGo search with HTML parsing
            search_url = DUCKDUCKGO_HTML_URL
            params = {
                'q': query,
                'b': '',  # No ads
                'kl': 'us-en',  # Language
                'df': '',  # Date filter
                's': '0',  # Start from first result
            }
            
            print(f"📡 Requesting web search: {search_url}")
            async with session.post(search_url, data=params, headers=DEFAULT_HEADERS, timeout=WEB_SEARCH_TIMEOUT) as response:
                print(f"📊 Web search response status: {response.status}")
                if response.status == 200:
                    html = await response.text()
                    print(f"📄 Received HTML content ({len(html)} chars)")
                    return self._parse_search_results(query, html, max_results)
                else:
                    print(f"❌ Bad web search response: {response.status}")
                    return None
                    
        except asyncio.TimeoutError:
            print("⏰ Web search timed out")
            return None
        except Exception as e:
            print(f"💥 Web search error: {str(e)}")
            return None
    
    def _parse_search_results(self, query, html, max_results):
        """
        Parse HTML search results and return both formatted and raw versions
        Returns dict with 'formatted' (for link output) and 'raw' (for AI analysis)
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            formatted_results = []
            raw_results = []
            
            # Find all result containers
            result_containers = soup.find_all('div', class_='result')
            
            for container in result_containers[:max_results]:
                try:
                    # Extract title and URL
                    title_link = container.find('a', class_='result__a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    url = title_link.get('href', '')
                    
                    if not title or not url:
                        continue
                    
                    # Clean up the URL (DuckDuckGo sometimes uses redirect URLs)
                    url = self._clean_url(url)
                    
                    # Extract snippet/description
                    snippet_elem = container.find('a', class_='result__snippet')
                    snippet = ""
                    if snippet_elem:
                        snippet = snippet_elem.get_text(strip=True)
                    
                    # Format for links (Discord display)
                    result_text = f"• **{title}**\n  🔗 {url}"
                    if snippet:
                        # Truncate long snippets
                        if len(snippet) > MAX_SNIPPET_LENGTH:
                            snippet = snippet[:MAX_SNIPPET_LENGTH] + "..."
                        result_text += f"\n  📝 {snippet}"
                    
                    formatted_results.append(result_text)
                    
                    # Format for AI analysis (clean text)
                    raw_text = f"Title: {title}\nURL: {url}"
                    if snippet:
                        raw_text += f"\nDescription: {snippet}"
                    raw_results.append(raw_text)
                    
                except Exception as e:
                    print(f"⚠️ Error parsing individual result: {e}")
                    continue
            
            if formatted_results:
                formatted_text = "\n\n".join(formatted_results)
                raw_text = "\n\n".join(raw_results)
                
                # Format the final response with persona
                response = self._get_persona_response('search', 'web_results',
                    {'query': query, 'results': formatted_text})
                
                if not response:
                    response = f"**{query}**:\n\n{formatted_text}"
                
                return {
                    'formatted': response,
                    'raw': raw_text
                }
            
            return None
            
        except Exception as e:
            print(f"💥 HTML parsing error: {e}")
            return None 
