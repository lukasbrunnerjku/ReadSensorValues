
def read_data_from_file(filename, **kwargs):
    data_lists = []
    for i in range(kwargs.get("size", 1)):
        data_lists.append([])  # add an empty list object
    with open(filename, "r") as file:
        lines = file.read().split("\n")
    for line in lines:
        # skip empty lines
        if len(line) < 1:
            continue
        str_values = line.split(",")
        # check if the size= argument actually makes sense
        if len(str_values) < kwargs.get("size", 1):
            print("Error in function: myfile.read_data_from_file()\n" +
                  "The keyword argument: size= is greater than the number of csv values in file: " + filename)
            return []
        for i, data_list in enumerate(data_lists):
                data_list.append(float(str_values[i]))
    return data_lists


def main():
    """
    This is an example of how to use this module!
    """
    data = read_data_from_file("myport_data.txt", size=8)
    print(data)


if __name__ == '__main__':
    main()
