from bs4 import BeautifulSoup
import requests
import json
import re
from scidownl import scihub_download
from scidownl import config

def google_scholar_pagination(query):
    data = []
    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36'
    }
    params = {
        'q': query,
        'hl': 'en',
        'start': 0
    }

    while True:
        html = requests.get('https://scholar.google.com/scholar', headers=headers, params=params).text
        soup = BeautifulSoup(html, 'html.parser')
        print(f'extrecting {params["start"] + 10} page...')
        # Container where all needed data is located
        for result in soup.select('.gs_r.gs_or.gs_scl'):
            try:
                title = result.select_one('.gs_rt').text
                title_link = result.select_one('.gs_rt a')['href']
                publication_info = result.select_one('.gs_a').text
                # snippet = result.select_one('.gs_rs').text
                cited_by_link = result.select_one('#gs_res_ccl_mid .gs_nph+ a')['href']
                data.append({
                    'page_num': params['start'] + 10,  # 0 -> 1 page. 70 in the output = 7th page
                    'title': title,
                    'title_link': title_link,
                    'publication_info': publication_info,
                    #     'snippet': snippet,
                    'cited_by_link': f'https://scholar.google.com{cited_by_link}',
                })
                # if title_link not in data:
                #     data.append(title_link)
            except:
                continue
        print(len(data))

        if params['start'] >= 60:
            break
        if soup.select('.gs_ico_nav_next'):
            params['start'] += 10
        else:
            break
    # print(json.dumps(data, indent=2, ensure_ascii=False))
    return data

API_KEY = 'YOUR_API_KEY'



def write_to_file(data):
    with open('./tempArticles/links.txt', 'w') as filehandle:
        for listitem in data:
            filehandle.write(f'{listitem}\n')


def read_from_file():
    places = []
    with open('./tempArticles/links.txt', 'r') as filehandle:
        for line in filehandle:
            curr_place = line[:-1]
            places.append(curr_place)
    return places


def doaj_request(query):
    page_number = 1
    data = []
    response = requests.get(f"https://doaj.org/api/search/articles/{query}?page=" +
                            str(page_number) + "&pageSize=10")
    my_json = response.content.decode('utf8')
    json_data = json.loads("[" + my_json.rstrip().replace("\n", ",") + "]")
    try:
        for l in json_data[0]["results"]:
            title = l["bibjson"]["title"]
            url = l["bibjson"]["link"][0]["url"]
            publisher = l["bibjson"]["journal"]["publisher"]
            year = l["bibjson"]["year"]
            data.append({
                'title': title,
                'link': url,
                'pub_year': year,
                'publisher': publisher
            })
    except:
        pass
    return data


def image_of_articles(results):

    for result in results:
        result['pic_links'] = []
        url = result["link"]
        response = ''
        try:
            response = requests.get(
                url='https://proxy.scrapeops.io/v1/',
                params={
                    'api_key': '29c53436-dde6-417b-942d-ac9d9736644b',
                    'url': url,
                    'render_js': 'true',
                    'residential': 'true',
                    'country': 'us'
                },
            )
            url = response.url
        except:
            pass
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, features="html.parser")
            images = soup.find_all('img')
            for img in images:
                for attr in ['src', 'data-src', 'data-original', 'data-srcset', 'data-lazy', 'data-large']:
                    img_src = img.get(attr)
                    if img_src:
                        img_url = requests.compat.urljoin(url, img_src)
                        result['pic_links'].append(img_url)
                        break


            # for img_url in range(len(image_urls)):
            #     filename = re.search(r'/([\w_-]+[.](jpg|gif|png|jpeg))$', image_urls[img_url])
            #     if not filename:
            #         print("Regex didn't match with the url: {}".format(url))
            #         continue
            #     filename = filename.group(1).split('.')
            #     with open(f'./tempArticles/{counter}_{filename[0]}.{filename[1]}', 'wb') as f:
            #         response = requests.get(image_urls[img_url])
            #         f.write(response.content)
            #         counter += 1

    return results


def link_extractor(results):
    links = []
    for result in results:
        links.append(result['link'])
    return links


def download_articles(results):
    counter = 0
    links = link_extractor(results)
    for i in range(len(links)):
        scihub_download(links[i], out='./tempArticles/' + str(i) + '.pdf')
        counter += 1


if __name__ == '__main__':
    # data = read_from_file()
    # data = google_scholar_pagination(data,'silver nanoparticles')
    # print(data)
    # write_to_file(data)
    # for i in range(len(data)):
    #     scihub_download(data[i], out='./articles/' + str(i) + '.pdf')
    data = doaj_request('silver nanoparticles')
    print(data)
