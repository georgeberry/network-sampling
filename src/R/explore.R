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

viz_df = read_tsv('/Users/g/Documents/network-sampling/output.tsv') %>%
  filter(!is.na(h_b_hat)) %>%
  mutate(clf_err_corrected = ifelse(clf_err_corrected == 'True', TRUE, FALSE),
         sampling_frac=samp_size/num_nodes,
         h_b_hat = h_b_hat,
         #h_b_hat = winsor1(h_b_hat),
         method = factor(method,
                         levels=c('sample_rds',
                                  'sample_nodes',
                                  'sample_edges',
                                  'sample_snowball',
                                  'sample_ideal'),
                         labels=c('RDS',
                                  'Node Sample',
                                  'Edge Sample',
                                  'Snowball Sample',
                                  'Ideal Sample'))) %>%
  select(-X1) %>%
  #filter(majority_size == 0.8,
  #       ingrp_pref_a == 0.8,
  #       ingrp_pref_b == 0.8) %>%
  rowwise() %>%
  mutate(category = paste0(clf_err_corrected, p_misclassify)) %>%
  ungroup() %>%
  mutate(category = factor(category))

levels(viz_df$category) = c("e=0.0",
                            "e=0.1\nno correction",
                            "e=0.2\nno correction",
                            "e=0.3\nno correction",
                            "e=0.1\ncorrection",
                            "e=0.2\ncorrection",
                            "e=0.3\ncorrection")


#### Bias analysis ###############################################################

levels(viz_df$category) = c("A",
                            "e=0.1\nno correction",
                            "B",
                            "e=0.3\nno correction",
                            "e=0.1\ncorrection",
                            "C",
                            "e=0.3\ncorrection")

# minority group proportion
p1 = viz_df %>%
  filter(method != "Ideal Sample",
         p_misclassify %in% c(0.0, 0.2),
         samp_size == 3000) %>%
  mutate(err = m_b - p_b) %>%
  ggplot(aes(x=category, y=err, color=method)) +
  geom_boxplot(outlier.alpha = 0.2) +
  geom_hline(yintercept=0, linetype='dashed') +
  stat_summary(fun.y='mean', geom='point', color='black') +
  theme_bw() +
  theme(legend.position="none",
        axis.title.y = element_text(size=14),
        axis.title.x = element_blank(),
        strip.text.x = element_text(size = 12)) +
  facet_grid(~ method) +
  lims(y=c(-0.25, 0.25)) +
  labs(title='Group proportion', y='Error')
show(p1)

# visibility of minority group
p2 = viz_df %>%
  filter(method != "Ideal Sample",
         p_misclassify %in% c(0.0, 0.2),
         samp_size == 3000) %>%
  mutate(err = top_20_hat - top_20_true) %>%
  ggplot(aes(x=category, y=err, color=method)) +
  geom_boxplot(outlier.alpha = 0.2) +
  geom_hline(yintercept=0, linetype='dashed') +
  stat_summary(fun.y='mean', geom='point', color='black') +
  theme_bw() +
  theme(legend.position="none",
        axis.title.y = element_text(size=14),
        axis.title.x = element_blank(),
        strip.text.x = element_text(size = 12)) +
  facet_grid(~ method) +
  lims(y=c(-0.25, 0.25)) +
  labs(title='Visibility', y='Error')
show(p2)

# save manually, 11 by 6
mp1 = multiplot(p1, p2, cols=1)


# minority ingroup proportion
p3 = viz_df %>%
  filter(method != "Ideal Sample",
         p_misclassify %in% c(0.0, 0.2),
         samp_size == 3000) %>%
  mutate(err = t_b - s_b) %>%
  ggplot(aes(x=category, y=err, color=method)) +
  geom_boxplot(outlier.alpha = 0.2) +
  geom_hline(yintercept=0, linetype='dashed') +
  stat_summary(fun.y='mean', geom='point', color='black') +
  theme_bw() +
  theme(legend.position="none",
        axis.title.y = element_text(size=14),
        axis.title.x = element_blank(),
        strip.text.x = element_text(size = 12)) +
  facet_grid(~ method) +
  lims(y=c(-0.6, 0.6)) +
  labs(title='Ingroup edge proportion', y='Error')
show(p3)

# coleman's homophily for minority group
p4 = viz_df %>%
  filter(method != "Ideal Sample",
         p_misclassify %in% c(0.0, 0.2),
         samp_size == 3000) %>%
  mutate(err = h_b_hat - h_b) %>%
  ggplot(aes(x=category, y=err, color=method)) +
  geom_boxplot(outlier.alpha = 0.2) +
  geom_hline(yintercept=0, linetype='dashed') +
  stat_summary(fun.y='mean', geom='point', color='black') +
  theme_bw() +
  theme(legend.position="none",
        axis.title.y = element_text(size=14),
        axis.title.x = element_blank(),
        strip.text.x = element_text(size = 12)) +
  facet_grid(~ method) +
  lims(y=c(-0.6, 0.6)) +
  labs(title='Homophily', y='Error')
show(p4)

# save manually, 11 by 6
mp2 = multiplot(p3, p4, cols=1)


# for a table
xtable(
  viz_df %>%
    filter(method != "Ideal Sample",
           p_misclassify %in% c(0.0, 0.2),
           samp_size == 3000) %>%
    mutate(err = h_b_hat - h_b) %>%
    group_by(method, p_misclassify, clf_err_corrected) %>%
    summarize(mu = median(err),
              sigma = sqrt(var(err))) %>%
    arrange(p_misclassify, clf_err_corrected, method),
    include.rownames=FALSE,
    digits=c(0,0,1,0,3,3))


#### err at sampling fraction ####################################################

levels(viz_df$category) = c("A",
                            "e=0.1\nno correction",
                            "e=0.2\nno correction",
                            "e=0.3\nno correction",
                            "B",
                            "C",
                            "D")

p5 = viz_df %>%
  filter(method == "RDS",
         p_misclassify == 0.2,
         category %in% c("A",
                         "B",
                         "C",
                         "D"),
         sampling_frac != 0.05) %>%
  mutate(Node = (m_b - p_b)^2,
         Edge = (t_b - s_b)^2,
         Homophily = (h_b_hat - h_b)^2,
         Visibility = (top_20_hat - top_20_true)^2) %>%
  group_by(graph_idx, sampling_frac) %>%
  summarize(node_nrmse = sqrt(mean(Node)) / mean(p_b),
            edge_nrmse = sqrt(mean(Edge)) / mean(s_b),
            homophily_nrmse = sqrt(mean(Homophily)) / mean(abs(h_b)),
            visibility_nrmse = sqrt(mean(Visibility)) / mean(top_20_true)) %>%
  ungroup() %>%
  group_by(sampling_frac) %>%
  summarize(node_nrmse = mean(node_nrmse),
            edge_nrmse = mean(edge_nrmse),
            homophily_nrmse = mean(homophily_nrmse),
            visibility_nrmse = mean(visibility_nrmse)) %>%
  select(sampling_frac,
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
  ggplot() +
  scale_shape_identity() +
  geom_point(aes(x=factor(sampling_frac), y=val, shape=5)) +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  theme(legend.position="none",
        axis.title.y = element_text(size=14),
        axis.title.x = element_blank(),
        strip.text.x = element_text(size = 12)) +
  facet_grid(~ key) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank()) +
  labs(title='RDS at sampling fraction', y='NRMSE') +
  lims(y=c(-0.1, 0.8))


#### As we increase p misclassify ################################################

p6 = viz_df %>%
  filter(method == "RDS",
         category %in% c("A",
                         "B",
                         "C",
                         "D"),
         samp_size == 3000) %>%
  mutate(Node = (m_b - p_b)^2,
         Edge = (t_b - s_b)^2,
         Homophily = (h_b_hat - h_b)^2,
         Visibility = (top_20_hat - top_20_true)^2) %>%
  group_by(graph_idx, p_misclassify) %>%
  summarize(node_nrmse = sqrt(mean(Node)) / mean(p_b),
            edge_nrmse = sqrt(mean(Edge)) / mean(s_b),
            homophily_nrmse = sqrt(mean(Homophily)) / mean(abs(h_b)),
            visibility_nrmse = sqrt(mean(Visibility)) / mean(top_20_true)) %>%
  ungroup() %>%
  group_by(p_misclassify) %>%
  summarize(node_nrmse = mean(node_nrmse),
            edge_nrmse = mean(edge_nrmse),
            homophily_nrmse = mean(homophily_nrmse),
            visibility_nrmse = mean(visibility_nrmse)) %>%
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
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank()) +
  labs(title='RDS at misclassification rate', y='NRMSE') +
  lims(y=c(-0.1, 0.8))


# 11 by 5
mp3 = multiplot(p5, p6, cols=1)


  

#### Covariance to check unbiasedness and descriptive stats ######################

mean(viz_df$p_b)
mean(viz_df$s_b)
mean(viz_df$h_b)

viz_df %>%
  filter(p_misclassify == 0.2, clf_err_corrected == FALSE) %>%
  mutate(err_p_b = p_b - m_b,
         err_s_b = t_b - s_b,
         err_h_b = h_b_hat - h_b) %>%
  group_by(method) %>%
  summarize(mean(err_p_b),
            mean(err_s_b),
            mean(err_h_b))

viz_df %>%
  filter(p_misclassify == 0.0, clf_err_corrected == FALSE) %>%
  summarize(mean(abs(h_b)))

viz_df %>%
  select(p_misclassify == 0.2, clf_err_corrected == FALSE)

viz_df %>%
  filter(method == 'RDS', samp_size == 2000, p_misclassify == 0.2, clf_err_corrected == TRUE) %>%
  mutate(err = h_b_hat - h_b) %>%
  summarize(mean(err), sd(err))

viz_df %>%
  filter(method == 'RDS', samp_size == 2000, p_misclassify == 0.2, clf_err_corrected == FALSE) %>%
  mutate(err = h_b_hat - h_b) %>%
  summarize(mean(err), sd(err))

viz_df %>%
  filter(method == 'RDS', samp_size == 2000, p_misclassify == 0.2, clf_err_corrected == TRUE) %>%
  mutate(err = top_20_hat - top_20_true) %>%
  summarize(mean(err), sd(err))

viz_df %>%
  filter(method == 'RDS', samp_size == 2000, p_misclassify == 0.2, clf_err_corrected == FALSE) %>%
  mutate(err = top_20_hat - top_20_true) %>%
  summarize(mean(err), sd(err))

# t_a = ties from a to a
# m_a = size of group a

viz_df %>%
  filter(method == 'RDS', p_misclassify <= 0.0) %>%
  summarize(cov(t_aa_raw, t_bb_raw))

viz_df %>%
  filter(method == 'RDS', p_misclassify <= 0.0) %>%
  summarize(cov(t_aa_raw, t_ab_raw))

viz_df %>%
  filter(method == 'RDS', p_misclassify <= 0.0) %>%
  summarize(cov(t_bb_raw, t_ab_raw))

viz_df %>%
  filter(method == 'RDS', p_misclassify <= 0.2) %>%
  summarize(cov(t_b, m_b))

viz_df %>%
  filter(method == 'RDS', p_misclassify <= 0.2) %>%
  summarize(cov(t_b, t_a))

viz_df %>%
  filter(method == 'RDS', p_misclassify <= 0.2) %>%
  summarize(cov(t_b, t_a))

viz_df %>%
  filter(method == 'RDS') %>%
  group_by(p_misclassify) %>%
  summarize()


viz_df %>%
  filter(clf_err_corrected == TRUE,
         method=='RDS') %>%
  mutate(Node = m_b - p_b,
         Edge = t_b - s_b,
         Homophily = winsor1(h_b_hat - h_b),
         Visibility = winsor1(top_20_hat - top_20_true)) %>%
  group_by(p_misclassify) %>%
  summarize(sd(Node),
            sd(Edge),
            sd(Homophily),
            sd(Visibility))

viz_df %>%
  filter(clf_err_corrected == TRUE,
         method=='RDS') %>%
  mutate(Node = m_b - p_b,
         Edge = t_b - s_b,
         Homophily = winsor1(h_b_hat - h_b),
         Visibility = winsor1(top_20_hat - top_20_true)) %>%
  group_by(p_misclassify) %>%
  summarize(sd(Node),
            sd(Edge),
            sd(Homophily),
            sd(Visibility))

#### NRMSE #######################################################################

viz_df %>%
  filter(method != "Ideal Sample",
         p_misclassify %in% c(0.0, 0.2),
         samp_size == 3000) %>%
  mutate(err = m_b - p_b) %>%
  group_by(category, method) %>%
  summarize(err = sqrt(mean(err^2)) / mean(p_b)) %>%
  ggplot(aes(x=category, y=err, color=method)) +
  geom_boxplot(outlier.alpha = 0.2) +
  geom_hline(yintercept=0, linetype='dashed') +
  stat_summary(fun.y='mean', geom='point', color='black') +
  theme_bw() +
  theme(legend.position="none",
        axis.title.y = element_text(size=14),
        axis.title.x = element_blank(),
        strip.text.x = element_text(size = 12)) +
  facet_grid(~ method) +
  labs(title='Group proportion error', y=expression(p[b]~~error))

viz_df %>%
  filter(method != "Ideal Sample",
         p_misclassify %in% c(0.0, 0.2),
         samp_size == 3000) %>%
  mutate(err = t_b - s_b) %>%
  group_by(category, method) %>%
  summarize(err = sqrt(mean(err^2)) / mean(s_b)) %>%
  ggplot(aes(x=category, y=err, color=method)) +
  geom_boxplot(outlier.alpha = 0.2) +
  geom_hline(yintercept=0, linetype='dashed') +
  stat_summary(fun.y='mean', geom='point', color='black') +
  theme_bw() +
  theme(legend.position="none",
        axis.title.y = element_text(size=14),
        axis.title.x = element_blank(),
        strip.text.x = element_text(size = 12)) +
  facet_grid(~ method) +
  labs(title='Ingroup edge proportion error', y=expression(p[b]~~error))

viz_df %>%
  filter(method != "Ideal Sample",
         p_misclassify %in% c(0.0, 0.2),
         samp_size == 3000) %>%
  mutate(err = h_b_hat - h_b) %>%
  group_by(category, method) %>%
  summarize(err = sqrt(mean(err^2)) / mean(abs(h_b))) %>%
  ggplot(aes(x=category, y=err, color=method)) +
  geom_boxplot(outlier.alpha = 0.2) +
  geom_hline(yintercept=0, linetype='dashed') +
  stat_summary(fun.y='mean', geom='point', color='black') +
  theme_bw() +
  theme(legend.position="none",
        axis.title.y = element_text(size=14),
        axis.title.x = element_blank(),
        strip.text.x = element_text(size = 12)) +
  facet_grid(~ method) +
  lims(y=c(0,2)) +
  labs(title='Homophily error', y=expression(p[b]~~error))


viz_df %>%
  filter(method != "Ideal Sample",
         p_misclassify %in% c(0.0, 0.2),
         samp_size == 3000) %>%
  mutate(err = top_20_hat - top_20_true) %>%
  group_by(category, method) %>%
  summarize(err = sqrt(mean(err^2)) / mean(top_20_true)) %>%
  ggplot(aes(x=category, y=err, color=method)) +
  geom_boxplot(outlier.alpha = 0.2) +
  geom_hline(yintercept=0, linetype='dashed') +
  stat_summary(fun.y='mean', geom='point', color='black') +
  theme_bw() +
  theme(legend.position="none",
        axis.title.y = element_text(size=14),
        axis.title.x = element_blank(),
        strip.text.x = element_text(size = 12)) +
  facet_grid(~ method) +
  labs(title='Homophily error', y=expression(p[b]~~error))




levels(viz_df$category) = c("A",
                            "e=0.1\nno correction",
                            "e=0.2\nno correction",
                            "e=0.3\nno correction",
                            "B",
                            "C",
                            "D")

viz_df %>%
  filter(method == "RDS",
         category %in% c("A",
                         "B",
                         "C",
                         "D"),
         samp_size == 3000) %>%
  mutate(Node = m_b - p_b,
         Edge = t_b - s_b,
         Homophily = h_b_hat - h_b,
         Visibility = top_20_hat - top_20_true) %>%
  group_by(p_misclassify) %>%
  summarize(Node = sqrt(mean(Node^2))/mean(p_b),
            Edge = sqrt(mean(Edge^2))/mean(p_b),
            Homophily = sqrt(mean(Homophily^2))/mean(p_b),
            Visibility = sqrt(mean(Visibility^2))/mean(p_b)) %>%
  select(p_misclassify, Node, Edge, Homophily, Visibility) %>%
  gather(key, val, Node, Edge, Homophily, Visibility) %>%
  mutate(key = factor(key,
                      levels=c('Node', 'Edge', 'Homophily', 'Visibility'),
                      labels=c('Node Proportion', 'Edge Proportion', 'Homophily', 'Visibility'))) %>%
  ggplot(aes(x=factor(p_misclassify), y=val, color=key)) +
  geom_point() +
  geom_hline(yintercept=0, linetype='dashed') +
  stat_summary(fun.y='mean', geom='point', color='black') +
  theme_bw() +
  theme(legend.position="none",
        axis.title.y = element_text(size=14),
        axis.title.x = element_blank(),
        strip.text.x = element_text(size = 12)) +
  facet_grid(~ key) +
  labs(title='RDS error at misclassification level', y='Error')


viz_df %>%
  filter(method == "RDS",
       category %in% c("A",
                       "B",
                       "C",
                       "D"),
       p_misclassify == 0.2,
       clf_err_corrected == TRUE) %>%
  mutate(Node = m_b - p_b,
         Edge = t_b - s_b,
         Homophily = h_b_hat - h_b,
         Visibility = top_20_hat - top_20_true) %>%
  group_by(sampling_frac) %>%
  summarize(Node = sqrt(mean(Node^2))/mean(p_b),
            Edge = sqrt(mean(Edge^2))/mean(p_b),
            Homophily = sqrt(mean(Homophily^2))/mean(p_b),
            Visibility = sqrt(mean(Visibility^2))/mean(p_b)) %>%
  select(sampling_frac, Node, Edge, Homophily, Visibility) %>%
  gather(key, val, Node, Edge, Homophily, Visibility) %>%
  mutate(key = factor(key,
                      levels=c('Node', 'Edge', 'Homophily', 'Visibility'),
                      labels=c('Node Proportion', 'Edge Proportion', 'Homophily', 'Visibility'))) %>%
  ggplot(aes(x=factor(sampling_frac), y=val, color=key)) +
  geom_boxplot(outlier.alpha = 0.2) +
  geom_hline(yintercept=0, linetype='dashed') +
  stat_summary(fun.y='mean', geom='point', color='black') +
  theme_bw() +
  theme(legend.position="none",
        axis.title.y = element_text(size=14),
        axis.title.x = element_blank(),
        strip.text.x = element_text(size = 12)) +
  facet_grid(~ key) +
  labs(title='RDS error at sampling fraction', y='Error')
