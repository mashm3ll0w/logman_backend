import secrets
import base64

def generate_key():
    """
    Generate 32 cryptographically strong random bytes amd URL-safe base64 encode the bytes.
    """

    random_bytes = secrets.token_bytes(32)
    url_safe_encoded_bytes = base64.urlsafe_b64encode(random_bytes)
    url_safe_encoded_string = url_safe_encoded_bytes.decode('utf-8')

    return url_safe_encoded_string

if __name__ == "__main__":
    key = generate_key()
    print(f"[+] Your key is: {key}")
    print("[!] Keep it secret or you're screwed!")
