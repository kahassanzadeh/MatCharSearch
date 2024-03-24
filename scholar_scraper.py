from bs4 import BeautifulSoup
import requests
import json


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


def write_to_file(data):
    with open('links.txt', 'w') as filehandle:
        for listitem in data:
            filehandle.write(f'{listitem}\n')


def read_from_file():
    places = []
    with open('links.txt', 'r') as filehandle:
        for line in filehandle:
            curr_place = line[:-1]
            places.append(curr_place)
    return places


def doaj_request(query):
    page_number = 1
    data = []
    response = requests.get(f"https://doaj.org/api/search/articles/{query}?page=" +
                            str(page_number) + "&pageSize=100")
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


if __name__ == '__main__':
    # data = read_from_file()
    # data = google_scholar_pagination(data,'silver nanoparticles')
    # print(data)
    # write_to_file(data)
    # for i in range(len(data)):
    #     scihub_download(data[i], out='./articles/' + str(i) + '.pdf')
    data = doaj_request('silver nanoparticles')
    print(data)

