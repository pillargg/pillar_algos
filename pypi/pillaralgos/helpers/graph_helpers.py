'''
Functions to help with graphing pretty graphs
'''

def plot_with_time(x,y,data, xformat='%H:%m'):
    '''
    Plots a scatterplot with the xaxis neatly formatted
    
    input
    -----
    x: str
        Column name. Column must be datetime
    y: str
    data: pd.DataFrame
    xformat: str
        Format xaxis should be displayed in, using strftime syntax
    '''
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import seaborn as sns
    
    fig, ax = plt.subplots()
    sns.scatterplot(x=x,y=y,data=data)
    
    myFmt = mdates.DateFormatter(xformat)
    ax.xaxis.set_major_formatter(myFmt)
