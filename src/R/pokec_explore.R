library(tidyverse)
library(xtable)

winsor1 = function (x, fraction=.005)
{
  if(length(fraction) != 1 || fraction < 0 ||
     fraction > 0.5) {
    stop("bad value for 'fraction'")
  }
  lim <- quantile(x, probs=c(fraction, 1-fraction))
  x[ x < lim[1] ] <- lim[1]
  x[ x > lim[2] ] <- lim[2]
  x
}

multiplot <- function(..., plotlist=NULL, file, cols=1, layout=NULL) {
  library(grid)
  
  # Make a list from the ... arguments and plotlist
  plots <- c(list(...), plotlist)
  
  numPlots = length(plots)
  
  # If layout is NULL, then use 'cols' to determine layout
  if (is.null(layout)) {
    # Make the panel
    # ncol: Number of columns of plots
    # nrow: Number of rows needed, calculated from # of cols
    layout <- matrix(seq(1, cols * ceiling(numPlots/cols)),
                     ncol = cols, nrow = ceiling(numPlots/cols))
  }
  
  if (numPlots==1) {
    print(plots[[1]])
    
  } else {
    # Set up the page
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout))))
    
    # Make each plot, in the correct location
    for (i in 1:numPlots) {
      # Get the i,j matrix positions of the regions that contain this subplot
      matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))
      
      print(plots[[i]], vp = viewport(layout.pos.row = matchidx$row,
                                      layout.pos.col = matchidx$col))
    }
  }
}

#### Age #########################################################################

viz_df = read_tsv('/Users/g/Documents/network-sampling/dfs/age_pokec_graph.tsv') %>%
  filter(!is.na(h_b_hat)) %>%
  mutate(clf_err_corrected = ifelse(clf_err_corrected == 'True', TRUE, FALSE),
         sampling_frac=samp_size/num_nodes,
         h_b_hat = h_b_hat,
         #h_b_hat = winsor1(h_b_hat),
         method = factor(method)) %>%
  select(-X1) %>%
  #filter(majority_size == 0.8,
  #       ingrp_pref_a == 0.8,
  #       ingrp_pref_b == 0.8) %>%
  rowwise() %>%
  mutate(category = paste0(clf_err_corrected, p_misclassify)) %>%
  ungroup() %>%
  mutate(category = factor(category))

levels(viz_df$category) = c("p=0.0",
                            "p=0.1\nno correction",
                            "p=0.2\nno correction",
                            "p=0.3\nno correction",
                            "p=0.1",
                            "p=0.2",
                            "p=0.3")


p8 = viz_df %>%
  filter(category %in% c("p=0.0",
                         "p=0.1",
                         "p=0.2",
                         "p=0.3"),
         samp_size==25000) %>%
  select(category, p_misclassify, method, m_b, p_b, t_b, s_b, h_b_hat, h_b, top_20_hat, top_20_true) %>%
  mutate(Node = (m_b - p_b)^2,
         Edge = (t_b - s_b)^2,
         Homophily = (h_b_hat - h_b)^2,
         Visibility = (top_20_hat - top_20_true)^2) %>%
  group_by(p_misclassify) %>%
  summarize(node_nrmse = sqrt(mean(Node)) / mean(p_b),
            edge_nrmse = sqrt(mean(Edge)) / mean(s_b),
            homophily_nrmse = sqrt(mean(Homophily)) / mean(abs(h_b)),
            visibility_nrmse = sqrt(mean(Visibility)) / mean(top_20_true)) %>%
  select(p_misclassify,
         node_nrmse,
         edge_nrmse,
         homophily_nrmse,
         visibility_nrmse) %>%
  gather(key,
         val,
         node_nrmse,
         edge_nrmse,
         homophily_nrmse,
         visibility_nrmse) %>%
  mutate(key = factor(key,
                      levels=c('node_nrmse',
                               'visibility_nrmse',
                               'edge_nrmse',
                               'homophily_nrmse'),
                      labels=c('Node',
                               'Visibility',
                               'Edge',
                               'Homophily'))) %>%
  ggplot(aes(x=factor(p_misclassify), y=val)) +
  scale_shape_identity() +
  geom_point(aes(x=factor(p_misclassify), y=val, shape=5)) +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  theme(legend.position="none",
        axis.title.y = element_text(size=14),
        axis.title.x = element_blank(),
        strip.text.x = element_text(size = 12)) +
  facet_grid(~ key) +
  labs(title='RDS performance on age in Pokec graph', y='NRMSE') +
  lims(y=c(-0.1, 0.4)) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank())
show(p8)

ggsave('/Users/g/Documents/network-sampling/plots/p8.pdf', p8, width=11, height=3)



#### Gender ######################################################################

viz_df = read_tsv('/Users/g/Documents/network-sampling/dfs/gender_pokec_graph.tsv') %>%
  filter(!is.na(h_b_hat)) %>%
  mutate(clf_err_corrected = ifelse(clf_err_corrected == 'True', TRUE, FALSE),
         sampling_frac=samp_size/num_nodes,
         h_b_hat = h_b_hat,
         #h_b_hat = winsor1(h_b_hat),
         method = factor(method)) %>%
  select(-X1) %>%
  #filter(majority_size == 0.8,
  #       ingrp_pref_a == 0.8,
  #       ingrp_pref_b == 0.8) %>%
  rowwise() %>%
  mutate(category = paste0(clf_err_corrected, p_misclassify)) %>%
  ungroup() %>%
  mutate(category = factor(category))

levels(viz_df$category) = c("p=0.0",
                            "p=0.1\nno correction",
                            "p=0.2\nno correction",
                            "p=0.3\nno correction",
                            "p=0.1",
                            "p=0.2",
                            "p=0.3")


p9 = viz_df %>%
  filter(category %in% c("p=0.0",
                         "p=0.1",
                         "p=0.2",
                         "p=0.3"),
         samp_size==25000) %>%
  select(category, p_misclassify, method, m_b, p_b, t_b, s_b, h_b_hat, h_b, top_20_hat, top_20_true) %>%
  mutate(Node = (m_b - p_b)^2,
         Edge = (t_b - s_b)^2,
         Homophily = (h_b_hat - h_b)^2,
         Visibility = (top_20_hat - top_20_true)^2) %>%
  group_by(p_misclassify) %>%
  summarize(node_nrmse = sqrt(mean(Node)) / mean(p_b),
            edge_nrmse = sqrt(mean(Edge)) / mean(s_b),
            homophily_nrmse = sqrt(mean(Homophily)) / mean(abs(h_b)),
            visibility_nrmse = sqrt(mean(Visibility)) / mean(top_20_true)) %>%
  select(p_misclassify,
         node_nrmse,
         edge_nrmse,
         homophily_nrmse,
         visibility_nrmse) %>%
  gather(key,
         val,
         node_nrmse,
         edge_nrmse,
         homophily_nrmse,
         visibility_nrmse) %>%
  mutate(key = factor(key,
                      levels=c('node_nrmse',
                               'visibility_nrmse',
                               'edge_nrmse',
                               'homophily_nrmse'),
                      labels=c('Node',
                               'Visibility',
                               'Edge',
                               'Homophily'))) %>%
  filter(key != 'Homophily') %>%
  ggplot(aes(x=factor(p_misclassify), y=val)) +
  scale_shape_identity() +
  geom_point(aes(x=factor(p_misclassify), y=val, shape=5)) +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  theme(legend.position="none",
        axis.title.y = element_text(size=14),
        axis.title.x = element_blank(),
        strip.text.x = element_text(size = 12)) +
  facet_grid(~ key) +
  lims(y=c(-0.05, 0.2)) +
  labs(title='RDS performance on gender in Pokec graph', y='NRMSE')+
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank())
  
show(p9)

ggsave('/Users/g/Documents/network-sampling/plots/p9.pdf', p9, width=11, height=3)


mp4 = multiplot(p8, p9, cols=1)

