from flask import Flask, render_template, request, session, redirect, url_for, send_file, jsonify
from werkzeug.utils import secure_filename
import os
from config import Config
from services.presentation_agent import PresentationAgent
import threading

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Progress tracking
progress_data = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Validate required fields
        if 'presentation' not in request.files:
            return render_template('index.html', error='Presentation file is required')
        
        presentation = request.files['presentation']
        customer_name = request.form.get('customer_name', '').strip()
        audience_type = request.form.get('audience_type', '').strip()
        
        if not presentation or presentation.filename == '':
            return render_template('index.html', error='Presentation file is required')
        
        if not customer_name:
            return render_template('index.html', error='Customer name is required')
        
        if not audience_type:
            return render_template('index.html', error='Audience type is required')
        
        if not presentation.filename.endswith('.pptx'):
            return render_template('index.html', error='Only .pptx files are supported')
        
        # Save files
        pptx_filename = secure_filename(presentation.filename)
        pptx_path = os.path.join(app.config['UPLOAD_FOLDER'], pptx_filename)
        presentation.save(pptx_path)
        
        # Handle optional files
        previous_mbr_path = None
        sa_notes_path = None
        
        if 'previous_mbr' in request.files:
            previous_mbr = request.files['previous_mbr']
            if previous_mbr and previous_mbr.filename and allowed_file(previous_mbr.filename):
                filename = secure_filename(previous_mbr.filename)
                previous_mbr_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                previous_mbr.save(previous_mbr_path)
        
        if 'sa_notes' in request.files:
            sa_notes = request.files['sa_notes']
            if sa_notes and sa_notes.filename and allowed_file(sa_notes.filename):
                filename = secure_filename(sa_notes.filename)
                sa_notes_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                sa_notes.save(sa_notes_path)
        
        additional_text = request.form.get('additional_text', '').strip()
        
        # Store in session
        session['pptx_path'] = pptx_path
        session['customer_name'] = customer_name
        session['audience_type'] = audience_type
        session['previous_mbr_path'] = previous_mbr_path
        session['sa_notes_path'] = sa_notes_path
        session['additional_text'] = additional_text
        session['presentation_name'] = pptx_filename
        session['previous_mbr_name'] = previous_mbr.filename if previous_mbr_path else None
        session['sa_notes_name'] = sa_notes.filename if sa_notes_path else None
        
        return redirect(url_for('review'))
    
    return render_template('index.html')

@app.route('/review')
def review():
    return render_template('review.html',
                         customer_name=session.get('customer_name'),
                         audience_type=session.get('audience_type'),
                         presentation_name=session.get('presentation_name'),
                         previous_mbr=session.get('previous_mbr_name'),
                         sa_notes=session.get('sa_notes_name'),
                         additional_text=session.get('additional_text'))

@app.route('/process', methods=['POST'])
def process():
    # Use a unique session identifier
    import uuid
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    
    # Initialize progress
    progress_data[session_id] = {'current': 0, 'total': 0, 'complete': False}
    
    # Copy session data for thread
    session_copy = {
        'pptx_path': session['pptx_path'],
        'customer_name': session['customer_name'],
        'audience_type': session['audience_type'],
        'previous_mbr_path': session.get('previous_mbr_path'),
        'sa_notes_path': session.get('sa_notes_path'),
        'additional_text': session.get('additional_text', '')
    }
    
    # Start processing in background thread
    thread = threading.Thread(target=process_presentation, args=(session_id, session_copy))
    thread.start()
    
    return redirect(url_for('processing'))

def process_presentation(session_id, session_data):
    try:
        agent = PresentationAgent()
        
        def progress_callback(current, total):
            progress_data[session_id] = {'current': current, 'total': total, 'complete': False}
        
        # Process presentation
        slide_analyses, prs = agent.process_presentation(
            session_data['pptx_path'],
            session_data['customer_name'],
            session_data['audience_type'],
            session_data.get('previous_mbr_path'),
            session_data.get('sa_notes_path'),
            session_data.get('additional_text', ''),
            progress_callback=progress_callback
        )
        
        # Generate outputs
        files = agent.generate_outputs(
            slide_analyses,
            prs,
            session_data['customer_name'],
            app.config['OUTPUT_FOLDER']
        )
        
        # Store results in progress_data for retrieval
        progress_data[session_id]['files'] = files
        progress_data[session_id]['slide_analyses'] = slide_analyses
        progress_data[session_id]['complete'] = True
        
    except Exception as e:
        print(f"Processing error: {str(e)}")
        progress_data[session_id]['error'] = str(e)

@app.route('/processing')
def processing():
    return render_template('processing.html')

@app.route('/progress')
def progress():
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({'current': 0, 'total': 1, 'complete': False})
    
    data = progress_data.get(session_id, {'current': 0, 'total': 1, 'complete': False})
    return jsonify(data)

@app.route('/download_page')
def download_page():
    session_id = session.get('session_id')
    
    # Get files from progress_data if available
    if session_id and session_id in progress_data:
        files = progress_data[session_id].get('files')
        slide_analyses = progress_data[session_id].get('slide_analyses')
        if files:
            session['output_files'] = files
        if slide_analyses:
            session['slide_analyses'] = slide_analyses
    
    files = session.get('output_files', {})
    
    # Extract action items for checklist
    action_items = []
    slide_analyses = session.get('slide_analyses', [])
    for analysis in slide_analyses:
        items = analysis.get('action_items', [])
        real_items = [item for item in items if 'none identified' not in item.lower()]
        for item in real_items:
            action_items.append({
                'text': item,
                'slide_num': analysis['slide_index'] + 1
            })
    
    # Store in session for later retrieval
    session['action_items'] = action_items
    
    return render_template('download_direct.html', files=files, action_items=action_items)

@app.route('/generate_followup', methods=['POST'])
def generate_followup():
    from services.bedrock_service import BedrockService
    from datetime import datetime
    
    selected_indices = request.form.getlist('selected_items')
    if not selected_indices:
        return redirect(url_for('download_page'))
    
    # Get action items from session
    action_items = session.get('action_items', [])
    
    # Get selected items
    selected_items = [action_items[int(i)] for i in selected_indices if int(i) < len(action_items)]
    
    if not selected_items:
        return redirect(url_for('download_page'))
    
    customer_name = session.get('customer_name', 'Customer')
    
    # Generate email and guide
    bedrock = BedrockService()
    email_draft = bedrock.generate_followup_email(customer_name, selected_items)
    implementation_guide = bedrock.generate_implementation_guide(customer_name, selected_items)
    
    # Save files
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    email_filename = f"{customer_name}_FollowupEmail_{timestamp}.txt"
    email_path = os.path.join(app.config['OUTPUT_FOLDER'], email_filename)
    with open(email_path, 'w') as f:
        f.write(email_draft)
    
    guide_filename = f"{customer_name}_ImplementationGuide_{timestamp}.md"
    guide_path = os.path.join(app.config['OUTPUT_FOLDER'], guide_filename)
    with open(guide_path, 'w') as f:
        f.write(implementation_guide)
    
    return render_template('followup.html', 
                         email_draft=email_draft,
                         email_file=email_filename,
                         guide_file=guide_filename)

@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
