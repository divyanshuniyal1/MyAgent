# client/main.py
import requests
import webbrowser

AUTH_URL = "http://localhost:8000"
BASE_URL = "http://localhost:8005"


def login():
    print("Opening Microsoft login in your browser...")
    print("After login, copy the 'access_token' from the response and paste it here.\n")
    webbrowser.open(f"{AUTH_URL}/auth/login/microsoft")
    token = input("Paste your access_token here: ").strip()
    return token


def chat(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    print("\nChat started. Type 'exit' to quit.\n")

    while True:
        msg = input("You: ")

        if msg.lower() == "exit":
            break

        res = requests.post(
            f"{BASE_URL}/chat",
            json={"message": msg},
            headers=headers
        )

        print("Agent:", res.text)


if __name__ == "__main__":
    token = login()
    chat(token)