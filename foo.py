from tempered import Tempered
from tempered.src.utils.soup import HtmlSoup

tempered = Tempered()
tempered.add_from_file("./foo.html")
html = tempered.render("foo.html", fade=True)

print(HtmlSoup(html).decode(pretty_print=True))
