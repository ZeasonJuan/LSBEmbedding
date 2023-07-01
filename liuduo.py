# import pymysql
# import requests
# from bs4 import BeautifulSoup
# db = pymysql.Connect(host="ruanzaisheng.com", user="root", password="UU1003youyou+-", database="MovieHub", charset='utf8')
# def extract_image_urls(url):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
#     }
#
#     session = requests.Session()
#
#
#     response = requests.get(url, headers=headers)
#
#     soup = BeautifulSoup(response.content, "html.parser")
#     graph_mode = soup.find("img", class_='profile lazyload')
#     if graph_mode is None:
#         return None
#     image_url = graph_mode.get("data-srcset").split(" 1x")[0][1:]
#     return image_url
#
#
# base_url = 'https://www.themoviedb.org/person/'
# image_base = "https://www.themoviedb.org/"
#
# cur = db.cursor()
# select_statement = "select credit_id from credit"
# cur.execute(select_statement)
# tmdb_id_list = list(cur.fetchall())
# for i in range(len(tmdb_id_list)):
#     tmdb_id_list[i] = tmdb_id_list[i][0]
#
# insert_statement = "update credit set credit_url = %s where credit_id = %s"
# for i in range(116165, 120000):
#     url = base_url + str(tmdb_id_list[i])
#     else_url = extract_image_urls(url)
#     if else_url is None:
#         print(i, "Fuck")
#         continue
#     poster_url = image_base + str(else_url)
#     data = [poster_url, tmdb_id_list[i]]
#     cur.execute(insert_statement, data)
#     db.commit()
#     print(i)
#
# db.close()
#     for img_tag in soup.find_all("img"):
#         src = img_tag.get("class")
#         if src:
#             image_urls.append(src)
#
#     return image_urls
#
# if __name__ == "__main__":
#     url = "https://example.com"  # 替换为您要获取图片URL的网站地址
#     image_urls = extract_image_urls(url)
#     for img_url in image_urls:
#         print(img_url)

a = [3, 5, 7, 2]
print([0] * 6)