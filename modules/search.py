"""
DuckDuckGo search module with persona-driven responses
"""
import asyncio
import aiohttp
import json
import random
import re
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from .persona_manager import PersonaManager

class TsundereSearch:
    def __init__(self, gemini_model, persona_file="persona_card.json"):
        self.model = gemini_model
        self.persona_manager = PersonaManager(persona_file)
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _clean_url(self, url):
        """Clean and decode URLs from DuckDuckGo redirects"""
        try:
            # Handle DuckDuckGo redirect URLs
            if url.startswith('/l/?uddg='):
                url_match = re.search(r'uddg=([^&]+)', url)
                if url_match:
                    from urllib.parse import unquote
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
    
    async def search_duckduckgo(self, query, max_results=5):
        """
        Search DuckDuckGo using their instant answer API
        Returns formatted search results with persona flair
        """
        try:
            print(f"🔍 Starting search for: {query}")
            session = await self._get_session()
            
            # DuckDuckGo Instant Answer API
            encoded_query = quote_plus(query)
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
            print(f"🌐 Requesting: {url}")
            
            async with session.get(url, timeout=10) as response:
                print(f"📡 Response status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"📊 Response keys: {list(data.keys())}")
                    
                    # Debug logging (can be enabled for troubleshooting)
                    debug_info = json.dumps({'query': query, 'response_keys': list(data.keys())}, indent=2)
                    # Store debug info for potential error reporting
                    if not data.get('Answer') and not data.get('Abstract') and not data.get('RelatedTopics') and not data.get('Definition'):
                        print(f"Search debug - no results found: {debug_info}")
                    
                    # Check for instant answer
                    if data.get('Answer'):
                        print("✅ Found instant answer")
                        return self._format_instant_answer(query, data)
                    
                    # Check for abstract (Wikipedia-like results)
                    elif data.get('Abstract'):
                        print("✅ Found abstract")
                        return self._format_abstract(query, data)
                    
                    # Check for related topics
                    elif data.get('RelatedTopics'):
                        print(f"✅ Found {len(data['RelatedTopics'])} related topics")
                        return self._format_related_topics(query, data, max_results)
                    
                    # Check for definition
                    elif data.get('Definition'):
                        print("✅ Found definition")
                        return self._format_definition(query, data)
                    
                    else:
                        # No results found - try web search as fallback
                        print("❌ No instant results, trying web search...")
                        fallback_result = await self.web_search(query, max_results)
                        print(f"🔄 Fallback result: {fallback_result[:100]}...")
                        return fallback_result
                else:
                    print(f"❌ API returned status {response.status}, trying web search fallback...")
                    fallback_result = await self.web_search(query, max_results)
                    print(f"🔄 Fallback result: {fallback_result[:100]}...")
                    return fallback_result
                    
        except asyncio.TimeoutError:
            print("⏰ API search timed out, trying web search fallback...")
            try:
                fallback_result = await self.web_search(query, max_results)
                print(f"🔄 Timeout fallback result: {fallback_result[:100]}...")
                return fallback_result
            except Exception:
                return self._get_timeout_response(query)
        except Exception as e:
            print(f"💥 API search error: {str(e)}, trying web search fallback...")
            try:
                fallback_result = await self.web_search(query, max_results)
                print(f"🔄 Error fallback result: {fallback_result[:100]}...")
                return fallback_result
            except Exception:
                return self._get_error_response(query, str(e))
    
    def _format_instant_answer(self, query, data):
        """Format instant answer results"""
        answer = data['Answer']
        answer_type = data.get('AnswerType', 'calculation')
        
        success_responses = self.persona_manager.persona.get("activity_responses", {}).get("search", {}).get("instant_answer", [])
        
        # Use answer_type for context-specific responses
        if answer_type in ['calculation', 'math']:
            # Get calculation-specific response from persona
            calc_responses = self.persona_manager.persona.get("activity_responses", {}).get("calculation", {}).get("success", [])
            if calc_responses:
                response = random.choice(calc_responses).format(result=answer, answer_type=answer_type, expression=query)
            else:
                response = f"**{answer}**"
        else:
            if success_responses:
                response = random.choice(success_responses).format(answer=answer, query=query, answer_type=answer_type)
            else:
                response = f"**{answer}**"
        return response
    
    def _format_abstract(self, query, data):
        """Format abstract/Wikipedia-like results"""
        abstract = data['Abstract']
        source = data.get('AbstractSource', 'Unknown')
        url = data.get('AbstractURL', '')
        
        # Truncate if too long
        if len(abstract) > 800:
            abstract = abstract[:800] + "..."
        
        success_responses = self.persona_manager.persona.get("activity_responses", {}).get("search", {}).get("abstract", [])
        
        if success_responses:
            response = random.choice(success_responses).format(
                query=query, abstract=abstract, source=source
            )
        else:
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
                if len(text) > 200:
                    text = text[:200] + "..."
                
                result_item = f"• {text}"
                if url:
                    result_item += f"\n  🔗 {url}"
                
                results.append(result_item)
        
        if results:
            results_text = "\n\n".join(results)
            
            success_responses = self.persona_manager.persona.get("activity_responses", {}).get("search", {}).get("related_topics", [])
            
            if success_responses:
                return random.choice(success_responses).format(query=query, results=results_text)
            else:
                return f"**{query}**:\n\n{results_text}"
        else:
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
        Web search using DuckDuckGo's HTML interface with proper parsing
        This provides more comprehensive results than the instant answer API
        """
        try:
            print(f"🌐 Starting web search for: {query}")
            session = await self._get_session()
            
            # DuckDuckGo search with HTML parsing
            search_url = "https://html.duckduckgo.com/html/"
            params = {
                'q': query,
                'b': '',  # No ads
                'kl': 'us-en',  # Language
                'df': '',  # Date filter
                's': '0',  # Start from first result
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            print(f"📡 Requesting web search: {search_url}")
            async with session.post(search_url, data=params, headers=headers, timeout=15) as response:
                print(f"📊 Web search response status: {response.status}")
                if response.status == 200:
                    html = await response.text()
                    print(f"📄 Received HTML content ({len(html)} chars)")
                    return self._parse_search_results(query, html, max_results)
                else:
                    print(f"❌ Bad web search response: {response.status}")
                    return self._get_error_response(query)
                    
        except asyncio.TimeoutError:
            print("⏰ Web search timed out")
            return self._get_timeout_response(query)
        except Exception as e:
            print(f"💥 Web search error: {str(e)}")
            return self._get_error_response(query, str(e))
    
    def _parse_search_results(self, query, html, max_results):
        """
        Parse HTML search results using BeautifulSoup for robust parsing
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            results = []
            
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
                        # Truncate long snippets
                        if len(snippet) > 150:
                            snippet = snippet[:150] + "..."
                    
                    # Format result
                    result_text = f"• **{title}**\n  🔗 {url}"
                    if snippet:
                        result_text += f"\n  📝 {snippet}"
                    
                    results.append(result_text)
                    
                except Exception as e:
                    print(f"⚠️ Error parsing individual result: {e}")
                    continue
            
            if results:
                results_text = "\n\n".join(results)
                
                success_responses = self.persona_manager.persona.get("activity_responses", {}).get("search", {}).get("web_results", [])
                
                if success_responses:
                    return random.choice(success_responses).format(query=query, results=results_text)
                else:
                    return f"**{query}**:\n\n{results_text}"
            
            return self._get_no_results_response(query)
            
        except Exception as e:
            print(f"💥 HTML parsing error: {e}")
            return self._get_error_response(query)