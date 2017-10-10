library(tidyverse)
library(xtable)

#
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

viz_df = read_tsv('/Users/g/Documents/network-sampling/output.tsv') %>%
# viz_df = read_tsv('/Users/g/Documents/network-sampling/dfs/output.tsv') %>%
  mutate(clf_err_corrected = ifelse(clf_err_corrected == 'True', TRUE, FALSE),
         sampling_frac=samp_size/num_nodes,
         h_b_hat = winsor1(h_b_hat),
         method = factor(method)) %>%
  select(-X1) %>%
  filter(majority_size == 0.8,
         ingrp_pref_a == 0.8,
         ingrp_pref_b == 0.8,
         sampling_frac <= 0.3,
         samp_size >= 1000,
         method != 'sample_rds_double') %>%
  rowwise() %>%
  mutate(category = paste0(clf_err_corrected, p_misclassify)) %>%
  ungroup() %>%
  mutate(category = factor(category))

levels(viz_df$method) = c("Edge Sample",
                          "Node Sample",
                          "RDS",
                          "Sample RDS Double",
                          "Snowball Sample")

levels(viz_df$category) = c("No clf error",
                            "Clf error,\nno correction",
                            "Clf error,\ncorrection")


#### Bias analysis ###############################################################

# minority group proportion
p1 = viz_df %>%
  filter(samp_size >= 1000) %>%
  mutate(err = m_b - p_b) %>%
  ggplot(aes(x=category, y=err, color=method)) +
  geom_hline(yintercept=0, linetype='dashed') +
  geom_boxplot() +
  theme_bw() +
  facet_grid(~ method) +
  stat_summary(fun.y='mean', geom='point', color='black')
  lims(y=c(-0.4, 0.4))
  
# minority ingroup proportion
p2 = viz_df %>%
  filter(samp_size >= 1000) %>%
  mutate(err = t_bb - s_bb) %>%
  ggplot(aes(x=category, y=err, color=method)) +
  geom_hline(yintercept=0, linetype='dashed') +
  geom_boxplot() +
  theme_bw() +
  facet_grid(~ method) +
  stat_summary(fun.y='mean', geom='point', color='black')
  lims(y=c(-0.4, 0.4))

mp1 = multiplot(p1, p2, cols=1)

# coleman's homophily for minority group
p3 = viz_df %>%
  filter(samp_size >= 1000) %>%
  mutate(err = h_b_hat - h_b) %>%
  ggplot(aes(x=category, y=err, color=method)) +
  geom_hline(yintercept=0, linetype='dashed') +
  geom_boxplot() +
  theme_bw() +
  facet_grid(~ method) +
  stat_summary(fun.y='mean', geom='point', color='black')
  lims(y=c(-0.6, 0.6))

# for a table
xtable(
  viz_df %>%
    mutate(err = h_b_hat - h_b) %>%
    group_by(method, category) %>%
    summarize(mu = median(err),
              sigma_2 = var(err)) %>%
    arrange(category, method),
  digits=c(0,0,0, 3, 3))

# visibility of minority group
p4 = viz_df %>%
  filter(samp_size >= 1000) %>%
  mutate(err = top_20_hat - top_20_true) %>%
  ggplot(aes(x=category, y=err, color=method)) +
  geom_hline(yintercept=0, linetype='dashed') +
  geom_boxplot() +
  theme_bw() +
  facet_grid(~ method) +
  lims(y=c(-0.4, 0.4))


#### mse at sampling fraction ####################################################

######## no classifier error #####################################################

# minority group proportion
viz_df %>%
  filter(p_misclassify == 0, clf_err_corrected == FALSE) %>%
  mutate(err = m_b - p_b) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method) +
  lims(y=c(-0.1, 0.1))

# minority ingroup proportion
viz_df %>%
  filter(p_misclassify == 0, clf_err_corrected == FALSE) %>%
  mutate(err = t_bb - s_bb) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method) +
  lims(y=c(-0.1, 0.1))

# coleman's homophily for minority group
viz_df %>%
  filter(p_misclassify == 0, clf_err_corrected == FALSE) %>%
  mutate(err = h_b_hat - h_b) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method) +
  lims(y=c(-0.1, 0.1))

# visibility of minority grouop
viz_df %>%
  filter(p_misclassify == 0, clf_err_corrected == FALSE) %>%
  mutate(err = top_20_hat - top_20_true) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method) +
  lims(y=c(-0.1, 0.1))

######## uncorrected classifier error ############################################

# minority group proportion
viz_df %>%
  filter(p_misclassify > 0, clf_err_corrected == FALSE) %>%
  mutate(err = m_b - p_b) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method) +
  lims(y=c(-0.3, 0.3))

# minority ingroup proportion
viz_df %>%
  filter(p_misclassify > 0, clf_err_corrected == FALSE) %>%
  mutate(err = t_bb - s_bb) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method) +
  lims(y=c(-0.4, 0.4))

# coleman's homophily for minority group
viz_df %>%
  filter(p_misclassify > 0, clf_err_corrected == FALSE) %>%
  mutate(err = h_b_hat - h_b) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method) +
  lims(y=c(-0.4, 0.4))

# visibility of minority grouop
viz_df %>%
  filter(p_misclassify > 0, clf_err_corrected == FALSE) %>%
  mutate(err = top_20_hat - top_20_true) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method) +
  lims(y=c(-0.4, 0.4))


######## corrected classifier error ##############################################

# minority group proportion
viz_df %>%
  filter(p_misclassify > 0, clf_err_corrected == TRUE) %>%
  mutate(err = m_b - p_b) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method) +
  lims(y=c(-0.4, 0.4))

# minority ingroup proportion
viz_df %>%
  filter(p_misclassify > 0, clf_err_corrected == TRUE) %>%
  mutate(err = t_bb - s_bb) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method) +
  lims(y=c(-0.4, 0.4))

# coleman's homophily for minority group
viz_df %>%
  filter(p_misclassify > 0, clf_err_corrected == TRUE) %>%
  mutate(err = h_b_hat - h_b) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method) +
  lims(y=c(-0.4, 0.4))

# visibility of minority grouop
viz_df %>%
  filter(p_misclassify > 0, clf_err_corrected == TRUE) %>%
  mutate(err = top_20_hat - top_20_true) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method) +
  lims(y=c(-0.4, 0.4))



#### Compare RDS to ideal variance given by either edge or node sampling #########

ColemanH = function(p_a, p_aa) {
  if (p_aa >= p_a) {
    return((p_aa - p_a) / (1 - p_a))
  } else if (p_aa < p_a) {
    return((p_aa - p_a) / p_a)
  }
}

# Comapre variance for sampling nodes
viz_df %>%
  filter(p_misclassify == 0.0,
         clf_err_corrected == FALSE,
         samp_size == 1000,
         method %in% c('sample_rds', 'sample_nodes')) %>%
  mutate(err = m_a - p_a) %>%
  group_by(method) %>%
  summarize(v = var(err))
  
# Comapre variance for sampling edges
viz_df %>%
  filter(p_misclassify == 0.0,
         clf_err_corrected == FALSE,
         samp_size == 1000,
         method %in% c('sample_rds', 'sample_edges')) %>%
  mutate(err = m_a - p_a) %>%
  group_by(method) %>%
  summarize(v = var(err))


# Comapre variance for homophily, using node sample for proportion estimate
# and edge sampling for edge estimate
rds_df = viz_df %>%
  filter(p_misclassify == 0.0,
         clf_err_corrected == FALSE,
         samp_size == 1000,
         method %in% c('sample_rds')) %>%
  select(graph_idx, samp_idx, h_b_hat, h_b)

node_df = viz_df %>%
  filter(p_misclassify == 0.0,
         clf_err_corrected == FALSE,
         samp_size == 1000,
         method %in% c('sample_nodes')) %>%
  select(graph_idx, samp_idx, m_b)

edge_df = viz_df %>%
  filter(p_misclassify == 0.0,
         clf_err_corrected == FALSE,
         samp_size == 1000,
         method %in% c('sample_edges')) %>%
  select(graph_idx, samp_idx, t_bb)

hom_df = left_join(rds_df, node_df, by=c('graph_idx', 'samp_idx')) %>%
  left_join(., edge_df, by=c('graph_idx', 'samp_idx')) %>%
  rowwise() %>%
  mutate(h_b_hat_comparison = ColemanH(m_b, t_bb),
         rds_err = h_b_hat - h_b,
         comparison_err = h_b_hat_comparison - h_b) %>%
  ungroup() %>%
  select(rds_err,
         comparison_err) %>%
  gather(kind, value, rds_err, comparison_err)

hom_df %>%
  group_by(kind) %>%
  summarize(mu = mean(value),
            sd = sqrt(var(value)))

hom_df %>%
  ggplot(aes(x = factor(kind), y = value, color = factor(kind))) +
  geom_hline(yintercept=0, linetype='dashed') +
  geom_boxplot() +
  theme_bw()
  

####


# Comapre variance for sampling nodes
viz_df %>%
  filter(p_misclassify > 0.0,
         clf_err_corrected == FALSE,
         samp_size == 1000,
         method %in% c('sample_rds', 'sample_nodes')) %>%
  mutate(err = m_a - p_a) %>%
  group_by(method) %>%
  summarize(v = var(err))

# Comapre variance for sampling edges
viz_df %>%
  filter(p_misclassify == 0.0,
         clf_err_corrected == FALSE,
         samp_size == 1000,
         method %in% c('sample_rds', 'sample_edges')) %>%
  mutate(err = m_a - p_a) %>%
  group_by(method) %>%
  summarize(v = var(err))


#### Ideal homophily analysis ####################################################

# Comapre variance for homophily, using node sample for proportion estimate
# and edge sampling for edge estimate
rds_df = viz_df %>%
  filter(p_misclassify > 0.0,
         clf_err_corrected == TRUE,
         samp_size == 1000,
         method %in% c('sample_rds')) %>%
  select(graph_idx, samp_idx, h_b_hat, h_b)

node_df = viz_df %>%
  filter(p_misclassify > 0.0,
         clf_err_corrected == TRUE,
         samp_size == 1000,
         method %in% c('sample_nodes')) %>%
  select(graph_idx, samp_idx, m_b)

edge_df = viz_df %>%
  filter(p_misclassify > 0.0,
         clf_err_corrected == TRUE,
         samp_size == 1000,
         method %in% c('sample_edges')) %>%
  select(graph_idx, samp_idx, t_bb)

hom_df = left_join(rds_df, node_df, by=c('graph_idx', 'samp_idx')) %>%
  left_join(., edge_df, by=c('graph_idx', 'samp_idx')) %>%
  rowwise() %>%
  mutate(h_b_hat_comparison = ColemanH(m_b, t_bb),
         rds_err = h_b_hat - h_b,
         comparison_err = h_b_hat_comparison - h_b) %>%
  ungroup() %>%
  select(rds_err,
         comparison_err) %>%
  gather(kind, value, rds_err, comparison_err)

hom_df %>%
  group_by(kind) %>%
  summarize(mu = mean(value),
            sd = sqrt(var(value)))

hom_df %>%
  ggplot(aes(x = factor(kind), y = value, color = factor(kind))) +
  geom_hline(yintercept=0, linetype='dashed') +
  geom_boxplot() +
  theme_bw()
