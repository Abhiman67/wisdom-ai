"""
LLM Service Module
Provides integration with open-source LLMs for generating spiritual responses
"""

import os
import json
import requests
from typing import Optional, Dict, Any
import time

# Try to import transformers for local model support
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("Warning: Transformers not available. Will use Ollama API instead.")
    TRANSFORMERS_AVAILABLE = False

class LLMService:
    """Service for generating AI responses using open-source LLMs"""
    
    def __init__(self):
        self.model_name = os.getenv("LLM_MODEL", "distilgpt2")  # More suitable for text generation
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
        self.use_grok = os.getenv("USE_GROK", "false").lower() == "true"
        self.grok_api_key = os.getenv("GROK_API_KEY", "")
        self.grok_api_url = os.getenv("GROK_API_URL", "https://api.x.ai/v1/chat/completions")
        self.local_model = None
        self.tokenizer = None
        
        # Initialize the appropriate model
        if self.use_grok and self.grok_api_key:
            self._init_grok()
        elif self.use_ollama:
            self._init_ollama()
        elif TRANSFORMERS_AVAILABLE:
            self._init_transformers()
        else:
            print("Warning: No LLM backend available. Using template responses.")
    
    def _init_grok(self):
        """Initialize Grok API connection"""
        try:
            if not self.grok_api_key:
                print("❌ Grok API key not provided")
                self.use_grok = False
                if TRANSFORMERS_AVAILABLE:
                    self._init_transformers()
                return
            
            print("✓ Grok API connection established")
            self.use_grok = True
            
        except Exception as e:
            print(f"❌ Grok initialization failed: {e}")
            self.use_grok = False
            if TRANSFORMERS_AVAILABLE:
                self._init_transformers()
    
    def _init_ollama(self):
        """Initialize Ollama connection"""
        try:
            # Test if Ollama is running
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                print("✓ Ollama connection established")
                self.use_ollama = True
            else:
                print("❌ Ollama not responding, falling back to transformers")
                self.use_ollama = False
                if TRANSFORMERS_AVAILABLE:
                    self._init_transformers()
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            self.use_ollama = False
            if TRANSFORMERS_AVAILABLE:
                self._init_transformers()
    
    def _init_transformers(self):
        """Initialize transformers model"""
        if not TRANSFORMERS_AVAILABLE:
            return
            
        try:
            print(f"🤖 Loading local LLM model: {self.model_name}")
            
            # Use a lightweight model for better performance
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.local_model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            print("✓ Local LLM model loaded successfully")
            
        except Exception as e:
            print(f"❌ Failed to load local model: {e}")
            self.local_model = None
            self.tokenizer = None
    
    def generate_response(
        self, 
        user_message: str, 
        verse: Dict[str, Any], 
        mood: str, 
        user_summary: Optional[str] = None
    ) -> str:
        """
        Generate a personalized spiritual response using LLM
        
        Args:
            user_message: User's input message
            verse: Selected verse with text and source
            mood: Detected mood
            user_summary: Optional summary of user's message
            
        Returns:
            Generated response string
        """
        print(f"[DEBUG] use_grok={self.use_grok}, use_ollama={self.use_ollama}, local_model={self.local_model}")
        # Create context for the LLM
        context = self._create_context(user_message, verse, mood, user_summary)
        
        if self.use_grok:
            return self._generate_with_grok(context)
        elif self.use_ollama:
            return self._generate_with_ollama(context)
        elif self.local_model and self.tokenizer:
            return self._generate_with_transformers(context)
        else:
            return self._generate_template_response(user_message, verse, mood)
    
    def _create_context(self, user_message: str, verse: Dict[str, Any], mood: str, user_summary: Optional[str]) -> str:
        """Create context prompt for the LLM"""
        
        prompt = f"""You are a compassionate and wise spiritual companion.  
The user is currently feeling {mood} and has expressed:  
"{user_message}"  

You have chosen this verse to comfort and guide them:  
"{verse['text']}"  
— {verse['source']}  

Write a warm, empathetic message directly to the user.  
- Acknowledge their feelings with kindness.  
- Introduce the verse naturally (say “Here is a verse I’d like to share with you,” not “the verse you shared”).  
- Explain how the verse relates to their situation.  
- Offer comfort and encouragement.  
- End with a hopeful note or gentle reflection.  

⚡Important:  
- Do NOT explain what you are doing.  
- Do NOT say “Here is a response” or “Of course.”  
- Do NOT miss the verse in response 
- Only output the final message to the user, under 120 words.  
"""

        return prompt
    
    def _generate_with_grok(self, context: str) -> str:
        """Generate response using Grok API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.grok_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "grok-beta",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a compassionate spiritual AI companion. Provide warm, empathetic responses that explain verses and offer comfort."
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            response = requests.post(
                self.grok_api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return content.strip()
            else:
                print(f"Grok API error: {response.status_code} - {response.text}")
                return self._generate_template_response("", {"text": "May you find peace and wisdom.", "source": "God AI"}, "neutral")
                
        except Exception as e:
            print(f"Grok generation failed: {e}")
            return self._generate_template_response("", {"text": "May you find peace and wisdom.", "source": "God AI"}, "neutral")
    
    def _generate_with_ollama(self, context: str) -> str:
        """Generate response using Ollama API"""
        print("[DEBUG] Calling Ollama API with context:", context[:100], "...")
        try:
            # Use a spiritual/helpful model if available, otherwise use llama2
            model = "llama2:7b"  # or "mistral" if available
            payload = {
                "model": model,
                "prompt": context,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 60
                }
            }
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=90  # Increased timeout for testing
            )
            print(f"[DEBUG] Ollama API status: {response.status_code}")
            print(f"[DEBUG] Ollama API response: {response.text[:200]}")
            if response.status_code == 200:
                result = response.json()
                print("[DEBUG] Ollama API result:", result)
                return result.get("response", "I'm here to offer you comfort and guidance.")
            else:
                print(f"[ERROR] Ollama API error: {response.status_code} - {response.text}")
                print("[DEBUG] Falling back to template response.")
                return self._generate_template_response("", {"text": "May you find peace and wisdom.", "source": "God AI"}, "neutral")
        except Exception as e:
            print(f"[ERROR] Ollama generation failed: {e}")
            print("[DEBUG] Falling back to template response.")
            return self._generate_template_response("", {"text": "May you find peace and wisdom.", "source": "God AI"}, "neutral")
    
    def _generate_with_transformers(self, context: str) -> str:
        """Generate response using local transformers model"""
        try:
            if not self.local_model or not self.tokenizer:
                return self._generate_template_response("", {"text": "May you find peace and wisdom.", "source": "God AI"}, "neutral")
            
            # Create a more focused prompt for better generation
            prompt = f"Spiritual Companion: {context}\nResponse:"
            
            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=300, truncation=True)
            
            # Generate response
            with torch.no_grad():
                outputs = self.local_model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 80,  # Generate up to 80 more tokens
                    num_return_sequences=1,
                    temperature=0.9,
                    do_sample=True,
                    top_p=0.95,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=2,
                    repetition_penalty=1.2
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the generated part (remove the input prompt)
            generated_text = response[len(prompt):].strip()
            
            # Clean up the response
            if generated_text and len(generated_text) > 15:
                # Take only the first complete response
                sentences = generated_text.split('.')
                if sentences and len(sentences[0]) > 20:
                    first_sentence = sentences[0].strip()
                    return f"I understand your feelings. {first_sentence}."
                
            # If generation failed, use template
            return self._generate_template_response("", {"text": "May you find peace and wisdom.", "source": "God AI"}, "neutral")
                
        except Exception as e:
            print(f"Transformers generation failed: {e}")
            return self._generate_template_response("", {"text": "May you find peace and wisdom.", "source": "God AI"}, "neutral")
    
    def _generate_template_response(self, user_message: str, verse: Dict[str, Any], mood: str) -> str:
        """Enhanced template-based response generation with verse explanation"""
        mood_responses = {
            "sadness": "I understand you're going through a difficult time. Let this verse bring you comfort and hope:",
            "happy": "I'm glad you're feeling joyful! Here's a verse to celebrate this moment:",
            "anger": "I sense you're feeling frustrated. This wisdom might help bring clarity and peace:",
            "fear": "I hear the worry in your words. Let this verse offer you strength and courage:",
            "surprise": "I can feel the surprise in your message. Here's some guidance for this moment:",
            "disgust": "I understand your concern. This verse might offer a different perspective:"
        }
        
        mood_intro = mood_responses.get(mood, "Here's a verse that might speak to your heart:")
        
        # Add verse explanation based on mood
        verse_explanations = {
            "sadness": "This verse reminds us that even in our darkest moments, there is comfort and strength available to us. It speaks to the healing power of faith and the promise that we are not alone in our struggles.",
            "happy": "This verse celebrates the joy and blessings in our lives. It reminds us to be grateful for the good moments and to share our happiness with others.",
            "anger": "This verse offers wisdom about managing difficult emotions. It reminds us that patience and understanding can help us navigate challenging situations with grace.",
            "fear": "This verse speaks to courage and trust. It reminds us that we have inner strength and that we can face our fears with faith and determination.",
            "surprise": "This verse offers guidance for unexpected moments. It reminds us that life's surprises can be opportunities for growth and learning.",
            "disgust": "This verse provides perspective on difficult situations. It reminds us that there are always different ways to view challenges and find meaning in them."
        }
        
        explanation = verse_explanations.get(mood, "This verse offers wisdom and guidance for your current situation. It reminds us that there is always hope and meaning to be found.")
        
        response = f"{mood_intro}\n\n\"{verse['text']}\"\n— {verse['source']}\n\n{explanation}\n\nHow does this verse speak to your heart today?"
        
        return response
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current LLM setup"""
        info = {
            "use_grok": self.use_grok,
            "use_ollama": self.use_ollama,
            "ollama_url": self.ollama_url if self.use_ollama else None,
            "local_model": self.model_name if self.local_model else None,
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "backend": "grok" if self.use_grok else ("ollama" if self.use_ollama else ("transformers" if self.local_model else "template"))
        }
        
        if self.use_ollama:
            try:
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    info["available_models"] = [model["name"] for model in models]
            except:
                info["available_models"] = []
        
        return info

# Global LLM service instance
llm_service = None

def initialize_llm():
    """Initialize the global LLM service"""
    global llm_service
    llm_service = LLMService()
    return llm_service

def get_llm_service():
    """Get the global LLM service instance"""
    return llm_service
