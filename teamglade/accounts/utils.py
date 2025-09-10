import logging

# Set up logging for bot detection
logger = logging.getLogger(__name__)

def detect_bot_behavior(request):
    """
    Additional bot detection based on request patterns
    Returns True if bot-like behavior is detected
    """
    suspicious_indicators = []

    # Check User-Agent, what browser/tool is making the request
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    bot_keywords = ['bot', 'crawler', 'spider', 'scraper', 'automated']
    if any(keyword in user_agent.lower() for keyword in bot_keywords):
        suspicious_indicators.append('bot_user_agent')

    # Check for missing common headers
    if not request.META.get('HTTP_ACCEPT'):
        suspicious_indicators.append('missing_accept_header')

    if not request.META.get('HTTP_ACCEPT_LANGUAGE'):
        suspicious_indicators.append('missing_accept_language')

    # Log suspicious activity
    if suspicious_indicators:
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'Unknown'))
        logger.warning(f"Suspicious registration attempt from IP {ip_address}. "
                       f"Indicators: {', '.join(suspicious_indicators)}. "
                       f"User-Agent: {user_agent}")

    # Return True if multiple indicators present
    # Here 2 is trade-off between security and usability
    # browsers can miss HTTP_ACCEPT_LANGUAGE (privacy setting) or proxies can cut HTTP_ACCEPT
    return len(suspicious_indicators) >= 2

