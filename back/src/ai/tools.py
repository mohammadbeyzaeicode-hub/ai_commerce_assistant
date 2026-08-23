import httpx

BASE_URL = "http://localhost:8000"   # آدرس FastAPI که از مرورگر تست می‌کنی

def check_inventory(item: str):
    r = httpx.get(f"{BASE_URL}/inventory?item={item}")
    return r.json()

def create_order(user_id: int, item: str, qty: int):
    payload = {"user_id": user_id, "item": item, "qty": qty}
    # r = httpx.post(f"{BASE_URL}/order", json=payload)
    # return r.json()
    
    return (f"Creating order: {payload}")
    

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_inventory",
            "description": "Check inventory of a specific item.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item": {"type": "string"}
                },
                "required": ["item"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_order",
            "description": "Create an order for a user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "item": {"type": "string"},
                    "qty": {"type": "integer"}
                },
                "required": ["user_id", "item", "qty"]
            }
        }
    }
]


def run_tool(name, args):
    if name == "check_inventory":
        return check_inventory(**args)
    if name == "create_order":
        return create_order(**args)
    return {"error": "unknown tool"}
