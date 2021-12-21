import math
from backend.models import *
def create_pagination(total_records,current_page):
    page_length = 20
    total_pages = int(total_records) / int(page_length)
    if total_records % 20 != 0:
        total_pages += 1
    if total_pages == 0:
        total_pages = 1
    total_pages = math.floor(total_pages)
    return {'total_records':total_records,'total_pages':total_pages,'current_page':current_page,'page_length':page_length}

