import boto3
import json

class LLM:
    def __init__(self, model_id):
        self.model_id = model_id
        self.bedrock = boto3.client(service_name="bedrock-runtime")
        
    def invoke(self, question, temperature=0.0, max_tokens=1024):
        body = json.dumps({
            "temperature": temperature,
            "max_tokens": max_tokens,
            "prompt": f"<s>[INST] {question}  [/INST]",
            "stop": ["</s>"]
        })
        response = self.bedrock.invoke_model(
            body=body, 
            modelId=self.model_id)

        response_body = json.loads(response.get("body").read())
        return response_body['outputs'][0]['text']
    