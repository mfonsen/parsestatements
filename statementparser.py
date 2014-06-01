# Statement Parser
# example usage: python statementparser.py '<input path>' '<output path+filename>'

#built in
import os.path, json, argparse, csv

#custom
import osuuspankki, spankki #bank specific handlers

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
                transactions.extend(handlermethod(f,path))
    return transactions

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
#transactionsOsuuspankki = filereader(args.input,'csv',osuuspankki.transactionslookup)
#transactionsOsuuspankki = osuuspankki.parseStatementTransactions(transactionsOsuuspankki)
#transactions.extend(transactionsOsuuspankki)

#read and process s-pankki
transactionsSpankki = filereader(args.input,'pdf',spankki.transactionslookup)
transactions.extend(transactionsSpankki)

#finally output all data
outputjson(transactions, args.outputjson)
outputCsv(transactions, args.outputcsv)
