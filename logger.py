# Function to log run time information
from datetime import datetime

def log_info(text: str, flush = False):
    log = f'({datetime.now().time().strftime("%H:%M")}) ||| {text}'
    if flush:
        print(log)
    else:
        return(log)