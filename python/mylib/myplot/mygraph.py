from matplotlib import pyplot as plt
import matplotlib.animation as animation


def plot_data(list_of_lists, label):
    """
    Plots the data in the list_of_lists e.g: [[], [], []]
    then 3 lines will be plotted labled as: label0, label1, label2
    """
    fig = plt.figure()
    ax = plt.subplot(1, 1, 1)
    ax.clear()
    for i, a_list in enumerate(list_of_lists):
        ax.plot(a_list, label=f"{label}{i}")
    plt.legend(loc="upper left")
    plt.show()


def plot_real_time_data(list_of_lists, update_func, label, interval):
    """
    Update the list_of_lists with the update_func every interval ms and
    then plot the new list_of_lists with the labels: label0, label1...
    """
    fig = plt.figure()
    ax = plt.subplot(1, 1, 1)

    def redraw(_, list_of_lists, update_func, label, ax):
        # update the list_of_lists
        update_func(list_of_lists)
        ax.clear()
        # plot the whole data from list_of_lists on a the cleared graph
        for i, data_list in enumerate(list_of_lists):
            ax.plot(data_list, label=f"{label}{i}")
        plt.legend(loc="upper left")  # fix the label pos or it will jump around

    # calls the redraw function with fargs as arguments every interval ms:
    ani = animation.FuncAnimation(fig,
                                  redraw,
                                  fargs=(list_of_lists, update_func, label, ax),
                                  interval=interval)
    plt.show()


def real_time_data_bar_chart(update_func, nob, label, interval, min=0, max=1023):
    """
    The update_func should take a list as argument which will be updated, the
    format: [bar0, bar1,... bar(nob-1)] with nob ... number of bars
    The bars are labeled like: label0, label1,...
    We call the update_func every interval ms and update the bar heights
    """
    a_list = [0 for _ in range(nob)]
    fig = plt.figure()
    bars = plt.bar([x + 1 for x in range(nob)], a_list, align="center", width=0.3,
                   tick_label=[f"{label}{x}" for x in range(nob)])
    plt.ylim(min, max)

    def rescale_bars(_, a_list, update_function, nob, bars):
        # update the a_list
        update_function(a_list, nob)
        # rescale bars accordingly
        for i, bar in enumerate(bars):
            bar.set_height(a_list[i])

    # calls the rescale_bars function with fargs as arguments every interval ms:
    ani = animation.FuncAnimation(fig,
                                  rescale_bars,
                                  fargs=(a_list, update_func, nob, bars),
                                  interval=interval)
    plt.show()


def main():
    """
    This is an example of how to use this module, the update function in an real
    life scenario would read data from a connection to a measurement unit instead!
    """
    import time
    import random

    def get_fake_data_for_bars(a_list, nob):
        for i in range(nob):
            a_list[i] = int(random.randrange(50, 900, 1))

    nob = 8  # number of bars
    real_time_data_bar_chart(get_fake_data_for_bars, nob, "sensor", 200)

    data = [[1, 2, 3, 7, 8, 15, 2],
            [1, 10, 3, 10, 8, 19, 2],
            [4, 2, 7, 7, 8, 10, 2]]

    plot_data(data, "sensor")

    def get_fake_data_for_plot(list_of_lists):
        for a_list in list_of_lists:
            a_list.append(int(random.randrange(0, 900, 10)))

    number_of_sensors = 5
    data = [[] for _ in range(0, number_of_sensors)]
    plot_real_time_data(data, get_fake_data_for_plot, "sensor", 200)


if __name__ == '__main__':
    main()
