#!/usr/bin/env python
# coding: utf-8

# Initialize
font_file   = "font/MiloTE.ttf"
fontI_file  = "font/MiloTE-inclined.ttf"
font_name   = "MiloTE"
fontI_name  = "MiloTE-I"

user_agent  = "Mozilla/5.0"

import sys, getopt, re, urllib.request, json
from datetime import datetime
import fpdf

# getopt
def usage(name):
    print("""Usage: %s [OPTIONS]
The program converts articles on the Economist to PDF.
It reads URLs from <stdin> in format "<URL>\\n<URL>\\n<URL>\\n..."
Options: 
    -d, --dir=          Local directory to store output file
    -p, --http-proxy=   HTTP proxy to fetch article
    -t, --text-only     Output text-only PDF
        --url-prefix=   URL prefix to access output file
    -v, --verbose       Print user-friendly message
    -q, --quiet         Redirect <stdout>
    -h, --help          Show help message
""" % (name), end="")

stdin = sys.stdin.read()
argv = sys.argv
proxy_handler = None
base_dir = ""
text_only = False
url_prefix = ""
verbosity = 0
try:
    opts, args = getopt.getopt(argv[1:], \
            "d:p:tvqh", ["dir=","http-proxy=", "text-only", "url-prefix=", "verbose", "quiet", "help"])
except getopt.GetoptError as err:
    print(err)
    usage(argv[0])
    exit()
for opt, arg in opts:
    if opt in ("-h", "--help"):
        usage(argv[0])
        sys.exit(0)
    elif opt in ("-d", "--dir"):
        base_dir = arg if arg.endswith('/') else (arg + '/')
    elif opt in ("-p", "--http-proxy"):
        proxy_handler = urllib.request.ProxyHandler({"http": arg, "https": arg})
    elif opt in ("-t", "--text-only"):
        text_only = True
    elif opt in ("--url-prefix"):
        url_prefix = arg if arg.endswith('/') else (arg + '/')
    elif opt in ("-v", "--verbose"):
        verbosity = 1
    elif opt in ("-q", "--quiet"):
        verbosity = -1

# install proxy
if proxy_handler:
    opener = urllib.request.build_opener(proxy_handler)
else:
    opener = urllib.request.build_opener()
opener.addheaders = [('User-Agent', user_agent)]
urllib.request.install_opener(opener)

# fetch html & generate PDF
urlArr = stdin.splitlines()

def main(url):

    regex = r"^https:\/\/www\.economist\.com\/(.*)\/(\d{4})\/(\d{2})\/(\d{2})\/(.*?)(?=\?|\Z)"
    pattern = re.compile(regex)
    if not pattern.fullmatch(url):
        return ""
    cat_dir = pattern.sub("\\1/", url)
    filename = pattern.sub("\\5_\\2-\\3-\\4.pdf", url)
    Path(base_dir + cat_dir).mkdir(parents=True, exist_ok=True)

    req = urllib.request.Request(url)
    req.add_header('User-agent', user_agent)
    response = urllib.request.urlopen(req)
    response.readline()
    b = response.readline()
    data = json.loads(b.decode())
    body = data['articleBody'].split('\n')
    urllib.request.urlretrieve(data['thumbnailUrl'], "/tmp/thumbnail.png")

    headline_ascii = data['headline'].encode("ascii", errors="ignore").decode() # Some Unicode characters cannot be stored in PDF's metadata

    html = "<h1>%s</h1>" % (data["headline"],)
    html += "<font face=\"%s\" size=16><p line-height=2>%s</p></font>" % (fontI_name, data["description"])
    if not text_only:
        html += "<p align=R><font color=#0000ff><u><a href=\"%s\">Webpage</a></u></font></p>" % (data["url"],)
        html += "<img src=\"/tmp/thumbnail.png\" width=538>"    # pixel width of an A4 page
    for line in body:
        html += "<p line-height=1.5>%s</p>" % (line,)
        if not line:
            continue
        if (line[-1] == '■'):
            break

    # generate PDF by html
    pdf = fpdf.FPDF()
    pdf.add_font(font_name,'',font_file)
    pdf.add_font(fontI_name,'',fontI_file)
    pdf.set_font(font_name)
    pdf.set_title(headline_ascii)
    pdf.set_author(data['author']['name'])
    pdf.set_creator(data['creator']['name'])
    pdf.set_producer("fpdf2 " + fpdf.FPDF_VERSION)
    pdf.set_creation_date(datetime.strptime(data['dateCreated'], "%Y-%m-%dT%H:%M:%SZ"))
    pdf.set_lang(data['inLanguage'])
    pdf.set_keywords(data['keywords'])
    pdf.set_subject(data['articleSection'])
    pdf.add_page()
    pdf.write_html(html)
    pdf.output(base_dir + cat_dir + filename)

    return (url_prefix + cat_dir + filename)

if __name__ == "__main__":
    if not urlArr:
        if (verbosity == 1):
            print("<stdin> is empty.")
        sys.exit(0)
    if (verbosity == -1):
        for item in urlArr:
            main(item)
    elif (verbosity == 0):
        for item in urlArr:
            print(main(item), end='')
    else:
        print("Ctrl + Click to open file.")
        for item in urlArr:
            print(main(item))
