import PyPDF2
import os

class ContextGatherer:
    """
    Gathers context from uploaded files and text input.
    Outlook integration ready but not called yet.
    """
    
    @staticmethod
    def gather_context(previous_mbr_file=None, sa_notes_file=None, additional_text=""):
        context_parts = []
        
        # Read previous MBR notes
        if previous_mbr_file:
            content = ContextGatherer._read_file(previous_mbr_file)
            if content:
                context_parts.append(f"PREVIOUS MBR NOTES:\n{content}")
        
        # Read SA/CSM notes
        if sa_notes_file:
            content = ContextGatherer._read_file(sa_notes_file)
            if content:
                context_parts.append(f"SA/CSM NOTES:\n{content}")
        
        # Add additional text
        if additional_text.strip():
            context_parts.append(f"ADDITIONAL CONTEXT:\n{additional_text}")
        
        # NOTE: Outlook integration ready but not active yet
        # Future: Add email context here
        # emails = outlook_service.search_emails(customer_name)
        
        return "\n\n".join(context_parts) if context_parts else "No additional context provided."
    
    @staticmethod
    def _read_file(filepath):
        ext = os.path.splitext(filepath)[1].lower()
        
        try:
            if ext == '.pdf':
                return ContextGatherer._read_pdf(filepath)
            elif ext == '.txt':
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
        
        return ""
    
    @staticmethod
    def _read_pdf(filepath):
        text = []
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text())
        return '\n'.join(text)
