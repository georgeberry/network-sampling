library(tidyverse)

viz_df = read_tsv('/Users/g/Documents/network-sampling/output.tsv') %>%
  mutate(clf_err_corrected = ifelse(clf_err_corrected == 'True', TRUE, FALSE))

#### mse at sampling fraction ####################################################

######## no classifier error #####################################################

# minority group proportion
viz_df %>%
  filter(p_misclassify == 0, clf_err_corrected == FALSE) %>%
  mutate(sampling_frac=samp_size/num_nodes,
         err = m_b - p_b) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method)

# minority ingroup proportion
viz_df %>%
  filter(p_misclassify == 0, clf_err_corrected == FALSE) %>%
  mutate(sampling_frac=samp_size/num_nodes,
         err = m_bb - p_bb) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method)

# coleman's homophily for minority group
viz_df %>%
  filter(p_misclassify == 0, clf_err_corrected == FALSE) %>%
  mutate(sampling_frac=samp_size/num_nodes,
         err = h_b_hat - h_b) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method)

# visibility of minority grouop
viz_df %>%
  filter(p_misclassify == 0, clf_err_corrected == FALSE) %>%
  mutate(sampling_frac=samp_size/num_nodes,
         err = top_20_hat - top_20_true) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method)

######## uncorrected classifier error ############################################

# minority group proportion
viz_df %>%
  filter(p_misclassify > 0, clf_err_corrected == FALSE) %>%
  mutate(sampling_frac=samp_size/num_nodes,
         err = m_b - p_b) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method)

# minority ingroup proportion
viz_df %>%
  filter(p_misclassify > 0, clf_err_corrected == FALSE) %>%
  mutate(sampling_frac=samp_size/num_nodes,
         err = m_bb - p_bb) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method)

# coleman's homophily for minority group
viz_df %>%
  filter(p_misclassify > 0, clf_err_corrected == FALSE) %>%
  mutate(sampling_frac=samp_size/num_nodes,
         err = h_b_hat - h_b) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method)

# visibility of minority grouop
viz_df %>%
  filter(p_misclassify > 0, clf_err_corrected == FALSE) %>%
  mutate(sampling_frac=samp_size/num_nodes,
         err = top_20_hat - top_20_true) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method)


######## corrected classifier error ##############################################

# minority group proportion
viz_df %>%
  filter(p_misclassify > 0, clf_err_corrected == TRUE) %>%
  mutate(sampling_frac=samp_size/num_nodes,
         err = m_b_crct - p_b) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method)

# minority ingroup proportion
viz_df %>%
  filter(p_misclassify > 0, clf_err_corrected == TRUE) %>%
  mutate(sampling_frac=samp_size/num_nodes,
         err = m_bb_crct - p_bb) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method)

# coleman's homophily for minority group
viz_df %>%
  filter(p_misclassify > 0, clf_err_corrected == TRUE) %>%
  mutate(sampling_frac=samp_size/num_nodes,
         err = h_b_hat_crct - h_b) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method)

# visibility of minority grouop
viz_df %>%
  filter(p_misclassify > 0, clf_err_corrected == TRUE) %>%
  mutate(sampling_frac=samp_size/num_nodes,
         err = top_20_hat_crct - top_20_true) %>%
  ggplot(aes(x=factor(sampling_frac), y=err, color=factor(method))) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method)


#### Bias analysis ###############################################################

# minority group proportion
viz_df %>%
  filter(samp_size == 1000) %>%
  mutate(err = m_b - p_b,
         category = paste(p_misclassify, clf_err_corrected)) %>%
  ggplot(aes(x=factor(category), y=err)) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method)

# minority ingroup proportion
viz_df %>%
  filter(samp_size == 1000) %>%
  mutate(err = m_bb - p_bb,
         category = paste(p_misclassify, clf_err_corrected)) %>%
  ggplot(aes(x=factor(category), y=err)) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method)

# coleman's homophily for minority group
viz_df %>%
  filter(samp_size == 1000) %>%
  mutate(err = h_b_hat - h_b,
         category = paste(p_misclassify, clf_err_corrected)) %>%
  ggplot(aes(x=factor(category), y=err)) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method)


# visibility of minority group
viz_df %>%
  filter(samp_size == 1000) %>%
  mutate(err = top_20_hat - top_20_true,
         category = paste(p_misclassify, clf_err_corrected)) %>%
  ggplot(aes(x=factor(category), y=err)) +
  geom_boxplot() +
  geom_hline(yintercept=0, linetype='dashed') +
  theme_bw() +
  facet_grid(~ method)


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
  select(graph_idx, samp_idx, m_bb)

hom_df = left_join(rds_df, node_df, by=c('graph_idx', 'samp_idx')) %>%
  left_join(., edge_df, by=c('graph_idx', 'samp_idx')) %>%
  rowwise() %>%
  mutate(h_b_hat_comparison = ColemanH(m_b, m_bb),
         rds_err = h_b_hat - h_b,
         comparison_err = h_b_hat_comparison - h_b) %>%
  ungroup() %>%
  select(rds_err,
         comparison_err) %>%
  gather(kind, value, rds_err, comparison_err)

hom_df %>%
  group_by(kind) %>%
  summarize(mu = mean(value),
            var = var(value))

hom_df %>%
  ggplot(aes(x = factor(kind), y = value, color = factor(kind))) +
  geom_hline(yintercept=0, linetype='dashed') +
  geom_boxplot() +
  theme_bw()
  