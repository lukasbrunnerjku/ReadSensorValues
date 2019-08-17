import mylib.myio.myport as mp
import mylib.myio.myfile as mf
import mylib.myplot.mygraph as mg

# open a serial connection to arduino uno
port = mp.MyPort("COM5", baudrate=19200)
# look at the properties of the connection
print(port)

# how much sensors should be read from:
number_of_sensors = 6
# now let's plot the incoming data of the arduino in real time
data = [[] for _ in range(0, number_of_sensors)]
# here we use the MyPort.read_csv function as our update function
# which will be called every 200ms and the graph is update in the same pace!
mg.plot_real_time_data(data, port.read_csv, "sensor", 80)

ans = input("Want to save the recorded data? (yes/no): ")
if "YES" in ans.upper():
    port.write_received_data_to_file("data.txt")

ans = input("Want to plot the saved data? (yes/no): ")
if "YES" in ans.upper():
    data = mf.read_data_from_file("data.txt", size=number_of_sensors)
    mg.plot_data(data, "sensor")

# close the port:
port.close()
