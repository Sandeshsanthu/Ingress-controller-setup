import requests
from urllib.parse import urljoin

def detect_ingress_properly(url):
    # Ensure the URL ends with a slash for proper joining
    if not url.endswith('/'):
        url += '/'
        
    test_path = "this-path-should-not-exist-12345"
    test_url = urljoin(url, test_path)
    
    print(f"Testing URL: {test_url}\n")

    try:
        # Request a non-existent path to trigger the Ingress error handler
        response = requests.get(test_url, timeout=10)
        headers = {k.lower(): v for k, v in response.headers.items()}
        body = response.text.lower()
        
        # 1. Check for Envoy
        if 'envoy' in headers.get('server', '') or any(h.startswith('x-envoy') for h in headers):
            return "✅ Envoy Proxy detected (via Headers)"
        if "envoy" in body or "uh" in body or "local_rate_limited" in body:
            return "✅ Envoy Proxy detected (via Error Body signatures)"

        # 2. Check for Nginx Ingress
        if 'nginx' in headers.get('server', ''):
            return "✅ Nginx Ingress detected (via Server Header)"
        if "nginx" in body or "openresty" in body:
            return "✅ Nginx Ingress detected (via Error Page body)"
        
        # 3. Behavioral Clues (common in K8s)
        if 'x-request-id' in headers:
            return "❓ Likely K8s Ingress: Found 'X-Request-ID' (commonly injected by Ingress-Nginx)"
        
        return "❌ No proxy signatures found. The Ingress is fully cloaked."

    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

# Run the test
target = "http://34.59.114.41/web"
print(detect_ingress_properly(target))
