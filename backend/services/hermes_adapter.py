"""
CrowdWisdom AI Studio — Hermes Agent Adapter Layer
Bridges the official NousResearch/hermes-agent framework into CrowdWisdom AI Studio.
Safely manages native agent initialization, tool execution via tools.registry,
and provides transparent fallback to direct LLM when needed.
"""
import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from config import settings

logger = logging.getLogger(__name__)

# Ensure vendor hermes_agent directory is in sys.path
_vendor_hermes = Path(__file__).parent.parent / "vendor" / "hermes_agent"
if _vendor_hermes.exists():
    _hermes_path_str = str(_vendor_hermes.resolve())
    if _hermes_path_str not in sys.path:
        sys.path.insert(0, _hermes_path_str)


class HermesAgentAdapter:
    """
    Adapter layer isolating the NousResearch/hermes-agent runtime.
    Provides native execution through AIAgent and tools.registry,
    with honest, transparent reporting of execution mode:
      - 'native_hermes': Genuine execution through NousResearch runtime
      - 'llm_fallback': Direct LLM API client fallback
    """

    FRAMEWORK_VERSION = "NousResearch/hermes-agent@c55af2c9"

    def __init__(
        self,
        agent_name: str,
        system_prompt: str,
        model: str = "meta-llama/llama-3.3-70b-instruct"
    ):
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.model = model
        self._hermes_instance = None
        self._is_hermes_available = False
        self._registered_tools: Dict[str, Callable] = {}
        self._last_execution_mode: str = "unconfigured"

    def register_tool(
        self,
        name: str,
        description: str,
        func: Callable,
        schema: Optional[Dict] = None,
        toolset: str = "crowdwisdom"
    ):
        """Registers a Python tool callable in the official Hermes registry and internal map."""
        self._registered_tools[name] = func

        # Attempt registration in official NousResearch tool registry
        try:
            import importlib
            tools_reg_mod = importlib.import_module("tools.registry")
            registry = getattr(tools_reg_mod, "registry")
            tool_schema = schema or {
                "name": name,
                "description": description,
                "parameters": {"type": "object", "properties": {}}
            }
            # Wrap func to adapt Hermes (args, **kw) signature to func kwargs
            def _wrapped_handler(args, **kw):
                if isinstance(args, dict):
                    return func(**args)
                return func(args)

            registry.register(
                name=name,
                toolset=toolset,
                schema=tool_schema,
                handler=_wrapped_handler,
                description=description,
                override=True
            )
            logger.info(f"[{self.agent_name}] Tool '{name}' registered in official Hermes registry.")
        except Exception as e:
            logger.warning(f"[{self.agent_name}] Tool '{name}' local registration only ({e}).")

    async def initialize(self, api_key: str, base_url: Optional[str] = None) -> bool:
        """
        Initializes the underlying official Hermes AIAgent instance.
        """
        try:
            # Set provider credentials into environment
            if base_url:
                os.environ["OPENAI_BASE_URL"] = base_url
            else:
                os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"
            os.environ["OPENROUTER_API_KEY"] = api_key
            os.environ["OPENAI_API_KEY"] = api_key

            def _load_agent():
                try:
                    import importlib
                    run_agent_mod = importlib.import_module("run_agent")
                    AIAgent = getattr(run_agent_mod, "AIAgent")
                    agent = AIAgent(
                        base_url=os.environ.get("OPENAI_BASE_URL"),
                        api_key=api_key,
                        model=self.model,
                        quiet_mode=True,
                        skip_memory=True,
                        save_trajectories=False,
                        enabled_toolsets=["crowdwisdom"],
                    )
                    return agent
                except (ImportError, ModuleNotFoundError) as ie:
                    logger.info(f"[{self.agent_name}] Hermes native module not available ({ie}).")
                    return None
                except Exception as ex:
                    logger.warning(f"[{self.agent_name}] Hermes AIAgent initialization notice: {ex}")
                    return None

            self._hermes_instance = await asyncio.to_thread(_load_agent)
            self._is_hermes_available = (self._hermes_instance is not None)
            return self._is_hermes_available

        except Exception as e:
            logger.error(f"[{self.agent_name}] Failed to initialize Hermes adapter: {e}")
            self._is_hermes_available = False
            return False

    async def execute_task(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        llm_fallback: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Executes a prompt through official Hermes if available, or through direct LLM fallback.
        Always returns explicit 'execution_mode' for honest observability.
        """
        full_prompt = prompt
        if context:
            full_prompt = f"CONTEXT:\n{json.dumps(context, indent=2)}\n\nTASK:\n{prompt}"

        # 1. Primary Path: Official Hermes Native Execution
        if self._is_hermes_available and self._hermes_instance:
            try:
                def _run_hermes():
                    return self._hermes_instance.chat(full_prompt)

                response_text = await asyncio.to_thread(_run_hermes)
                self._last_execution_mode = "native_hermes"
                return {
                    "execution_mode": "native_hermes",
                    "framework_version": self.FRAMEWORK_VERSION,
                    "source": "official_hermes_agent",
                    "content": response_text,
                    "agent": self.agent_name
                }
            except Exception as e:
                logger.warning(f"[{self.agent_name}] Hermes execution failed ({e}), falling back to direct LLM.")

        # 2. Secondary Path: Direct LLM Fallback
        if llm_fallback:
            self._last_execution_mode = "llm_fallback"
            response_json = await llm_fallback.chat_json(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": full_prompt}
                ]
            )
            return {
                "execution_mode": "llm_fallback",
                "framework_version": self.FRAMEWORK_VERSION,
                "source": "verified_llm_adapter",
                "content": response_json,
                "agent": self.agent_name
            }

        self._last_execution_mode = "failed"
        raise RuntimeError(f"[{self.agent_name}] Neither Hermes native runtime nor LLM fallback could execute.")

    @property
    def last_execution_mode(self) -> str:
        return self._last_execution_mode

    @property
    def is_native_available(self) -> bool:
        return self._is_hermes_available
