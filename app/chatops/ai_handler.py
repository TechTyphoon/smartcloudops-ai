"""
Smart CloudOps AI - Flexible AI Handler
Supports both OpenAI and Google Gemini APIs
"""

import logging
import os
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def initialize(self, api_key: str) -> bool:
        """Initialize the AI provider."""
        pass

    @abstractmethod
    def process_query(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Process a query with the AI provider."""
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current model."""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI GPT provider implementation."""

    def __init__(self):
        self.client = None
        self.model = "gpt-3.5-turbo"

    def initialize(self, api_key: str) -> bool:
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI provider initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {str(e)}")
            return False

    def process_query(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Process query with OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 500),
                temperature=kwargs.get("temperature", 0.3),
                timeout=kwargs.get("timeout", 30),
            )

            return {
                "status": "success",
                "response": response.choices[0].message.content.strip(),
                "model": self.model,
                "tokens_used": response.usage.total_tokens if response.usage else None,
                "provider": "openai",
            }
        except Exception as e:
            logger.error(f"OpenAI query failed: {str(e)}")
            return {"status": "error", "error": str(e), "provider": "openai"}

    def get_model_info(self) -> Dict[str, str]:
        """Get OpenAI model information."""
        return {"provider": "openai", "model": self.model, "name": "GPT-3.5 Turbo"}


class LocalProvider(AIProvider):
    """Local AI provider for testing and development."""

    def __init__(self):
        self.model = "local-assistant"

    def initialize(self, api_key: str = None) -> bool:
        """Initialize local provider (no API key needed)."""
        logger.info("Local AI provider initialized successfully")
        return True

    def process_query(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Process query with local responses."""
        try:
            # Get the user query from messages
            user_message = ""
            for message in messages:
                if message.get("role") == "user":
                    user_message = message.get("content", "")
                    break

            # Generate contextual responses based on query content
            response = self._generate_response(user_message.lower())

            return {
                "status": "success",
                "response": response,
                "model": self.model,
                "tokens_used": len(response.split()),
                "provider": "local",
            }
        except Exception as e:
            logger.error(f"Local provider query failed: {str(e)}")
            return {"status": "error", "error": str(e), "provider": "local"}

    def _generate_response(self, query: str) -> str:
        """Generate contextual responses based on query patterns."""
        # Check specific patterns first (most specific to least specific)
        if "anomaly" in query or "alert" in query or "detection" in query:
            return """**Anomaly Analysis**: Recent HIGH severity anomaly detected (score: 0.633)

**Key Metrics**:
- CPU Usage: 85.5% (threshold exceeded)
- Memory Usage: 72.3%
- Active Connections: 1,520 (high)
- Response Time: 250ms

**Immediate Actions**:
1. Scale resources if sustained high load
2. Investigate connection pool usage
3. Check for memory leaks
4. Review slow queries in database

**Monitoring**: Continue observing metrics for next 30 minutes"""

        elif "recommendation" in query or "improve" in query or "optimization" in query:
            return """**System Optimization Recommendations**:

**Performance**:
- Consider horizontal scaling for high connection loads
- Implement connection pooling optimization
- Add Redis caching layer for frequent queries

**Monitoring**:
- Set up alerting thresholds for key metrics
- Create custom dashboards for business metrics
- Implement distributed tracing

**Security**:
- Regular security scans are active
- Credentials properly secured
- Network monitoring enabled

**Next Steps**: Prioritize connection pool optimization and Redis implementation"""

        elif "error" in query or "problem" in query or "troubleshoot" in query:
            return """**Troubleshooting Guide**:

**Recent Issues**:
- AWS credentials warnings (non-critical for local dev)
- Slack webhook not configured (notifications disabled)

**Common Solutions**:
1. **503 Errors**: Check if all containers are running
2. **Connection Issues**: Verify PostgreSQL container health
3. **Slow Responses**: Review Grafana metrics for bottlenecks
4. **Authentication Errors**: Verify API keys in environment

**Debug Commands**:
```bash
docker-compose ps
docker logs cloudops-smartcloudops-app-1
curl http://localhost:3003/health
```"""

        elif "status" in query or "health" in query:
            return """**Current System Status**: ✅ All systems operational

**Infrastructure Health**:
- Flask Application: Running (Port 3003)
- PostgreSQL Database: Connected
- Prometheus Monitoring: Active (9090)
- Grafana Dashboard: Accessible (3004)
- Node Exporter: Collecting metrics (9100)

**ML System Status**:
- Anomaly Detection: Functional
- Model: IsolationForest loaded (18 features)
- Last prediction: HIGH severity anomaly detected

**Recommendations**:
1. Monitor the recent HIGH severity anomaly
2. Review system metrics in Grafana
3. Check application logs for any warnings"""
            return """**Troubleshooting Guide**:

**Recent Issues**:
- AWS credentials warnings (non-critical for local dev)
- Slack webhook not configured (notifications disabled)

**Common Solutions**:
1. **503 Errors**: Check if all containers are running
2. **Connection Issues**: Verify PostgreSQL container health
3. **Slow Responses**: Review Grafana metrics for bottlenecks
4. **Authentication Errors**: Verify API keys in environment

**Debug Commands**:
```bash
docker-compose ps
docker logs cloudops-smartcloudops-app-1
curl http://localhost:3003/health
```"""

        else:
            return f"""**Smart CloudOps AI Assistant** - Local Mode

I can help you with:
- **System Status**: Current health and performance metrics
- **Anomaly Analysis**: Detailed investigation of detected issues  
- **Troubleshooting**: Step-by-step problem resolution
- **Recommendations**: Performance and security improvements

**Query processed**: "{query[:100]}..."

**Available Commands**:
- "system status" - Get current infrastructure health
- "analyze anomaly" - Review recent anomaly detections
- "recommendations" - Get optimization suggestions
- "troubleshoot errors" - Debug common issues

*Note: Running in local mode - for production use, configure OpenAI or Gemini API keys.*"""

    def get_model_info(self) -> Dict[str, str]:
        """Get local model information."""
        return {"provider": "local", "model": self.model, "name": "Local Assistant"}


class GeminiProvider(AIProvider):
    """Google Gemini provider implementation."""

    def __init__(self):
        self.client = None
        self.model = "gemini-1.5-pro"

    def initialize(self, api_key: str) -> bool:
        """Initialize Gemini client."""
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model)
            logger.info("Gemini provider initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini provider: {str(e)}")
            return False

    def process_query(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Process query with Gemini."""
        try:
            # Convert OpenAI format to Gemini format
            gemini_messages = self._convert_messages(messages)

            import google.generativeai as genai

            response = self.client.generate_content(
                gemini_messages,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=kwargs.get("max_tokens", 500),
                    temperature=kwargs.get("temperature", 0.3),
                ),
            )

            return {
                "status": "success",
                "response": response.text.strip(),
                "model": self.model,
                "tokens_used": (
                    response.usage_metadata.total_token_count
                    if hasattr(response, "usage_metadata")
                    else None
                ),
                "provider": "gemini",
            }
        except Exception as e:
            logger.error(f"Gemini query failed: {str(e)}")
            return {"status": "error", "error": str(e), "provider": "gemini"}

    def _convert_messages(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI message format to Gemini format."""
        converted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                converted.append(f"System: {content}")
            elif role == "user":
                converted.append(f"User: {content}")
            elif role == "assistant":
                converted.append(f"Assistant: {content}")

        return "\n\n".join(converted)

    def get_model_info(self) -> Dict[str, str]:
        """Get Gemini model information."""
        return {"provider": "gemini", "model": self.model, "name": "Gemini 1.5 Pro"}


class FlexibleAIHandler:
    """Flexible AI handler supporting multiple providers."""

    def __init__(self, provider: str = "auto"):
        """
        Initialize AI handler.

        Args:
            provider: "openai", "gemini", or "auto" (detects based on available API keys)
        """
        self.provider_name = provider
        self.provider = None
        self.system_prompt = self._get_system_prompt()
        self.conversation_history: List[Dict[str, str]] = []

        # Initialize provider
        self._initialize_provider()

    def _initialize_provider(self):
        """Initialize the appropriate AI provider."""
        if self.provider_name == "local":
            # Explicitly use local provider
            self.provider = LocalProvider()
            self.provider.initialize()
            return
            
        if self.provider_name == "auto":
            # Try to detect available provider
            if os.getenv("OPENAI_API_KEY"):
                self.provider_name = "openai"
            elif os.getenv("GEMINI_API_KEY"):
                self.provider_name = "gemini"
            else:
                logger.warning("No AI provider API keys found, using local provider")
                self.provider_name = "local"
                self.provider = LocalProvider()
                self.provider.initialize()
                return

        if self.provider_name == "openai":
            self.provider = OpenAIProvider()
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                if not self.provider.initialize(api_key):
                    logger.warning("OpenAI provider failed, falling back to local")
                    self.provider_name = "local"
                    self.provider = LocalProvider()
                    self.provider.initialize()
        elif self.provider_name == "gemini":
            self.provider = GeminiProvider()
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                if not self.provider.initialize(api_key):
                    logger.warning("Gemini provider failed, falling back to local")
                    self.provider_name = "local"
                    self.provider = LocalProvider()
                    self.provider.initialize()
        else:
            logger.error(f"Unknown provider: {self.provider_name}, falling back to local")
            self.provider_name = "local"
            self.provider = LocalProvider()
            self.provider.initialize()

    def _get_system_prompt(self) -> str:
        """Get the system prompt for DevOps assistant role."""
        return """You are a Senior DevOps Engineer and Cloud Operations expert. Your role is to assist with:

1. **Infrastructure Analysis**: Analyze AWS resources, monitoring data, and system metrics
2. **Troubleshooting**: Help diagnose issues using logs, metrics, and system status
3. **Best Practices**: Provide guidance on DevOps, security, and cloud operations
4. **Automation**: Suggest improvements and automation opportunities
5. **Monitoring**: Interpret Prometheus metrics and Grafana dashboards

**Response Guidelines**:
- Be concise and actionable
- Use technical terminology appropriately
- Provide specific recommendations when possible
- Include relevant metrics or data points
- Suggest next steps for investigation

**Current System Context**:
- AWS infrastructure with EC2 instances
- Prometheus + Grafana monitoring stack
- Flask application with metrics endpoints
- Node Exporter for system metrics

Always respond in a professional, helpful manner focused on operational excellence."""

    def sanitize_input(self, query: str) -> str:
        """Sanitize and validate user input with comprehensive security checks."""
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")

        # Remove potentially dangerous characters and patterns
        sanitized = query.strip()

        # Remove script tags and their content
        sanitized = re.sub(
            r"<script[^>]*>.*?</script>", "", sanitized, flags=re.IGNORECASE | re.DOTALL
        )

        # Remove alert calls
        sanitized = re.sub(r"alert\s*\([^)]*\)", "", sanitized, flags=re.IGNORECASE)

        # Remove other dangerous characters
        sanitized = re.sub(r'[<>"]', "", sanitized)

        # Limit query length
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000] + "..."

        # Enhanced injection prevention patterns
        dangerous_patterns = [
            # Command injection
            r"system\s*\(",
            r"eval\s*\(",
            r"exec\s*\(",
            r"subprocess\.",
            r"os\.system",
            r"commands\.",
            # SQL injection
            r"SELECT\s+.*FROM",
            r"INSERT\s+INTO",
            r"UPDATE\s+.*SET",
            r"DELETE\s+FROM",
            r"DROP\s+TABLE",
            r"CREATE\s+TABLE",
            r"ALTER\s+TABLE",
            r"UNION\s+SELECT",
            r"OR\s+1\s*=\s*1",
            r"AND\s+1\s*=\s*1",
            # Python code injection
            r"__import__",
            r"import\s+os",
            r"import\s+sys",
            r"import\s+subprocess",
            r"globals\(",
            r"locals\(",
            r"compile\(",
            # File system access
            r"open\s*\(",
            r"file\s*\(",
            r"read\s*\(",
            r"write\s*\(",
            # Network access
            r"urllib\.",
            r"requests\.",
            r"socket\.",
            r"http\.",
            # Reflection and metaprogramming
            r"getattr\(",
            r"setattr\(",
            r"hasattr\(",
            r"delattr\(",
            r"type\(",
            r"isinstance\(",
            # Dangerous built-ins
            r"input\(",
            r"raw_input\(",
            r"exec\(",
            r"eval\(",
            # Unicode normalization attacks
            r"\\u[0-9a-fA-F]{4}",
            r"\\x[0-9a-fA-F]{2}",
            # Template injection
            r"\{\{.*\}\}",
            r"\{%.*%\}",
            r"\{#.*#\}",
            # XSS patterns
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe",
            r"<object",
            r"<embed",
            r"<form",
            r"<input",
            r"<textarea",
            r"<select",
            r"<button",
            # Path traversal
            r"\.\./",
            r"\.\.\\",
            r"~",
            r"/etc/",
            r"/proc/",
            r"/sys/",
            r"C:\\",
            r"D:\\",
            # Shell command patterns (more specific)
            r"\$\(.*\)",
            r"`.*`",
            r"&&\s*[a-zA-Z]",
            r"\|\|\s*[a-zA-Z]",
            r";\s*[a-zA-Z]",
            r"&\s*[a-zA-Z]",
            r"\|\s*[a-zA-Z]",
            r">\s*[a-zA-Z]",
            r"<\s*[a-zA-Z]",
            r">>\s*[a-zA-Z]",
            r"<<\s*[a-zA-Z]",
            # Environment variable access
            r"\$\{.*\}",
            r"\$[A-Z_]+",
            # Hex encoded payloads
            r"\\x[0-9a-fA-F]{2,}",
            # URL encoded payloads
            r"%[0-9a-fA-F]{2}",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                logger.warning(f"Potentially dangerous pattern detected: {pattern}")
                raise ValueError(
                    f"Query contains potentially unsafe content: {pattern}"
                )

        # Additional validation checks
        if self._contains_suspicious_encoding(sanitized):
            raise ValueError("Query contains suspicious encoding patterns")

        if self._contains_obfuscated_code(sanitized):
            raise ValueError("Query contains obfuscated code patterns")

        if self._contains_privilege_escalation(sanitized):
            raise ValueError("Query contains privilege escalation patterns")

        return sanitized

    def _contains_suspicious_encoding(self, text: str) -> bool:
        """Check for suspicious encoding patterns."""
        # Check for excessive encoding
        encoded_chars = len(re.findall(r"%[0-9a-fA-F]{2}", text))
        if encoded_chars > len(text) * 0.3:  # More than 30% encoded
            return True

        # Check for double encoding
        if re.search(r"%25[0-9a-fA-F]{2}", text):
            return True

        return False

    def _contains_obfuscated_code(self, text: str) -> bool:
        """Check for obfuscated code patterns."""
        # Check for excessive use of special characters
        special_chars = len(re.findall(r"[^\w\s]", text))
        special_char_ratio = special_chars / len(text) if text else 0

        if special_char_ratio > 0.7:  # More than 70% special chars (increased from 50%)
            logger.debug(f"High special character ratio: {special_char_ratio:.2f}")
            return True

        # Check for repeated patterns that might indicate obfuscation
        # Only check for repeated special characters, not alphanumeric
        if re.search(
            r"([^\w\s])\1{20,}", text
        ):  # Same special character repeated 20+ times
            logger.debug("Detected repeated special character pattern")
            return True

        return False

    def _contains_privilege_escalation(self, text: str) -> bool:
        """Check for privilege escalation patterns."""
        privilege_patterns = [
            r"sudo",
            r"su\s+",
            r"runas",
            r"elevate",
            r"privilege",
            r"admin",
            r"root",
            r"chmod\s+777",
            r"chown\s+root",
            r"setuid",
            r"setgid",
        ]

        for pattern in privilege_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def add_context(self, context: Dict[str, Any]) -> str:
        """Add system context to the conversation."""
        context_prompt = "\n\n**Current System Context**:\n"

        if context.get("system_health"):
            context_prompt += f"- System Health: {context['system_health']}\n"

        if context.get("prometheus_metrics"):
            context_prompt += f"- Prometheus Status: {context['prometheus_metrics']}\n"

        if context.get("recent_alerts"):
            context_prompt += f"- Recent Alerts: {context['recent_alerts']}\n"

        if context.get("resource_usage"):
            context_prompt += f"- Resource Usage: {context['resource_usage']}\n"

        return context_prompt

    def process_query(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process ChatOps query with AI integration."""
        try:
            # Check if AI provider is available
            if not self.provider:
                return {
                    "status": "error",
                    "error": "AI functionality not available",
                    "message": f"No AI provider configured. Set {self.provider_name.upper()}_API_KEY environment variable.",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            # Sanitize input
            sanitized_query = self.sanitize_input(query)

            # Prepare context
            context = context or {}
            context_prompt = self.add_context(context)

            # Build messages
            messages = [
                {"role": "system", "content": self.system_prompt + context_prompt},
                {"role": "user", "content": sanitized_query},
            ]

            # Add conversation history (last 10 messages)
            if self.conversation_history:
                recent_history = self.conversation_history[-10:]
                messages = (
                    [{"role": "system", "content": self.system_prompt + context_prompt}]
                    + recent_history
                    + [{"role": "user", "content": sanitized_query}]
                )

            # Process with AI provider
            result = self.provider.process_query(messages)

            if result["status"] == "success":
                # Update conversation history
                self.conversation_history.append(
                    {"role": "user", "content": sanitized_query}
                )
                self.conversation_history.append(
                    {"role": "assistant", "content": result["response"]}
                )

                # Keep history manageable
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]

                logger.info(
                    f"Successfully processed query with {self.provider_name}: {sanitized_query[:50]}..."
                )

                return {
                    "status": "success",
                    "response": result["response"],
                    "query": sanitized_query,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "model": result.get("model", "unknown"),
                    "provider": result.get("provider", self.provider_name),
                    "tokens_used": result.get("tokens_used"),
                }
            else:
                return {
                    "status": "error",
                    "error": result.get("error", "Unknown error"),
                    "message": "AI processing failed",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "provider": result.get("provider", self.provider_name),
                }

        except ValueError as e:
            logger.warning(f"Input validation error: {str(e)}")
            return {
                "status": "error",
                "error": "Invalid input",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"AI processing error: {str(e)}")
            return {
                "status": "error",
                "error": "Processing failed",
                "message": "Unable to process query at this time",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history.copy()

    def clear_history(self) -> bool:
        """Clear conversation history."""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
        return True

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current AI provider."""
        if self.provider:
            return {
                "provider": self.provider_name,
                "available": True,
                "model_info": self.provider.get_model_info(),
            }
        else:
            return {
                "provider": self.provider_name,
                "available": False,
                "model_info": None,
            }
