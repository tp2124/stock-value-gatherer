import urllib
import os
import json
import time
import optparse
import logging
from collections import namedtuple

#seconds between next pull
TIMEBETWEENPULLS = 60

#specific output file
FILEOUTPUT = None

# STOCKSTOWATCH=['AAPL','FSICX','FUSVX', 'TTWO', 'VFIAX', 'SPX']
STOCKSTOWATCH=['AAPL', 'TTWO']
#Reference: http://www.gummy-stuff.org/Yahoo-data.htm
#for data flag definitions
StockATTR = namedtuple('StockAttr', ['code', 'name', 'value'])

def StockAttr(inCode, inName, inValue=None):
    return StockATTR(inCode, inName, inValue)

STOCKDATAFLAGS = [StockAttr('s', 'Symbol'), StockAttr('n','Name'), StockAttr('d1', 'Last Trade Date'), StockAttr('l','Last Trade with Time'), \
                    StockAttr('a','Ask'), StockAttr('b','Bid'), StockAttr('v',"Volume"), StockAttr('k2','Change Percent'), StockAttr('g',"Day's Low"), \
                    StockAttr('h',"Day's High"), StockAttr('m3','50Day Moving Avg'), StockAttr('m4', '200Day Moving Avg'), \
                    StockAttr('j','Year Low'), StockAttr('k','Year High'), StockAttr('s7','Short Ratio'), StockAttr('p2','Change in Percentage')]
# DATATOWATCH=['s', 'n', 'd1', 'l', 'a','b','v', 'k2', 'g', 'h', 'm3', 'm4', 'j', 'k', 's7', 'p2']
# DATAKEYS = ['Symbol', 'Name', 'Last Trade Date', 'Last Trade with time', 'Ask', 'Bid', 'Volume', 'Change Percent', "Day's Low", "Day's High", 'Year Low', 'Year High', 'Short Ratio', 'Change in %']

#Logger
logger = logging.getLogger('Stock_Project')
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(levelname)s\n%(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


# logger.debug('debug message')
# logger.info('info message')
# logger.warn('warn message')
# logger.error('error message')
# logger.critical('critical message')

def writeJSONFile(raw_data, fullFilePath):
    #Function to create .json representation for the stock report
    outputData = {}
    outputData['gatherTime'] = time.asctime()
    outputData['stocks'] = []

    rawListData = raw_data.replace('\n', '').split(',')
    offset = 0
    curStockValues = {}

    for stock in STOCKSTOWATCH:
        for attr in STOCKDATAFLAGS:
            curStockValues[attr.code] = rawListData[offset]
            offset += 1
        offset = 0
        outputData['stocks'].append(curStockValues)

    json_file = open(fullFilePath + '.json', 'w')
    json_file.write(json.dumps(outputData, sort_keys=True, indent=4))
    json_file.close()

def pullDownData(bLoop=True, debug=False):
    #Function incharge of pulling down the data from Yahoo
    #Defaults to creating a .csv of the data as that is Yahoo's default
    if debug:
        logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)

    # loop that checks stock prices every 20 seconds and adds them to the file
    while True:
        myURL = 'http://finance.yahoo.com/d/quotes.csv?s='
        for symbol in STOCKSTOWATCH:
            myURL += symbol + '+'
        myURL = myURL[0:len(myURL)-1] + '&f='
        for data in STOCKDATAFLAGS:
            myURL += data.code

        #ping URL
        try:
            logger.debug(myURL)
            stocks = urllib.urlopen(myURL).read()
        except IOError:
            logger.error("error reading the socket\n")
            time.sleep(TIMEBETWEENPULLS) #if we don't sleep here loop constently retrys with no delay
            continue

        logger.debug(stocks)
        stocksFile = None
        destDir = os.path.dirname(os.path.realpath(__file__))
        genFileName = ''
        if FILEOUTPUT:
            stocksFile = open('%s.csv' % FILEOUTPUT, 'w')
            genFileName = destDir + '\\' + FILEOUTPUT
        else:
            #Get Date
            date = time.strftime("%c", time.gmtime()).split()[0].replace('/', '-')
            destDir += '\\' + date
            logger.debug(destDir)
            if not os.path.exists(destDir):
                os.mkdir(destDir)
            genFileName = '%s\\%s' % (destDir, time.asctime().replace(":", '-'))
            stocksFile = open(genFileName + '.csv', 'w')
        logger.info('writing to: %s' % stocksFile.name)
        
        writeJSONFile(stocks, genFileName)

        for attr in STOCKDATAFLAGS:
            stocksFile.write(attr.name + ',')
        stocksFile.write('\n\n' + stocks)
        stocksFile.close()
        time.sleep(TIMEBETWEENPULLS)

if __name__ == '__main__':
    #CMD Args
    parser = optparse.OptionParser("usage: [options] arg")
    parser.add_option("-o", '--output', dest='outputName', type='string', default='', help='Specific Output file name')
    parser.add_option('-t', '--time', dest='waitTime', type='int', default='30', help='Time between data pulls (seconds)')
    parser.add_option('-d', '--debug', dest='verbose', action='store_true', help='Print Debug Messages')
    (options, args) = parser.parse_args()
    FILEOUTPUT = options.outputName
    TIMEBETWEENPULLS = options.waitTime

    pullDownData(debug=options.verbose)


