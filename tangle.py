import argparse
import urllib2
import json
import datetime
from dateutil.parser import parse
from collections import OrderedDict
from iota import Transaction, TryteString

__version__ = 1.0

headers = {
    'content-type': 'application/json',
    'X-IOTA-API-Version': '1'
}

def run(address, hostname, port):

    dataset = {}

    print 'Using IOTA light node %s:%s' % (hostname, port)
    print 'Finding transactions from address %s' % address

    command = {
        'command': 'findTransactions',
        'addresses': [address[:-9]]
    }

    stringified = json.dumps(command)

    request = urllib2.Request(url="%s:%s" % (hostname, port), data=stringified, headers=headers)
    returnData = urllib2.urlopen(request).read()
    jsonData = json.loads(returnData)
    if 'hashes' in jsonData:

        print 'Transactions found, retrieving last 10...'

        command = {
            'command': 'getTrytes',
            'hashes': jsonData['hashes'][-10:]
        }

        stringified = json.dumps(command)

        request = urllib2.Request(url="%s:%s" % (hostname, port), data=stringified, headers=headers)
        returnData = urllib2.urlopen(request).read()
        jsonData = json.loads(returnData)
        tx_count = 1
        if 'trytes' in jsonData:
            num_tx = len(jsonData['trytes'])
            for tryte in jsonData['trytes']:
                tx = Transaction.from_tryte_string(tryte)
                enc_message = TryteString(tx.signature_message_fragment)
                epoch = datetime.datetime.fromtimestamp(float(tx.attachment_timestamp)/1000.)
                fmt = "%Y-%m-%d %H:%M:%S"
                timestamp = epoch.strftime(fmt)
                try:
                    data = json.loads(enc_message.decode())
                except ValueError:
                    # Decoding seems to blow up every so often.
                    pass
                # These are specific to my mqtt data stream, need to make this more flexible.
                if 'topic' in data and 'mcutemp' in data:
                    dataset[timestamp] = {'device': data['topic'], 'temp': data['mcutemp'], 'tx': tx.hash}
                    print 'Fetching transaction %s of %s ...' % (tx_count, num_tx)
                    tx_count += 1
        sorted_data = OrderedDict(sorted(dataset.items(), key=lambda x: parse(x[0])))
        for value in sorted(sorted_data.keys(), reverse=True):
            print '%s %s' % (value, sorted_data[value])

def main():
    description = 'Simple IOTA interface to messages stored on the Tangle'
    parser = argparse.ArgumentParser(version=__version__, description=description)
    parser.add_argument('-a', '--address', help='Address on the Tangle where sensor data is stored', default=None)
    parser.add_argument('-host', '--hostname', help='Tangle light node address', default='https://nodes.thetangle.org')
    parser.add_argument('-port', '--port', help='Tangle light node port', default='443')
    args = parser.parse_args()
    run(args.address, args.hostname, args.port)

if __name__ == '__main__':
    main()
