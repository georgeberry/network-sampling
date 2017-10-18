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

#

viz_df = read_tsv('/Users/g/Documents/network-sampling/pokec_graph.tsv') %>%
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

levels(viz_df$method) = c("Edge Sample",
                          "Ideal Sampling",
                          "Node Sample",
                          "RDS",
                          "Snowball Sample")

levels(viz_df$category) = c("p=0.0",
                            "p=0.2\nno correction",
                            "p=0.2")

p8 = viz_df %>%
  select(category, method, m_b, p_b, t_b, s_b, h_b_hat, h_b, top_20_hat, top_20_true) %>%
  mutate(err_p = m_b - p_b,
         err_s = t_b - s_b,
         err_h = h_b_hat - h_b,
         err_v = top_20_hat - top_20_true) %>%
  gather(key, err, err_p, err_s, err_h, err_v) %>%
  mutate(key = factor(key,
                      levels=c('err_p', 'err_s', 'err_h', 'err_v'),
                      labels=c('Group proportion', 'Edge proportion', 'Homophily', 'Visibility'))) %>%
  ggplot(aes(x=factor(category), y=err)) +
  geom_boxplot(outlier.alpha = 0.2) +
  geom_hline(yintercept=0, linetype='dashed') +
  stat_summary(fun.y='mean', geom='point', color='black') +
  theme_bw() +
  theme(legend.position="none",
        axis.title.y = element_text(size=14),
        axis.title.x = element_blank(),
        strip.text.x = element_text(size = 12)) +
  facet_grid(~ key) +
  lims(y=c(-0.3, 0.3))+
  labs(title='RDS performance on Pokec graph', y='Error')

ggsave('/Users/g/Documents/network-sampling/plots/p8.pdf', p8, width=11, height=3)
