parsestatements
===============

For parsing Finnish Osuuspankki (CSV, transactions only) and S-Pankki (PDF) statements to JSON. This is a tool that works for me, no much effort has been done beyond that goal.

Summary in Finnish: Osuuspankin (CSV, vain tilitapahtumat) ja S-Pankin (PDF) tiliotteiden parsiminen JSON-muotoon. Tämä toimii minulle eikä muita tavoitteita ole ollut.

If you find this useful or have any thoughts, please contact me: http://iki.fi/mf

Known issues
------------
  * in my test material, I don't have all possible transaction types. These need to be added manually. 
    * At least in S-Pankki it's possible to add custom types that replace actual transaction type. This makes it quite hard to detect the correct type.
  * originally tested in Ubuntu, later only in OSX

Usage
-----

Prerequisites
  * Linux/Mac
  * Python
  * All statements in a directory on in directories beneath it
    * Osuuspankki
      * statements in CSV format, transactions only (no headers or footers)
      * directory name = account IBAN (no account information available inside files)
      * file name = tapahtumat{startdate}-{enddate}.csv  (default; example: tapahtumat20091201-20091231.csv)
    * S-Pankki
      * statements in text format as parsed by pdftotext tool (see below)

<code>python statementparser.py '{source directory, will be handled recursively}' '{output file in json}'</code>

Using pdftotext to convert S-Pankki PDF-files to text
-----------------------------------------------------
Pdftotext is a tool for converting PDF files to text (http://en.wikipedia.org/wiki/Pdftotext)

Installing pdftotext 
  * Mac: available on homebrew: <code>brew install poppler</code>, 
  * Ubuntu: sudo apt-get install xpdf

To execute pdftotext on all PDF files in a directory
  * Run <code>find . -name '*.pdf' \( -exec pdftotext -raw "$PWD"/{} \;  \)</code>

Todo
----
  * port to Javascript/Node
  * include pdf to text conversion as a library (pdf2json in npm?)
  * publish a tool to use the data
