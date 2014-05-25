# coding=UTF-8

# Statement Parser
# example usage: python statementparser.py '<input path>' '<output path+filename>'

#built in
import os.path, json, argparse

#custom
import osuuspankki, spankki #bank specific handlers
import converter #iban conversion

#write results as json
def outputjson(transactions, path):
    with open(path, 'wb') as fp:
        json.dump(transactions, fp, indent=0)

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
                print "Reading statement: " + path
                f = open(os.path.join(dirname,filename), 'r')
                handlermethod(f,path,transactions)
    return transactions

#24.12.2000 --> 2000-12-24
def convertToJsonDate(dateString):
    dateString = dateString[6:10] + "-" + dateString[3:5] + "-" + dateString[0:2]
    #time.strptime(dateString, '%Y-%m-%d')
    return dateString

#convert dates and curriences to a format usable in json
def cleanForJson(transactions):
    for i, val in enumerate(transactions):
        result = transactions[i]

        #convert noteSum to cents + dates to iso format
        #@todo: take maketrans into use
        result['noteSum'] = result['noteSum'].replace("+","")
        result['noteSum'] = (result['noteSum'].replace(".",""))
        result['noteSum'] = (result['noteSum'].replace(",",""))
        result['noteSum'] = int(result['noteSum'])
        result['noteKirjausPvm'] = convertToJsonDate(result['noteKirjausPvm'])
        result['noteArvoPvm'] = convertToJsonDate(result['noteArvoPvm'])
        result['StDateStart'] = convertToJsonDate(result['StDateStart'])
        result['StDateEnd'] = convertToJsonDate(result['StDateEnd'])
        result['StAccountIban'] = result['StAccountIban'].replace(" ","")
        #osuuspankki does not support this field
        if 'noteMaksuPvm' in result:
            result['noteMaksuPvm'] = convertToJsonDate(result['noteMaksuPvm'])
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

#main

#@todo: put handler modules as a list, iterate through list
transactions = []
transactionsTemp = []

#files to parse, output file
parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("output")
args = parser.parse_args()

#read and process osuuspankki
transactionsTemp = filereader(args.input,'csv',osuuspankki.transactionslookup)
transactionsTemp = osuuspankki.parseStatementTransactions(transactionsTemp)

#merge handler module results
transactions.extend(transactionsTemp)

#read and process s-pankki
transactionsTemp = filereader(args.input,'txt',spankki.transactionslookup)
transactionsTemp = spankki.parseStatementTransactions2(transactionsTemp)

#merge handler module results
transactions.extend(transactionsTemp)

#cleanup values
cleanForJson(transactions)

#finally output all data
outputjson(transactions, args.output)