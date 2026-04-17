# client/main.py
import httpx
import uuid

ORCHESTRATOR_URL = "http://localhost:8005/chat"


def build_request(method: str, params: dict) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": method,
        "params": params,
    }


def parse_response(data: dict):
    if "error" in data:
        err = data["error"]
        raise Exception(f"JSON-RPC error {err['code']}: {err['message']}")
    return data.get("result")


def get_token() -> str:
    token = input("Paste your JWT token: ").strip()
    return token


def main():
    print("Multi-Agent Chat Client (JSON-RPC 2.0)")
    print("----------------------------------------")
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        payload = build_request("chat", {"message": user_input})

        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(ORCHESTRATOR_URL, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                result = parse_response(data)
                print(f"Agent: {result.get('response')}")
                print(f"Agents called: {result.get('agents_called', [])}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()