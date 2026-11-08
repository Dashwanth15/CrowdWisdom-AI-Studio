import httpx
r = httpx.get("https://image.pollinations.ai/prompt/financial_trader_office?width=1080&height=1920&nologo=true")
print("Status:", r.status_code)
print("Text:", r.text)

