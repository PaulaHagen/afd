import pandas as pd
import re
import bundestag_api


def identify_interruptions(protocols):
    '''
    For a given dataframe of protocols, returns a dataframe, where the main text is separated from the interruptions.
    Any utterances from moderating people, that do not speak for any party, are excluded.
    Final Columns: id, main_text, interruptions

    Params: 
     pd.DataFrame: data

    Returns:
     pd.DataFrame: data with column 'main_text' and 'interruptions'
    '''
    new_protocols = protocols.copy()
    new_protocols['main_text'], new_protocols['interruptions'] = '', ''

    # Define the parties
    parties = ['SPD', 'CDU/CSU', 'DIE LINKE', 'BÜNDNIS 90/DIE GRÜNEN', 'AfD', 'FDP']

    # Loop over all texts:
    for index, row in new_protocols.iterrows():
        t = row['text']

        # Regular expression to identify interruptions (but not when it's just one party in parentheses 
        # -> we need to keep that info to know, who is speaking)
        interruption_pattern_main = re.compile(r'\((?!(?:' + '|'.join(parties) + ')\\))[^)]+\\)')

        # Separate main text and interruptions
        main_text = re.sub(interruption_pattern_main, '', t)

        # Find all matches of interruptions in the parliament session text
        interruption_pattern_inter = re.compile(r'\([^)]+\)')
        interruptions = interruption_pattern_inter.findall(t)

        # Write main text into new column
        new_protocols.at[index, 'main_text'] = main_text
        new_protocols.at[index, 'interruptions'] = interruptions

    return new_protocols


def get_mdb(key = 'rgsaY4U.oZRQKUHdJhF9qguHMkwCGIoLaqEcaHjYLF'):
    '''
    Returns a list of relevant politician, who are MdB (of period 18 and 19)

    Returns:
     list: politicians with full name
    '''
    bta = bundestag_api.btaConnection(apikey = key)
    data = bta.search_person(num = 10000)

    mdb = []
    try:

        for p in data:
            if p['wahlperiode'] == 18 or p['wahlperiode'] == 19:
                mdb.append(p['vorname'] + ' ' + p['nachname'])
    except: KeyError

    try:     
        for p in data:  
            for role in p['person_roles']:
                if role['funktion'] == 'MdB' and (18 in role['wahlperiode_nummer'] or 19 in role['wahlperiode_nummer']):
                    mdb.append(role['nachname'] + ' ' + role['nachname'])

    except: KeyError

    return list(set(mdb)) # Turn into set to remove duplicates


def remove_president_text(protocols):
    '''
    For a given dataframe of protocols, returns a dataframe, where all utterances by presidents (-> neutral, no party)
    from the main text are removed.
    Columns: id, text, main_text, interruptions, neutral_text

    Params: 
     pd.DataFrame: data

    Returns:
     pd.DataFrame: data, with new column neutral_text
    '''
    new_protocols = protocols.copy()
    new_protocols['neutral_text'] = ''

    # Define the parties and persons
    parties = ['SPD', 'CDU/CSU', 'DIE LINKE', 'BÜNDNIS 90/DIE GRÜNEN', 'AfD', 'FDP']

    mdb = get_mdb()

    neutral_persons = ['Präsident Dr. Wolfgang Schäuble:', 'Präsident Dr. Wolfgang Schäuble :', 'Präsident Dr. Wolfgang Schäuble :', 'Präsident Dr. Wolfgang Schäuble:',
                   'Präsident Dr. Norbert Lammert:', 'Präsident Dr. Norbert Lammert:', 'Präsident Prof. Dr. Norbert Lammert:', 'Präsident Dr. Norbert Lammert :', 'Präsident Dr. Norbert Lammert :',
                   'Vizepräsidentin Claudia Roth:', 'Vizepräsident Dr. Hans-Peter Friedrich', 'Vizepräsident Dr. Hans-Peter Friedrich', 'Vizepräsident Wolfgang Kubicki',
                   'Vizepräsident Thomas Oppermann:', 'Vizepräsidentin Petra Pau:', 'Alterspräsident Dr. Hermann Otto Solms:', 'Alterspräsident Dr. Hermann Otto Solms:'
                   'Vizepräsident Johannes Singhammer:', 'Vizepräsidentin Ulla Schmidt:', 'Vizepräsident Peter Hintze:',
                   'Vizepräsidentin Edelgard Bulmahn:', 'Alterspräsident Dr. Heinz Riesenhuber:']

    # Loop over all texts:
    for index, row in new_protocols.iterrows():
        t = row['main_text']
        
        # Initialize a list to store utterances of neutral persons
        neutral_utterances = []

        # Split the data into utterances based on newlines
        utterances = [line.strip() for line in t.split('\n') if line.strip()]
        # Flag to check if the current utterance is from a neutral person
        is_neutral_person = False

        # Iterate through each utterance
        for utterance in utterances:
            # Check if the utterance belongs to a neutral person
            if any(neutral_person in utterance for neutral_person in neutral_persons):
                is_neutral_person = True
            elif utterance.endswith(":"):
                is_neutral_person = False
    
            # Add the utterance to the list if it's from a neutral person
            if is_neutral_person:
                neutral_utterances.append(utterance)

        # Save neutral utterances as new column
        new_protocols.at[index, 'neutral_text'] = neutral_utterances

        # Remove neutral utterances from main text
        utterances_new = utterances.copy()
        for u in utterances:
            if u in neutral_utterances and u not in mdb and u not in parties: # Make sure, important info doesn't get removed!
                utterances_new.remove(u) 
        
        new_protocols.at[index, 'main_text'] = '\n'.join(utterances_new)

    return new_protocols


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
