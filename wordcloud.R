#saveRDS(out, file = "/Users/int-veen/afd/wordcloud.rds")
#out <- readRDS(file = "/Users/int-veen/afd/wordcloud.rds")

library(wordcloud)
library(RColorBrewer)

top_words_list <- top_words(out, n = 50)  #  Top-50 Wörter für jedes Thema
str(top_words_list)

# Initialisieren Data Frame für die Results
top_words_df <- data.frame(theme = character(), word = character(), frequency = numeric(), stringsAsFactors = FALSE)

# Iterieren jedes ThemaS und füllen vom Data Frame
for (i in 1:length(top_words_list)) {
  # Wörter für das Thema i
  words <- top_words_list[[i]]
  
  # nur Wörter verwenden, die auch in data_dfm enthalten sind
  valid_words <- words[words %in% colnames(data_dfm)]
  
  # BerechnenFrequenzen für gültige Wörter
  if (length(valid_words) > 0) {
    frequencies <- colSums(data_dfm[, valid_words, drop = FALSE])
    theme_df <- data.frame(theme = paste("Theme", i), word = names(frequencies), frequency = frequencies)
    top_words_df <- rbind(top_words_df, theme_df)  # Fügen Sie die Ergebnisse zusammen
  }
}

print(top_words_df)

# Order words according to frequency
top_words_df <- top_words_df[order(top_words_df$theme, -top_words_df$frequency),]
print(top_words_df)

# Group data by theme
migration = top_words_df  %>% filter(., theme == "Theme 1")
familie = top_words_df  %>% filter(., theme == "Theme 2")
klima = top_words_df  %>% filter(., theme == "Theme 3")
corona = top_words_df  %>% filter(., theme == "Theme 4")
ns = top_words_df  %>% filter(., theme == "Theme 5")

#set.seed(1234) # for reproducibility 
cloud_migration = wordcloud(words = migration$word, 
                        freq = migration$frequency, 
                        min.freq = 1, 
                        max.words = 100,  
                        random.order = FALSE, 
                        rot.per = 0.25, 
                        scale=c(3.5,0.25), 
                        colors = "pink") 

cloud_familie = wordcloud(words = familie$word, 
                        freq = familie$frequency, 
                        min.freq = 1, 
                        max.words = 100,  
                        random.order = FALSE, 
                        rot.per = 0.25, 
                        scale=c(3.5,0.25), 
                        colors = "orange")

cloud_klima = wordcloud(words = klima$word, 
                        freq = klima$frequency, 
                        min.freq = 1, 
                        max.words = 100,  
                        random.order = FALSE, 
                        rot.per = 0.25, 
                        scale=c(3.5,0.25), 
                        colors = "lightgreen") 

cloud_corona = wordcloud(words = corona$word, 
                        freq = corona$frequency, 
                        min.freq = 1, 
                        max.words = 100,  
                        random.order = FALSE, 
                        rot.per = 0.25, 
                        scale=c(3.5,0.25), 
                        colors = "purple") 

cloud_ns = wordcloud(words = ns$word, 
                        freq = ns$frequency, 
                        min.freq = 1, 
                        max.words = 100,  
                        random.order = FALSE, 
                        rot.per = 0.25, 
                        scale=c(3.5,0.25), 
                        colors = "lightblue") 

