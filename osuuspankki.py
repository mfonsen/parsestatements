# coding=UTF-8
import re
import time
import converter
import csv

import cleantransactions


#Reads Osuuspankki CSV-files without header, footer

#read file to a list
def readStatement(f): #f: open file
    r = []
    s = csv.reader(f, delimiter=';', quotechar='|')

    #create a new list and remove empty rows
    for row in s:
        if len(row)!=0:
            r.append(row)

    #remove header
    r.pop(0)

    #decode cell by cell
    #commented out due to unresolved encoding issues when writing to CSV
    #for row in r:
        #for i, val in enumerate(row):
            #row[i] = val.decode("windows-1252")

    #@todo:close file?
    return r

#Parse statement metadata
def parseStatementMetadata(statement, path):
    result = {}

    #result['StFullPath'] = path

    result['StAccountBic'] = "OKOYFIHH"

    filename = path.split("/")[-1]
    result['StAccountIban'] = path.split("/")[-2]

    #parse statement time span
    result['StDateStart'] = filename[16:18] + "." + filename[14:16] + "." + filename[10:14]
    result['StDateEnd'] = filename[25:27] + "." + filename[23:25] + "." + filename[19:23]

    result["path"] = path;


    #@todo: set account number based on directory    

    #print m1.groupdict()

    return result


#Merge metadata and transactions
def mergeRawTransactions(transactions,metaData):
    #store row number, can be used to replace later transactions with improved parsing
    row = 0
    for i, val in enumerate(transactions):
        row += 1
        transaction = val

        result = {}
        result['rawTransaction'] = transaction
        result['StRow'] = row

        result = dict(result.items() + metaData.items())
        transactions[i] = result
    return transactions

#Parse transactions
def parseStatementTransactions(transactions):

    #precompiled matchers
    matchers = {}

    #line feeds do not exist in material

    """
    Viesti:
                                333333-3333333
                        LYHENNYS
                 9 999,99 EUROA
    KORKO                  999,99 EUROA
    """
    matchers['OP MESSAGE ONLY'] = re.compile(
                                                "Viesti:\s*(?P<noteDescription>.*)$"
                                                )
    #unsupported types, store as is
    #@todo: parse if necessary
    """
    SEPA-MAKSU                         Viesti:                            SAAJA/MOTTAG./BEN: ZZZ ZZZ
    """
    matchers['OP TYPE-TYPE2/COUNTERPART-MESSAGE'] = re.compile(
            "(?:.*)\s+Viesti:\s+(?P<noteDescription>.*)$"
           )
    """
    SEPA-MAKSU Maksajan viite: /OP99/ZZZ 999ZZZ999 Viesti:
    """
    matchers['OP TYPE-COUNTERPART REFERENCE-EMPTY MESSAGE'] = re.compile(
            "(?:.*)\s+Maksajan viite:\s+(?P<noteDescription>.*)Viesti:$"
        )


    print "*** Before Parsing ***"


    matches = 0

    for i, val in enumerate(transactions):

        matched = False
        print transactions[i]
        transaction = transactions[i]['rawTransaction']
        #print "Transaction: " + str(transaction)

        result = {}





        #try to parse "viesti"
        if transaction[8].strip()!="":
            for matcher in iter(matchers):
                #print "###: " + transaction[8]
                m1 = re.match(matchers[matcher],transaction[8])

                #message was parsed with results
                if m1 != None:

                    result = m1.groupdict().copy()
                    #save matcher for debugging
                    result['matcher'] = str(matcher)
                    matches = matches+1
                    matched = True

                    break
            #no matcher returned results, save as is
            if not matched:
                #save matcher for debugging
                result['matcher'] = "OP NO MATCH"
                print "Cannot parse description, saved anyway: \"" + transaction[8] + "\""#+";" + transaction[3] + ";" + transaction[4]#\n"  + '\n'.join(transaction)
        else:
                result['matcher'] = "OP EMPTY DESCRIPTION"

                matches = matches+1
                matched = True
                #print "Description was empty!, saved: \"" + transaction[8] + "\""#+";" + transaction[3] + ";" + transaction[4]#\n"  + '\n'.join(transaction)


        #store fields
        result['noteKirjausPvm'] = transaction[0] #Kirjauspäivä
        result['noteArvoPvm'] = transaction[1] #Arvopäivä
        result['noteSum'] = transaction[2] #Määrä EUROA
        #for some reason notetypeid is in parenthesis
        #result['noteTypeId'] = transaction[3][1:-1] #Tapahtumalajikoodi
        result['noteTypeId'] = transaction[4] #Selitys
        #for some reason notetypeid is in parenthesis
        result['notePayerPayee'] = transaction[5][1:-1] #Saaja/Maksaja
        transaction[6] = transaction[6].strip()
        if converter.validate_old(transaction[6]):
            result['noteTargetClassic'] = transaction[6]
        elif transaction[6]!="":
            result['noteTargetIban'] = transaction[6][0:22]
            result['noteTargetBic'] = transaction[6][25:33]
        #for some reason notetypeid is in parenthesis
        result['noteReference'] = transaction[7][1:-1] #Viite
        if not result.has_key('noteDescription'):
            result['noteDescription'] = transaction[8] #Viesti
        result['noteArchiveId'] = transaction[9] #Arkistotunnus

        transactions[i] = dict(transactions[i].items() + result.items())

    #debug
    print "*** Parsed " + str(matches) + "/" + str(len(transactions)) +  "***"

    #source: http://stackoverflow.com/questions/8653516/python-list-of-dictionaries-search
    #todo: http://docs.python.org/2/library/collections.html, http://stackoverflow.com/questions/5490078/python-counting-repeating-values-of-a-dictionary
    def search(name, list):
        return [element for element in list if element.has_key('matcher') and element['matcher'] == name ]

    def searchEmpty(list):
        return [element for element in list if not (element.has_key('matcher')) ]

    for matcher in iter(matchers):
        print matcher + ": " + str(len(search(matcher,transactions)))
    print "NO MATCH" + ": " + str(len(search("NO MATCH",transactions)))
    print "EMPTY DESCRIPTION" + ": " + str(len(search("EMPTY DESCRIPTION",transactions)))

    print "Not identified: " + str(len(searchEmpty(transactions)))

    #@todo: decode back

    return transactions

#parses openfile in path, extends transcations list with found transaction 
def transactionslookup(openfile, path):
    print "*** Reading file: " + path
    transactions = readStatement(openfile)
    print "Gather statement meta data"
    metadata = parseStatementMetadata(transactions, path)
    print "*** Merge metadata and transactions"
    mergeRawTransactions(transactions,metadata)
    print "*** Parsing transactions: " + path
    parseStatementTransactions(transactions)
    print "*** Cleaning: " + path
    cleantransactions.cleanData(transactions)
    return transactions