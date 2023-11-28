import PyPDF2

def get_pdf_reading_time(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)

        total_text = ''
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            total_text += page.extract_text()

        # Calculate reading time based on the extracted text
        words = total_text.split()
        word_count = len(words)
        average_wpm = 50  # Average words per minute for reading
        reading_time = word_count / average_wpm

        return round(reading_time*60)



def format_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    if hours > 0:
        return f'{hours}hr {minutes}min {remaining_seconds}s'
    elif minutes > 0:
        return f'{minutes}min {remaining_seconds}s'
    else:
        return f'{seconds}s'

def format_duration_minutes(minutes):
    if minutes > 60:
        remaining_minutes = minutes % 60
        hour = minutes // 60
        return f'{hour}hr {remaining_minutes}min'
    else:
        return f'{minutes}min'