# Economist2PDF
Convert articles on the Economist to PDF

PS: The program depends on python library [fpdf2](https://github.com/PyFPDF/fpdf2)

```
Usage: %s [OPTIONS]
The program converts articles on the Economist to PDF.
It reads URLs from <stdin> in format "<URL>\n<URL>\n<URL>\n..."
Options: 
    -d, --dir=          Local directory to store output file
    -p, --http-proxy=   HTTP proxy to fetch article
    -t, --text-only     Output text-only PDF
        --url-prefix=   URL prefix to access output file
    -v, --verbose       Print user-friendly message
    -q, --quiet         Redirect <stdout>
    -h, --help          Show help message
```

DISCLAIMER: This program is FOR EDUCATIONAL PURPOSE ONLY. Do not distribute the output files, and immediately delete them after browsing.
