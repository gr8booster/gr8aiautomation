"""
Website fetching and content extraction
"""
import httpx
import re
from bs4 import BeautifulSoup
from typing import Optional, List, Dict
from urllib.parse import urljoin, urlparse
from .schema import WebsiteExtraction, FormInfo, CTAInfo, BusinessType

# Safe fetching with timeouts
TIMEOUT = 15.0
MAX_SIZE = 5 * 1024 * 1024  # 5MB
USER_AGENT = "GR8-AI-Automation-Bot/1.0"

BUSINESS_KEYWORDS = {
    BusinessType.ECOMMERCE: ['shop', 'cart', 'product', 'buy', 'store', 'checkout', 'price', 'add to cart'],
    BusinessType.SERVICE: ['service', 'consultation', 'appointment', 'schedule', 'book', 'contact us'],
    BusinessType.BLOG: ['blog', 'article', 'post', 'author', 'published', 'category', 'tag'],
    BusinessType.SAAS: ['pricing', 'plans', 'subscription', 'trial', 'demo', 'signup', 'features', 'api'],
    BusinessType.PORTFOLIO: ['portfolio', 'work', 'project', 'case study', 'about me'],
}

CTA_VERBS = ['buy', 'get', 'start', 'try', 'download', 'sign up', 'signup', 'join', 'learn', 'contact', 'book', 'schedule', 'subscribe', 'register']

async def fetch_and_extract_website(url: str) -> WebsiteExtraction:
    """
    Fetch and extract structured data from a website
    """
    # Normalize URL
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    # Fetch content
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        response = await client.get(
            url,
            headers={'User-Agent': USER_AGENT}
        )
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if 'text/html' not in content_type:
            raise ValueError(f"Not an HTML page: {content_type}")
        
        # Check size
        content = response.content
        if len(content) > MAX_SIZE:
            content = content[:MAX_SIZE]
        
        html = content.decode('utf-8', errors='ignore')
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract metadata
    title = None
    if soup.title:
        title = soup.title.string
    
    description = None
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        description = meta_desc['content']
    
    # Extract keywords
    keywords = []
    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
    if meta_keywords and meta_keywords.get('content'):
        keywords = [k.strip() for k in meta_keywords['content'].split(',')]
    
    # Extract headings
    h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all('h1')]
    h2_tags = [h2.get_text(strip=True) for h2 in soup.find_all('h2')[:10]]  # Limit to first 10
    
    # Extract navigation links
    nav_links = []
    nav = soup.find('nav') or soup.find('header')
    if nav:
        for link in nav.find_all('a', href=True)[:20]:
            text = link.get_text(strip=True)
            href = urljoin(url, link['href'])
            if text:
                nav_links.append({'text': text, 'href': href})
    
    # Extract forms
    forms = []
    for form in soup.find_all('form')[:5]:  # Limit to 5 forms
        inputs = []
        has_email = False
        has_phone = False
        
        for input_tag in form.find_all(['input', 'textarea', 'select']):
            input_type = input_tag.get('type', 'text')
            input_name = input_tag.get('name', '')
            input_placeholder = input_tag.get('placeholder', '')
            
            if input_type in ['text', 'email', 'tel', 'textarea', 'select']:
                inputs.append(f"{input_name or input_placeholder or input_type}")
            
            if input_type == 'email' or 'email' in input_name.lower():
                has_email = True
            if input_type == 'tel' or 'phone' in input_name.lower():
                has_phone = True
        
        forms.append(FormInfo(
            action=form.get('action'),
            method=form.get('method', 'GET').upper(),
            inputs=inputs,
            has_email=has_email,
            has_phone=has_phone
        ))
    
    # Extract CTAs (buttons and prominent links)
    ctas = []
    for element in soup.find_all(['button', 'a'], limit=30):
        text = element.get_text(strip=True).lower()
        if any(verb in text for verb in CTA_VERBS):
            cta_text = element.get_text(strip=True)
            cta_url = None
            if element.name == 'a' and element.get('href'):
                cta_url = urljoin(url, element['href'])
            
            ctas.append(CTAInfo(
                text=cta_text,
                url=cta_url,
                type='button' if element.name == 'button' else 'link'
            ))
    
    # Extract main content text
    # Remove script, style, nav, footer
    for element in soup(['script', 'style', 'nav', 'footer', 'header']):
        element.decompose()
    
    content_text = soup.get_text(separator=' ', strip=True)
    # Limit content length
    content_text = content_text[:5000]
    
    # Extract social links
    social_links = {}
    social_patterns = {
        'facebook': r'facebook\.com/([^/\s"]+)',
        'instagram': r'instagram\.com/([^/\s"]+)',
        'twitter': r'twitter\.com/([^/\s"]+)',
        'linkedin': r'linkedin\.com/(?:company|in)/([^/\s"]+)',
    }
    
    html_lower = html.lower()
    for platform, pattern in social_patterns.items():
        match = re.search(pattern, html_lower)
        if match:
            social_links[platform] = match.group(0)
    
    # Detect business type based on content
    content_lower = (title or '').lower() + ' ' + (description or '').lower() + ' ' + content_text.lower()
    
    business_scores = {bt: 0 for bt in BusinessType}
    for business_type, keywords_list in BUSINESS_KEYWORDS.items():
        for keyword in keywords_list:
            if keyword in content_lower:
                business_scores[business_type] += 1
    
    business_type = max(business_scores, key=business_scores.get)
    if business_scores[business_type] == 0:
        business_type = BusinessType.OTHER
    
    # Detect features
    has_blog = 'blog' in content_lower or any('blog' in link['href'] for link in nav_links)
    has_shop = business_type == BusinessType.ECOMMERCE or 'shop' in content_lower
    has_booking = 'book' in content_lower or 'appointment' in content_lower or 'schedule' in content_lower
    
    return WebsiteExtraction(
        url=url,
        title=title,
        description=description,
        h1_tags=h1_tags,
        h2_tags=h2_tags,
        nav_links=nav_links,
        forms=forms,
        ctas=ctas,
        content_text=content_text,
        keywords=keywords,
        business_type=business_type,
        has_blog=has_blog,
        has_shop=has_shop,
        has_booking=has_booking,
        social_links=social_links
    )
