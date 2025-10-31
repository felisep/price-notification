import re


def clean_number(number):
    # Use regular expression to find all digits
    cleaned_number = re.findall(r'\d+', str(number))
    # Join all found digits into a single string
    cleaned_number = ''.join(cleaned_number)
    # Check if cleaned_number is empty
    if not cleaned_number:
        raise ValueError("No digits found in the input string")
    # Convert to integer and divide by 10 to get the correct price
    return int(cleaned_number) // 10
