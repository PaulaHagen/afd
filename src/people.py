import pandas as pd
import re
import bundestag_api


def get_neutral_persons():
    '''
    Returns a list of politicians, who are speaking in the Bundestag (of period 18 and 19) but have official moderating roles.
    --> They do not speak for any party but in a neutral way.

    Returns:
     list: politicians with full name
    '''
    neutral_persons = ['Präsident Dr. Wolfgang Schäuble:', 'Präsident Dr. Wolfgang Schäuble :', 'Präsident Dr. Wolfgang Schäuble :', 'Präsident Dr. Wolfgang Schäuble:',
                   'Präsident Dr. Norbert Lammert:', 'Präsident Dr. Norbert Lammert:', 'Präsident Prof. Dr. Norbert Lammert:', 'Präsident Dr. Norbert Lammert :', 'Präsident Dr. Norbert Lammert :',
                   'Vizepräsidentin Claudia Roth:', 'Vizepräsident Dr. Hans-Peter Friedrich', 'Vizepräsident Dr. Hans-Peter Friedrich', 'Vizepräsident Wolfgang Kubicki',
                   'Vizepräsident Thomas Oppermann:', 'Vizepräsidentin Petra Pau:', 'Alterspräsident Dr. Hermann Otto Solms:', 'Alterspräsident Dr. Hermann Otto Solms:'
                   'Vizepräsident Johannes Singhammer:', 'Vizepräsidentin Ulla Schmidt:', 'Vizepräsident Peter Hintze:',
                   'Vizepräsidentin Edelgard Bulmahn:', 'Alterspräsident Dr. Heinz Riesenhuber:']
    
    return neutral_persons


def get_mdb(key = 'rgsaY4U.oZRQKUHdJhF9qguHMkwCGIoLaqEcaHjYLF'):
    '''
    Returns a list of relevant politicians, who are MdB (of period 18 and 19)

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


def get_regierende(mdb_format = False, include_party = False):
    '''
    Returns a list of politicians, who are part of the federal government (of period 18 and 19) or Ministerpräsident during that time.
    Returns also their party.

    Returns:
     list: politicians with full name and party [name, party_name]
    '''
    # im Folgenden die Bundesregierung 18
    bundreg_18 = [['Dr. Angela Merkel, Bundeskanzlerin', 'CDU/CSU'], 
               ['Sigmar Gabriel, Bundesminister des Auswärtigen', 'SPD'],
               ['Dr. Frank-Walter Steinmeier, Bundesminister des Auswärtigen', 'SPD'],
               ['Dr. Thomas de Maizière, Bundesminister des Innern', 'CDU/CSU'],
               ['Heiko Maas, Bundesminister der Justiz und für Verbraucherschutz', 'SPD'],
               ['Dr. Wolfgang Schäuble, Bundesminister der Finanzen', 'CDU/CSU'],
               ['Peter Altmaier, Bundesminister der Finanzen', 'CDU/CSU'],
               ['Sigmar Gabriel, Bundesminister für Wirtschaft und Energie', 'SPD'],
               ['Brigitte Zypries, Bundesministerin für Wirtschaft und Energie', 'SPD'],
               ['Andrea Nahles, Bundesministerin für Arbeit und Soziales', 'SPD'],
               ['Katarina Barley, Bundesministerin für Arbeit und Soziales', 'SPD'],
               ['Dr. Hans-Peter Friedrich, Bundesminister für Ernährung und Landwirtschaft', 'CDU/CSU'], 
               ['Christian Schmidt, Bundesminister für Ernährung und Landwirtschaft', 'CDU/CSU'],
               ['Dr. Ursula von der Leyen, Bundesministerin der Verteidigung', 'CDU/CSU'],
               ['Manuela Schwesig, Bundesministerin für Familie, Senioren, Frauen und Jugend', 'SPD'], 
               ['Dr. Katarina Barley, Bundesministerin für Familie, Senioren, Frauen und Jugend', 'SPD'],
               ['Katarina Barley, Bundesministerin für Familie, Senioren, Frauen und Jugend', 'SPD'],
               ['Hermann Gröhe, Bundesminister für Gesundheit', 'CDU/CSU'],
               ['Alexander Dobrindt, Bundesminister für Verkehr und digitale Infrastruktur', 'CDU/CSU'],
               ['Christian Schmidt, Bundesminister für Verkehr und digitale Infrastruktur', 'CDU/CSU'],
               ['Dr. Barbara Hendricks, Bundesministerin für Umwelt, Naturschutz, Bau und Reaktorsicherheit', 'SPD'],
               ['Dr. Johanna Wanka, Bundesministerin für Bildung und Forschung', 'CDU/CSU'],
               ['Dr. Gerd Müller, Bundesminister für wirtschaftliche Zusammenarbeit und Entwicklung', 'CDU/CSU'],
               ['Peter Altmaier, Bundesminister für besondere Aufgaben', 'CDU/CSU'],

               # Staatssekretärinnen und Staatsministerinnen
               ['Dr. Helge Braun, Staatsminister bei der Bundeskanzlerin', 'CDU/CSU'],
               ['Monika Grütters, Staatsministerin bei der Bundeskanzlerin', 'CDU/CSU'],
               ['Aydan Özoğuz, Staatsministerin bei der Bundeskanzlerin', 'SPD'],
               ['Dr. Maria Böhmer, Staatsministerin im Auswärtigen Amt', 'CDU/CSU'],
               ['Michael Roth, Staatsminister im Auswärtigen Amt', 'SPD'],
               ['Dr. Günter Krings, Parl. Staatssekretär beim Bundesminister des Innern', 'CDU/CSU'],
               ['Dr. Ole Schröder, Parl. Staatssekretär beim Bundesminister des Innern', 'CDU/CSU'],
               ['Ulrich Kelber, Parl. Staatssekretär beim Bundesminister der Justiz und für Verbraucherschutz', 'SPD'],
               ['Christian Lange, Parl. Staatssekretär beim Bundesminister der Justiz und für Verbraucherschutz', 'SPD'],
               ['Steffen Kampeter, Parl. Staatssekretär beim Bundesminister der Finanzen', 'CDU/CSU'],
               ['Dr. Michael Meister, Parl. Staatssekretär beim Bundesminister der Finanzen', 'CDU/CSU'],
               ['Jens Spahn, Parl. Staatssekretär beim Bundesminister der Finanzen', 'CDU/CSU'],
               ['Uwe Beckmeyer, Parl. Staatssekretär beim Bundesminister für Wirtschaft und Energie', 'SPD'],
               ['Uwe Beckmeyer, Parl. Staatssekretär bei der Bundesministerin für Wirtschaft und Energie', 'SPD'],
               ['Iris Gleicke, Parl. Staatssekretärin beim Bundesminister für Wirtschaft und Energie', 'SPD'],
               ['Iris Gleicke, Parl. Staatssekretärin bei der Bundesministerin für Wirtschaft und Energie', 'SPD'],
               ['Brigitte Zypries, Parl. Staatssekretärin beim Bundesminister für Wirtschaft und Energie', 'SPD'],
               ['Dirk Wiese, Parl. Staatssekretär bei der Bundesministerin für Wirtschaft und Energie', 'SPD'],
               ['Anette Kramme, Parl. Staatssekretärin bei der Bundesministerin für Arbeit und Soziales', 'SPD'],
               ['Gabriele Lösekrug-Möller, Parl. Staatssekretärin bei der Bundesministerin für Arbeit und Soziales', 'SPD'],
               ['Peter Bleser, Parl. Staatssekretär beim Bundesminister für Ernährung und Landwirtschaft', 'CDU/CSU'],
               ['Dr. Maria Flachsbarth, Parl. Staatssekretärin beim Bundesminister für Ernährung und Landwirtschaft', 'CDU/CSU'],
               ['Dr. Ralf Brauksiepe, Parl. Staatssekretär bei der Bundesministerin der Verteidigung', 'CDU/CSU'],
               ['Markus Grübel, Parl. Staatssekretär bei der Bundesministerin der Verteidigung', 'CDU/CSU'],
               ['Elke Ferner, Parl. Staatssekretärin bei der Bundesministerin für Familie, Senioren, Frauen und Jugend', 'SPD'],
               ['Caren Marks, Parl. Staatssekretärin bei der Bundesministerin für Familie, Senioren, Frauen und Jugend', 'SPD'],
               ['Ingrid Fischbach, Parl. Staatssekretärin beim Bundesminister für Gesundheit', 'CDU/CSU'],
               ['Annette Widmann-Mauz, Parl. Staatssekretärin beim Bundesminister für Gesundheit', 'CDU/CSU'],
               ['Dorothee Bär, Parl. Staatssekretärin beim Bundesminister für Verkehr und digitale Infrastruktur', 'CDU/CSU'],
               ['Enak Ferlemann, Parl. Staatssekretär beim Bundesminister für Verkehr und digitale Infrastruktur', 'CDU/CSU'],
               ['Katherina Reiche, Parl. Staatssekretärin beim Bundesminister für Verkehr und digitale Infrastruktur', 'CDU/CSU'],
               ['Norbert Barthle, Parl. Staatssekretär beim Bundesminister für Verkehr und digitale Infrastruktur', 'CDU/CSU'],
               ['Florian Pronold, Parl. Staatssekretär bei der Bundesministerin Umwelt, Naturschutz, Bau und Reaktorsicherheit', 'SPD'],
               ['Rita Schwarzelühr-Sutter, Parl. Staatssekretärin bei der Bundesministerin für Umwelt, Naturschutz, Bau und Reaktorsicherheit', 'SPD'],
               ['Stefan Müller, Parl. Staatssekretär bei der Bundesministerin für Bildung und Forschung', 'CDU/CSU'],
               ['Thomas Rachel, Parl. Staatssekretär bei der Bundesministerin für Bildung und Forschung', 'CDU/CSU'],
               ['Hans-Joachim Fuchtel, Parl. Staatssekretär beim Bundesminister für wirtschaftliche Zusammenarbeit und Entwicklung', 'CDU/CSU'],
               ['Christian Schmidt, Parl. Staatssekretär beim Bundesminister für wirtschaftliche Zusammenarbeit und Entwicklung', 'CDU/CSU'],
               ['Thomas Silberhorn, Parl. Staatssekretär beim Bundesminister für wirtschaftliche Zusammenarbeit und Entwicklung', 'CDU/CSU']
    ]

    # im Folgenden die (genannten) Mitglieder der Regierung 17 (für Sitzung 1-3 der Wahlperiode 18)
    bundreg_17 = [['Dr. Hans-Peter Friedrich, Bundesminister des Innern','CDU/CSU'],
               ['Dr. Thomas de Maizière, Bundesminister der Verteidigung', 'CDU/CSU'],
               ['Dr. Kristina Schröder, Bundesministerin für Familie, Senioren, Frauen und Jugend', 'CDU/CSU'],
               ['Dr. Ursula von der Leyen, Bundesministerin für Arbeit und Soziales', 'CDU/CSU'],
               ['Peter Altmaier, Bundesminister für Umwelt, Naturschutz und Reaktorsicherheit', 'CDU/CSU'],
               ['Dr. Maria Böhmer, Staatsministerin bei der Bundeskanzlerin', 'CDU/CSU'],
               ['Ernst Burgbacher, Parl. Staatssekretär beim Bundesminister für Wirtschaft und Technologie', 'FDP'],
               ['Cornelia Pieper, Staatsministerin im Auswärtigen Amt', 'FDP'],
               ['Dr. Ole Schröder, Parl. Staatssekretär beim Bundesminister des Innern', 'CDU/CSU'],
               ['Dr. Guido Westerwelle, Bundesminister des Auswärtigen', 'CDU/CSU'],
               ['Hartmut Koschyk, Parl. Staatssekretär beim Bundesminister der Finanzen', 'CDU/CSU']
               ]
    
    # im Folgenden die (genannten) Mitglieder der Regierung 19
    bundreg_19 = [['Dr. Angela Merkel, Bundeskanzlerin', 'CDU/CSU'], 
               ['Heiko Maas, Bundesminister des Auswärtigen', 'SPD'],
               ['Horst Seehofer, Bundesminister des Innern, für Bau und Heimat', 'CDU/CSU'], # umbenannt
               ['Dr. Katarina Barley, Bundesministerin der Justiz und für Verbraucherschutz', 'SPD'],
               ['Christine Lambrecht, Bundesministerin der Justiz und für Verbraucherschutz', 'SPD'],
               ['Olaf Scholz, Bundesminister der Finanzen', 'SPD'],
               ['Peter Altmaier, Bundesminister für Wirtschaft und Energie', 'CDU/CSU'],
               ['Hubertus Heil, Bundesminister für Arbeit und Soziales', 'SPD'],
               ['Julia Klöckner, Bundesministerin für Ernährung und Landwirtschaft', 'CDU/CSU'],
               ['Dr. Ursula von der Leyen, Bundesministerin der Verteidigung', 'CDU/CSU'],
               ['Annegret Kramp-Karrenbauer, Bundesministerin der Verteidigung', 'CDU/CSU'],
               ['Dr. Franziska Giffey, Bundesministerin für Familie, Senioren, Frauen und Jugend', 'SPD'],
               ['Christine Lambrecht, Bundesministerin für Familie, Senioren, Frauen und Jugend', 'SPD'],
               ['Jens Spahn, Bundesminister für Gesundheit', 'CDU/CSU'],
               ['Andreas Scheuer, Bundesminister für Verkehr und digitale Infrastruktur', 'CDU/CSU'],
               ['Svenja Schulze, Bundesministerin für Umwelt, Naturschutz und nukleare Sicherheit', 'SPD'], # umbenannt
               ['Anja Karliczek, Bundesministerin für Bildung und Forschung', 'CDU/CSU'],
               ['Dr. Gerd Müller, Bundesminister für wirtschaftliche Zusammenarbeit und Entwicklung', 'CDU/CSU'],
               ['Dr. Helge Braun, Bundesminister für besondere Aufgaben', 'CDU/CSU'],

               # Staatssekretärinnen und Staatsministerinnen
               ['Monika Grütters, Staatsministerin bei der Bundeskanzlerin', 'CDU/CSU'],
               ['Dr. Hendrik Hoppenstedt, Staatsminister bei der Bundeskanzlerin', 'CDU/CSU'],
               ['Annette Widmann-Mauz, Staatsministerin bei der Bundeskanzlerin', 'CDU/CSU'],
               ['Dorothee Bär, Staatsministerin bei der Bundeskanzlerin', 'CDU/CSU'],
               ['Bettina Hagedorn, Parl. Staatssekretärin beim Bundesminister der Finanzen', 'SPD'],
               ['Christine Lambrecht, Parl. Staatssekretärin beim Bundesminister der Finanzen', 'SPD'],
               ['Sarah Ryglewski, Parl. Staatssekretärin beim Bundesminister der Finanzen', 'SPD'],
               ['Dr. Günter Krings, Parl. Staatssekretär beim Bundesminister des Innern, für Bau und Heimat', 'CDU/CSU'],
               ['Marco Wanderwitz, Parl. Staatssekretär beim Bundesminister des Innern, für Bau und Heimat', 'CDU/CSU'],
               ['Volkmar Vogel, Parl. Staatssekretär beim Bundesminister des Innern, für Bau und Heimat', 'CDU/CSU'],
               ['Stephan Mayer, Parl. Staatssekretär beim Bundesminister des Innern, für Bau und Heimat', 'CDU/CSU'],
               ['Niels Annen, Staatsminister im Auswärtigen Amt', 'SPD'],
               ['Michelle Müntefering, Staatsministerin im Auswärtigen Amt', 'SPD'],
               ['Michael Roth, Staatsminister im Auswärtigen Amt', 'SPD'],
               ['Thomas Bareiß, Parl. Staatssekretär beim Bundesminister für Wirtschaft und Energie', 'CDU/CSU'],
               ['Christian Hirte, Parl. Staatssekretär beim Bundesminister für Wirtschaft und Energie', 'CDU/CSU'],
               ['Marco Wanderwitz, Parl. Staatssekretär beim Bundesminister für Wirtschaft und Energie', 'CDU/CSU'],
               ['Oliver Wittke, Parl. Staatssekretär beim Bundesminister für Wirtschaft und Energie', 'CDU/CSU'],
               ['Elisabeth Winkelmeier-Becker, Parl. Staatssekretärin beim Bundesminister für Wirtschaft und Energie', 'CDU/CSU'],
               ['Rita Hagl-Kehl, Parl. Staatssekretärin bei der Bundesministerin der Justiz und für Verbraucherschutz', 'SPD'],
               ['Christian Lange, Parl. Staatssekretär bei der Bundesministerin der Justiz und für Verbraucherschutz', 'SPD'],
               ['Kerstin Griese, Parl. Staatssekretärin beim Bundesminister für Arbeit und Soziales', 'SPD'],
               ['Anette Kramme, Parl. Staatssekretärin beim Bundesminister für Arbeit und Soziales', 'SPD'],
               ['Dr. Peter Tauber, Parl. Staatssekretär bei der Bundesministerin der Verteidigung', 'CDU/CSU'],
               ['Thomas Silberhorn, Parl. Staatssekretär bei der Bundesministerin der Verteidigung', 'CDU/CSU'],
               ['Hans-Joachim Fuchtel, Parl. Staatssekretär bei der Bundesministerin für Ernährung und Landwirtschaft', 'CDU/CSU'],
               ['Michael Stübgen, Parl. Staatssekretär bei der Bundesministerin für Ernährung und Landwirtschaft', 'CDU/CSU'],
               ['Uwe Feiler, Parl. Staatssekretär bei der Bundesministerin für Ernährung und Landwirtschaft', 'CDU/CSU'],
               ['Caren Marks, Parl. Staatssekretärin bei der Bundesministerin für Familie, Senioren, Frauen und Jugend', 'SPD'],
               ['Stefan Zierke, Parl. Staatssekretär bei der Bundesministerin für Familie, Senioren, Frauen und Jugend', 'SPD'],
               ['Dr. Thomas Gebhart, Parl. Staatssekretär beim Bundesminister für Gesundheit', 'CDU/CSU'],
               ['Sabine Weiss, Parl. Staatssekretärin beim Bundesminister für Gesundheit', 'CDU/CSU'],
               ['Steffen Bilger, Parl. Staatssekretär beim Bundesminister für Verkehr und digitale Infrastruktur', 'CDU/CSU'],
               ['Enak Ferlemann, Parl. Staatssekretär beim Bundesminister für Verkehr und digitale Infrastruktur', 'CDU/CSU'],
               ['Rita Schwarzelühr-Sutter, Parl. Staatssekretärin bei der Bundesministerin für Umwelt, Naturschutz und nukleare Sicherheit', 'SPD'],
               ['Florian Pronold, Parl. Staatssekretär bei der Bundesministerin für Umwelt, Naturschutz und nukleare Sicherheit', 'SPD'],
               ['Michael Meister, Parl. Staatssekretär bei der Bundesministerin für Bildung und Forschung', 'CDU/CSU'],
               ['Thomas Rachel, Parl. Staatssekretär bei der Bundesministerin für Bildung und Forschung', 'CDU/CSU'],
               ['Norbert Barthle, Parl. Staatssekretär beim Bundesminister für wirtschaftliche Zusammenarbeit und Entwicklung', 'CDU/CSU'],
               ['Dr. Maria Flachsbarth, Parl. Staatssekretärin beim Bundesminister für wirtschaftliche Zusammenarbeit und Entwicklung', 'CDU/CSU']
    ]


    landreg = [['Winfried Kretschmann, Ministerpräsident (Baden-Württemberg)', 'BÜNDNIS 90/DIE GRÜNEN'],
               ['Markus Söder, Ministerpräsident (Bayern)', 'CDU/CSU'],
               ['Horst Seehofer, Ministerpräsident (Bayern)', 'CDU/CSU'],
               ['Michael Müller, Regierender Bürgermeister (Berlin)', 'SPD'],
               ['Franziska Giffey, Regierende Bürgermeisterin (Berlin)', 'SPD'],
               ['Dietmar Woidke, Ministerpräsident (Brandenburg)', 'SPD'],
               ['Carsten Sieling, Präsident des Senats und Bürgermeister (Bremen)', 'SPD'],
               ['Andreas Bovenschulte, Präsident des Senats und Bürgermeister (Bremen)', 'SPD'],
               ['Olaf Scholz, Erster Bürgermeister (Hamburg)', 'SPD'],
               ['Peter Tschentscher, Erster Bürgermeister (Hamburg)', 'SPD'],
               ['Volker Bouffier, Ministerpräsident (Hessen)', 'CDU/CSU'],
               ['Erwin Sellering, Ministerpräsident (Mecklenburg-Vorpommern)', 'SPD'],
               ['Manuela Schwesig, Ministerpräsidentin (Mecklenburg-Vorpommern)', 'SPD'],
               ['Stephan Weil, Ministerpräsident (Niedersachsen)', 'SPD'],
               ['Armin Laschet, Ministerpräsident (Nordrhein-Westfalen)', 'CDU/CSU'],
               ['Hendrik Wüst, Ministerpräsident (Nordrhein-Westfalen)', 'CDU/CSU'],
               ['Malu Dreyer, Ministerpräsidentin (Rheinland-Pfalz)', 'CDU/CSU'],
               ['Annegret Kramp-Karrenbauer, Ministerpräsidentin (Saarland)', 'CDU/CSU'],
               ['Tobias Hans, Ministerpräsident (Saarland)', 'CDU/CSU'],
               ['Stanislaw Tillich, Ministerpräsident (Sachsen)', 'CDU/CSU'],
               ['Michael Kretschmer, Ministerpräsident (Sachsen)', 'CDU/CSU'],
               ['Reiner Haseloff, Ministerpräsident (Sachsen-Anhalt)', 'CDU/CSU'],
               ['Torsten Albig, Ministerpräsident (Schleswig-Holstein)', 'SPD'],
               ['Daniel Günther, Ministerpräsident (Schleswig-Holstein)', 'CDU/CSU'],
               ['Thomas Kemmerich, Ministerpräsident (Thüringen)', 'FDP'],
               ['Bodo Ramelow, Ministerpräsident (Thüringen)', 'DIE LINKE']
               ]
    

    government = bundreg_17 + bundreg_18 + bundreg_19 + landreg

    # Change format to format of the other MdB --> "<Full Name> (<party>):\n"
    gov_mdb_format = []
    for person in government:
        name_end = person[0].index(',')
        name = person[0][:name_end]
        party = person[1]
        gov_mdb_format.append(f'{name} ({party}):')

    if mdb_format: # return format of "<Full Name> (<party>):\n"
        if include_party:
            return gov_mdb_format
        else:
            return [pair[0] for pair in gov_mdb_format]

    else: # return original format
        if include_party:
            return government
        else:
            return [pair[0] for pair in government]