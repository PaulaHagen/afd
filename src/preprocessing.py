import pandas as pd
import re
import bundestag_api
import ast
import datetime
from src.people import *
from src.load_data import get_metadata


def identify_interruptions(protocols):
    '''
    For a given dataframe of protocols, returns a dataframe, where the main text is separated from the interruptions.
    Final Columns: id, main_text, interruptions

    Params: 
     pd.DataFrame: data

    Returns:
     pd.DataFrame: data with column 'main_text' and 'interruptions'
    '''
    new_protocols = protocols.copy()
    new_protocols['main_text'], new_protocols['interruptions'] = '', ''

    # Define the parties
    parties = ['SPD', 'CDU/CSU', 'DIE LINKE', 'BÜNDNIS 90/DIE GRÜNEN', 'AfD', 'FDP', 'parteilos']

    # Loop over all texts:
    for index, row in new_protocols.iterrows():
        t = row['text']

        # Regular expression to identify interruptions (but not when it's just one party in parentheses 
        # -> we need to keep that info to know, who is speaking)
        # This also tracks the cities in parentheses, e.g., in Claudia Roth (Augsburg) (BÜNDNIS 90/DIE GRÜNEN)
        # -> so they are not included in main_text later
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


def remove_president_text(protocols):
    '''
    For a given dataframe of protocols, returns a dataframe, where all utterances by presidents and other neutral or moderating people
    from the main text are removed. They are saved in a column "neutral_text"
    Columns: id, text, main_text, interruptions, neutral_text

    Params: 
     pd.DataFrame: data

    Returns:
     pd.DataFrame: data, with new column neutral_text
    '''
    new_protocols = protocols.copy()
    new_protocols['neutral_text'] = ''

    # Define the parties and persons
    parties = ['SPD', 'CDU/CSU', 'DIE LINKE', 'BÜNDNIS 90/DIE GRÜNEN', 'AfD', 'FDP', 'parteilos']

    mdb = get_mdb()

    neutral_persons = get_neutral_persons()

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


def clean_gov_persons(protocols):
    '''
    For a given dataframe of protocols, returns a dataframe, where all mentionings of government people now follow the same format
    as the other MdB: "<<full name>> (<<party name>>):"
    Does this for main_text and interruptions
    Columns: id, text, main_text, interruptions, neutral_text

    Params: 
     pd.DataFrame: data

    Returns:
     pd.DataFrame: data, with modified column main_text
    '''
    new_protocols = protocols.copy()

    # Get government persons
    regierende_original = get_regierende(mdb_format=False, include_party=True)
    regierende_correct = get_regierende(mdb_format=True, include_party=True)

    for index, row in new_protocols.iterrows():
        t_main = str(row['main_text'])
        t_inter = str(row['interruptions'])

        # Split the data into utterances based on newlines
        utterances_main = [line.strip() for line in t_main.split('\n') if line.strip()]
        utterances_inter = [line.strip() for line in t_inter.split('\n') if line.strip()]

        # Replace all occurrences of government persons with new format
        for i in range(len(regierende_original)):
            person_old = f'{regierende_original[i][0]}:'
            person_new = regierende_correct[i]
            utterances_main = [u.replace(person_old, person_new) for u in utterances_main]
            utterances_inter = [u.replace(person_old, person_new) for u in utterances_inter]

        # Save new text in main_text column
        new_protocols.at[index, 'main_text'] = '\n'.join(utterances_main)
        new_protocols.at[index, 'interruptions'] = '\n'.join(utterances_inter)

    return new_protocols


def clean_and_split_text(protocols):
    '''
    For a given dataframe of protocols, returns a "clean" version of that dataframe. Uses the cleaning functions defined above.
    Columns: id, text, main_text, interruptions, neutral_text

    Params: 
     pd.DataFrame: data

    Returns:
     pd.DataFrame: data split into party contributions. Columns: protocol_id, party, text
    '''
    clean = identify_interruptions(protocols)
    clean = remove_president_text(clean)
    clean = clean_gov_persons(clean)

    return clean


def party_shares_main(protocols):
    '''
    For a given dataframe of protocols, returns a dataframe with 1 row per protocol and party (for the main text!)
    -> rows: row_num*5 for 18th period and row_num*6 for 19th period (+ "parteilos")
    Columns: protocol_id, party, text, text_type (here: main_text)

    Params: 
     pd.DataFrame: data

    Returns:
     pd.DataFrame: data split into party contributions. Columns: protocol_id, party, text, text_type
    '''
    # Initialise result list
    party_data = []

    # Loop over all texts:
    for index, row in protocols.iterrows():
        # Initialise result dictionary
        party_dict = {}

        # Split the data into lines
        lines = str(row['main_text']).split('\n')

        # Iterate through the lines to identify speakers and assign utterances to parties
        current_party = None
        current_speaker = None

        for line in lines:
            if line.strip():  # Skip empty lines
                if '(' in line and ')' in line and ':' in line:
                    
                    # Extract party information
                    party_start = line.index('(') + 1
                    party_end = line.index(')')
                    current_party = line[party_start:party_end]
                    party_dict.setdefault(current_party, [])
                    
                    # Extract speaker information
                    speaker_end = line.index(':')
                    current_speaker = line[:speaker_end].strip()
                    
                elif current_party and current_speaker:
                    # Assign utterances to the current speaker within the party
                    party_dict[current_party].append({current_speaker: line.strip()})

        # Write in result df
        this_id = row['id']

        for party, utterances in party_dict.items():
            utterances_str = '\n'.join([string for u in utterances for string in u.values()])
            party_data.append({'id': this_id, 'party': party, 'text': utterances_str, 'text_type': 'main_text'})

    new_protocols = pd.DataFrame(party_data)

    return new_protocols


def party_shares_inter(protocols):
    '''
    For a given dataframe of protocols, returns a dataframe with 1 row per protocol and party (for the interruptions!)
    -> rows: row_num*5 for 18th period and row_num*6 for 19th period (+ "parteilos")
    Columns: protocol_id, party, text, 

    Params: 
     pd.DataFrame: data

    Returns:
     pd.DataFrame: data split into party contributions. Columns: protocol_id, party, text
    '''
    # Initialise result list
    party_data = []

    # Define the parties
    parties = ['SPD', 'CDU/CSU', 'DIE LINKE', 'BÜNDNIS 90/DIE GRÜNEN', 'AfD', 'FDP', 'parteilos']

    # Define pattern for detecting text in brackets [ ]
    pattern = re.compile(r'\[[^\[\]]*\]')

    # Loop over all texts:
    for index, row in protocols.iterrows():
        # Initialise result dictionary
        party_dict = {}

        # Make sure interruptions is not empty
        if row['interruptions'] != '[]':

            # Turn interruptions list into list data type (is string before)
            interruptions_list = ast.literal_eval(row['interruptions'])
            # Turn the interruptions list into the correct string format with new lines, when new speaker or new utterance
            result_list = []
            
            for item in interruptions_list:

                # Remove parentheses around text
                item = item.replace('(', '')
                item = item.replace(')', '')

                # Remove city information in parentheses after name (so it isn't read as party name later on)
                item = pattern.sub(lambda x: x.group(0) if any(word in x.group(0) for word in parties) else '', item)

                # Turn the interruptions list into the correct string format with new lines, when new speaker or new utterance
                if ':' in item: # filter actual speech (not just applause)
                    # append new lines, so the format is the same as in the main text
                    item_list = item.split(': ')
                    item_string = ':\n'.join(item_list)
                    item_list = item_string.split(' – ')
                    item_string = '\n'.join(item_list)
                    result_list.append(item_string)
            
            # Turn list into text
            interruptions_text = '\n'.join(result_list)

            # Split the data into lines
            lines = interruptions_text.split('\n')

            # Iterate through the lines to identify speakers and assign utterances to parties
            current_party = None
            current_speaker = None
            
            for line in lines:
                if line.strip():  # Skip empty lines
                    if '[' in line and ']' in line and ':' in line:
                        
                        # Extract party information
                        party_start = line.index('[') + 1
                        party_end = line.index(']')
                        current_party = line[party_start:party_end]
                        party_dict.setdefault(current_party, [])
                        
                        # Extract speaker information
                        speaker_end = line.index(':')
                        current_speaker = line[:speaker_end].strip()
                        
                    elif current_party and current_speaker:
                        # Assign utterances to the current speaker within the party
                        party_dict[current_party].append({current_speaker: line.strip()})

                
            # Write in result df
            this_id = row['id']

            for party, utterances in party_dict.items():
                utterances_str = '\n'.join([string for u in utterances for string in u.values()])
                party_data.append({'id': this_id, 'party': party, 'text': utterances_str, 'text_type': 'interruption'})

    new_protocols = pd.DataFrame(party_data)

    return new_protocols
    

def party_shares(protocols):
    '''
    For a given dataframe of protocols, returns a dataframe with 1 row per protocol and party and text_type (interruptions vs main text) 
    -> rows: row_num*5 for 18th period and row_num*6 for 19th period (+ "parteilos")
    Columns: protocol_id, party, text_type, text

    Params: 
     pd.DataFrame: data

    Returns:
     pd.DataFrame: data split into party contributions. Columns: protocol_id, party, text, text_type
    '''
    party_shares_main_df = party_shares_main(protocols)
    party_shares_inter_df = party_shares_inter(protocols)
    new_protocols = pd.concat([party_shares_main_df, party_shares_inter_df], ignore_index=True)
    return new_protocols


def add_metadata(df_text_of_parties):
    '''
    For a given dataframe with 1 row per protocol and party and text_type (interruptions vs main text) 
    adds metadata date and wahlperiode
    Columns: protocol_id, party, text_type, text, date, wahlperiode

    Params: 
     pd.DataFrame: data

    Returns:
     pd.DataFrame: data split into party contributions. Columns: protocol_id, party, text, text_type, date, wahlperiode
    '''
    metadata = get_metadata()
    
    for md in metadata:
        for index, row in df_text_of_parties.iterrows():
            if int(md['id']) == row['id']:
                df_text_of_parties.at[index, 'wahlperiode'] = int(md['wahlperiode'])
                df_text_of_parties.at[index, 'datum'] = datetime.datetime.strptime(md['datum'],'%Y-%m-%d')

    return df_text_of_parties