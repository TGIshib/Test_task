import csv
import sys
import urllib.request
import io
from bs4 import BeautifulSoup

wiki_url_array = []
url_array = []


def get_index_of_href_row(html_table):
    index = 0
    for html_row in html_table:
        row_header = html_row.find('th')
        index += 1
        if row_header is None:
            continue
        else:
            if row_header.getText() == 'Website':
                return index
    return -1


def find_href(html_row):
    a_href = html_row.find('td').find('a')  # find <a> tag where link is located
    ref = a_href['href']
    ref_start = 0
    for char in ref:  # find preceding unwanted characters
        if (char >= 'a' and char <= 'z') or (char >= 'A' and char <= 'Z'):
            break
        else:
            ref_start += 1
    return ref[ref_start:]


def append_line_to_answer(wiki_url, site_url):
    wiki_url_array.append('"' + wiki_url + '"')
    url_array.append(site_url)


if len(sys.argv) < 2:  # no input file name
    print('Enter path to the excel file')
    sys.exit()
 
file_path = sys.argv[1]

try:
    with open(file_path, newline='') as csv_input:
        wiki_links_reader = csv.reader(csv_input, delimiter=' ', quotechar='|')
        for row in wiki_links_reader:
            if len(row) == 0:
                continue
            wiki_url = row[0]
            html_text = io.TextIOWrapper(urllib.request.urlopen(wiki_url), encoding='utf-8').read()
            parser = BeautifulSoup(html_text, "html.parser")
            html_table = parser.find('table', {'class': 'infobox'}).find_all('tr')  # find all rows in the 'infobox' table
            tr_index = get_index_of_href_row(html_table)  # index of the row where site url is located
            for html_row in html_table:
                if tr_index < 0:
                    append_line_to_answer(wiki_url, 'had not found')
                    continue
                tr_index -= 1
                if tr_index == 0:
                    href = find_href(html_row)
                    append_line_to_answer(wiki_url, href)
                    break
 
    with open('answer.csv', 'w', newline='') as csv_output:
        links_writer = csv.writer(csv_output, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for wiki_link, link in zip(url_array, wiki_url_array):
            links_writer.writerow(wiki_link + ',' + link)

except IOError:
    print("Could not read file: " + file_path)
except urllib.request.HTTPError as e1:
    print(e1.code())
except urllib.request.URLError as e2:
    print(e2.code())
except:
    print('Error')
