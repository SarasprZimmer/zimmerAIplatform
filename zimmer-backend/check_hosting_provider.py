import socket
import dns.resolver
import requests
from urllib.parse import urlparse

def check_domain_info():
    """Check domain information to help identify hosting provider"""
    print("🔍 Domain Information Check")
    print("=" * 50)
    
    domain = "zimmerai.com"
    
    try:
        # Get IP address
        ip = socket.gethostbyname(domain)
        print(f"Domain: {domain}")
        print(f"IP Address: {ip}")
        
        # Try to get hosting provider info
        try:
            response = requests.get(f"http://{domain}", timeout=5)
            server_header = response.headers.get('Server', 'Unknown')
            print(f"Server Header: {server_header}")
        except:
            print("Server Header: Could not retrieve")
        
        # Check common hosting provider patterns
        hosting_providers = {
            'cpanel': ['cpanel', 'whm', 'webmail'],
            'plesk': ['plesk', 'webmail'],
            'directadmin': ['directadmin'],
            'hostinger': ['hostinger'],
            'godaddy': ['godaddy', 'secureserver'],
            'bluehost': ['bluehost'],
            'hostgator': ['hostgator'],
            'siteground': ['siteground'],
            'dreamhost': ['dreamhost'],
            'a2hosting': ['a2hosting'],
            'inmotion': ['inmotion'],
            'liquidweb': ['liquidweb'],
            'knownhost': ['knownhost'],
            'interserver': ['interserver'],
            'vultr': ['vultr'],
            'digitalocean': ['digitalocean'],
            'linode': ['linode'],
            'aws': ['amazon', 'aws'],
            'google': ['google'],
            'azure': ['microsoft', 'azure']
        }
        
        print(f"\n🔍 Checking for hosting provider patterns...")
        
        # Check MX records
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            print(f"MX Records:")
            for mx in mx_records:
                mx_host = str(mx.exchange).rstrip('.')
                print(f"  - {mx_host} (Priority: {mx.preference})")
                
                # Check if MX record suggests hosting provider
                for provider, patterns in hosting_providers.items():
                    for pattern in patterns:
                        if pattern.lower() in mx_host.lower():
                            print(f"    → Likely hosting provider: {provider.upper()}")
        except Exception as e:
            print(f"Could not resolve MX records: {e}")
        
        # Check A records
        try:
            a_records = dns.resolver.resolve(domain, 'A')
            print(f"A Records:")
            for a in a_records:
                print(f"  - {a}")
        except Exception as e:
            print(f"Could not resolve A records: {e}")
        
        # Check for common SMTP servers
        print(f"\n🔍 Checking for SMTP servers...")
        smtp_servers_to_check = [
            f"mail.{domain}",
            f"smtp.{domain}",
            f"email.{domain}",
            domain,
            f"webmail.{domain}",
            f"mail.zimmerai.com",
            f"smtp.zimmerai.com"
        ]
        
        for smtp_server in smtp_servers_to_check:
            try:
                smtp_ip = socket.gethostbyname(smtp_server)
                print(f"✅ {smtp_server} → {smtp_ip}")
            except:
                print(f"❌ {smtp_server} → Not found")
        
        return ip, server_header
        
    except Exception as e:
        print(f"Error checking domain: {e}")
        return None, None

def suggest_smtp_settings(ip, server_header):
    """Suggest SMTP settings based on hosting provider"""
    print(f"\n💡 SMTP Configuration Suggestions")
    print("=" * 50)
    
    suggestions = []
    
    # Common hosting provider SMTP settings
    if 'cpanel' in str(server_header).lower():
        suggestions.extend([
            {"name": "cPanel Standard", "server": "mail.zimmerai.com", "port": 465, "ssl": True},
            {"name": "cPanel Alternative", "server": "mail.zimmerai.com", "port": 587, "ssl": False},
            {"name": "cPanel Direct", "server": "zimmerai.com", "port": 465, "ssl": True},
        ])
    
    # Generic suggestions for any hosting provider
    suggestions.extend([
        {"name": "Standard SSL", "server": "mail.zimmerai.com", "port": 465, "ssl": True},
        {"name": "Standard TLS", "server": "mail.zimmerai.com", "port": 587, "ssl": False},
        {"name": "Alternative SSL", "server": "zimmerai.com", "port": 465, "ssl": True},
        {"name": "Alternative TLS", "server": "zimmerai.com", "port": 587, "ssl": False},
        {"name": "Direct SSL", "server": "zimmerai.com", "port": 465, "ssl": True},
        {"name": "Direct TLS", "server": "zimmerai.com", "port": 587, "ssl": False},
    ])
    
    print("Try these configurations in order:")
    for i, config in enumerate(suggestions, 1):
        print(f"\n{i}. {config['name']}")
        print(f"   SMTP_SERVER={config['server']}")
        print(f"   SMTP_PORT={config['port']}")
        print(f"   SSL: {config['ssl']}")
    
    print(f"\n🔧 If none work, you may need to:")
    print("1. Contact your hosting provider for SMTP settings")
    print("2. Check if SMTP is enabled in your hosting control panel")
    print("3. Verify your email account is active")
    print("4. Check if your hosting provider blocks outgoing SMTP")
    
    return suggestions

def test_connection_issues():
    """Test for common connection issues"""
    print(f"\n🔧 Connection Issue Diagnosis")
    print("=" * 50)
    
    # Test if we can reach the domain at all
    try:
        socket.gethostbyname("mail.zimmerai.com")
        print("✅ DNS resolution works for mail.zimmerai.com")
    except:
        print("❌ DNS resolution failed for mail.zimmerai.com")
    
    # Test if we can reach the domain at all
    try:
        socket.gethostbyname("zimmerai.com")
        print("✅ DNS resolution works for zimmerai.com")
    except:
        print("❌ DNS resolution failed for zimmerai.com")
    
    # Test common ports
    ports_to_test = [25, 465, 587, 2525]
    for port in ports_to_test:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(("mail.zimmerai.com", port))
            sock.close()
            if result == 0:
                print(f"✅ Port {port} is open on mail.zimmerai.com")
            else:
                print(f"❌ Port {port} is closed on mail.zimmerai.com")
        except:
            print(f"❌ Could not test port {port} on mail.zimmerai.com")

if __name__ == "__main__":
    print("🚀 Hosting Provider and SMTP Configuration Check")
    print("=" * 60)
    
    ip, server_header = check_domain_info()
    suggestions = suggest_smtp_settings(ip, server_header)
    test_connection_issues()
    
    print(f"\n" + "=" * 60)
    print("📋 Next Steps:")
    print("1. Try the suggested SMTP configurations above")
    print("2. If none work, contact your hosting provider")
    print("3. Ask for the correct SMTP server and port for outgoing mail")
    print("4. Verify that SMTP is enabled for your email account") 