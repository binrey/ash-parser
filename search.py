from bs4 import BeautifulSoup
import requests as req
import argparse
import yaml
import io


def clean_db(pdict):
    keys = list(pdict.keys())
    for key in keys:
        if type(pdict[key]) is not list:
            continue
        vlist = pdict[key].copy()
        good_ids = []
        for i, v in enumerate(vlist):
            if len(v.split()) == 2:
                good_ids.append(i)
        if len(good_ids):
            pdict[key] = [pdict[key][i].lower() for i in good_ids]
        else:
            pdict.pop(key)
    return pdict


def save_data(obj):
    with io.open('data.yaml', 'w') as outfile:
        yaml.dump(obj, outfile, default_flow_style=False, allow_unicode=True)


def load_data():
    with open("data.yaml", 'r', encoding="utf8") as stream:
        return yaml.load(stream, Loader=yaml.FullLoader)


def read_page(pdict, url):
    html_resp = req.get(url)
    soup = BeautifulSoup(html_resp.text, 'lxml')
    people = soup.findAll("a", class_="mem_link")

    n_updated, n_new = 0, 0
    for i, p in enumerate(people):
        key = str(p.attrs["href"])
        name = str(p.contents[0]).lower()
        if len(name.split()) == 2:
            fname, sname = name.split()
            name_v1 = fname + " " + sname
            name_v2 = sname + " " + fname
            if key not in pdict:
                pdict[key] = [name_v1, name_v2]
                n_new += 1
            else:
                for name in [name_v1, name_v2]:
                    if name not in pdict[key]:
                        pdict[key] += [name]
                        n_updated += 1

    result = False
    if n_new + n_updated:
        print("{}: new users {:3}, updated users {:3}".format(url, n_new, n_updated))
        result = True

    return pdict, result


def update_data_base(nposts=50):
    pdict = load_data()
    #pdict = clean_db(pdict)

    start_num = pdict["last_post"]
    print("Обновление базы данных...")
    print("Текущая версия базы имеет {} пользователей, старт поиска с {} поста...".format(len(pdict) - 1, start_num + 1))
    for num in range(nposts):
        post_num = start_num + num + 1
        url = "https://vk.com/alphadance_ru?w=wall-51593777_{}".format(post_num)
        pdict, updated = read_page(pdict, url)
        if updated:
            pdict["last_post"] = post_num
    if pdict["last_post"] != start_num:
        save_data(pdict)
        print("Обновленная база сохранена, теперь имеет {} пользователей".format(len(pdict) - 1))
    else:
        print("Обновлений нет, база уже актуальна! :)")


def main():
    pdict = load_data()
    parser = argparse.ArgumentParser()
    parser.add_argument("--url")
    args = vars(parser.parse_args())
    args["url"] = "https://vk.com/alphadance_ru"
    requiredHtml = args["url"]

    read_page(pdict, requiredHtml)
    save_data(pdict)



if __name__ == "__main__":
    update_data_base(20)
