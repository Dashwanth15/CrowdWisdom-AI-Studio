import httpx

r = httpx.get("https://image.pollinations.ai/prompt/cat?nologo=true", follow_redirects=True, timeout=15)
print("Default model status:", r.status_code, "Length:", len(r.content))

r2 = httpx.get("https://image.pollinations.ai/prompt/cat?model=flux&nologo=true", follow_redirects=True, timeout=15)
print("Flux model status:", r2.status_code, "Length:", len(r2.content))

r3 = httpx.get("https://image.pollinations.ai/prompt/cat?model=turbo&nologo=true", follow_redirects=True, timeout=15)
print("Turbo model status:", r3.status_code, "Length:", len(r3.content))

