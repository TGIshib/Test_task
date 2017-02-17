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


def append_line_to_answer(wiki_url, site_url):
    wiki_url_array.append(wiki_url)
    url_array.append('"' + site_url + '"')


def remove_quotes(url):
    if len(url) == 0 or url == '"' or url == '""':
        return url
    start_index = 0
    if url[0] == '"':
        start_index += 1
    end_index = len(url) - 1
    if url[end_index] != '"':
        end_index += 1
    return url[start_index:end_index]

if len(sys.argv) < 2:  # no input file name
    print('Please enter path to the excel file')
    sys.exit()

file_path = sys.argv[1]

try:
    with open(file_path, newline='') as csv_input:
        wiki_links_reader = csv.reader(csv_input, delimiter=' ', quotechar='|')
        for row in wiki_links_reader:
            if len(row) == 0:
                continue
            wiki_url = remove_quotes(row[0])
            try:
                html_text = io.TextIOWrapper(urllib.request.urlopen(wiki_url), encoding='utf-8').read()
                parser = BeautifulSoup(html_text, "html.parser")
                html_table = parser.find('table', {'class': 'infobox'}).find_all('tr')  # find all rows in the 'infobox' table
                tr_index = get_index_of_href_row(html_table)  # index of the row where site url is located
                for html_row in html_table:
                    if tr_index < 0:
                        append_line_to_answer(wiki_url, 'website url had not found')
                        break
                    tr_index -= 1
                    if tr_index == 0:
                        a_href = html_row.find('td').find('a')  # find <a> tag where link is located
                        href = a_href['href']
                        append_line_to_answer(wiki_url, href)
                        break
            except urllib.request.HTTPError:
                append_line_to_answer(wiki_url, 'HTTPError')
            except urllib.request.URLError:
                append_line_to_answer(wiki_url, 'URLError')
            except:
                 append_line_to_answer(wiki_url, 'something is wrong')

    with open('answer.csv', 'w', newline='') as csv_output:
        links_writer = csv.writer(csv_output, quotechar='|')
        for link, wiki_link in zip(url_array, wiki_url_array):
            links_writer.writerow([wiki_link, link])

except IOError:
    print("Could not read file")
except:
    print('Something is wrong')
