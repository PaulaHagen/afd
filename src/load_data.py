import pandas as pd
import numpy as np
# you might need to install lxml

def get_df():
    '''
    Returns Bundestagsprotokolle of period 18 and 19 as pandas Dataframe
    :return: pandas dataframe containing data
    '''
    # Initialize data frame
    df = pd.DataFrame()
    
    # Iterate over the documents of period 18 and append to df 
    protokolle_18 = np.arange(18001, 18246)
    default_path_18 = 'data/pp18/'
  
    for p in  protokolle_18:
        p_path = default_path_18 + str(p) + '.xml'
        p_df = pd.read_xml(p_path, xpath = '//DOKUMENT')  # name of XML ('DOKUMENT') has to be specified
        df = pd.concat([df, p_df])


    # Now repeat for period 19
    protokolle_19 = np.arange(19001, 19240)
    default_path_19 = 'data/pp19/'

    for p in  protokolle_19:
        p_path = default_path_19 + str(p) + '.xml'
        p_df = pd.read_xml(p_path, xpath = '//DOKUMENT')  # name of XML ('DOKUMENT') has to be specified
        df = pd.concat([df, p_df])

    return df