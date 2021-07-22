from bs4 import BeautifulSoup
import requests as req
import argparse
from search import load_data, update_data_base
from functools import partial


def main():
    def find_id(dbase, name2find):
        name2find = name2find.lower()
        result = None
        for k, v in dbase.items():
            if result is not None:
                break
            if k != "last_post":
                for name in v:
                    if name == name2find:
                        result = k
                        break
        return "?" if result is None else result[1:]

    parser = argparse.ArgumentParser()
    #sub1 = parser.add_subparsers(title="parse", dest="pik")
    #sub1.add_parser("p")
    parser.add_argument("--url", required=False, help="html-адресс страницы конкурса на форуме АСХ")
    #sub = parser.add_subparsers(title="upd_base", dest="puk")
    #sub.add_parser("ddde")
    parser.add_argument("--upd", const="y", nargs="?", required=False, help="обновить базу данных")
    args = vars(parser.parse_args())

    if args["upd"] == "y":
        update_data_base(50)

    find_id = partial(find_id, dbase=load_data())
    requiredHtml = args["url"]

    while requiredHtml is None:
        requiredHtml = input("html-адресс страницы конкурса на форуме АСХ:")

    dnd_finder = "Участников"
    classic_finder = "Участвовало"
    html_resp = req.get(requiredHtml)
    soup = BeautifulSoup(html_resp.text, 'lxml')

    res = []
    new_span = False
    final = False
    blocks = {}
    block_name = ""
    for tag in soup.findAll():
        if tag.name == "span":
            for b in tag.find_all("b"):
                txt = str(b.next)
                if len(txt) > 0 and (dnd_finder in txt or classic_finder in txt):
                    block_name = "🌟 ФИНАЛ " + txt.split(".")[0].split("(")[0]
                    if block_name not in blocks:
                        blocks.update({block_name: []})
                    new_span = True
        if not new_span:
            continue
        if tag.name == "b":
            if str(tag.next) == "ФИНАЛ":
                final = True
            else:
                final = False
        if final and tag.name == "br":
            br = str(tag.next)
            if len(br) > 10:
                if "alphadance" in br.lower():
                    br = br.split("-")
                    if "dnd" in block_name.lower() or "jnj" in block_name.lower():
                        sname, fname, *_ = br[2].split("(")[0].split()
                        vkid = find_id(name2find=sname + " " + fname)
                        blocks[block_name].append(br[0] + " - [{}|{} {}]".format(vkid, fname, sname))
                    else:
                        sname1, fname1, *_ = br[2].split("(")[0].split()
                        vkid1 = find_id(name2find=sname1 + " " + fname1)
                        sname2, fname2, *_ = br[3].split("(")[0].split()
                        vkid2 = find_id(name2find=sname2 + " " + fname2)
                        blocks[block_name].append(br[0] + " - [{}|{} {}] и [{}|{} {}]".format(vkid1, fname1, sname1, vkid2, fname2, sname2))


    for k, v in blocks.items():
        if len(v) > 0:
            print("\n" + k)
            v.sort()
            for line in v:
                print(line)


if __name__ == "__main__":
    main()
