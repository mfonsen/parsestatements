# coding=UTF-8
import re

#parse s-pankki pdf statements in txt format
#examples in multiline strings

#read file to a list
def readStatement(f): #f: open file
    data =[]
    s = ""

    counter = 0
    for line in f:
        data.append(line.rstrip())
        counter=counter+1
    
    #join the list to a string
    s = '\n'.join(data)
    
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
    y = []
    y.append(s)

    #@todo: Is this really needed?
    f.close()
    
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
    return transactions       

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
    '''
    04.03.2008 04.03.2008 SELLER 9,99-
    04.03.2008 KORTTIOSTO
    99999999999999
    SELLER
    SELLER HELSINKI
    9999 9999 9999 9999
    99999999999999
    '''
    '''    
    26.11.2007 26.11.2007 SELLER 999,99+
    26.11.2007 KORTTIOSTON KORJAUS
    99999999999999
    SELLER
    SELLER HELSINKI
    9999 9999 9999 9999
    99999999999999
    '''    
    matchers['KORTTIOSTO CLASSIC'] = re.compile(
        reNoteMaksuPvm+"\s+"+reNoteArvoPvm+"\s+(?:.*)\s"+reNoteSum+"$\s*"
        +reNoteKirjausPvm + " (?P<noteTypeId>KORTTIOSTO|KORTTIOSTON KORJAUS)$\s"
        +reNoteReference+"$\s*"
        "(?:.*)$\s*"
        +reNotePayerPayee+"$\s*"
        +reNoteCardClassic
        ,re.MULTILINE)
    """
    12.11.2008 11.11.2008 SELLER 999,99+
    11.11.2008 KORJAUS
    """
    """
    19.08.2008 19.08.2008 SELLER 999,99-
    19.08.2008 KORTTIOSTO
    """    
    """
    20.02.2008 20.02.2008 SELLER 9.999,99+
    20.02.2008 PALKKA
    """
    """
    08.02.2008 08.02.2008 SELLER 9.999,99-
    08.02.2008 TALLETUS
    """ 
    """
    10.05.2010 10.05.2010 SELLER 9.999,99+
    10.05.2010 MAKSUTAPAETU
    """
    """
    09.04.2010 10.04.2010 SELLER 9.999,99+
    09.04.2010 BONUS
    """
    """
    23.02.2009 23.02.2009 SELLER 9.999,99+
    23.02.2009 TALLETUSKORKO
    """
    """
    31.12.2012 31.12.2012 SELLER 9.999,99-
    01.01.2013 LÄHDEVERO
    """
    """
    24.08.2011 24.08.2011 SELLER 9.999,99-
    24.08.2011 TILINYLITYSMAKSU
    """
    """
    28.06.2013 28.06.2013 SELLER 9.999,99-
    01.07.2013 TILINYLITYSKORKO
    KAUSI 01.06.2013 - 30.06.2013
    """
    """
    02.07.2013 02.07.2013 SELLER 9.999,99-
    02.07.2013 TILINYLITYSILMOITUS
    """
    """
    15.02.2011 15.02.2011 SELLER 9.999,99-
    15.02.2011 PALVELUMAKSU
    TAMMIKUU 2011
    Hylätyt maksut 1 kpl 9,99
    """
    """
    31.12.2007 31.12.2007 SELLER 9.999,99+
    01.01.2008 HYVITYSKORKO
    KAUSI 01.01.2007 - 31.12.2007
    """
    """
    31.08.2011 30.08.2011 SELLER 9.999,99-
    31.08.2011 OMA TILISIIRTO
    message message
    """
    '''
    23.09.2011 23.09.2011 SELLER 9.999,99+
    23.09.2011 LAPSILISÄ
    LAPSILISÄ
    MAKSAJAN VIITE
    LL39 345985439757394895783
    ARKISTOINTITUNNUS
    53499539534953459344
    '''
    """
    09.11.2011 09.11.2011 SELLER 9.999,99+
    09.11.2011 TUKI/ETUUS
    VANHEMPAINPÄIVÄRAHA
    MAKSAJAN VIITE
    VR39 345985439757394895783
    ARKISTOINTITUNNUS
    53499539534953459344
    """
    """
    28.09.2011 27.09.2011 SELLER 9.999,99+
    28.09.2011 TILISIIRTO
    message message
    ARKISTOINTITUNNUS
    53499539534953459344
    """
    """
    05.12.2007 03.12.2007 SELLER 9.999,99+
    05.12.2007 TILISIIRTO
    message message
    """    
    matchers['KORTTIOSTO SHORT'] = re.compile(
         reNoteMaksuPvm+"\s+"+reNoteArvoPvm+"\s+"+reNotePayerPayee+"\s"+reNoteSum+"$\s*"
         +reNoteKirjausPvm+" (?P<noteTypeId>TILISIIRTO|KORTTIOSTO|KORJAUS|PALKKA|TALLETUS|MAKSUTAPAETU|BONUS|TALLETUSKORKO|LÄHDEVERO|TILINYLITYSMAKSU|TILINYLITYSKORKO|TILINYLITYSILMOITUS|OMA TILISIIRTO|HYVITYSKORKO|PALVELUMAKSU|LAPSILISÄ|TUKI\/ETUUS)$\s*"
         "(?P<noteDescription>.*\s*)?$\s*"
         "(ARKISTOINTITUNNUS\s*$\s*)?"+reNoteArchiveId+"?"
         ,re.MULTILINE) 
    """
    02.05.2011 02.05.2011 SELLER 9.999,99-
    02.05.2011 KORTTIOSTO
    9999999999999999 99999999999999
    SELLER VANTAA
    """
    """
    19.09.2011 19.09.2011 SELLER 9.999,99+
    19.09.2011 KORTTIOSTON KORJAUS
    9999999999999999 99999999999999
    SELLER VANTAA
    """
    """
    08.12.2010 08.12.2010 SELLER 9.999,99+
    08.12.2010 KORTTITAP. KORJAUS
    9999999999999999 99999999999999
    SELLER VANTAA
    """    
    """
    11.06.2013 11.06.2013 SELLER 9.999,99-
    11.06.2013 AUTOMAATTINOSTO
    999999******9999 99999999999999
    SELLER VANTAA
    """
    """ 
    01.02.2012 01.02.2012 KORTIN UUSINTA/NYTT KORT 10,00-
    01.02.2012 KORTIN UUSINTA
    999999******9999 99999999999999
    KORTIN UUSINTA/NYTT KORT
    """
    """
    07.06.2013 07.06.2013 NOSTOPALKKIO/UTTAGSAVG. 5,00-
    07.06.2013 NOSTOPALKKIO
    999999******9999 99999999999999
    NOSTOPALKKIO/UTTAGSAVG. SELLER
    """
    """
    23.12.2009 23.12.2009 SELLER 9.999,99-
    23.12.2009 KÄTEISNOSTO KORTILLA
    9999999999999999 99999999999999
    SELLER VANTAA
    """
    matchers['KORTTIOSTO IBAN'] = re.compile(
        reNoteMaksuPvm+"\s+"+reNoteArvoPvm+"\s+(?:.*)\s"+reNoteSum+"$\s*"
        +reNoteKirjausPvm + " (?P<noteTypeId>KORTTIOSTO|KORTTIOSTON KORJAUS|KORJAUS|KORTTITAP. KORJAUS|AUTOMAATTINOSTO|KORTIN UUSINTA|NOSTOPALKKIO|KÄTEISNOSTO KORTILLA)\s*$\s*"
        +reNoteCardIban+" "+reNoteReference+"$\s*"
        +reNotePayerPayee+"$\s*"
        ,re.MULTILINE)
    '''
    24.07.2009 24.07.2009 SELLER 9.999,99-
    24.07.2009 999999-99999999
    TILISIIRTO
    '''
    '''
    08.01.2009 08.01.2009 SELLER 9.999,99-
    08.01.2009 999999-99999999
    TILISIIRTO
    99999999999999999999
    '''
    '''
    07.06.2010 06.06.2010 SELLER 9.999,99-
    07.06.2010 999999-999999
    VERKKOMAKSU
    99999999999999999999
    Viesti
    '''
    '''
    29.09.2008 27.09.2008 SELLER 9.999,99-
    29.09.2008 999999-999999
    TERVEYDENHOITOMAKSU
    99999999999999999999
    '''
    '''
    23.02.2011 23.02.2011 SELLER 9.999,99-
    23.02.2011 999999-999999
    TILISIIRTO
    message message
    '''

    """
    14.12.2007 14.12.2007 SELLER 9.999,99-
    14.12.2007 999999-999999
    TALLETUS
    """    
    matchers['TILISIIRTO CLASSIC'] = re.compile(
         reNoteMaksuPvm+"\s+"+reNoteArvoPvm+"\s+(?:.*)\s"+reNoteSum+"$\s*"
         +reNoteKirjausPvm + " "+reNoteTargetClassic+"\s*$\s*"
         "(?P<noteTypeId>TALLETUS|TILISIIRTO|VERKKOMAKSU|TERVEYDENHOITOMAKSU|AUTOKULUT|VAPAA-AJANKULUT|ASUMISKULUT|SÄHKÖMAKSU)$\s*"
         +reNoteReference+"?\s*"
         "(?P<noteDescription>.+)?"
         ,re.MULTILINE)
 
    '''
    03.08.2011 03.08.2011 SELLER 9.999,99-
    03.08.2011 TILISIIRTO
    99999999999999999999
    IBAN
    FI9999999999999999
    BIC
    OKOYFIHH
    '''
    '''
    25.07.2011 24.07.2011 SELLER 9.999,99-
    25.07.2011 VERKKOMAKSU
    99999999999999999999
    IBAN
    FI9999999999999999
    BIC
    NDEAFIHH
    message message
    '''
    matchers['TILISIIRTO VIITENUMEROLLA IBAN'] = re.compile(
        reNoteMaksuPvm+"\s+"+reNoteArvoPvm+"\s+"+reNotePayerPayee+"\s"+reNoteSum+"$\s*"
        +reNoteKirjausPvm + " (?P<noteTypeId>TILISIIRTO|VERKKOMAKSU)$\s*"
        +reNoteReference+"$\s*"
        "IBAN$\s*"
        +reNoteTargetIban+"$\s*"
        "BIC$\s*"
        +reNoteTargetBic+"$\s*"
        "(?P<noteDescription>.*)$\s*"
        ,re.MULTILINE)    
    """
    28.10.2013 27.10.2013 SELLER 9.999,99-
    28.10.2013 LASKUNMAKSU
    message message
    IBAN
    FI9999999999999999
    BIC
    HANDFIHH
    """
    matchers['TILISIIRTO VIESTI IBAN'] = re.compile(
        reNoteMaksuPvm+"\s+"+reNoteArvoPvm+"\s+"+reNotePayerPayee+"\s"+reNoteSum+"$\s*"
        +reNoteKirjausPvm + " (?P<noteTypeId>LASKUNMAKSU)$\s*"
        "(?P<noteDescription>.*)$\s*"
        "IBAN$\s*"
        +reNoteTargetIban+"$\s*"
        "BIC$\s*"
        +reNoteTargetBic+"$\s*"
                                             ,re.MULTILINE)
    '''
    20.01.2010 19.01.2010 SELLER 9.999,99+
    20.01.2010 TILISIIRTO 387220
    message message
    '''
    matchers['TILISIIRTO YKSINKERTAISELLA ARKISTOINTITUNNUKSELLA'] = re.compile(
        reNoteMaksuPvm+"\s+"+reNoteArvoPvm+"\s+"+reNotePayerPayee+"\s"+reNoteSum+"$\s*"
        +reNoteKirjausPvm + " (?P<noteTypeId>TILISIIRTO) "+reNoteReference+"$\s*"
        "(?P<noteDescription>.+)"
        ,re.MULTILINE)    

    """
    31.12.2007 31.12.2007 LÄHDEVERO 9,99-
    01.01.2008
    """    
    """
    21.07.2008 19.07.2008 AUTOMAATTINOSTO 99,99-
    21.07.2008
    """    
    """
    16.06.2008 16.06.2008 PANO/OTTO 99,99+
    16.06.2008
    """    
    #type is incorrectly saved into payerpayee field
    matchers['LÄHDEVERO'] = re.compile(
        reNoteMaksuPvm+"\s+"+reNoteArvoPvm+"\s+(?P<noteTypeId>LÄHDEVERO|AUTOMAATTINOSTO|PANO/OTTO)\s"+reNoteSum+"$\s*"
        +reNoteKirjausPvm + "$"
        ,re.MULTILINE) 

    print "*** Before Parsing ***"
    
    
    matches = 0
    
    for i, val in enumerate(transactions):
        
        matched = False
        transaction = transactions[i]['rawTransaction']
        #print "Transaction: " + str(transaction)
        
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
        
    print "*** Parsed " + str(matches) + "/" + str(len(transactions)) +  "***"
    

    #source: http://stackoverflow.com/questions/8653516/python-list-of-dictionaries-search
    #todo: http://docs.python.org/2/library/collections.html, http://stackoverflow.com/questions/5490078/python-counting-repeating-values-of-a-dictionary
    def search(name, list):
        return [element for element in list if element.has_key('noteType') and element['noteType'] == name ]
    
    def searchEmpty(list):
        return [element for element in list if not (element.has_key('noteType')) ]
    

    for matcher in iter(matchers):
        print matcher + ": " + str(len(search(matcher,transactions)))
    
    print "Not identified: " + str(len(searchEmpty(transactions)))
   
    return transactions

def transactionslookup(openfile, path,transactions):
    statement = readStatement(openfile)
    transactions.extend(mergeRawTransactions(splitStatement(statement),parseStatementMetadata(statement,path)))
    return transactions
