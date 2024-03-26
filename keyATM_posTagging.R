# Forschungsfrage 1 - keyATM Base

# set your work directory
options(stringsAsFactors = FALSE) 
library(keyATM)
library(quanteda)
library(magrittr)
library(stopwords) # Laden des stopwords-Pakets
library(dplyr) # für eine Filter operation
library(udpipe)

# Einlesen der Daten 
textdata <- read.csv("/Users/int-veen/Documents/afd/df_text_of_parties.csv", sep = ",",
                     encoding = "UTF-8") 
afd_textdata <- textdata %>% filter(party == "AfD")
textdata <- afd_textdata

# Erstellung eines Korpus
bundestag_corpus <- corpus(textdata$text, docnames = textdata$X) # Build a dictionary of lemmas

udmodel_german <- udpipe::udpipe_download_model(language = "german")
udmodel_german<- udpipe::udpipe_load_model("german-gsd-ud-2.5-191206.udpipe")

# tokenise, tag, dependency parsing
text_anndf <- udpipe::udpipe_annotate(udmodel_german, x = textdata$text,trace = 50) %>%
  as.data.frame() %>%
  dplyr::select(-sentence)

saveRDS(text_anndf,file="text_anndf.rds")

filtered_text <- text_anndf %>% filter(upos %in% c('NOUN','PROPN', 'ADJ'))

saveRDS(filtered_text,file="filtered_text.rds")

tokens <-  as.tokens(split(filtered_text$lemma, filtered_text$doc_id))

#  Stoppwortliste
stopwords_iso <- stopwords("de", source = "stopwords-iso")
stopwords_snowball <- stopwords("de", source = "snowball")
stopwords_marimo <- stopwords("de", source = "marimo")
stopwords_nltk <- stopwords("de", source = "nltk")

stopwords_extended <- append(stopwords_iso, stopwords_snowball)
stopwords_extended <- append(stopwords_extended, stopwords_marimo)                            
stopwords_extended <- append(stopwords_extended, stopwords_nltk)  

# Create a DTM (may take a while)
corpus_tokens <- tokens %>%
  tokens(remove_punct = TRUE, remove_numbers = TRUE, remove_symbols = TRUE) %>%
  tokens_tolower() %>%
  #tokens_replace(lemma_data$inflected_form,
  #               lemma_data$lemma,
  #               valuetype = "fixed") %>%
  tokens_remove(pattern = stopwords_extended, padding = T)

corpus_tokens <- tokens(corpus_tokens, what = "fastestword") %>%
  tokens_remove(pattern = "", valuetype = "fixed")

# Ermittlung und Verarbeitung von Kollokationen 
bundestag_collocations <- quanteda.textstats::textstat_collocations(
  corpus_tokens,
  min_count = 25)
bundestag_collocations <- bundestag_collocations[1:250, ]
corpus_tokens <- tokens_compound(corpus_tokens, bundestag_collocations)

# Create DTM, but remove terms which occur in less than 1% of all documents
data_dfm <- corpus_tokens %>%
  tokens_remove("") %>%
  dfm() %>%
  dfm_trim(min_docfreq = 0.1, max_docfreq=0.50, docfreq_type = "prop")

# have a look at the number of documents and terms in the matrix
dim(data_dfm )

# show the most frequent words
head(data_dfm, 25)

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

data_dfm <- data_dfm[, !(colnames(data_dfm) %in% top10_terms)]
# due to vocabulary pruning, we have empty rows in our DTM
# LDA does not like this. So we remove those docs from the
# DTM and the metadata
sel_idx <- rowSums(data_dfm) > 0
data_dfm <- data_dfm[sel_idx, ]
textdata <- textdata[sel_idx, ]

#ncol(data_dfm)  # the number of unique words
#dim(data_dfm) # wie viele Wörter sind in der DTM

#View(data_dfm)
#data_dfm@Dimnames[["features"]]

########################
###  keyATM BASE     ###
########################

# keyATM_read function reads your data for keyATM
keyATM_docs <- keyATM_read(texts = data_dfm ) 

summary(keyATM_docs)

# PREPARING KEYWORDS

keywords <- list(
  Flucht           = c("flüchtling", "illegal", "islam","ausländer", "migration", 
                       "afrika", "syrien"),
  Familie          = c( "eltern", "geschlecht", "mutter", "gleichberechtigung", "quote"),
  Klimawandel      = c("energiewende", "nachhaltig", "klima", "umwelt", "umweltschutz", 
                       "klimawandel", "klimaschutz", "co2"),
  Corona           = c("lockdown","corona", "meinungsfreiheit", "maske", "virus"),
  NS_Vergangenheit = c("jude", "jüdisch", "nazi", "linksextrem", "deutsche_geschichte",
                        "stolz")
)


###########################
###  CHECKING KEYWORDS  ###
###########################
# Keywords should appear reasonable times (typically more than 0.1% of the corpus) in the documents. 
key_viz <- visualize_keywords(docs = keyATM_docs, keywords = keywords)
key_viz
save_fig(key_viz, "keyword.pdf", width = 6.5, height = 4)
values_fig(key_viz)


# Choosing keywords with an unsupervised topic model

set.seed(225)  # set the seed before split the dfm
docs_withSplit <- keyATM_read(texts = data_dfm,
                              split = 0.3)  # split each document

out <- weightedLDA(
  docs              = docs_withSplit$W_split,  # 30% of the corpus
  number_of_topics  = 5,  # the number of potential themes in the corpus
  model             = "base",
  options           = list(seed = 250)
)
top_words(out)  # top words can aid selecting keywords

out <- keyATM(
  docs              = docs_withSplit,  # 70% of the corpus
  no_keyword_topics = 5,               # number of topics without keywords
  keywords          = keywords,        # selected keywords
  model             = "base",          # select the model
  options           = list(seed = 250)
)
top_words(out)

# KEY ATM BASE
out <- keyATM(
  docs              = keyATM_docs,    # text input
  no_keyword_topics = 5,              # number of topics without keywords
  keywords          = keywords,       # keywords
  model             = "base",         # select the model
  options           = list(seed = 250)
)
top_words(out)

#save(out, file = "SAVENAME.rds")
#out <- readRDS(file = "SAVENAME.rds")

plot_topicprop(out, show_topic = 1:5)
top_docs(out) 





