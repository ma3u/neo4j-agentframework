"""
LLM Handler for RAG Answer Generation
Supports multiple LLM backends: Ollama (local), OpenAI, or simple fallback
"""

import os
import json
import logging
from typing import Dict, Optional, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMInterface(ABC):
    """Abstract base class for LLM implementations"""

    @abstractmethod
    def generate(self, prompt: str, context: str, **kwargs) -> str:
        """Generate an answer based on prompt and context"""
        pass


class BitNetLLM(LLMInterface):
    """BitNet implementation for ultra-efficient local LLM"""

    def __init__(self, base_url: str = None):
        """Initialize BitNet client"""
        # Try container network first, then localhost
        self.base_url = base_url or os.getenv("BITNET_ENDPOINT", "http://bitnet-llm:8001")
        self._test_connection()

    def _test_connection(self):
        """Test if BitNet is running"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/health", timeout=2)
            if response.status_code == 200:
                health = response.json()
                logger.info(f"BitNet connected: {health.get('model', 'Unknown')}")
                logger.info(f"Quantization: {health.get('quantization', 'Unknown')}")
            else:
                logger.warning(f"BitNet health check failed: HTTP {response.status_code}")
        except Exception as e:
            logger.warning(f"BitNet not available at {self.base_url}: {e}")

    def generate(self, prompt: str, context: str, **kwargs) -> str:
        """Generate answer using BitNet"""
        try:
            import requests

            # Create a focused prompt for BitNet
            full_prompt = f"""Based on the following context, answer the question concisely.

Context:
{context[:1000]}

Question: {prompt}

Answer:"""

            response = requests.post(
                f"{self.base_url}/generate",
                json={
                    "prompt": full_prompt,
                    "max_tokens": kwargs.get('max_tokens', 150)
                },
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                answer = result.get('generated_text', '')

                # BitNet returns a response message - extract actual answer
                # Format: "BitNet-b1.58 model response: [prompt text] is processed..."
                if "BitNet-b1.58 model response:" in answer:
                    # This is the simplified mode response - use fallback instead
                    return None

                # Extract just the answer part (remove the prompt echo if present)
                if "Answer:" in answer:
                    answer = answer.split("Answer:")[-1].strip()

                # Remove the prompt if it's echoed
                if "Context:" in answer:
                    return None  # Prompt was echoed, use fallback

                return answer.strip() if answer and len(answer) > 10 else None

            logger.error(f"BitNet generation failed: HTTP {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"BitNet generation failed: {e}")
            return None


class OllamaLLM(LLMInterface):
    """Ollama implementation for local LLM"""

    def __init__(self, model: str = None, base_url: str = None):
        """Initialize Ollama client"""
        self.model = model
        self.base_url = base_url or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self._test_connection()

    def _test_connection(self):
        """Test if Ollama is running and select best model"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                logger.info(f"Ollama connected. Available models: {model_names}")

                # If no model specified, try to use the best available one
                if not self.model and model_names:
                    # Prefer these models in order
                    preferred = ['qwen2:latest', 'llama2', 'mistral', 'phi', 'phi4:latest', 'deepseek-r1:7b']
                    for pref in preferred:
                        if pref in model_names:
                            self.model = pref
                            logger.info(f"Auto-selected model: {self.model}")
                            break
                    if not self.model:
                        # Use first available model
                        self.model = model_names[0]
                        logger.info(f"Using first available model: {self.model}")
                return True
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False

    def generate(self, prompt: str, context: str, **kwargs) -> str:
        """Generate answer using Ollama"""
        try:
            import requests

            system_prompt = """You are a helpful assistant that answers questions based on the provided context.
            Always base your answers on the context provided. If the context doesn't contain enough information,
            say so. Be concise and direct in your responses."""

            full_prompt = f"""Context:
{context}

Question: {prompt}

Answer based on the context above:"""

            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            }

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()['response']
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return None


class OpenAILLM(LLMInterface):
    """OpenAI GPT implementation"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """Initialize OpenAI client"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

        if not self.api_key:
            logger.warning("OpenAI API key not provided")

    def generate(self, prompt: str, context: str, **kwargs) -> str:
        """Generate answer using OpenAI"""
        if not self.api_key:
            return None

        try:
            import openai
            openai.api_key = self.api_key

            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on provided context. Be concise and accurate."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {prompt}"
                }
            ]

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return None


class LangChainLLM(LLMInterface):
    """LangChain-based LLM implementation with prompt templates"""

    def __init__(self):
        """Initialize LangChain components"""
        try:
            from langchain.prompts import PromptTemplate
            from langchain.chains import LLMChain
            from langchain_community.llms import Ollama

            self.prompt_template = PromptTemplate(
                input_variables=["context", "question"],
                template="""You are an expert on graph databases, particularly Neo4j.
                Use the following context to answer the question. If the context doesn't
                contain the answer, say you don't have enough information.

Context: {context}

Question: {question}

Answer: """
            )

            # Try to use Ollama if available
            try:
                # Check what models are available
                import requests
                ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
                response = requests.get(f"{ollama_host}/api/tags")
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    if models:
                        model_name = models[0]['name']  # Use first available
                        self.llm = Ollama(model=model_name)
                        logger.info(f"Using Ollama via LangChain with model: {model_name}")
                    else:
                        self.llm = None
                else:
                    self.llm = None
            except:
                # Fallback to a simple implementation
                logger.info("Ollama not available, using fallback")
                self.llm = None

        except ImportError:
            logger.warning("LangChain not fully configured")
            self.llm = None

    def generate(self, prompt: str, context: str, **kwargs) -> str:
        """Generate answer using LangChain"""
        if self.llm:
            try:
                from langchain.chains import LLMChain
                chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
                response = chain.run(context=context, question=prompt)
                return response
            except Exception as e:
                logger.error(f"LangChain generation failed: {e}")
        return None


class SmartFallbackLLM(LLMInterface):
    """Improved fallback that extracts answers from context intelligently"""

    def generate(self, prompt: str, context: str, **kwargs) -> str:
        """Generate answer using smart extraction from context"""
        prompt_lower = prompt.lower()

        # For "what" or "how" questions - HANDLE FIRST (before yes/no detection!)
        if "what" in prompt_lower or "how" in prompt_lower:
            return self._summarize_context(context, prompt_lower)

        # For author questions, extract author information
        elif "author" in prompt_lower or "who wrote" in prompt_lower:
            return self._extract_authors(context, prompt_lower)

        # For counting questions (already handled by "how many")
        elif "how many" in prompt_lower:
            return self._extract_count(context, prompt_lower)

        # For listing questions
        elif any(word in prompt_lower for word in ["list", "what are", "which"]):
            return self._extract_list(context, prompt_lower)

        # For yes/no questions (AFTER "what/how" check)
        elif any(word in prompt_lower for word in ["is ", "are ", "can ", "does ", "do "]):
            return self._analyze_boolean(context, prompt_lower)

        # Default: summarize relevant parts
        else:
            return self._summarize_context(context, prompt_lower)

    def _extract_authors(self, context: str, prompt: str) -> str:
        """Extract author information from context"""
        import re

        authors = set()
        # Look for author patterns
        patterns = [
            r'by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+wrote',
            r'[Aa]uthor[s]?[:\s]+([^,\n]+)',
            r'written\s+by\s+([^,\n]+)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, context, re.IGNORECASE | re.MULTILINE)
            authors.update(matches)

        # Look for specific names in context
        known_authors = [
            'Ian Robinson', 'Jim Webber', 'Emil Eifrem',
            'Michael Hunger', 'Max De Marzi', 'Nicole White',
            'Mark Needham', 'Amy Hodler', 'Matthias Broecheler'
        ]

        for author in known_authors:
            if author.lower() in context.lower():
                authors.add(author)

        if authors:
            author_list = list(authors)[:10]
            return f"Based on the context, the following authors are mentioned:\n" + \
                   "\n".join([f"• {author}" for author in author_list])
        else:
            return "I couldn't identify specific author names in the provided context."

    def _extract_count(self, context: str, prompt: str) -> str:
        """Extract count information from context"""
        import re

        numbers = re.findall(r'\b(\d+)\b', context)

        if "author" in prompt:
            # Count unique author mentions
            author_count = len(re.findall(r'[A-Z][a-z]+\s+[A-Z][a-z]+', context))
            return f"Based on the context, I can identify approximately {author_count} author references."
        elif numbers:
            return f"The context contains these numbers: {', '.join(set(numbers)[:10])}"
        else:
            return "I couldn't find specific numerical information in the context."

    def _extract_list(self, context: str, prompt: str) -> str:
        """Extract list items from context"""
        import re

        # Look for bullet points or numbered lists
        items = re.findall(r'[-•*]\s+([^\n]+)', context)
        if not items:
            items = re.findall(r'\d+\.\s+([^\n]+)', context)

        if items:
            return "Based on the context, here are the relevant items:\n" + \
                   "\n".join([f"• {item[:100]}" for item in items[:10]])
        else:
            # Extract key phrases
            sentences = context.split('.')[:5]
            return "Key points from the context:\n" + \
                   "\n".join([f"• {s.strip()}" for s in sentences if len(s.strip()) > 20])

    def _analyze_boolean(self, context: str, prompt: str) -> str:
        """Analyze context for yes/no questions"""
        # Simple keyword-based analysis
        positive_indicators = ['yes', 'true', 'correct', 'is a', 'are']
        negative_indicators = ['no', 'false', 'not', 'isn\'t', 'aren\'t']

        context_lower = context.lower()
        pos_count = sum(1 for word in positive_indicators if word in context_lower)
        neg_count = sum(1 for word in negative_indicators if word in context_lower)

        if pos_count > neg_count:
            return "Based on the context, the answer appears to be yes."
        elif neg_count > pos_count:
            return "Based on the context, the answer appears to be no."
        else:
            return "The context doesn't provide a clear yes/no answer to this question."

    def _summarize_context(self, context: str, prompt: str) -> str:
        """Provide a summary of relevant context"""
        # Find most relevant sentences
        sentences = [s.strip() for s in context.split('.') if len(s.strip()) > 20]

        # Simple relevance scoring based on keyword overlap
        keywords = set(prompt.lower().split())
        scored_sentences = []

        for sentence in sentences[:20]:  # Limit to first 20 sentences
            score = sum(1 for word in keywords if word in sentence.lower())
            if score > 0:
                scored_sentences.append((score, sentence))

        # Sort by relevance score
        scored_sentences.sort(key=lambda x: x[0], reverse=True)

        if scored_sentences:
            top_sentences = [sent for _, sent in scored_sentences[:3]]
            return "Based on the context:\n" + " ".join(top_sentences)
        else:
            return f"Context summary: {context[:300]}..."


class LLMHandler:
    """Main LLM handler that manages multiple backends"""

    def __init__(self, preferred_backend: str = "auto"):
        """
        Initialize LLM handler

        Args:
            preferred_backend: One of "bitnet", "ollama", "openai", "langchain", "fallback", or "auto"
        """
        self.backends = []

        if preferred_backend == "auto":
            # Try backends in order of preference (BitNet first!)
            self._try_add_backend(BitNetLLM)
            self._try_add_backend(OllamaLLM)
            self._try_add_backend(LangChainLLM)
            self._try_add_backend(OpenAILLM)
        elif preferred_backend == "bitnet":
            self._try_add_backend(BitNetLLM)
        elif preferred_backend == "ollama":
            self._try_add_backend(OllamaLLM)
        elif preferred_backend == "openai":
            self._try_add_backend(OpenAILLM)
        elif preferred_backend == "langchain":
            self._try_add_backend(LangChainLLM)

        # Always add fallback as last resort
        self.backends.append(SmartFallbackLLM())

        logger.info(f"LLM Handler initialized with {len(self.backends)} backend(s)")

    def _try_add_backend(self, backend_class):
        """Try to add a backend, catching any initialization errors"""
        try:
            backend = backend_class()
            self.backends.append(backend)
            logger.info(f"Added {backend_class.__name__} backend")
        except Exception as e:
            logger.warning(f"Could not initialize {backend_class.__name__}: {e}")

    def generate_answer(self, question: str, context: str, **kwargs) -> str:
        """
        Generate an answer using available LLM backends

        Args:
            question: The user's question
            context: Retrieved context from the knowledge base
            **kwargs: Additional parameters for the LLM

        Returns:
            Generated answer string
        """
        for backend in self.backends:
            try:
                answer = backend.generate(question, context, **kwargs)
                if answer:
                    return answer
            except Exception as e:
                logger.warning(f"Backend {backend.__class__.__name__} failed: {e}")
                continue

        # If all backends fail, return a simple message
        return "I apologize, but I couldn't generate a proper answer. Please check the system configuration."


# Example usage
if __name__ == "__main__":
    # Initialize handler
    handler = LLMHandler(preferred_backend="auto")

    # Test question
    context = """
    Neo4j is a graph database. It was created by Neo4j, Inc.
    The founders include Emil Eifrem, Johan Svensson, and Peter Neubauer.
    Graph databases are great for connected data.
    """

    question = "Who created Neo4j?"

    answer = handler.generate_answer(question, context)
    print(f"Question: {question}")
    print(f"Answer: {answer}")