"""---If the libary is in a different folder we need to use the sys module---"""
import sys
# insert at 1, 0 is the script path:
sys.path.insert(1, "C:/Users/Luki/Documents/GitHub/ReadSensorValues/python")

"""--------------Bar chart and MyPort example------------------"""
import mylib.myio.myport as mp
import mylib.myplot.mygraph as mg


port = mp.MyPort("COM5", baudrate=19200) # open a serial connection to arduino uno
print(port) # look at the properties of the connection
nob = 8 # nob ... number of bars
mg.real_time_data_bar_chart(port.read_csv_for_bar, nob, "sensor", 80)
port.close() # close the port!
