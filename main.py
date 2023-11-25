#!/usr/bin/env python
# coding: utf-8

# Initialize
icon        = "assets/economist.png"
font_file   = "assets/MiloTE.ttf"
fontI_file  = "assets/MiloTE-inclined.ttf"
font_name   = "MiloTE"
fontI_name  = "MiloTE-I"

economist_icon  = "assets/economist.png"
audio_icon      = "assets/audio.png"
font_path       = "assets/MiloTE.ttf"
fontI_path      = "assets/MiloTE-inclined.ttf"
fallback_font   = "assets/Courier.otf"
font_name       = "MiloTE"
fontI_name      = "MiloTE-I"

user_agent  = "Mozilla/5.0"

import sys, getopt, re, urllib.request, json
from datetime import datetime
from pathlib import Path
import fpdf

# Input: getopt
def usage(name):
    print("""Usage: %s [OPTIONS]
The program converts articles on the Economist to PDF. 
It reads URLs from <stdin> in format "<URL>\\n<URL>\\n<URL>\\n..."
Options: 
    -d, --dir=          Local directory to store output file
    -p, --http-proxy=   HTTP proxy to fetch article, e.g. `http://[username:password@]hostname:port`
    -t, --text-only     Output text-only PDF
    -v, --verbose       Print user-friendly message
    -q, --quiet         Redirect <stdout> to NULL
    -h, --help          Show help message
""" % (name), end="")

stdin = sys.stdin.read()
argv = sys.argv
proxy_handler = urllib.request.ProxyHandler()
base_dir = ""
text_only = False
verbosity = 0
try:
    opts, args = getopt.getopt(argv[1:], \
            "d:p:tvqh", ["dir=","http-proxy=", "text-only", "verbose", "quiet", "help"])
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
    elif opt in ("-v", "--verbose"):
        verbosity = 1
    elif opt in ("-q", "--quiet"):
        verbosity = -1

# Install proxy
opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPBasicAuthHandler())
opener.addheaders = [('User-Agent', user_agent)]
urllib.request.install_opener(opener)

# Regex
urlArr = stdin.splitlines()
regex = r"^https:\/\/www\.economist\.com\/(.*)\/(\d{4})\/(\d{2})\/(\d{2})\/(.*?)(?=\?|\Z).*"
pattern = re.compile(regex)

def main(url):

    if not pattern.fullmatch(url):
        return ""
    cat_dir = pattern.sub("\\1/", url)
    filename = pattern.sub("\\5_\\2-\\3-\\4.pdf", url)
    Path(base_dir + cat_dir).mkdir(parents=True, exist_ok=True)

    # Request
    req = urllib.request.Request(url)
    content = urllib.request.urlopen(req).readlines()
    subheadline = re.search(r" \| <!-- -->(.*?)<", content[19].decode()).group(1)
    audio = re.search(r"<audio .*? src=\"(.*?)\" title=\"(.*?)\"", content[19].decode())
    if audio is not None:
        audio_link = audio.group(1)
        audio_alt = audio.group(2)
    data = json.loads(content[1].decode())
    body = data['articleBody'].split('\n')
    try:
        date = datetime.strptime(data['datePublished'], "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        date = datetime.strptime(data['datePublished'], "%Y-%m-%dT%H:%M:%S.%fZ")
    headline_ascii = data['headline'].encode("ascii", errors="ignore").decode() # Some Unicode characters cannot be stored in PDF's metadata
    if text_only:
        headline_ascii += "(Text Only)"
    # Retrieve Thumbnail
    urllib.request.urlretrieve(data['thumbnailUrl'], "thumbnail.png")

    # Compose HTML string
    html = str()
    html += "<h1>%s</h1>" % (data["headline"],)
    html += "<font face=\"%s\" size=16><p line-height=2>%s</p></font>" % (fontI_name, data["description"])
    html += "<p align=\"right\">Published on %s</p>" % (date.strftime("%b %d %Y, %I:%M %p"))
    if text_only:
        #html += "<p>---------------------------------------------------------------------------------------------------------------------------</p>"
        pass
    else:
        html += "<img src=\"thumbnail.png\" width=538>"    # pixel width of an A4 page
    for line in body:
        if (line and line[-1] == '■'):
            html += "<p line-height=1.5>%s</p>" % (line[:-1],)
            break
        html += "<p line-height=1.5>%s</p>" % (line,)

    # Initialize PDF
    class PDF(fpdf.FPDF):
        def header(self):
            self.image(icon, 10, 10, 20, link="https://www.economist.com/", alt_text="The Economist")
            self.cell(0, 10, "%s | %s" % (data['articleSection'], subheadline), align="R", link=data["url"])
            # Line Break:
            self.ln(16)

        def footer(self):
            self.set_y(-16)
            if audio is not None:
                self.image(audio_icon, 12, None, 6, link=audio_link, alt_text=audio_alt)
            self.cell(0, -6, f"{self.page_no()}/{{nb}}", align="R")

    # Generate PDF
    pdf = PDF()
    pdf.add_font(font_name,'',font_path)
    pdf.add_font(fontI_name,'',fontI_path)
    pdf.add_font(family="fallback", fname=fallback_font)
    pdf.set_font(font_name)
    pdf.set_fallback_fonts(["fallback"])
    pdf.set_title(headline_ascii)
    pdf.set_author(data['author']['name'])
    pdf.set_creator(data['creator']['name'])
    pdf.set_producer("Python fpdf2 %s" % (fpdf.FPDF_VERSION,))
    pdf.set_creation_date(date)
    pdf.set_lang(data['inLanguage'])
    pdf.set_keywords(data['keywords'])
    pdf.set_subject(data['articleSection'])
    pdf.add_page()
    pdf.ln(-8)
    pdf.write_html(html)
    pdf.output(base_dir + cat_dir + filename)

    return (cat_dir + filename)

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
        for item in urlArr:
            print(main(item))
