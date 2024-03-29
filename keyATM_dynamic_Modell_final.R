# Setzen des Arbeitsverzeichnisses und Laden notwendiger Pakete
options(stringsAsFactors = FALSE) 
install.packages("keyATM")
install.packages("quanteda")
install.packages("magrittr")
install.packages("stopwords") # Laden des stopwords-Pakets
install.packages("dplyr") # für eine Filter operation
install.packages("udpipe")
install.packages("wordcloud")
install.packages("RColorBrewer")
install.packages("future")
install.packages("future.apply")

library(keyATM)
library(quanteda)
library(magrittr)
library(stopwords) # Laden des stopwords-Pakets
library(dplyr) # für eine Filter operation
library(udpipe)
library(wordcloud)
library(RColorBrewer)
library('stringr')
library(data.table)
library(parallel)
library(future)
library(future.apply)

# Einlesen der Daten 
textdata <- read.csv("/Users/int-veen/Documents/df_text_of_parties.csv", sep = ",",
                     encoding = "UTF-8")

textdata$period <- ifelse(textdata$date >= as.Date("2013-10-22") & textdata$date <= as.Date("2017-10-24"),"18. Wahlperiode", ifelse(textdata$date >= as.Date("2017-10-24") & textdata$date <= as.Date("2021-10-26"), "19. Wahlperiode", NA))
textdata$month <- lapply(textdata$date, function(x) str_extract(x, "-([0-9]+)-", group=1)) # ifelse(textdata$date >= as.Date("2013-10-22") & textdata$date <= as.Date("2017-10-24"),"18. Wahlperiode", ifelse(textdata$date >= as.Date("2017-10-24") & textdata$date <= as.Date("2021-10-26"), "19. Wahlperiode", NA))


# Sample erstellen
textdata <- sample_n(textdata,1500)

# welches jahr wie oft vorkommt in dem Sample
year_freq <- table(textdata$year)
print(year_freq)

# welche periode wie oft vorkommt in dem Sample
period_freq <- table(textdata$period)
print(period_freq)

# nach Datum sortieren
textdata <- textdata[order(as.Date(textdata$date, format = "%Y-%m-%d")),]


# Entfernen von fehlenden Werten (falls erforderlich)
textdata <- na.omit(textdata)

# Erstellung eines Korpus mit docvars für Parteien und Wahlperioden
bundestag_corpus <- corpus(textdata$text, docnames = textdata$X, docvars = data.frame(party = textdata$party, period = textdata$period, year = textdata$year))

# Download und Laden des udpipe Modells für das Deutsche
udmodel_german <- udpipe::udpipe_download_model(language = "german")
udmodel_german_model <- udpipe::udpipe_load_model("german-gsd-ud-2.5-191206.udpipe")



z <- udpipe::udpipe_annotate(udmodel_german_model, x = textdata$text, trace = 50) %>%
  as.data.frame() %>%
  dplyr::select(-sentence)



text_anndf <- z

filtered_text <- text_anndf %>% filter(upos %in% c('NOUN', 'PROPN', 'ADJ'))

#saveRDS(filtered_text, file = "filtered_text.rds")

tokens <- as.tokens(split(filtered_text$lemma, filtered_text$doc_id))

# Stoppwortliste erstellen
stopwords_iso <- stopwords("de", source = "stopwords-iso")
stopwords_snowball <- stopwords("de", source = "snowball")
stopwords_marimo <- stopwords("de", source = "marimo")
stopwords_nltk <- stopwords("de", source = "nltk")

stopwords_extended <- c(stopwords_iso, stopwords_snowball, stopwords_marimo, stopwords_nltk)

# Erstellung eines DTM (Document-Term Matrix)
corpus_tokens <- tokens %>%
  tokens(remove_punct = TRUE, remove_numbers = TRUE, remove_symbols = TRUE) %>%
  tokens_tolower() %>%
  tokens_remove(pattern = stopwords_extended, padding = TRUE)

corpus_tokens <- tokens(corpus_tokens, what = "fastestword") %>%
  tokens_remove(pattern = "", valuetype = "fixed")

# Ermittlung und Verarbeitung von Kollokationen
bundestag_collocations <- quanteda.textstats::textstat_collocations(
  corpus_tokens,
  min_count = 25)
bundestag_collocations_limited <- bundestag_collocations[1:250, ]
corpus_tokens <- tokens_compound(corpus_tokens, bundestag_collocations_limited)

# Erstellen der DTM, Entfernen von Begriffen, die in weniger als 1% aller Dokumente vorkommen
data_dfm <- corpus_tokens %>%
  tokens_remove("") %>%
  dfm() %>%
  dfm_trim(min_docfreq = 0.1, max_docfreq = 0.90, docfreq_type = "prop")

top10_terms <- c("frau", "mann", "geehrter_herr_präsident_geehrt_dame_herr",
                 "herr_minister", "frau_ministerin", "frau_präsidentin ", "lieb_kollege",
                 "dame_herr","herr", "herr_präsident_dame_herr",
                 "deutsch_bundestag","merkel", "kanzlerin","frau_merkel",
                 "thomas", "martin", "alexander", "matthias", "andreas", "markus",
                 "stefan", "micheal", "christian", "bernd", "sebastian", "michael", "kerstin", 
                 "frank", "peter", "dirk", "christopf", "bettina", "uwe", "christoh",
                 "nobert", "udo", "johannes", "stephan", "katrin", "marc", "gabriel", "mark",
                 "ulrich", "karsten", "ulrike", "susanne", "bernhard", "paul", "katharina", "ursula",
                 "christopf", "sabine", "jens", "christoph", "jan", "hans_jürgen", "corinna", "güntzler",
                 "wolfgang", "kühn", "marcus", "jörg", "christoph", "jens", "nicole", "norbert", "felser",
                 "albert", "simon", "freese", "albrecht","michel_brandt", "klaus_dieter", "mario_brandenburg",
                 "detlev", "torsten_herbst_katja", "wiehle", "lindholz", "jürgen", "wendt", "sandra",
                 "tobias", "axel", "keuter", "brehm", "thorsten", "silvia", "müller","uhl", "rohde",
                 "grundl", "dilcher", "mohr"
)

# Entfernen der meistgenannten Begriffe (nach Bedarf angepasst)
data_dfm <- data_dfm[, !(colnames(data_dfm) %in% top10_terms)]
# Entfernen leerer Dokumente nach Vokabularbereinigung
sel_idx <- rowSums(data_dfm) > 0
data_dfm <- data_dfm[sel_idx, ]
textdata <- textdata[sel_idx, ]

# Vorbereitung der Daten für keyATM
keyATM_docs <- keyATM_read(texts = data_dfm)


#dynamic
vars <- docvars(bundestag_corpus)
vars <- cbind(vars, textdata$date)
head(vars)
                   
# Dann transformieren wir die 'party' und 'period' Spalten in Faktoren und erstellen Dummy-Variablen
vars$party <- factor(vars$party, levels = c("DIE LINKE", "SPD", "BÜNDNIS 90/DIE GRÜNEN", "CDU/CSU", "FDP", "AfD"))
vars$period <- factor(vars$period, levels = c("18. Wahlperiode", "19. Wahlperiode"))
vars$period_zwei <- ifelse(vars$period == "18. Wahlperiode",1, ifelse(vars$period == "19. Wahlperiode", 2, NA))
vars$periode_year <- as.integer(vars$year) - 2012
head(vars)
tail(vars)


keywords <- list(   Flucht           = c("flüchtling", "illegal", "islam","ausländer", "migration", "afrika", "syrien"),   
                    Familie          = c( "eltern", "geschlecht", "mutter", "gleichberechtigung", "quote"),   
                    Klimawandel      = c("energiewende", "nachhaltig", "klima", "umwelt", "umweltschutz","klimawandel", "klimaschutz", "co2"),   
                    Corona           = c("lockdown","corona", "meinungsfreiheit", "maske", "virus"),   
                    NS_Vergangenheit = c("jude", "jüdisch", "nazi", "linksextrem", "deutsche_geschichte", "stolz") 
)

get_keywords <- function(keywords) {
  names <- names(keywords)
  extended_keywords = c()
  for (i in 1:length(keywords)) {
    kw <- c()
    for (j in 1:length(keywords[[i]])){
      column <- colnames(dfm_select(data_dfm, pattern=paste("*", keywords[[i]][j], "*", sep="")))
      kw <- c(kw, column)
    }
    extended_keywords[[names[i]]] <- kw
  }
  return(extended_keywords)
}
kw <- get_keywords(keywords)

out_dynamic <- keyATM(
  docs              = keyATM_docs,
  no_keyword_topics = 3,
  keywords          = kw,
  model             = "dynamic",
  model_settings    = list(time_index = vars$periode_year,
                           num_states = max(vars$period_zwei)),
  options           = list(verbose = TRUE, prune=FALSE)
)
top_words(out_dynamic)
fig_alpha <- plot_alpha(out_dynamic)
fig_alpha

out_dynamic_theta <- keyATM(
  docs              = keyATM_docs,
  no_keyword_topics = 3,
  keywords          = kw,
  model             = "dynamic",
  model_settings    = list(time_index = vars$periode_year,
                           num_states = max(vars$period_zwei)),
  options           = list(seed = 250, store_theta = TRUE, thinning = 5)
)
fig_timetrend <- plot_timetrend(out_dynamic_theta, time_index_label = vars$periode_year, xlab = "Years")
fig_timetrend
