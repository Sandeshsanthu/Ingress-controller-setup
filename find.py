import requests

def detect_proxy_signatures(url):
    """
    Checks for Envoy and Nginx Ingress signatures in HTTP headers.
    """
    try:
        # We use a 5-second timeout to avoid hanging
        response = requests.get(url, timeout=5)
        headers = response.headers
        
        # Get the 'Server' header (case-insensitive dictionary in requests)
        server = headers.get('server', '').lower()
        
        results = {
            "Envoy": False,
            "Nginx_Ingress": False,
            "Detected_Headers": []
        }

        # 1. Check for Envoy Signatures
        # Envoy typically sets 'server: envoy' or unique x-envoy headers
        envoy_headers = [h for h in headers if h.lower().startswith('x-envoy')]
        if 'envoy' in server or envoy_headers:
            results["Envoy"] = True
            results["Detected_Headers"].extend(envoy_headers)

        # 2. Check for Nginx Ingress Signatures
        # Ingress controllers often use 'nginx' as the server name
        if 'nginx' in server:
            results["Nginx_Ingress"] = True
            
        # Specific Ingress-Nginx signatures like x-request-id (common default)
        if 'x-request-id' in headers and not results["Envoy"]:
            # x-request-id is very common in K8s Ingress environments
            results["Detected_Headers"].append('x-request-id')

        return results

    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

# --- Execution ---
target_url = "http://34.59.114.41/web" # Replace with your target
analysis = detect_proxy_signatures(target_url)

if isinstance(analysis, dict):
    print(f"Results for: {target_url}")
    print(f"- Envoy Detected: {analysis['Envoy']}")
    print(f"- Nginx Ingress/Proxy Detected: {analysis['Nginx_Ingress']}")
    if analysis['Detected_Headers']:
        print(f"- Found identifying headers: {', '.join(analysis['Detected_Headers'])}")
else:
    print(analysis)
