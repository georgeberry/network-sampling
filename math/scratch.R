library(tidyverse)

df <- read_tsv('/Users/g/Desktop/sim_table_plus_all.tsv') %>%
  mutate(h_a = paste0("Ingroup: ", h_a),
         majority_size = paste0("Majority fraction: ", majority_size))

# node sampling
node_sample_df = df %>%
  mutate(node_sample_err = prop_d_a - trueprop_d_a) %>%
  select(method, node_sample_err, majority_size, h_a) %>%
  filter(method != 'population')

ggplot(data=node_sample_df) +
  theme_bw() +
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank()) +
  geom_hline(yintercept=0, alpha=0.5) + 
  geom_violin(aes(y=node_sample_err, x=method, color=method)) +
  stat_summary(fun.y="mean", geom="point", aes(y=node_sample_err, x=method, color=method), shape=43, size=4) +
  facet_grid(majority_size~h_a) +
  scale_color_discrete(name="Sampling method",
                       labels=c("Edge",
                                "Ego network",
                                "Node",
                                "Random walk",
                                "RDS",
                                "Snowball")) +
  labs(title="Node sampling error", y="Sampling error") +
  lims(y=c(-0.5, 0.5))

# edge sampling
edge_sample_df = df %>%
  mutate(edge_sample_err = prop_d_aa - trueprop_d_aa) %>%
  select(method, edge_sample_err, majority_size, h_a) %>%
  filter(method != 'population')

ggplot(data=edge_sample_df) +
  theme_bw() +
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank()) +
  geom_hline(yintercept=0, alpha=0.5) +
  geom_violin(aes(y=edge_sample_err, x=method, color=method)) +
  stat_summary(fun.y="mean", geom="point", aes(y=edge_sample_err, x=method, color=method), shape=43, size=4) +
  facet_grid(majority_size~h_a) +
  scale_color_discrete(name="Sampling method",
                       labels=c("Edge",
                                "Ego network",
                                "Node",
                                "Random walk",
                                "RDS",
                                "Snowball")) +
  labs(title="Edge sampling error", y="Sampling error") +
  lims(y=c(-0.5, 0.5))

# Correlation between edge and node error
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

# coleman plots
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
                                      true_prop_a)
  ) %>%
  mutate(coleman_est = coleman_numerator_est / coleman_denominator_est,
         coleman_true = coleman_numerator_true / coleman_denominator_true,
         coleman_err = coleman_est - coleman_true) %>%
  select(method, coleman_err, h_a, majority_size)

ggplot(df_coleman) + 
  theme_bw() + 
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank()) +
  geom_hline(yintercept=0, alpha=0.5) + 
  geom_violin(aes(x=method, y=coleman_err, color=method)) +
  stat_summary(fun.y="mean", geom="point", aes(y=coleman_err, x=method, color=method), shape=43, size=4) +
  facet_grid(majority_size~h_a) +
  scale_color_discrete(name="Sampling method",
                       labels=c("Edge",
                                "Ego network",
                                "Node",
                                "Random walk",
                                "RDS",
                                "Snowball")) +
  labs(title="Coleman homophily sampling error", y="Sampling error") +
  lims(y=c(-0.5, 0.5))
