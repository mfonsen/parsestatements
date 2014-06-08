parsestatements
===============

For parsing Finnish Osuuspankki (CSV, transactions only) and S-Pankki (PDF) statements to JSON and CSV. 

All processed bank statements from both banks are put together in one file. The resulting CSV file can for example be imported to Google Docs for futher studying  (enable file conversion before uploading). The JSON file on otherhand can be taken for example to Mongodb. 

I have succesfully processed over 5000 bank transactions using this tool.

Osuuspankki provides quite reasonable CSV format which is easy to read. S-Pankki on other hand provides only PDF files which in this tool are first converted to plain text and then processed using regular expressions.  

If you find this useful or have any thoughts, please tweet at @mfonsen or find contact information from http://iki.fi/mf.

Summary in Finnish: Tiliotteiden parsija. Osuuspankin (CSV, vain tilitapahtumat) ja S-Pankin (PDF) tiliotteiden muuntaminen JSON ja CSV-muotoihin. 

Known issues
------------
  * Tested only using a mac, earlier versions also on Linux. Might work on Windows.
  * I don't know all possible transaction types. These need to be added manually. 
    * At least in S-Pankki it's possible to add custom types that replace actual transaction type. This makes it quite hard to detect the correct type.
     * In most cases names of these types can be added to spankki.py, where reNoteTypeId is defined

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

S-Pankki example transactions per parsed format
===============================================

### SPANKKI CARD CLASSIC
```
04.03.2008 04.03.2008 SELLER 9,99-
04.03.2008 KORTTIOSTO
99999999999999
SELLER
SELLER HELSINKI
9999 9999 9999 9999
99999999999999
.
26.11.2007 26.11.2007 SELLER 999,99+
26.11.2007 KORTTIOSTON KORJAUS
99999999999999
SELLER
SELLER HELSINKI
9999 9999 9999 9999
99999999999999
```

### SPANKKI BASIC
```
12.11.2008 11.11.2008 SELLER 999,99+
11.11.2008 KORJAUS

19.08.2008 19.08.2008 SELLER 999,99-
19.08.2008 KORTTIOSTO

20.02.2008 20.02.2008 SELLER 9.999,99+
20.02.2008 PALKKA

08.02.2008 08.02.2008 SELLER 9.999,99-
08.02.2008 TALLETUS

10.05.2010 10.05.2010 SELLER 9.999,99+
10.05.2010 MAKSUTAPAETU

09.04.2010 10.04.2010 SELLER 9.999,99+
09.04.2010 BONUS

23.02.2009 23.02.2009 SELLER 9.999,99+
23.02.2009 TALLETUSKORKO

31.12.2012 31.12.2012 SELLER 9.999,99-
01.01.2013 LÄHDEVERO
 
24.08.2011 24.08.2011 SELLER 9.999,99-
24.08.2011 TILINYLITYSMAKSU
 
23.05.2008 25.05.2008 OSUUSKAUPPA 9,99+
23.05.2008 OSUUSMAKSUN KORKO
 
28.06.2013 28.06.2013 SELLER 9.999,99-
01.07.2013 TILINYLITYSKORKO
KAUSI 01.06.2013 - 30.06.2013
 
02.07.2013 02.07.2013 SELLER 9.999,99-
02.07.2013 TILINYLITYSILMOITUS
 
15.02.2011 15.02.2011 SELLER 9.999,99-
15.02.2011 PALVELUMAKSU
TAMMIKUU 2011
Hylätyt maksut 1 kpl 9,99
 
31.12.2007 31.12.2007 SELLER 9.999,99+
01.01.2008 HYVITYSKORKO
KAUSI 01.01.2007 - 31.12.2007
 
31.08.2011 30.08.2011 SELLER 9.999,99-
31.08.2011 OMA TILISIIRTO
message message

23.09.2011 23.09.2011 SELLER 9.999,99+
23.09.2011 LAPSILISÄ
LAPSILISÄ
MAKSAJAN VIITE
LL39 345985439757394895783
ARKISTOINTITUNNUS
53499539534953459344

09.11.2011 09.11.2011 SELLER 9.999,99+
09.11.2011 TUKI/ETUUS
VANHEMPAINPÄIVÄRAHA
MAKSAJAN VIITE
VR39 345985439757394895783
ARKISTOINTITUNNUS
53499539534953459344
 
28.09.2011 27.09.2011 SELLER 9.999,99+
28.09.2011 TILISIIRTO
message message
ARKISTOINTITUNNUS
53499539534953459344
 
05.12.2007 03.12.2007 SELLER 9.999,99+
05.12.2007 TILISIIRTO
message message

05.07.2010 05.07.2010 S-PANKKI OY 9,99-
05.07.2010 OTTOPISTE TAP.KYSELY
9999999999999999 5 kuukausi 06
Saldokysely 1 kpl
```

### SPANKKI CARD IBAN
```
02.05.2011 02.05.2011 SELLER 9.999,99-
02.05.2011 KORTTIOSTO
9999999999999999 99999999999999
SELLER VANTAA

19.09.2011 19.09.2011 SELLER 9.999,99+
19.09.2011 KORTTIOSTON KORJAUS
9999999999999999 99999999999999
SELLER VANTAA

08.12.2010 08.12.2010 SELLER 9.999,99+
08.12.2010 KORTTITAP. KORJAUS
9999999999999999 99999999999999
SELLER VANTAA

11.06.2013 11.06.2013 SELLER 9.999,99-
11.06.2013 AUTOMAATTINOSTO
999999******9999 99999999999999
SELLER VANTAA

01.02.2012 01.02.2012 KORTIN UUSINTA/NYTT KORT 10,00-
01.02.2012 KORTIN UUSINTA
999999******9999 99999999999999
KORTIN UUSINTA/NYTT KORT

07.06.2013 07.06.2013 NOSTOPALKKIO/UTTAGSAVG. 5,00-
07.06.2013 NOSTOPALKKIO
999999******9999 99999999999999
NOSTOPALKKIO/UTTAGSAVG. SELLER

23.12.2009 23.12.2009 SELLER 9.999,99-
23.12.2009 KÄTEISNOSTO KORTILLA
9999999999999999 99999999999999
SELLER VANTAA
```
    
### SPANKKI ACCOUNT CLASSIC
```
24.07.2009 24.07.2009 SELLER 9.999,99-
24.07.2009 999999-99999999
TILISIIRTO

08.01.2009 08.01.2009 SELLER 9.999,99-
08.01.2009 999999-99999999
TILISIIRTO
99999999999999999999

07.06.2010 06.06.2010 SELLER 9.999,99-
07.06.2010 999999-999999
VERKKOMAKSU
99999999999999999999
Viesti

29.09.2008 27.09.2008 SELLER 9.999,99-
29.09.2008 999999-999999
TERVEYDENHOITOMAKSU
99999999999999999999

23.02.2011 23.02.2011 SELLER 9.999,99-
23.02.2011 999999-999999
TILISIIRTO
message message

14.12.2007 14.12.2007 SELLER 9.999,99-
14.12.2007 999999-999999
TALLETUS
```

### SPANKKI ACCOUNT IBAN REFERENCE
```
03.08.2011 03.08.2011 SELLER 9.999,99-
03.08.2011 TILISIIRTO
99999999999999999999
IBAN
FI9999999999999999
BIC
OKOYFIHH

25.07.2011 24.07.2011 SELLER 9.999,99-
25.07.2011 VERKKOMAKSU
99999999999999999999
IBAN
FI9999999999999999
BIC
NDEAFIHH
message message
```

### SPANKKI ACCOUNT IBAN MESSAGE
```
28.10.2013 27.10.2013 SELLER 9.999,99-
28.10.2013 LASKUNMAKSU
message message
IBAN
FI9999999999999999
BIC
HANDFIHH
```

### SPANKKI REFERENCE 2ND ROW
```
20.01.2010 19.01.2010 SELLER 9.999,99+
20.01.2010 TILISIIRTO 387220
message message
```

### SPANKKI TYPE 1ST ROW
```
31.12.2007 31.12.2007 LÄHDEVERO 9,99-
01.01.2008

21.07.2008 19.07.2008 AUTOMAATTINOSTO 99,99-
21.07.2008

16.06.2008 16.06.2008 PANO/OTTO 99,99+
16.06.2008

12.10.2007 12.10.2007 SIIRTO SÄÄSTÖKASSASTA 9,99+
12.10.2007 99999999999999
```
