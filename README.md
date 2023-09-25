# Economist2PDF
Convert articles on the Economist to PDF

**DISCLAIMER**: This program is FOR EDUCATIONAL PURPOSE ONLY. Do not distribute the output files, and immediately delete them after browsing.

<pre>
Usage: main.py [OPTIONS]
The program converts articles on the Economist to PDF.
It reads URLs from &lt;stdin&gt; in format "&lt;URL&gt;\n&lt;URL&gt;\n&lt;URL&gt;\n..."
Options: 
    -d, --dir=          Local directory to store output file
    -p, --http-proxy=   HTTP proxy to fetch article, e.g. <i>http://[username:password@]hostname:port</i>
    -t, --text-only     Output text-only PDF
    -v, --verbose       Print user-friendly message
    -q, --quiet         Redirect <stdout>
    -h, --help          Show help message
</pre>

PS: The program depends on python library [fpdf2](https://github.com/PyFPDF/fpdf2). Install by executing:
``` bash
pip install fpdf2
```
