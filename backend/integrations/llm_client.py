"""
CrowdWisdom AI Studio — LLM Client
Unified client supporting OpenRouter and NVIDIA NIM.
"""
import json
import logging
import re
from typing import Any, Dict, List, Optional
import httpx

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Unified LLM client for OpenRouter and NVIDIA NIM.
    Both providers expose an OpenAI-compatible API.
    """

    def __init__(self, api_key: str, provider: str = "gemini", model: Optional[str] = None):
        self.api_key = api_key
        self.provider = provider

        if provider == "gemini":
            self.base_url = "https://generativelanguage.googleapis.com/v1beta"
            self.model = model or "gemini-3.5-flash-lite"
        elif provider == "openrouter":
            self.base_url = "https://openrouter.ai/api/v1"
            self.model = model or "meta-llama/llama-3.3-70b-instruct"
        elif provider == "nvidia_nim":
            self.base_url = "https://integrate.api.nvidia.com/v1"
            self.model = model or "nvidia/nemotron-3.5-bolt-e4b"
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if provider == "openrouter":
            self.headers["HTTP-Referer"] = "https://crowdwisdomtrading.com"
            self.headers["X-Title"] = "CrowdWisdom AI Studio"

    async def _chat_gemini(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
    ) -> str:
        """Execute chat completion using Google Gemini native API."""
        system_inst = None
        contents = []
        for m in messages:
            if m.get("role") == "system":
                system_inst = {"parts": [{"text": m.get("content", "")}]}
            else:
                role = "model" if m.get("role") == "assistant" else "user"
                contents.append({"role": role, "parts": [{"text": m.get("content", "")}]})

        if not contents:
            contents = [{"role": "user", "parts": [{"text": "Hello"}]}]

        gen_config: Dict[str, Any] = {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        }
        if response_format and response_format.get("type") == "json_object":
            gen_config["response_mime_type"] = "application/json"

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": gen_config,
        }
        if system_inst:
            payload["systemInstruction"] = system_inst

        candidate_models = [self.model, "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        unique_models = list(dict.fromkeys(candidate_models))

        last_err = None
        async with httpx.AsyncClient(timeout=60.0) as client:
            for mod in unique_models:
                mod_name = mod if not mod.startswith("models/") else mod.split("/", 1)[1]
                url = f"{self.base_url}/models/{mod_name}:generateContent?key={self.api_key}"
                try:
                    resp = await client.post(url, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"]
                except httpx.HTTPStatusError as e:
                    last_err = e
                    if e.response.status_code in (503, 404, 429):
                        logger.warning(f"Gemini model {mod_name} returned {e.response.status_code}. Retrying with next model...")
                        continue
                    raise
                except Exception as e:
                    last_err = e
                    logger.warning(f"Gemini call {mod_name} notice: {e}. Retrying with next model...")
                    continue
            if last_err:
                raise last_err
            raise RuntimeError("Gemini content generation failed across all candidate models.")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
    ) -> str:
        """Send a chat completion request and return the response text."""
        if self.provider == "gemini":
            try:
                return await self._chat_gemini(messages, temperature, max_tokens, response_format)
            except Exception as gemini_err:
                from config import settings
                if settings.NVIDIA_NIM_API_KEY:
                    logger.warning(f"Gemini call encountered error ({gemini_err}). Seamlessly falling back to NVIDIA NIM...")
                    nim_client = LLMClient(api_key=settings.NVIDIA_NIM_API_KEY, provider="nvidia_nim")
                    return await nim_client.chat(messages, temperature, max_tokens, response_format)
                raise

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=self.headers,
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                # If error is due to response_format not supported, retry without it
                if response_format and e.response.status_code == 400:
                    payload.pop("response_format", None)
                    resp = await client.post(
                        f"{self.base_url}/chat/completions",
                        json=payload,
                        headers=self.headers,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
                raise

    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> Dict:
        """Send a chat request expecting JSON response."""
        # Ensure system message instructs JSON
        formatted_messages = [dict(m) for m in messages]
        json_instruction = "\n\nCRITICAL: Respond ONLY with a valid JSON object. No explanation, markdown fences, or preamble."

        if formatted_messages and formatted_messages[0]["role"] == "system":
            formatted_messages[0]["content"] += json_instruction
        else:
            formatted_messages.insert(0, {"role": "system", "content": json_instruction})

        try:
            # Try with json_object format first
            response_text = await self.chat(
                formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 402, 403, 429):
                raise
            # Fall back to standard format without response_format if model doesn't support json_object
            response_text = await self.chat(
                formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=None,
            )
        except Exception:
            # Fall back to standard format
            response_text = await self.chat(
                formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=None,
            )

        # Clean markdown code blocks if present
        def _parse_candidate(raw_text: str) -> Optional[Dict]:
            cleaned = raw_text.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()

            # 1. Direct parse
            try:
                return json.loads(cleaned)
            except Exception:
                pass

            # 2. Regex extraction of outer { ... }
            match = re.search(r'(\{[\s\S]*\})', cleaned)
            if match:
                candidate = match.group(1)
                try:
                    return json.loads(candidate)
                except Exception:
                    # Strip trailing commas
                    repaired = re.sub(r',\s*([}\]])', r'\1', candidate)
                    try:
                        return json.loads(repaired)
                    except Exception:
                        pass
            return None

        parsed = _parse_candidate(response_text)
        if parsed is not None:
            return parsed

        # Automatic LLM repair retry if initial parse failed
        logger.warning(f"Initial LLM response was not valid JSON. Requesting corrective repair...")
        try:
            repair_messages = [
                *formatted_messages,
                {"role": "assistant", "content": response_text},
                {
                    "role": "user",
                    "content": "CRITICAL REPAIR: Your previous response was not valid JSON syntax. Please output ONLY the exact, complete JSON object. Ensure all quotes, keys, colons, and braces are strictly valid RFC-8259 JSON without any markdown or extra text."
                }
            ]
            retry_text = await self.chat(
                repair_messages,
                temperature=0.2,
                max_tokens=max_tokens,
                response_format=None,
            )
            repaired_parsed = _parse_candidate(retry_text)
            if repaired_parsed is not None:
                return repaired_parsed
        except Exception as retry_err:
            logger.error(f"Corrective JSON repair request failed: {retry_err}")

        logger.error(f"Failed to parse LLM JSON: {response_text[:300]}")
        raise ValueError(f"LLM returned invalid JSON: {response_text[:200]}")

    async def test_connection(self) -> Dict[str, Any]:
        """Test the LLM provider connection."""
        try:
            response = await self.chat(
                messages=[{"role": "user", "content": "Say 'connection successful' in one sentence."}],
                max_tokens=50,
            )
            return {"success": True, "response": response.strip(), "model": self.model}
        except Exception as e:
            return {"success": False, "error": str(e), "model": self.model}
