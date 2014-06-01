# -*- coding: UTF-8 -*-

# Statement Parser
# example usage: python statementparser.py '<input path>' '<output path+filename>'

#built in
import os.path, json, argparse, csv

#custom
import osuuspankki, spankki #bank specific handlers
import converter #iban conversion

#write results as csv
def outputCsv(transactions, path):
    keys = [
        #statement metadata
        "StAccountBic",
        "StAccountIban",
        "StDateStart",
        "StDateEnd",
        "path",

        #transaction metadata
        #"rawTransaction",
        "StRow",
        "matcher",

        #transaction 
        "noteKirjausPvm",
        "noteArvoPvm",
        "noteSum",
        "noteTypeId",
        "noteType",
        "notePayerPayee",
        "noteTargetClassic",
        "noteTargetIban",
        "noteTargetBic",
        "noteReference",
        "noteDescription",
        "noteArchiveId",

        #transaction, not in osuuspankki
        "noteMaksuPvm",
        "noteCard"
            ]

    with open(path, 'wb') as f:
        #not using dictwriter due to unresolved encoding issues
        writer = csv.writer(f)
        #write header
        writer.writerow(keys)

        for transaction in transactions:
            row = []
            for key in keys:
                if key in transaction:
                    row.append(transaction[key])
                else:
                    row.append("")
            writer.writerow(row)
            

#write results as json
def outputjson(transactions, path):
    result = cleanForJson(transactions)
    with open(path, 'wb') as fp:
        json.dump(result, fp, indent=0)

#iterates files in sourcepath that have sourceextension. 
#In the end of each iteration calls handlermethod(f,path,transactions). 
#Handlermethod is assumed to extend transactions list with new items
def filereader(sourcepath, sourceextension,handlermethod):
    transactions = []
    path =""
    for dirname, dirnames, filenames in os.walk(sourcepath):
        for filename in filenames:
            if filename.endswith(sourceextension):
                path = os.path.join(dirname,filename)
                #print "Reading statement: " + path
                f = open(os.path.join(dirname,filename), 'r')
                handlermethod(f,path,transactions)
    return transactions

#24.12.2000 --> 2000-12-24
def convertToIsoDate(dateString):
    dateString = dateString[6:10] + "-" + dateString[3:5] + "-" + dateString[0:2]
    #time.strptime(dateString, '%Y-%m-%d')
    return dateString

def cleanData(transactionsToClean):
    transactions = transactionsToClean

    for i, val in enumerate(transactions):
        result = transactions[i]

        #convert noteSum to cents + dates to iso format
        #@todo: take maketrans into use
        result['noteSum'] = result['noteSum'].replace("+","")
        result['noteSum'] = (result['noteSum'].replace(".",""))
        result['noteSum'] = (result['noteSum'].replace(",",""))
        result['noteSum'] = int(result['noteSum'])
        result['noteKirjausPvm'] = convertToIsoDate(result['noteKirjausPvm'])
        result['noteArvoPvm'] = convertToIsoDate(result['noteArvoPvm'])
        result['StDateStart'] = convertToIsoDate(result['StDateStart'])
        result['StDateEnd'] = convertToIsoDate(result['StDateEnd'])
        result['StAccountIban'] = result['StAccountIban'].replace(" ","")
        #osuuspankki does not support this field
        if 'noteMaksuPvm' in result:
            result['noteMaksuPvm'] = convertToIsoDate(result['noteMaksuPvm'])
        if 'noteTargetClassic' in result:
            result['noteTargetIban'] = converter.old_to_iban(result['noteTargetClassic'])
            result['noteTargetBic'] = '{0:s}'.format(converter.bic_of_iban(result['noteTargetIban']))
            result.pop("noteTargetClassic", None)
        if 'noteTargetIban' in result:
            result['noteTargetIban'] = result['noteTargetIban'].replace(" ","")
        if 'noteCard' in result:
            result['noteCard'] = result['noteCard'].replace(" ","")

        #remove null values, strip leading, trailing whitespace
        for key in result.keys():
            if result[key]== None:
                del result[key]
            elif isinstance(result[key], basestring):
                result[key] = result[key].strip()
                if result[key]=="":
                    del result[key]
    return transactionsToClean


#convert dates and curriences to a format usable in json
def cleanForJson(transactionsToClean):
    transactions = transactionsToClean

    #reduce json size
    for i in transactions:
        i.pop("rawTransaction", None)

    for i, val in enumerate(transactions):
        result = transactions[i]

        for key in result.keys():
            #convert encoding for Osuuspankki
            #work around to resolve encoding issues when saving to CSV
            if result["StAccountBic"]=="OKOYFIHH":
                if isinstance(result[key],str):
                    result[key] = result[key].decode("windows-1252")
    return transactions


#main

#@todo: put handler modules as a list, iterate through list
transactions = []
transactionsTemp = []

#files to parse, output file
parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("outputjson")
parser.add_argument("outputcsv")
args = parser.parse_args()

#read and process osuuspankki
transactionsTemp = filereader(args.input,'csv',osuuspankki.transactionslookup)
transactionsTemp = osuuspankki.parseStatementTransactions(transactionsTemp)

#merge handler module results
transactions.extend(transactionsTemp)

#read and process s-pankki
transactionsTemp = filereader(args.input,'txt',spankki.transactionslookup)
transactionsTemp = spankki.parseStatementTransactions(transactionsTemp)

#merge handler module results
transactions.extend(transactionsTemp)

#clean data
transactions = cleanData(transactions)

#finally output all data
outputCsv(transactions, args.outputcsv)
outputjson(transactions, args.outputjson)
