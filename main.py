import requests
import re

class Book:
    def __init__(self, title = None, authors = None, languages = None, original_languages = None, date = None, publisher = None, description = None, framing = None, topics = None, price = None):
        self.title = title
        self.authors = authors
        self.languages = languages
        self.original_languages = original_languages
        self.date = date
        self.publisher = publisher
        self.description = description
        self.framing = framing
        self.topics = topics
        self.price = price
    
    def __repr__(self):
        return self.title if self.title is not None else ""
    
    def __str__(self):
        return self.title if self.title is not None else ""
    
    def set_val(self, t, val):
        if t == "Título:":
            self.title = val
        elif t == "Autor/es:":
            self.authors = val
        elif t == "Lengua de publicación:":
            self.languages = val
        elif t == "Lengua/s de traducción:":
            self.original_languages = val
        elif t == "Fecha Edición:":
            self.date = val
        elif t == "Publicación:":
            self.publisher = val
        elif t == "Descripción:":
            self.description = val
        elif t == "Encuadernación:":
            self.framing = val
        elif t == "Materia/s:":
            self.topics = val
        elif t == "Precio:":
            self.price = val

if __name__ == "__main__":
    isbn = input("Enter isbn: ")

    cookie_raw = requests.get('http://www.mcu.es/webISBN/tituloSimpleFilter.do?cache=init&prev_layout=busquedaisbn&layout=busquedaisbn&language=es')
    cookie = cookie_raw.headers['Set-Cookie']
    cookie = cookie.split(';')[0]

    headers = {'Cookie': cookie}
    data = [('params.cisbnExt', isbn),('action', 'Buscar')]
    books_raw = requests.post("http://www.mcu.es/webISBN/tituloSimpleDispatch.do", headers=headers, data=data)
    web = books_raw.text
    # print(web)
    link_match = re.search("/webISBN/tituloDetalle\.do[^\"]+", web)

    if link_match is not None:
        link = 'http://www.mcu.es' + link_match.group(0)
        link = link.replace('&amp;', '&')
        # print(link)

        details_raw = requests.get(link, headers=headers)

        import xml.etree.ElementTree as ET
        raw_match = re.search("<table.*</table>", details_raw.text, re.DOTALL)
        if raw_match is not None:
            raw = raw_match.group(0)
            # print(raw)
            root = ET.fromstring(raw)

            rows = root.findall('tr')
            book = Book()
            for row in rows:
                th = row.find("./th")
                td = row.find("./td")
                detail = th.text
                if detail in ["Fecha Edición:", "Descripción:", "Encuadernación:", "Precio:"]:
                    value = td.text
                    if detail == "Precio:":
                        value = float(value.replace(' Euros', ''))
                elif detail in ["Título:", "Lengua de publicación:"]:
                    value = td[0].text
                elif detail in ["Publicación:"]:
                    value = td[0][0].text
                else:
                    value = []
                    for span in td:
                        value.append(span.text.replace("\n", '').replace("\t", ''))
                book.set_val(detail, value)
            print(book)
            print(book.__dict__)
    else:
        print("Not found")