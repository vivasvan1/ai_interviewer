import re


# Function to remove prefixes
def clean_prefix(text):
    # Regular expression to match prefixes like '1.', '2.', or '-' followed by a space
    return re.sub(r'^\d+\.\s*|-', '', text).strip()

# Function to format questions_text to an array
def question_arr_formatter(question_text):
    """
    Splits the input text into an array of questions, removes empty lines,
    and cleans any prefixes from each question.
    """
    text = question_text
    
    #remove unwanted header from the question_text
    index = question_text.find("1. ")
    if (index != -1):
        text = text[index:]
        
    # Split the input text into an array by newline characters
    raw_arr = text.split("\n")
    
    # Remove empty strings from the array
    filtered_list = [item for item in raw_arr if item.strip()]
    
    # Clean prefixes from each item in the filtered list
    cleaned_questions = [clean_prefix(item) for item in filtered_list]
    
    return cleaned_questions


