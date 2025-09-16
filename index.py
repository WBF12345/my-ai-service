from openai import OpenAI
from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# 从环境变量获取API密钥
api_key = os.environ.get('DEEPSEEK_API_KEY', '您的API密钥')

class AIIntegrationSystem:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        self.setup_services()
    
    def setup_services(self):
        self.services = {
            "文案生成": self.generate_content,
            "客服回复": self.customer_service,
            "代码助手": self.code_assistant
        }
    
    def generate_content(self, params):
        prompt = f"请为{params.get('industry', '某行业')}创作{params.get('num', 5)}条{params.get('style', '营销')}文案。要求：{params.get('requirements', '吸引人')}"
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=500
        )
        return response.choices[0].message.content
    
    def customer_service(self, params):
        conversation = [
            {"role": "system", "content": "你是专业客服代表"},
            {"role": "user", "content": params.get('question', '')}
        ]
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=conversation,
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content
    
    def code_assistant(self, params):
        prompt = f"请用{params.get('language', 'Python')}编写代码：{params.get('task', '')}要求：{params.get('requirements', '有注释')}"
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=800
        )
        return response.choices[0].message.content

ai_system = AIIntegrationSystem(api_key)

@app.route('/api/services', methods=['GET'])
def list_services():
    return jsonify({
        "services": list(ai_system.services.keys()),
        "status": "active",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/ai-service', methods=['POST'])
def ai_service():
    try:
        data = request.json
        service_type = data.get('service_type', '')
        params = data.get('params', {})
        
        if service_type not in ai_system.services:
            return jsonify({"error": "不支持的服务类型"})
        
        result = ai_system.services[service_type](params)
        return jsonify({
            "status": "success",
            "service": service_type,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)