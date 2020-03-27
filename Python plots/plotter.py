# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 11:49:56 2020

@author: Queralt Altés Buch
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import mpld3
from mpld3 import plugins

DATA_PATH = "../COVID 19/"

def csv_to_df(csv_file):
    '''
    Returns a DataFrame with the data of the csv_file with 
    - the names of regions as columns
    - timestamp as index
    '''
    df = pd.read_csv(csv_file)
    days = pd.to_datetime(list(df.columns)[2:], format='%Y/%m/%d')
    regions = list(df.CCAA.values)
    data = df.as_matrix(columns=list(df.columns)[2:])
    df_new = pd.DataFrame(data.T, index=days, columns=regions)
    return df_new

def plot_ccaa(df, columns, title, rate=False, dif=False, pop=False):
    '''
    Plots the data of certain columns of the df.
    Parameters
    ----------
    df : DataFrame
        the data (index=timestamp, columns=regions)
    columns: list
        list of the regions that have to be plotted
    title: string
        title of the graph
    rate: Boolean
        True for plotting the evolution of the rate (data one day/data day before)
    dif: Boolean
        True for plotting the daily data evolution
    pop: Boolean
        True for plotting the evolution of the data per 100000 inhabitants
    '''
    df.plot(y=columns, marker='o', title=title)
    if rate:
        shift = df.shift(periods=+1)
        rates = df/shift
        rates.plot(y=columns, marker='o', title='Tasa de '+title)
    if dif:
        shift = df.shift(periods=+1)
        dif = df-shift
        dif.plot(y=columns, marker='o', title=title+' cada día')
    if pop:
        population={'Andalucía':8414240,            # Data from INE 2019
                    'Aragón':1319291,
                    'Asturias':1022800,
                    'Baleares':1149460,
                    'Canarias':2153389,
                    'Cantabria':581078,
                    'Castilla-La Mancha':2032863,
                    'Castilla y León':2399548,
                    'Cataluña':7675217,
                    'Ceuta':84777,
                    'C. Valenciana':5003769,
                    'Extremadura':1067710,
                    'Galicia':2699499,
                    'Madrid':6663394,
                    'Melilla':86487,
                    'Murcia':1493898,
                    'Navarra':654214,
                    'País Vasco':2207776,
                    'La Rioja':316798,
                    'Total':47026208}
        df_by_pop = pd.DataFrame(index=df.index)
        for ca in columns:
            df_by_pop[ca]=df[ca]/population[ca]*100000
        df_by_pop.plot(y=columns, marker='o', title=title+' por cada 100000 habitantes')

def plot_distr_hosp(dict_df, ca):
    '''
    Plots the line of cases that needed hospitalization and fills in different
    colours the part that is in intensive care and the rest
    Parameters
    ----------
    dict_df : dictionary
        dictionary of all the data frames with items being: cases, death, hosp, healed, uci
    ca: string
        Name of the region to plot
    '''
    df_hosp=dict_df['hosp']
    df_uci=dict_df['uci']

    x=df_hosp.index
    y0=[0]*len(x)
    y1=df_uci[x[0]:][ca]
    y2=df_hosp[ca]          # Because UCI is a subset of hosp

    plt.figure()
    plt.plot(x,y2,label='Casos que han precisado hospitalización (incluyendo UCI)')
#    plt.plot(df_hosp[ca])
#    plt.plot(df_uci[x[0]:][ca])
    #plt.plot(df_uci[df_hosp.index[0]:][ca] + df_hosp[ca])
    plt.title('Distribución de los casos que han precisado hospitalización en ' + ('Catalunya' if ca=='Cataluña' else ca))
    plt.fill_between(x, y2, y1, alpha=0.4, label='Casos sin ingreso en UCI')
    plt.fill_between(x, y1, y0, alpha=0.4, label='Casos con ingreso en UCI')
    plt.legend(loc='upper left')
    
def plot_distr_cases(dict_df,ca):
    '''
    Plots the line of confirmed cases and fills in different
    colours distinguishing: active, deaths and healed.
    Parameters
    ----------
    dict_df : dictionary
        dictionary of all the data frames with items being: cases, death, hosp, healed, uci
    ca: string
        Name of the region to plot
    '''
    df_cases=dict_df['cases']
    df_deaths=dict_df['deaths']
    df_healed=dict_df['healed']
    x=df_healed.index
    y1=df_cases[x[0]:][ca]
    y2=df_deaths[x[0]:][ca]+df_healed[x[0]:][ca]
    y3=df_healed[x[0]:][ca]
    plt.figure()
    plt.plot(x,y1,color='red',label='Casos confirmados acumulados')
    plt.title('Distribución de los casos registrados en ' + ('Catalunya' if ca=='Cataluña' else ca))
    plt.fill_between(x, y1, y2, alpha=0.4, label='Casos activos')
    plt.fill_between(x, y2, y3, alpha=0.4, label='Personas fallecidas acumuladas')
    plt.fill_between(x, y3, [0]*len(x), alpha=0.4, label='Personas curadas acumuladas')
    plt.legend(loc='upper left')
    
    
def bar_dif_new(df_cases,df_deaths,df_healed,ca):
    '''
    Plots a bar chart comparing the daily confirmed cases and 
    actual daily new cases of one region
    '''
    labels = list(df_healed.index.date)# ['G1', 'G2', 'G3', 'G4', 'G5']
    idx = df_healed.index
    shift = df_cases.shift(periods=+1)
    dif = df_cases[idx[0]:]-shift[idx[0]:]                # Difference of confirmed cases
    new = dif[idx[0]:] + df_deaths[idx[0]:] + df_healed   # Actual new cases

    x = np.arange(len(labels)) #np.array(list(df_hosp.index.day))  # #np.array(df_hosp.index.values)  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, dif[idx[0]:][ca], width, label='Casos confirmados de un día: Casos del día anterior + Nuevos casos - Altas - Fallecidos')
    rects2 = ax.bar(x + width/2, new[idx[0]:][ca], width, label='Nuevos casos diarios')
    ax.set_ylabel('Personas')
    ax.set_title('Comparación de casos confirmados diarios con nuevos casos diarios en '+ca)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = int(rect.get_height())
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')
    autolabel(rects1)
    autolabel(rects2)
    fig.tight_layout()
    plt.show()
    
def plot_log(df, columns, title, min_num=200):
    '''
    Logarithmic plot of certain columns of df, since the first day than more 
    than Y=min_num was registered.
    Parameters
    ----------
    df : DataFrame
        the data (index=timestamp, columns=regions)
    columns: list
        list of the regions that have to be plotted
    title: string
        Title of the plot
    min_num: integer
        Value of Y that corresponds to X=0
    '''
    g = df[df > min_num]
    r = []
    for c in columns:
        r.append(g[c].dropna(how="any").values)
    plt.figure()
    plt.title(title)
    for i, c in zip(r, columns):
        plt.plot(i, label=c)
    plt.semilogy()
    plt.legend()

def interactive_plot(df,columns,title,save_name,logy=False,min_num=50,show=False):
    '''
    Interactive plot of certain columns of df.
    Parameters
    ----------
    df : DataFrame
        the data (index=timestamp, columns=regions)
    columns: list
        list of the regions that have to be plotted
    title: string
        Title of the plot
    save_name: string
        Name given to the saved html file
    logy: Boolean
        True if logarithmic plot
    min_num: integer
        Value of Y that corresponds to X=0 (only used when logy=True)
    '''
    fig, ax = plt.subplots(figsize=(10,6))
    if logy:
        g = df[df > min_num]
        r = []
        for c in columns:
            r.append(g[c].dropna(how="any").values)
        for i, c in zip(r, columns):
            ax.plot(i, label=c)
        ax.semilogy()
    else:   
        for c in columns:
            ax.plot(df[c], label=c)
        #    for key, val in df[columns].iteritems():
        #        l, = ax.plot(val.index, val.values, '-o', label=key)
    #ax.legend()                

    handles, labels = ax.get_legend_handles_labels() # return lines and labels
    interactive_legend = plugins.InteractiveLegendPlugin(handles,
                                                         labels,
                                                         alpha_unsel=0.2,
                                                         alpha_over=1.5, 
                                                         start_visible=True)
    plugins.connect(fig, interactive_legend)
    fig.subplots_adjust(right=0.7)
    ax.set_xlabel('Días', size=14)
    ax.set_ylabel('Personas', size=14)
    ax.set_title(title, size=18)
    if show:
        mpld3.show()
    mpld3.save_html(fig,'docs/'+save_name+'.html', template_type='simple')

#%% Importing data

df_cases = csv_to_df(DATA_PATH+'ccaa_covid19_casos.csv')         # número de casos registrados por Comunidad Autónoma.
df_deaths = csv_to_df(DATA_PATH+'ccaa_covid19_fallecidos.csv')   # número de fallecidos registrados por Comunidad Autónoma
df_uci = csv_to_df(DATA_PATH+'ccaa_covid19_uci.csv')             # número de personas en la UCI registrados por Comunidad Autónoma
df_healed = csv_to_df(DATA_PATH+'ccaa_covid19_altas.csv')        # número de personas curadas registradas por Comunidad Autónoma
df_hosp = csv_to_df(DATA_PATH+'ccaa_covid19_hospitalizados.csv') # número de personas hospitalizadas por Comunidad Autónoma

ccaa = list(df_cases.columns)
ccaa_small = ['Andalucía', 'Aragón', 'Baleares',
              'Castilla-La Mancha', 'Castilla y León', 'Cataluña',
              'C. Valenciana', 'Extremadura', 'Galicia', 'Madrid',
              'Murcia', 'Navarra', 'País Vasco', 'La Rioja']
ccaa_5 = ['Madrid','Cataluña','País Vasco', 'C. Valenciana', 'Navarra']
dict_df={'cases':df_cases,'deaths':df_deaths,'healed':df_healed,'uci':df_uci,'hosp':df_hosp}
population={'Andalucía':8414240,            # Data from INE 2019
            'Aragón':1319291,
            'Asturias':1022800,
            'Baleares':1149460,
            'Canarias':2153389,
            'Cantabria':581078,
            'Castilla-La Mancha':2032863,
            'Castilla y León':2399548,
            'Cataluña':7675217,
            'Ceuta':84777,
            'C. Valenciana':5003769,
            'Extremadura':1067710,
            'Galicia':2699499,
            'Madrid':6663394,
            'Melilla':86487,
            'Murcia':1493898,
            'Navarra':654214,
            'País Vasco':2207776,
            'La Rioja':316798,
            'Total':47026208}

#%% Examples of plots with plot_ccaa

# Casos registrados
plot_ccaa(df_cases, ccaa_5, 'Casos registrados', rate=True, dif=True, pop=True)
plot_ccaa(df_cases, ['Total'], 'Casos registrados', rate=True, dif=True)
plot_ccaa(df_cases, ccaa_5+['Total'], 'Casos registrados', rate=True, dif=True)
plot_ccaa(df_cases, ccaa, 'Casos registrados', rate=True, dif=True)
plot_ccaa(df_cases, ccaa, 'Casos registrados', pop=True)

# Fallecidos
plot_ccaa(df_deaths, ccaa_5, 'Fallecidos registrados', rate=True, dif=True,pop=True)

# Casos han precisado hospitalización
plot_ccaa(df_uci, ccaa_5, 'Casos han precisado ingreso en UCI')
plot_ccaa(df_hosp, ccaa_5, 'Casos han precisado hospitalización (incluyendo UCI)')

# Personas curadas
plot_ccaa(df_healed, ccaa_5, 'Personas curadas registradas')


#%% Study of one CA

# Distribución de los casos en Madrid y Cataluña
plot_distr_hosp(dict_df, 'Madrid')
plot_distr_cases(dict_df,'Madrid')
plot_distr_hosp(dict_df, 'Cataluña')
plot_distr_cases(dict_df,'Cataluña')

#bar_dif_new(df_cases,df_deaths,df_healed,'Cataluña')
#bar_dif_new(df_cases,df_deaths,df_healed,'Madrid')

# Evolución de algunas regiones desde el primer día en que se registraron más de 50 casos
plot_log(df_cases, ccaa_5, 'Casos confirmados', min_num=50)


#%% Interactive plot

interactive_plot(df_cases,ccaa,
                 'Evolución desde el primer día en que se registraron más de 50 casos en cada región',
                 'hoy_log_casos_acumulados',
                 logy=True)

interactive_plot(df_cases,ccaa[:-1],
                 'Casos confirmados por comunidad autónoma',
                 'hoy_casos_acumulados',
                 logy=False)

interactive_plot(df_deaths,ccaa,
                 'Evolución desde el primer día en que se registró más de 5 muertes',
                 'hoy_log_fallecidos_acumulados',
                 logy=True,min_num=5)

interactive_plot(df_deaths,ccaa[:-1],
                 'Fallecidos por comunidad autónoma',
                 'hoy_fallecidos_acumulados',
                 logy=False,min_num=5)

#%% Interactive plot of data per 100000 inhabitants

dict_title={'cases':'Casos confirmados', 'deaths':'Fallecidos',
            'healed':'Personas curadas', 
            'hosp':'Personas que han precisado hospitalización (incluyendo UCI)',
            'uci':'Personas que han precisado ingreso en la UCI'}
dict_save={'cases':'casos', 'deaths':'fallecidos',
            'healed':'curados', 
            'hosp':'hospitalizados',
            'uci':'uci'}

study='deaths'
columns = ccaa
df = dict_df[study]
df_by_pop = pd.DataFrame(index=df.index)
for ca in columns:
    df_by_pop[ca]=df[ca]/population[ca]*100000
interactive_plot(df_by_pop,ccaa,
                 dict_title[study]+' por cada 100000 habitante',
                 'hoy_'+dict_save[study]+'_por_100000_habitante')

#%% Interactive plot of new confirmed cases

columns = ccaa[:-1]
study='healed'
logy=False 

logy_save='log_' if logy else ''
df = dict_df[study]
shift = df.shift(periods=+1)
dif = df-shift
interactive_plot(dif,columns,
                 dict_title[study]+' diarios por Comunidad Autónoma',
                 'hoy_'+logy_save+dict_save[study]+'_diarios',
                 logy=logy)

#%% Plot of distribution (active, healed, dead)

def plot_global_distr(dict_df,ccaa):
    fig, axs = plt.subplots(4,5,sharex=True,figsize=(12,10))
    pos=[[0,0],[0,1],[0,2],[0,3],[0,4],
         [1,0],[1,1],[1,2],[1,3],[1,4],
         [2,0],[2,1],[2,2],[2,3],[2,4],
         [3,0],[3,1],[3,2],[3,3],[3,4]]
#         [4,0],[4,1],[4,2],[4,3]
    df_cases=dict_df['cases']
    df_deaths=dict_df['deaths']
    df_healed=dict_df['healed']
    x=df_healed.index
    fig.suptitle('Distribución de los casos registrados por Comunidad Autónoma',fontsize=16)
    for i, ca in zip(pos, ccaa):
        y1=df_cases[x[0]:][ca]
        y2=df_deaths[x[0]:][ca]+df_healed[x[0]:][ca]
        y3=df_healed[x[0]:][ca]
        axs[i[0],i[1]].plot(x,y1,color='red',label='Casos confirmados acumulados')
        axs[i[0],i[1]].set_title(ca)
        axs[i[0],i[1]].fill_between(x, y1, y2, alpha=0.4, label='Casos activos')
        axs[i[0],i[1]].fill_between(x, y2, y3, alpha=0.4, label='Personas fallecidas acumuladas')
        axs[i[0],i[1]].fill_between(x, y3, [0]*len(x), alpha=0.4, label='Personas curadas acumuladas')
#        axs[i[0],i[1]].set_xticks(rotate=-45)
        plt.setp(axs[i[0],i[1]].get_xticklabels(), rotation=70, horizontalalignment='right')
    axs[0,0].legend(loc='lower left', bbox_to_anchor= (0.0, 1.21), ncol=4,
                   borderaxespad=0, frameon=False, fontsize=12)
    #mpld3.save_html(fig,'docs/hoy_distribucion_casos.html', template_type='simple')    
    
plot_global_distr(dict_df,ccaa)

