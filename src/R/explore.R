library(tidyverse)

viz_df = read_tsv('/Users/g/Documents/network-sampling/outfile_dd.tsv')

viz_df %>%
  ggplot(aes(x = factor(method), y=err_prob_a, color=factor(method))) +
  geom_hline(yintercept=0, linetype='dashed') +
  geom_boxplot() +
  theme_bw() +
  facet_grid(majority_size ~ h_a)


hom_df = read_tsv('/Users/g/Documents/network-sampling/outfile.tsv')

hom_df %>%
  ggplot(aes(x = factor(method), y=err_prob_a, color=factor(method))) +
  geom_hline(yintercept=0, linetype='dashed') +
  geom_boxplot() +
  theme_bw() +
  facet_grid(majority_size ~ h_a)


resamp_df = read_tsv('/Users/g/Documents/network-sampling/test_resample.tsv')

resamp_df %>%
  ggplot(aes(x = factor(kind), y = value)) +
  geom_hline(yintercept=0.6, linetype='dashed') +
  geom_boxplot() +
  theme_bw()
