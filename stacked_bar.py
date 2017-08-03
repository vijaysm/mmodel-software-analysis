import matplotlib.pyplot as plt
import seaborn as sns


def stacked_bar_chart(pivoted_df, stack_vals, labels, y_label, filename, color1, color2):
    #
    # stacked_bar_chart: draws and saves a barchart figure to filename
    #
    # pivoted_df: dataframe which has been pivoted so columns correspond to the values to be plotted
    # stack_vals: the column names in pivoted_df to plot
    # level_values_field: column in the dataframe which has the values to be plotted along the x axis (typically time dimension)
    # chart_title: how to title chart
    # x_label: label for x axis
    # y_label: label for y axis
    # filename: full path filename to save file
    # color1: first color in spectrum for stacked bars
    # color2: last color in spectrum for stacked bars; routine will select colors from color1 to color2 evenly spaced
    #
    # Implementation: based on (http://randyzwitch.com/creating-stacked-bar-chart-seaborn/; https://gist.github.com/randyzwitch/b71d47e0d380a1a6bef9)
    # this routine draws overlapping rectangles, starting with a full bar reaching the highest point (sum of all values), and then the next shorter bar
    # and so on until the last bar is drawn.  These are drawn largest to smallest with overlap so the visual effect is that the last drawn bar is the
    # bottom of the stack and in effect the smallest rectangle drawn.
    #
    # Here "largest" and "smallest" refer to relationship to foreground, with largest in the back (and tallest) and smallest in front (and shortest).
    # This says nothing about which part of the bar appear large or small after overlap.
    #
    sns.set_style('ticks')

    color_spectrum = list(color1.range_to(color2, len(stack_vals)))
    plt.clf()
    #
    stack_total_column = 'Stack_subtotal_xyz'  # placeholder name which should not exist in pivoted_df
    bar_num = 0
    legend_rectangles = []
    legend_names = []
    for bar_part in stack_vals:    # for every item in the stack we need to compute a rectangle
        stack_color = color_spectrum[bar_num].get_hex_l()  # get_hex_l ensures full hex code of color
        sub_count = 0
        pivoted_df[stack_total_column] = 0
        stack_value = ""
        for stack_value in stack_vals:  # for every item in the stack we create a new subset [stack_total_column] of 1 to N of the sub values
            pivoted_df[stack_total_column] += pivoted_df[stack_value]  # sum up total
            sub_count += 1
            if sub_count >= len(stack_vals) - bar_num:  # we skip out after a certain number of stack values
                break
        # now we have set the subtotal and can plot the bar.  reminder: each bar is overalpped by smaller subsequent bars starting from y=0 axis
        bar_plot = sns.barplot(data=pivoted_df, x=pivoted_df[labels],
                               y=stack_total_column, color=stack_color)
        legend_rectangles.append(plt.Rectangle((0, 0), 1, 1, fc=stack_color, edgecolor='none'))
        legend_names.append(stack_value)   # the "last" stack_value is the name of that part of the stack
        bar_num += 1

    l = plt.legend(legend_rectangles, legend_names, loc=2, ncol=1, prop={'size': 12})
    l.draw_frame(False)
    bar_plot.set(xlabel='', ylabel=y_label)
    plt.xticks(rotation=90)

    plt.tight_layout()

    ax = plt.gca()
    ax.set_yscale("log")
    ax.tick_params(bottom='off')
    plt.savefig(filename)
    # plt.show()
    plt.close()
