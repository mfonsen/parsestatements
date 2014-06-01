from datetime import datetime, date
import converter #iban conversion


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

