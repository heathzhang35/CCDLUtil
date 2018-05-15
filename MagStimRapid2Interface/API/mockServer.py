from mock import patch, MagicMock
import server

# Mock out the serial port
with patch('serial.Serial') as mockedSerialPort:
    serialObj = MagicMock()
    mockedSerialPort.side_effect = lambda: serialObj
    
    # Print out whatever is being written to the serial port
    def show_me(data):
        print data
    serialObj.write.side_effect = show_me
    
    server.do_main()
