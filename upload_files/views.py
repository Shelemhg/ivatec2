# upload_files/views.py


import magic
from lxml import etree

from django.shortcuts import render
from django.http import JsonResponse


# =====================
# Global Variables
# =====================

MAX_UPLOAD_COUNT = 10
MAX_NAME_LENGTH = 10



#####################################
### ONLY TO BYPASS CSRF PROTECTION
####################################
from django.views.decorators.csrf import csrf_exempt






def is_pdf_file(file):
    
    try:
        mime = magic.Magic()
        file_type = mime.from_buffer(file.read())
        return file_type.startswith('PDF document')
    
    except Exception as e:
        
        print(f"Error: {e}")
        return False


def is_xml_file(file):
    
    try:
        parser = etree.XMLParser(recover=True)
        etree.fromstring(file.read(), parser)
        return True
    
    except etree.XMLSyntaxError:
        
        return False










#####################################
### ONLY TO BYPASS CSRF PROTECTION
####################################
@csrf_exempt



def validate_files(request):
    
    if request.method == 'POST':
        
        uploaded_files = request.FILES.getlist('uploaded_files[]')
        
        # Separate files into PDF and XML lists
        pdf_files = []
        xml_files = []
        results = []
        
        
        # Variables to store results
        files_attempted_to_upload = None    # int
        long_names = []     # List of Dictionaries: long_names.append({"filename": str, "length": int})
        invalid_formats = []    # List of Dictionaries: long_names.append({"filename": "invalid.doc", "filetype": "DOC"})
        unpaired_files = []    # List
        
        

        # Validate the number of uploaded files
        if len(uploaded_files) > MAX_UPLOAD_COUNT:
            
            return JsonResponse({'message': 'Too many files uploaded. Exceeds limit.'}, status=400)

        
        for file in uploaded_files:
            
            # Determine the file type (PDF or XML) based on its "magic bytes"
            is_pdf = is_pdf_file(file)
            is_xml = is_xml_file(file)


            # Validate file names
            if len(file.name) > MAX_NAME_LENGTH:
                results.append({'file_name': file.name, 'message': 'File name is too long.'})
            else:
                # If it's a valid PDF
                if is_pdf:
                    pdf_files.append(file)
                # If it's a valid XML
                elif is_xml:
                    xml_files.append(file)
                else:
                    results.append({'file_name': file.name, 'message': 'Invalid file type.'})

        # Validate pairs (one PDF and one XML with the same name)
        valid_pairs = []
        for pdf_file in pdf_files:
            xml_file_name = pdf_file.name.replace('.pdf', '.xml')
            if xml_file_name in [xml.name for xml in xml_files]:
                valid_pairs.append({'pdf': pdf_file.name, 'xml': xml_file_name})
            else:
                results.append({'file_name': pdf_file.name, 'message': 'No matching XML file found.'})

        # Return the results
        response_data = {
            'results': results,
            'valid_pairs': valid_pairs,
        }
        return JsonResponse(response_data)
    
    else:
    
        return JsonResponse({'message': 'Invalid request method'}, status=400)