import pandas as pd
import bundestag_api


def get_metadata(key = 'rgsaY4U.oZRQKUHdJhF9qguHMkwCGIoLaqEcaHjYLF'):
    '''
    Returns Bundestagsprotokolle of period 18 and 19 as list of dictionaries
    
    Meta data are:
    aktualisiert, datum, dokumentart, dokumentnummer, fundstelle, herausgeber, id, 
    pdf_hash, titel, typ, vorgangsbezug, vorgangsanzahl, wahlperiode

    Params: 
     str: current api key

    Returns:
     list: metadata as list of dicts
    '''
    # Initialize data (will be list of dictionaries)
    all_protocolls_18_19 = []
    
    bta = bundestag_api.btaConnection(apikey = key)
    data = bta.query(resource="plenarprotokoll", num=1000)
    count = 0
    
    for d in data:
        if (d['wahlperiode'] == 18 or d['wahlperiode'] == 19) and d['herausgeber'] == 'BT':  # nur Bundestag (nicht Bundesrat)
            all_protocolls_18_19.append(d)
            count+=1
            
    print(f'Plenarprotkolle (Bundestag) aus den Wahlperioden 18 und 19 geladen. Anzahl: {count}')

    return all_protocolls_18_19


def clean_protocols(protocols):
    '''
    For a given dataframe of protocols (with text), returns a cleaned version with only the main text:
    - no contents
    - no title
    - no appendix
    Params: 
     pd.DataFrame: data

    Returns:
     pd.DataFrame: cleaned data
    '''
    # alle Namen in Liste speichern
    known_names = ['Präsident Dr. Wolfgang Schäuble:', 'Präsident Dr. Wolfgang Schäuble :', 
                   'Präsident Dr. Norbert Lammert:', 'Präsident Dr. Norbert Lammert:', 'Präsident Prof. Dr. Norbert Lammert:', 'Präsident Dr. Norbert Lammert :', 'Präsident Dr. Norbert Lammert :',
                   'Vizepräsidentin Claudia Roth:', 'Vizepräsident Dr. Hans-Peter Friedrich', 'Vizepräsident Wolfgang Kubicki',
                   'Vizepräsident Thomas Oppermann:', 'Vizepräsidentin Petra Pau:', 'Alterspräsident Dr. Hermann Otto Solms:',
                   'Vizepräsident Johannes Singhammer:', 'Vizepräsidentin Ulla Schmidt:', 'Vizepräsident Peter Hintze:',
                   'Vizepräsidentin Edelgard Bulmahn:', 'Alterspräsident Dr. Heinz Riesenhuber:']
    
    protocols['text_split'] = ''
    protocols['text_relevant'] = ''
    
    for index, row in protocols.iterrows():
        t = row['text']
        split_text = t.split('\n\n\n\n\n\n')    # Inhaltsverzeichnis löschen: alles vor: \n\n\n\n\n\n\n\n
        protocols.at[index, 'text_split'] = split_text
        
        for s in split_text:
            s = s.strip()
            isrelevant = False
            for n in known_names:
                if s.startswith(n):
                    isrelevant = True
            if isrelevant:
                protocols.at[index, 'text_relevant'] = s
    
    # zusätzlich bei "Die Sitzung ist geschlossen" oder "(Schluss: )" abschneiden?
    
    return protocols


def party_shares(protocols):
    '''
    For a given dataframe of protocols, returns a dataframe with 1 row per protocol and party 
    -> rows: row_num*5 for 18th period and row_num*6 for 19th period
    Columns: protocol_id, party, text

    Params: 
     pd.DataFrame: data

    Returns:
     pd.DataFrame: cleaned data
    '''
    return protocols


def get_textdata(pure_text = True, key = 'rgsaY4U.oZRQKUHdJhF9qguHMkwCGIoLaqEcaHjYLF'):
    '''
    Returns protocoll text + protocoll id
    metadata as list of dicts
    Params: 
     bool: pure_text (if True, return cleaned text with clean_protocoll() function)
     str: current api key

    Returns:
     pd.DataFrame: data as dataframe
    '''
    bta = bundestag_api.btaConnection(apikey = key)
    metadata = get_metadata()
    result_list = []

    for protocol in metadata:
        p = bta.get_plenaryprotocol(protocol['id']) # get extensive data for specific protocol
        result_list.append([protocol['id'], p['text']])
    
    protocols = pd.DataFrame(result_list, columns = ['id', 'text'])
                                  
    if pure_text:
        protocols = clean_protocols(protocols)[['id', 'text_relevant']] # select only main text
        protocols = protocols.rename(columns = {'text_relevant': 'text'})
        return protocols
    else: 
        return protocols