import boto3
import json
import os

class BedrockService:
    def __init__(self):
        # Use credentials from environment variables
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-3-5-sonnet-20241022-v2:0')
    
    def generate_followup_email(self, customer_name, selected_items):
        items_text = "\n".join([f"- {item['text']} (Slide {item['slide_num']})" for item in selected_items])
        
        prompt = f"""Generate a professional follow-up email for {customer_name} after an MBR presentation.

The customer agreed to the following action items:
{items_text}

Create a concise, professional email that:
1. Thanks them for the meeting
2. Summarizes the agreed action items
3. Proposes next steps and timeline
4. Offers continued support

Keep it brief and actionable. Use a professional but friendly tone."""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1500,
            "messages": [{"role": "user", "content": prompt}]
        })
        
        response = self.client.invoke_model(modelId=self.model_id, body=body)
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    def generate_implementation_guide(self, customer_name, selected_items):
        items_text = "\n".join([f"- {item['text']} (Slide {item['slide_num']})" for item in selected_items])
        
        prompt = f"""Create a detailed implementation guide for {customer_name}'s TAM based on these agreed action items:

{items_text}

For each action item, provide:
1. Detailed implementation steps
2. AWS services and resources needed
3. Estimated timeline
4. Prerequisites and dependencies
5. Success criteria
6. Relevant AWS documentation links

Format as a structured markdown document."""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "messages": [{"role": "user", "content": prompt}]
        })
        
        response = self.client.invoke_model(modelId=self.model_id, body=body)
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    def analyze_slide(self, slide_content, customer_name, audience_type, context):
        prompt = f"""You are an expert AWS Technical Account Manager preparing for an MBR with {customer_name} ({audience_type} audience).

SLIDE CONTENT:
{slide_content}

CUSTOMER CONTEXT:
{context}

Generate DETAILED, SPECIFIC talking points for this slide. Your talking points must:
- Be actionable and specific (not generic statements)
- Reference actual data, metrics, or elements from the slide
- Connect to AWS services, best practices, or customer outcomes
- Be ready to speak for 2-3 minutes per point
- Include specific numbers, percentages, or trends if present in the slide

For slides with tables: analyze the data and create talking points about trends, comparisons, or insights.
For slides with charts: describe what the visual shows and its business implications.
For slides with minimal content: use the title and context to infer the likely discussion points.

Provide analysis in this format:

TALKING POINTS:
1. [Detailed, specific talking point with context]
2. [Detailed, specific talking point with context]
3. [Detailed, specific talking point with context]
4. [Optional: Additional detailed point]
5. [Optional: Additional detailed point]

ACTION ITEMS:
- [Priority: HIGH/MEDIUM/LOW] Specific action item with owner and timeline
(If none applicable, write "None identified for this slide.")

ANTICIPATED QUESTIONS:
Q: [Specific technical or business question the customer might ask]
A: [Detailed answer with AWS documentation reference: https://docs.aws.amazon.com/...]

Q: [Another specific question]
A: [Detailed answer with AWS documentation reference: https://docs.aws.amazon.com/...]"""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 3000,
            "messages": [{"role": "user", "content": prompt}]
        })
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        return self._parse_response(response_body['content'][0]['text'])
    
    def _parse_response(self, text):
        talking_points = []
        action_items = []
        questions = []
        
        lines = text.split('\n')
        current_section = None
        current_item = []
        
        for line in lines:
            line = line.strip()
            
            # Detect section headers
            if 'TALKING POINTS:' in line:
                current_section = 'talking'
                continue
            elif 'ACTION ITEMS:' in line or 'ACTION ITEM:' in line:
                current_section = 'actions'
                continue
            elif 'ANTICIPATED QUESTIONS:' in line:
                current_section = 'questions'
                continue
            
            # Skip empty lines
            if not line:
                if current_item:
                    # Save accumulated item
                    item_text = ' '.join(current_item)
                    if current_section == 'talking':
                        talking_points.append(item_text)
                    elif current_section == 'actions':
                        action_items.append(item_text)
                    elif current_section == 'questions':
                        questions.append(item_text)
                    current_item = []
                continue
            
            # Accumulate lines for current item
            if current_section:
                current_item.append(line)
        
        # Don't forget last item
        if current_item:
            item_text = ' '.join(current_item)
            if current_section == 'talking':
                talking_points.append(item_text)
            elif current_section == 'actions':
                action_items.append(item_text)
            elif current_section == 'questions':
                questions.append(item_text)
        
        return {
            'talking_points': talking_points,
            'action_items': action_items,
            'questions': questions
        }
