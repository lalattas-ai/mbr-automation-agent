from services.bedrock_service import BedrockService
from services.pptx_service import PPTXService
from services.context_gatherer import ContextGatherer

class PresentationAgent:
    def __init__(self):
        self.bedrock = BedrockService()
        self.pptx = PPTXService()
    
    def process_presentation(self, pptx_path, customer_name, audience_type, 
                           previous_mbr=None, sa_notes=None, additional_text="",
                           progress_callback=None):
        # Gather context
        context = ContextGatherer.gather_context(previous_mbr, sa_notes, additional_text)
        
        # Extract slides
        slides_content, prs = self.pptx.extract_slides(pptx_path)
        total_slides = len(slides_content)
        
        # Analyze each slide
        slide_analyses = []
        for idx, slide in enumerate(slides_content):
            if progress_callback:
                progress_callback(idx + 1, total_slides)
            
            analysis = self.bedrock.analyze_slide(
                slide['content'],
                customer_name,
                audience_type,
                context
            )
            
            slide_analyses.append({
                'slide_index': idx,
                'talking_points': analysis['talking_points'],
                'action_items': analysis['action_items'],
                'questions': analysis['questions']
            })
        
        return slide_analyses, prs
    
    def generate_outputs(self, slide_analyses, prs, customer_name, output_folder):
        # Add talking points to presentation
        prs = self.pptx.add_talking_points(prs, slide_analyses)
        pptx_file = self.pptx.save_presentation(prs, customer_name, output_folder)
        
        # Generate action items
        action_file = self.pptx.save_action_items(slide_analyses, customer_name, output_folder)
        
        # Generate Q&A
        qa_file = self.pptx.save_qa(slide_analyses, customer_name, output_folder)
        
        return {
            'presentation': pptx_file,
            'action_items': action_file,
            'qa': qa_file
        }
