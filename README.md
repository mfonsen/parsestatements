parsestatements
===============

For parsing Finnish Osuuspankki (CSV, transactions only) and S-Pankki (PDF) statements to JSON and CSV. 

All processed bank statements from both banks are put together in one file. The resulting CSV file can for example be imported to Google Docs for futher studying. The JSON file on otherhand can be taken for example to Mongodb. 

I have succesfully processed over 5000 bank transactions using this tool.

If you find this useful or have any thoughts, please tweet at @mfonsen or find contact information from http://iki.fi/mf.

Summary in Finnish: Osuuspankin (CSV, vain tilitapahtumat) ja S-Pankin (PDF) tiliotteiden parsiminen ja liittäminen yhteen JSON ja CSV-muodoissa. 

Known issues
------------
  * in my test material, I don't have all possible transaction types. These need to be added manually. 
    * At least in S-Pankki it's possible to add custom types that replace actual transaction type. This makes it quite hard to detect the correct type.
  * Tested only using a mac, should work as is on Linux. Might work on Windows.

Usage
-----

Prerequisites
  * Python
  * All statements in a directory on in directories beneath it
    * Osuuspankki
      * statements in CSV format, transactions only (no headers or footers)
      * directory name = account IBAN (no account information available inside files)
      * file name = tapahtumat{startdate}-{enddate}.csv  (default; example: tapahtumat20091201-20091231.csv)
    * S-Pankki
      * statements in PDF format
      * pdftotext tool in path (see below)
      * directory structure or file names do not matter

<code>python statementparser.py '{source directory, will be handled recursively}' '{output file in json}' '{output file in csv}'</code>

Installing pdftotext to process S-Pankki PDF files
--------------------------------------------------
Pdftotext is a tool for converting PDF files to text (http://en.wikipedia.org/wiki/Pdftotext)
  * Mac: available as part of xpdf: http://www.foolabs.com/xpdf/download.html (in bin64 directory), 
  * Ubuntu: sudo apt-get install xpdf
  * Windows: also available as part of xpdf, haven't tested though

Todo
----
  * debug mode to make it easier to spot unsupported input data
  * publish a tool to use the data (implemented using javascript, Mongodb, Node, Angular)
  * link to other tools for parsing Osuuspankki data, there seems to be at least a couple of those. I have not found any tools to process S-Pankki files
