parsestatements
===============

For parsing Finnish Osuuspankki (CSV, transactions only) and S-Pankki (PDF) statements to JSON and CSV. 

All processed bank statements from both banks are put together in one file. The resulting CSV file can for example be imported to Google Docs for futher studying  (enable file conversion before uploading). The JSON file on otherhand can be taken for example to Mongodb. 

I have succesfully processed over 5000 bank transactions using this tool.

Osuuspankki provides quite reasonable CSV format which is easy to read. S-Pankki on other hand provides only PDF files which in this tool are first converted to plain text and then processed using regular expressions.  

If you find this useful or have any thoughts, please tweet at @mfonsen or find contact information from http://iki.fi/mf.

Summary in Finnish: Osuuspankin (CSV, vain tilitapahtumat) ja S-Pankin (PDF) tiliotteiden parsiminen ja liittäminen yhteen JSON ja CSV-muotoihin. 

Known issues
------------
  * Tested only using a mac, earlier versions also on Linux. Might work on Windows.
  * in my test material, I don't have all possible transaction types. These need to be added manually. 
    * At least in S-Pankki it's possible to add custom types that replace actual transaction type. This makes it quite hard to detect the correct type.
  * S-Pankki file format is difficult to read. Even if it works for me, it might not work anyone else.

Usage
-----

Prerequisites
  * Python 2.7 or later
  * All statements in one directory on in directories beneath it
    * Osuuspankki
      * statements in CSV format, transactions only (no headers or footers)
      * directory name = account IBAN (no account information available inside files). This directory can be inside other directories
      * file name = tapahtumat{startdate}-{enddate}.csv  (default; example: tapahtumat20091201-20091231.csv)
    * S-Pankki
      * statements in PDF format
      * pdftotext tool in installed path (see below)
      * directory structure or file names do not matter

<code>python statementparser.py '{source directory, will be handled recursively}' '{output file in json}' '{output file in csv}'</code>

Installing pdftotext to process S-Pankki PDF files
--------------------------------------------------
Pdftotext is a tool for converting PDF files to plain text (http://en.wikipedia.org/wiki/Pdftotext)
  * Mac: available as part of xpdf: http://www.foolabs.com/xpdf/download.html (in bin64 directory inside the zip file), 
  * Ubuntu: sudo apt-get install xpdf
  * Windows: also available as part of xpdf, haven't tested though

Todo
----
  * debug mode to make it easier to spot unsupported input data
  * publish a tool to use the data (implemented using javascript, Mongodb, Node, Angular)
  * link to other tools for parsing Osuuspankki data, there seems to be at least a couple of those. I have not found any tools to process S-Pankki files. Might be much better as I focused to S-Pankki
    * Using a tool like pdf2json might allow more accurate conversion as it retains original positions of text. Implementation would take time and I don't have the motivation as I got all my data out safely after switching banks.
