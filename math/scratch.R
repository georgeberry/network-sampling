library(tidyverse)

df <- read_tsv('/Users/g/Desktop/sim_table_plus_all.tsv')

#
df_err = df %>%
  mutate(
    node_p_err = prop_d_a-trueprop_d_a,
    ingroup_p_err = prop_d_aa-trueprop_d_aa,
    params = paste0('p_a=',as.character(trueprop_d_a), ' h_a=', as.character(h_a))
  ) %>%
  select(method, node_p_err, ingroup_p_err, params) %>%
  filter(method %in% c('sample_edges', 'sample_nodes', 'sample_RWRW', 'sample_random_walk')) %>%
  sample_n(10000)

ggplot(df_err) +
  geom_point(aes(y=ingroup_p_err, x=node_p_err)) +
  facet_grid(params ~ method)

# gen data directly
df_coleman = df %>%
  mutate(
    est_prop_a = d_a / (d_a + d_b),
    true_prop_a = true_d_a / num_nodes,
    est_prop_aa = d_aa / (d_aa + d_ab + d_ba),
    true_prop_aa = true_d_aa / (true_d_aa + true_d_ab + true_d_ba)
    ) %>%
  filter(method != 'population') %>%
  mutate(
    coleman_numerator_est = est_prop_aa - est_prop_a,
    coleman_numerator_true = true_prop_aa - true_prop_a
  ) %>%
  mutate(
    coleman_denominator_est = ifelse(coleman_numerator_est >= 0,
                                     1 - est_prop_a,
                                     est_prop_a),
    coleman_denominator_true = ifelse(coleman_numerator_true >= 0,
                                      1 - true_prop_a,
                                      true_prop_a),
  ) %>%
  mutate(coleman_est = coleman_numerator_est / coleman_denominator_est,
         coleman_true = coleman_numerator_true / coleman_denominator_true,
         coleman_err = coleman_est - coleman_true) %>%
  select(method, coleman_err, h_a, trueprop_d_a)

ggplot(df_coleman) + 
  theme_bw() + 
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank()) +
  geom_hline(yintercept=0, linetype='dashed') + 
  geom_violin(aes(x=method, y=coleman_err, color=method)) +
  facet_grid(trueprop_d_a ~ h_a)
