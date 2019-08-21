import serial

class Port(serial.Serial):

    def __init__(self, port, baudrate=9600, timeout=0.5):
        serial.Serial.__init__(self,
                               port=port,
                               baudrate=baudrate,
                               bytesize=serial.EIGHTBITS,
                               parity=serial.PARITY_NONE,
                               stopbits=serial.STOPBITS_ONE,
                               timeout=timeout)

    def read_csv(self, list_of_lists):
        """
        The number of list in list_of_lists e.g: [[], [], []] where we have 3
        list inside determines how much sensor values are acually read!
        If the arduino sends us always 8 csv sensor values we can save the
        first 3 sensor values in the list_of_lists!
        --------------------------------------------------------------------
        Returns True if reading attempt was successful, prints error message
        and False if something went wrong!
        """
        try:
            bytes = self.readline()
            line = bytes.decode("ascii")[:-2]
            str_values = line.split(",")
        except Exception as e:
            print(e, "\nbytes:", bytes)
            return False

        if len(str_values) < len(list_of_lists):
            print("Garbage Value: " + line + " less data received than expected!")
            return False
        try:
            for value in str_values:
                float(value)
        except ValueError:
            print("Garbage Value: " + line + " received, which cannot be converted to float!")
            return False

        for i, a_list in enumerate(list_of_lists):
            a_list.append(float(str_values[i]))
        return True

    def read_csv_for_bar(self, a_list, number_of_bars):
        """
        Takes a_list as input which will be updated with the csv values from
        the serial port where number_of_bars specifies how moch values
        will be written in a_list e.g: number_of_bars = 3 then a_list will
        look like [bar0, bar1, bar2] even if we receive 8 csv values,
        in the mygraph module a format like: [bar0, bar1, bar2,...] will be expected
        in real_time_data_bar_chart's update_func!
        --------------------------------------------------------------------
        Returns True if reading attempt was successful, prints error message
        and False if something went wrong!
        """
        try:
            bytes = self.readline()
            line = bytes.decode("ascii")[:-2]
            str_values = line.split(",")
        except Exception as e:
            print(e, "\nbytes:", bytes)
            return False

        if len(str_values) < number_of_bars:
            print("Garbage Value: " + line + " less data received than expected!")
            return False
        try:
            for value in str_values:
                float(value)
        except ValueError:
            print("Garbage Value: " + line + " received, which cannot be converted to float!")
            return False

        for i in range(number_of_bars):
            a_list[i] = float(str_values[i])
        return True


def main():
    """
    This is an exaple of how to use this module!
    """
    # create an instance of Port, baudrate has to match with arduino!
    port = Port("COM5", baudrate=19200)
    # print a description to check port properties
    print(port)
    number_of_sensors = 8
    list_of_lists = [[] for _ in range(number_of_sensors)]
    print(list_of_lists)
    # get 6 valid readings from port:
    readings = 6
    while readings > 0:
        if port.read_csv(list_of_lists):
            readings -= 1
    print("-----Data saved inside the list_of_lists-------")
    print(list_of_lists)

    a_list = [0 for _ in range(8)]
    while not port.read_csv_for_bar(a_list, 8):
        pass
    print("-----Data saved inside the a_list-------")
    print(a_list)

    port.close()


if __name__ == '__main__':
    main()
