# upload_files/views.py

from django.shortcuts import render
from django.http import JsonResponse
import magic
from lxml import etree


# =====================
# Global Variables
# =====================
MAX_UPLOAD_COUNT = 10
MAX_NAME_LENGTH = 50




def is_pdf_file(file):
    try:
        mime = magic.Magic()
        file_type = mime.from_buffer(file.read(1024))  # Read only a portion of the file to determine its type
        return file_type.startswith('PDF document')
    except Exception as e:
        print(f"Error: {e}")
        return False


def is_xml_file(uploaded_file):
    try:
        xml_parser = etree.XMLParser(recover=True)
        etree.fromstring(uploaded_file.read(), parser=xml_parser)
        return True
    except Exception as e:
        print(f"XML parsing error: {e}")
        return False






#####################################
### ONLY TO BYPASS CSRF PROTECTION
####################################
from django.views.decorators.csrf import csrf_exempt
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

        
        schema = "./sat.gob.mx_sitio_internet_cfd_4_cfdv40.xsd"
        
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