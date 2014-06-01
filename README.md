parsestatements
===============

For parsing Finnish Osuuspankki (CSV, transactions only) and S-Pankki (PDF) statements to JSON and CSV. 

Summary in Finnish: Osuuspankin (CSV, vain tilitapahtumat) ja S-Pankin (PDF) tiliotteiden parsiminen JSON ja CSV-muotoon. 

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
      * statements in PDF format
      * pdftotext tool in path (see below)

<code>python statementparser.py '{source directory, will be handled recursively}' '{output file in json}' '{output file in csv}'</code>

Using pdftotext to convert S-Pankki PDF-files to text
-----------------------------------------------------
Pdftotext is a tool for converting PDF files to text (http://en.wikipedia.org/wiki/Pdftotext)

Installing pdftotext 
  * Mac: available as part of xpdf: http://www.foolabs.com/xpdf/download.html (in bin64 directory), 
  * Ubuntu: sudo apt-get install xpdf
  * Windows: also available as part of xpdf, haven't tested though

Todo
----
  * port to Javascript/Node
  * debug mode to make it easier to spot unsupported input data
  * publish a tool to use the data
  * link to other tools for parsing Osuuspankki data, there seems to be at least a couple of those
