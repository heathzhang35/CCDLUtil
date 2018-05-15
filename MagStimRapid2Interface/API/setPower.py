import argparse
import requests

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Sets the power level of the TMS machine via a server on the given port')
    parser.add_argument('port', type=int)
    parser.add_argument('powerLevel', type=int)
    args = parser.parse_args()

    res = requests.post('http://localhost:%d/TMS/power/%d' % (args.port, args.powerLevel))
    print res.status_code, res.text
    res.close()
