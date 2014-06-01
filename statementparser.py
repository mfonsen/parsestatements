# Statement Parser
# example usage: python statementparser.py '<input path>' '<output path+filename>'

#built in
import os.path, json, argparse, csv
from datetime import datetime, date

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
        #converted to iban, always empty: "noteTargetClassic",
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
    encodedTransactions = encodeOsuuspankkiTransactions(transactions)

    with open(path, 'wb') as fp:
        json.dump(encodedTransactions, fp, indent=0)

#convert encoding for Osuuspankki
#work around to resolve encoding issues when saving to CSV
def encodeOsuuspankkiTransactions(transactions):
    encodedTransactions = []
    for i, val in enumerate(transactions):
        transaction = transactions[i]
        encodedTransaction = {}

        for key in transaction.keys():
            if transaction["StAccountBic"]=="OKOYFIHH":
                if isinstance(transaction[key],str):
                    encodedTransaction[key] = transaction[key].decode("windows-1252")
                else:
                    encodedTransaction[key] = transaction[key]
            else:
                encodedTransaction[key] = transaction[key]
        encodedTransactions.append(encodedTransaction)
    return encodedTransactions

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
    return datetime.strptime(dateString[0:10], "%d.%m.%Y").date().isoformat()

#clean data in place
def cleanData(transactionsToClean):
    transactions = transactionsToClean

    #output currently does not support writing rawTransactions key
    for i in transactions:
        i.pop("rawTransaction", None)

    for i, val in enumerate(transactions):
        result = transactions[i]

        #convert noteSum to cents
        #@todo: take maketrans into use
        print transactions[i]
        result['noteSum'] = result['noteSum'].replace("+","")
        result['noteSum'] = (result['noteSum'].replace(".",""))
        result['noteSum'] = (result['noteSum'].replace(",",""))
        result['noteSum'] = int(result['noteSum'])
        #convert dates to iso format
        result['noteKirjausPvm'] = convertToIsoDate(result['noteKirjausPvm'])
        result['noteArvoPvm'] = convertToIsoDate(result['noteArvoPvm'])
        result['StDateStart'] = convertToIsoDate(result['StDateStart'])
        result['StDateEnd'] = convertToIsoDate(result['StDateEnd'])
        if 'noteMaksuPvm' in result:
            #osuuspankki does not support this field
            result['noteMaksuPvm'] = convertToIsoDate(result['noteMaksuPvm'])
        #convert account numbers to iban+bic format
        if 'noteTargetClassic' in result:
            result['noteTargetIban'] = converter.old_to_iban(result['noteTargetClassic'])
            result['noteTargetBic'] = '{0:s}'.format(converter.bic_of_iban(result['noteTargetIban']))
            result.pop("noteTargetClassic", None)
        #strip white space in iban & card numbers
        result['StAccountIban'] = result['StAccountIban'].replace(" ","")
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


#main

#@todo: put handler modules as a list, iterate through list
transactions = []

#files to parse, output files
parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("outputjson")
parser.add_argument("outputcsv")
args = parser.parse_args()

#read and process osuuspankki
transactionsOsuuspankki = filereader(args.input,'csv',osuuspankki.transactionslookup)
transactionsOsuuspankki = osuuspankki.parseStatementTransactions(transactionsOsuuspankki)
transactions.extend(transactionsOsuuspankki)

#read and process s-pankki
transactionsSpankki = filereader(args.input,'pdf',spankki.transactionslookup)
transactionsSpankki = spankki.parseStatementTransactions(transactionsSpankki)
transactions.extend(transactionsSpankki)

#clean data
cleanData(transactions)

#finally output all data
outputjson(transactions, args.outputjson)
outputCsv(transactions, args.outputcsv)
