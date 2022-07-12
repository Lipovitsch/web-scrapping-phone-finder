'''
[PL]
Program odnajdujący główny numer kontaktowy na podanej stronie internetowej firmy.
Założenie:
    - główny numer telefonu znajduje się na stronie głównej lub w podstronie 'kontakt'
      i jest to pierwszy znaleziony numer (stwierdzenie na podstawie obserwacji różnych stron)
Działanie programu:
    - skanowanie strony głównej w celu znalezienia numeru
    - w przypadku braku numeru na stronie głównej, skanowanie w poszukiwaniu linków
      do podstrony o nazwie: ['kontakt', 'contact', 'company'] i skanowanie tej strony
Ograniczenia:
    - jeśli numer jest umieszczony głębiej w strukturze strony, nie zostanie znaleziony
    - jeśli strona jest w innym języku niż polski, niemiecki lub angielski, podstrona kontaktu
      nie zostanie znaleziona
    - numer telefonu, który nie jest w formacie US, PL, DE lub nie zaczyna się od '+' nie zostanie wykryty
Przykład użycia:
    python scrape.py https://www.bosch.com/
    Zwraca: +4971140040990
    
[EN]
Program for finding the main contact number on a given company website.
Assumption:
    - the main phone number can be found on the main page or in the 'contact' subpage
      and it is the first number found (statement based on observation of various websites)
Program operation:
    - scanning the home page to find the number
    - if there is no number on the home page, scan for links
      to the subpage named: ['contact', 'contact', 'company'] and scan this page
Limitations:
    - if the number is placed deeper in the page structure, it will not be found
    - if the website is in a language other than Polish, German or English, contact subpage
      will not be found
    - phone number which is not in format US, PL, DE or it starts not with '+' will not be detect
Example of usage:
    python scrape.py https://www.bosch.com/
    Output: +4971140040990
'''

import requests
import sys

from bs4 import BeautifulSoup
from phonenumbers import PhoneNumberMatcher


def search_phone_number(soup: BeautifulSoup, url: str):
    '''Function searches for phone number using specific html tags
    and region list for phone detection'''
    
    tag_name_list = ['p', 'a', 'span', 'div']
    region_list = [None, 'PL', 'US', 'DE']
    numbers = []
    tags = soup.find_all(tag_name_list)
    
    for region in region_list:
        for tag in tags:
            # region 'DE' detects numbers that are not real phone number
            # so it should be considered only with page that ends with .de
            if region == 'DE' and '.de' not in url:
                continue
            
            phone = PhoneNumberMatcher(tag.text, region)
            try:
                number = phone.next()
                numbers.append(number.raw_string)
                break
            except:
                pass
            
        if numbers != []:
            break
        
    return numbers


def main():
    url = sys.argv[1]
    html_content = requests.get(url, timeout=5).text
    soup = BeautifulSoup(html_content, 'lxml')
    
    numbers = search_phone_number(soup, url)
    if numbers == []:
        contact_name_list = ['kontakt', 'contact', 'company']
        href_contact = ''
        all_links = soup.find_all('a')
        
        for contact in contact_name_list:
            for link in all_links:
            
                if contact in link.text.lower().strip():
                    href_contact = link.get('href')
                    break
            
            if href_contact != '':
                if url in href_contact:
                    url = href_contact
                elif url.endswith('/'):
                    url = url[:-1] + href_contact
                else:
                    url += href_contact
                html_content = requests.get(url, timeout=5).text
                soup = BeautifulSoup(html_content, 'lxml')
                numbers = search_phone_number(soup, url)
                break
        
    if numbers != []:
        print(numbers[0])
    else:
        print("Number cannot be found")
        
        
if __name__ == '__main__':
    main()
