"""
Ollama Client - Supports both local CLI and remote HTTP API access
"""

import os
import json
import subprocess
import requests
from typing import Dict, Any, Optional, List
from ..core.utils import colored_print
from ..core.models import Colors


class OllamaClient:
    """Client that can connect to local or remote Ollama instances"""
    
    def __init__(self):
        # Configuration from environment variables
        self.use_remote = os.getenv('OLLAMA_USE_REMOTE', 'false').lower() == 'true'
        self.remote_host = os.getenv('OLLAMA_REMOTE_HOST', 'localhost')
        self.remote_port = os.getenv('OLLAMA_REMOTE_PORT', '11434')
        self.api_key = os.getenv('OLLAMA_API_KEY', '')  # For cloud services that require auth
        self.local_cmd = os.getenv('OLLAMA_CMD', 'ollama')
        self.default_model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        
        # Construct API base URL
        self.api_base_url = f"http://{self.remote_host}:{self.remote_port}"
        
        colored_print(f"Ollama Client initialized:", Colors.CYAN)
        if self.use_remote:
            colored_print(f"  Mode: Remote API ({self.api_base_url})", Colors.YELLOW)
        else:
            colored_print(f"  Mode: Local CLI ({self.local_cmd})", Colors.YELLOW)
        colored_print(f"  Default Model: {self.default_model}", Colors.YELLOW)
    
    def is_available(self) -> bool:
        """Check if Ollama (local or remote) is available"""
        if self.use_remote:
            return self._check_remote_availability()
        else:
            return self._check_local_availability()
    
    def _check_local_availability(self) -> bool:
        """Check if local Ollama is available"""
        try:
            result = subprocess.run([self.local_cmd, "list"], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_remote_availability(self) -> bool:
        """Check if remote Ollama API is available"""
        try:
            response = requests.get(f"{self.api_base_url}/api/tags", 
                                  headers=self._get_headers(), timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers
    
    def list_models(self) -> List[str]:
        """List available models"""
        if self.use_remote:
            return self._list_remote_models()
        else:
            return self._list_local_models()
    
    def _list_local_models(self) -> List[str]:
        """List local models"""
        try:
            result = subprocess.run([self.local_cmd, "list"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                return [line.split()[0] for line in lines if line.strip()]
            return []
        except Exception:
            return []
    
    def _list_remote_models(self) -> List[str]:
        """List remote models"""
        try:
            response = requests.get(f"{self.api_base_url}/api/tags", 
                                  headers=self._get_headers())
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception:
            return []
    
    def generate(self, prompt: str, model: Optional[str] = None, 
                 stream: bool = False) -> Dict[str, Any]:
        """Generate response from Ollama"""
        model = model or self.default_model
        
        if self.use_remote:
            return self._generate_remote(prompt, model, stream)
        else:
            return self._generate_local(prompt, model)
    
    def _generate_local(self, prompt: str, model: str) -> Dict[str, Any]:
        """Generate using local Ollama CLI"""
        try:
            result = subprocess.run([self.local_cmd, "run", model, prompt], 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'response': result.stdout.strip(),
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'response': '',
                    'error': result.stderr or 'Unknown error'
                }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'response': '',
                'error': 'Request timed out'
            }
        except Exception as e:
            return {
                'success': False,
                'response': '',
                'error': str(e)
            }
    
    def _generate_remote(self, prompt: str, model: str, stream: bool = False) -> Dict[str, Any]:
        """Generate using remote Ollama API"""
        try:
            payload = {
                'model': model,
                'prompt': prompt,
                'stream': stream
            }
            
            response = requests.post(f"{self.api_base_url}/api/generate", 
                                   json=payload, 
                                   headers=self._get_headers(),
                                   timeout=120)
            
            if response.status_code == 200:
                if stream:
                    # Handle streaming response
                    full_response = ""
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line)
                            if 'response' in data:
                                full_response += data['response']
                            if data.get('done', False):
                                break
                    return {
                        'success': True,
                        'response': full_response,
                        'error': None
                    }
                else:
                    data = response.json()
                    return {
                        'success': True,
                        'response': data.get('response', ''),
                        'error': None
                    }
            else:
                return {
                    'success': False,
                    'response': '',
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'response': '',
                'error': 'Request timed out'
            }
        except Exception as e:
            return {
                'success': False,
                'response': '',
                'error': str(e)
            }
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> Dict[str, Any]:
        """Chat with Ollama using conversation format"""
        model = model or self.default_model
        
        if self.use_remote:
            return self._chat_remote(messages, model)
        else:
            # For local CLI, convert to simple prompt
            prompt = self._convert_messages_to_prompt(messages)
            return self._generate_local(prompt, model)
    
    def _chat_remote(self, messages: List[Dict[str, str]], model: str) -> Dict[str, Any]:
        """Chat using remote Ollama API"""
        try:
            payload = {
                'model': model,
                'messages': messages,
                'stream': False
            }
            
            response = requests.post(f"{self.api_base_url}/api/chat", 
                                   json=payload, 
                                   headers=self._get_headers(),
                                   timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'response': data.get('message', {}).get('content', ''),
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'response': '',
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'response': '',
                'error': str(e)
            }
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to simple prompt for CLI"""
        prompt_parts = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n".join(prompt_parts)


# Global instance
ollama_client = OllamaClient()