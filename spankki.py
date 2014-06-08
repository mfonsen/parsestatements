# coding=UTF-8
import re, subprocess, os

import cleantransactions

#parse s-pankki pdf statements in txt format
#examples in multiline strings

#regular expressions can be tested easily in http://regex101.com/#python by using following flags: ms

#remove page breaks and other meta data
def removeMetaData(s):
    """
    21.01.2008 21.01.2008 SELLER 3,20-
    21.01.2008 KORTTIOSTO
    99999999999999
    PANOT KIRJAUSPÄIVÄN ALUSTA 0,00+
    OTOT KIRJAUSPÄIVÄN ALUSTA 3,60-
    * JATKUU *
    -
    2 (2)
    SIVU
    TILIOTE 1
    PÄIVÄMÄÄRÄ 31.01.2008
    KAUSI 01.01.2008 - 31.01.2008
    S-TILI EUR 999999 99999999
    SAAJA/MAKSAJA
    SAAJAN TILINUMERO
    VIESTI MÄÄRÄ EUR
    MAKSUPÄIVÄ
    ARVOPÄIVÄ
    KIRJAUSPÄIVÄ
    SELLER
    SELLER HELSINKI
    9999 9999 9999 9999
    99999999999999
    """
    """
    16.05.2011 KORTTIOSTO
    9999999999999999 99999999999999
    K-CITYMARKET ZZZ ZZZ
    * JATKUU *
    -
    3 (5)
    SIVU
    TILIOTE 5
    SAAJAN TILINUMERO
    VIESTI MÄÄRÄ EUR
    MAKSUPÄIVÄ
    ARVOPÄIVÄ
    KIRJAUSPÄIVÄ
    16.05.2011 16.05.2011 Seller 23,30-
    16.05.2011 KORTTIOSTO
    9999999999999999 99999999999999
    Seller Helsinki
    """
    """
    PANOT KIRJAUSPÄIVÄN ALUSTA 9.999,99+
    OTOT KIRJAUSPÄIVÄN ALUSTA 0,00-
    """
    #remove page changes
    #data example
    """
    * JATKUU *\n\n1 (4)\n\n120,50-\n\n2,60-\n\n\x0cSIVU\n\nTILIOTE\nP\xc3\x84IV\xc3\x84M\xc3\x84\xc3\x84R\xc3\x84\nKAUSI\nS-TILI\n\nKIRJAUSP\xc3\x84IV\xc3\x84\n\nMAKSUP\xc3\x84IV\xc3\x84\nARVOP\xc3\x84IV\xc3\x84\n\nSAAJA/MAKSAJA\nSAAJAN TILINUMERO\nVIESTI\n\n2\n
    """
    s = re.sub("(?:PANOT KIRJAUSPÄIVÄN ALUSTA [\d\.,]*\+\nOTOT KIRJAUSPÄIVÄN ALUSTA [\d\.,]*-\n)?\* JATKUU \*.*?KIRJAUSPÄIVÄ\n","",s,flags=re.DOTALL) #|re.DEBUG    

    return s


#store statement metadata
def parseStatementMetadata(statement,path):
    #data example
    """
    ...
    KAUSI 01.02.2011 - 28.02.2011
    ...
    säilyttäkää tiliote kuittina tapahtumista.
    FI99 9999 9999 9999 99
    SBANFIHH
    ...    
    """
    
    matchRow1 = re.compile(".*KAUSI\s+(?P<StDateStart>[\d\.]+)+\s-\s(?P<StDateEnd>[\d\.]+).*tapahtumista\.\s+(?P<StAccountIban>\w\w[\d\s]+)\s+(?P<StAccountBic>\w+)\s",flags=re.DOTALL)
    m1 = re.match(matchRow1,statement)
        
    #print m1.groupdict()

    metadata = m1.groupdict().copy()
    metadata["path"] = path;
    
    return metadata
    
#split to transactions
def splitStatement(statement):
    transactions = []
    #find all items that start with 3 dates and end to 3 dates OR text "SALDO"
    #(?= means match if followed by - does not consume follower
    #/[^\S\n]/ whitespace but not linefeed
    
    #non linefeed white space was needed because of following entries (two dates on a row)
    """
    31.12.2007 31.12.2007 S-PANKKI OY 9,99+
    01.01.2008 HYVITYSKORKO
    KAUSI 01.01.2007 - 31.12.2007
    31.12.2007 31.12.2007 LÄHDEVERO 9,99-
    01.01.2008
    """

    transactions= re.findall("(?:\d+\.\d+\.\d+\s+\d+\.\d+\.\d+\\s+.*?)(?=\d+\.\d+\.\d+[^\S\n]+\d+\.\d+\.\d+\\s+|SALDO)",statement,flags=re.DOTALL)
    
    #debug
    #print "transactions:" + str(len(transactions)) + str(transactions)
    #for line in transactions:
    #    print line + "<change>"
    #print "### AFTER SPLITTING ###" 
    return transactions

#Parse merge metadata and transactions
def mergeRawTransactions(transactions,metaData):
    #store row number, can be used to replace later transactions with improved parsing
    row = 0
    for i, val in enumerate(transactions):
        row += 1
        transaction = transactions[i].splitlines()
        
        result = {}
        result['rawTransaction'] = transaction
        result['StRow'] = row
        result = dict(result.items() + metaData.items())
        transactions[i] = result

#Parse transactions
def parseStatementTransactions(transactions):
    """
        #type specific elements
        #noteDescription
        #noteArchiveId
        #noteReference
        #noteTargetIban
        #noteTargetBic
        #noteCard - Payment card number
        #noteTargetClassic
    """
    
    #precompiled matchers

    reNoteTypeId = ("(?P<noteTypeId>"
    #type ids visible on S-Pankki web site (custom types user can select)
    "ASUMISKULUT|AUTOKULUT|E-LASKU|ELATUSMAKSU|ELÄKEVAKUUTUSMAKSU"
    "|FYSIOTERAPIAMAKSU|HAMMASHOITOMAKSU|HOITOMAKSU|JÄSENMAKSU|KAASUMAKSU|KODINHOITOMAKSU"
    "|KOULUMAKSU|LASKUNMAKSU|LEHTITILAUS|LUOTTOKORTTIMAKSU|LUPAMAKSU|LÄMPÖLASKU/ÖLJY|LÄÄKÄRINPALKKIO"
    "|MÖKKIKULUT|NUOHOUSMAKSU|OMA TILISIIRTO|OSAMAKSULAINA|PALKKA|POLTTOAINELASKU|PUHELINLASKU|PUHTAANAPITO"
    "|PÄIVÄHOITOMAKSU|RUOKALASKU|SAIRAANHOITOMAKSU|SÄHKÖMAKSU|TALOKULUT|TERVEYDENHOITOMAKSU|TILISIIRTO|VAKUUTUS"
    "|VAPAA-AJAN MAKSUT|VENEMAKSUT|VERKKOMAKSU|VERO|VESIMAKSU|VISAMAKSU|VUOKRANMAKSU|YHTIÖVASTIKE"
    #other type ids found on personal statements, more probably need to be added here
    "|KORTTIOSTO|KORTTIOSTON KORJAUS|KORJAUS"
    "|TALLETUS|MAKSUTAPAETU|BONUS|TALLETUSKORKO|LÄHDEVERO|TILINYLITYSMAKSU|TILINYLITYSKORKO|TILINYLITYSILMOITUS"
    "|HYVITYSKORKO|PALVELUMAKSU|LAPSILISÄ|TUKI\/ETUUS|OSUUSMAKSUN KORKO|OTTOPISTE TAP.KYSELY"
    "|KORTTITAP. KORJAUS|AUTOMAATTINOSTO|KORTIN UUSINTA|NOSTOPALKKIO"
    "|KÄTEISNOSTO KORTILLA|AUTOMAATTINOSTO|PANO/OTTO|SIIRTO SÄÄSTÖKASSASTA|VAPAA-AJANKULUT"
    #end string
    ")")
    reNoteMaksuPvm = "(?P<noteMaksuPvm>\d+\.\d+\.\d+)"
    reNoteArvoPvm = "(?P<noteArvoPvm>\d+\.\d+\.\d+)"
    reNotePayerPayee = "(?P<notePayerPayee>.*)" 
    reNoteSum = "(?P<noteSum>\d*\.?\d+,\d+[+-])"
    reNoteKirjausPvm = "(?P<noteKirjausPvm>\d+\.\d+\.\d+)"
    reNoteReference = "(?P<noteReference>[0-9]+)"
    reNoteCardClassic = "(?P<noteCard>[0-9]+ [0-9]+ [0-9]+ [0-9]+)"
    reNoteCardIban = "(?P<noteCard>[0-9\*]+)"
    reNoteArchiveId = "(?P<noteArchiveId>[0-9A-Z]+)"
    #source: http://www.ohjelmointiputka.net/koodivinkit/24548-python-tilinumeron-tarkistus
    reNoteTargetClassic = "(?P<noteTargetClassic>[0-9]{6}-[0-9]{2,8})"
    #source: http://snipplr.com/view/15322/iban-regex-all-ibans/
    reNoteTargetIban = "(?P<noteTargetIban>[a-zA-Z]{2}[0-9]{2}[a-zA-Z0-9]{4}[0-9]{7}([a-zA-Z0-9]?){0,16})"
    #source: http://snipplr.com/view/15320/bic-bank-identifier-code-regex/
    reNoteTargetBic = "(?P<noteTargetBic>[a-zA-Z]{4}[a-zA-Z]{2}[a-zA-Z0-9]{2}([a-zA-Z0-9]{3})?)"

    matchers = {}

    #for example please see README.md
   
    matchers['SPANKKI CARD CLASSIC'] = re.compile(
        reNoteMaksuPvm+"\s+"+reNoteArvoPvm+"\s+(?:.*)\s"+reNoteSum+"$\s*"
        +reNoteKirjausPvm+"\s+"+reNoteTypeId + "$\s"
        +reNoteReference+"$\s*"
        "(?:.*)$\s*"
        +reNotePayerPayee+"$\s*"
        +reNoteCardClassic
        ,re.MULTILINE)

    matchers['SPANKKI BASIC'] = re.compile(
         reNoteMaksuPvm+"\s+"+reNoteArvoPvm+"\s+"+reNotePayerPayee+"\s"+reNoteSum+"$\s*"
         +reNoteKirjausPvm+"\s+"+ reNoteTypeId + "$\s*"
         "(?P<noteDescription>.*\s*)?$\s*"
         "(ARKISTOINTITUNNUS\s*$\s*)?"+reNoteArchiveId+"?"
         ,re.MULTILINE) 

    matchers['SPANKKI CARD IBAN'] = re.compile(
        reNoteMaksuPvm+"\s+"+reNoteArvoPvm+"\s+(?:.*)\s"+reNoteSum+"$\s*"
        +reNoteKirjausPvm+"\s+"+reNoteTypeId + "$\s*"
        +reNoteCardIban+" "+reNoteReference+"$\s*"
        +reNotePayerPayee+"$\s*"
        ,re.MULTILINE)

    matchers['SPANKKI ACCOUNT CLASSIC'] = re.compile(
         reNoteMaksuPvm+"\s+"+reNoteArvoPvm+"\s+(?:.*)\s"+reNoteSum+"$\s*"
         +reNoteKirjausPvm + " "+reNoteTargetClassic+"\s*$\s*"
         + reNoteTypeId + "$\s*"
         +reNoteReference+"?\s*"
         "(?P<noteDescription>.+)?"
         ,re.MULTILINE)
 
    matchers['SPANKKI ACCOUNT IBAN REFERENCE'] = re.compile(
        reNoteMaksuPvm+"\s+"+reNoteArvoPvm+"\s+"+reNotePayerPayee+"\s"+reNoteSum+"$\s*"
        +reNoteKirjausPvm+"\s+"+reNoteTypeId +  "$\s*"
        +reNoteReference+"$\s*"
        "IBAN$\s*"
        +reNoteTargetIban+"$\s*"
        "BIC$\s*"
        +reNoteTargetBic+"$\s*"
        "(?P<noteDescription>.*)$\s*"
        ,re.MULTILINE)    

    matchers['SPANKKI ACCOUNT IBAN MESSAGE'] = re.compile(
        reNoteMaksuPvm+"\s+"+reNoteArvoPvm+"\s+"+reNotePayerPayee+"\s"+reNoteSum+"$\s*"
        +reNoteKirjausPvm+"\s+"+reNoteTypeId + "$\s*"
        "(?P<noteDescription>.*)$\s*"
        "IBAN$\s*"
        +reNoteTargetIban+"$\s*"
        "BIC$\s*"
        +reNoteTargetBic+"$\s*"
        ,re.MULTILINE)

    matchers['SPANKKI REFERENCE 2ND ROW'] = re.compile(
        reNoteMaksuPvm+"\s+"+reNoteArvoPvm+"\s+"+reNotePayerPayee+"\s"+reNoteSum+"$\s*"
        +reNoteKirjausPvm+"\s+"+reNoteTypeId+" "+reNoteReference+"$\s*"
        "(?P<noteDescription>.+)"
        ,re.MULTILINE)    

    #@todo: type is incorrectly saved into payerpayee field
    matchers['SPANKKI TYPE 1ST ROW'] = re.compile(
        reNoteMaksuPvm+"\s+"+reNoteArvoPvm+"\s+" + reNoteTypeId + "\s+"+reNoteSum+"$\s*"
        +reNoteKirjausPvm + "\s*(?P<noteReference>.+)?$"
        ,re.MULTILINE) 

    matches = 0
    
    for i, val in enumerate(transactions):
        
        matched = False
        #print "Transaction: " + str(transactions[i])
        transaction = transactions[i]['rawTransaction']
        
        result = {}
        for matcher in iter(matchers):
            m1 = re.match(matchers[matcher],'\n'.join(transaction))
            
            if m1 != None:

                result = m1.groupdict().copy()
                
                #skip detected noteType
                result['noteType'] = str(matcher)
                #save matcher for debugging
                result['matcher'] = str(matcher)
                
                #convert sum to international format
                from string import maketrans   # Required to call maketrans function.
                result['noteSum'] = result['noteSum'][-1] + result['noteSum'].rstrip('+-').translate(maketrans(',', '.'),'+.')
                                
                transactions[i] = dict(transactions[i].items() + result.items())
                
                #debug
                #print str(transactions[i])
                
                matches = matches+1
                matched = True

                break 
            #else:
                #print "No match!:" + str(matcher)  + "\n" + '\n'.join(transaction) + "%%%"
        if not matched: 
            print "No match!: \n"  + '\n'.join(transaction)
        
    print "*** parsed " + str(matches) + "/" + str(len(transactions)) +  "***"
    

    #source: http://stackoverflow.com/questions/8653516/python-list-of-dictionaries-search
    #todo: http://docs.python.org/2/library/collections.html, http://stackoverflow.com/questions/5490078/python-counting-repeating-values-of-a-dictionary
    def search(name, list):
        return [element for element in list if element.has_key('noteType') and element['noteType'] == name ]
    
    def searchEmpty(list):
        return [element for element in list if not (element.has_key('noteType')) ]
    

    for matcher in iter(matchers):
        print matcher + ": " + str(len(search(matcher,transactions)))
    
    print "Not identified: " + str(len(searchEmpty(transactions)))
   
def transactionslookup(openfile, path):
    print "*** Executing pdftotext for: " + path
    statement = subprocess.Popen(["pdftotext", "-raw",path,"-enc", "UTF-8","-"],  stdout=subprocess.PIPE).communicate()[0]
    print "Parse statement meta data"
    metadata = parseStatementMetadata(statement,path)
    print "*** Removing meta data from statement"
    statement = removeMetaData(statement)
    print "*** Split to transactions"
    transactions = splitStatement(statement)
    print "*** Merge "
    mergeRawTransactions(transactions,metadata)
    print "*** Parsing: " + path
    parseStatementTransactions(transactions)
    print "*** Cleaning: " + path
    cleantransactions.cleanData(transactions)
    return transactions
