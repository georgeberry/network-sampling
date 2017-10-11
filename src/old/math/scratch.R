library(tidyverse)

df <- read_tsv('/Users/g/Desktop/sim_table_plus_all.tsv') %>%
  mutate(h_a = paste0("Ingroup: ", h_a),
         majority_size = paste0("Majority fraction: ", majority_size))

#### node sampling  ##############################################################
node_sample_df = df %>%
  mutate(node_sample_err = prop_d_a - trueprop_d_a) %>%
  select(method, node_sample_err, majority_size, h_a) %>%
  filter(method != 'population')
  # group_by(method, majority_size, h_a) %>%
  # summarize(
  #   node_sample_err_mean = mean(node_sample_err),
  #   node_sample_err_ucl = quantile(node_sample_err, 0.95),
  #   node_sample_err_lcl = quantile(node_sample_err, 0.05))

p1 = ggplot(data=node_sample_df) +
  theme_bw() +
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        legend.position="bottom") +
  geom_hline(yintercept=0, alpha=0.5, linetype='dashed') + 
  geom_violin(aes(y=node_sample_err, x=method, color=method)) +
  stat_summary(fun.y="mean",
               geom="point",
               shape=43,
               size=3,
               aes(y=node_sample_err, x=method, color=method)) +
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

ggsave('/Users/g/Drive/project-RA/network-sampling/paper/p1.pdf', width=9, height=6)

#### edge sampling  ##############################################################
edge_sample_df = df %>%
  mutate(edge_sample_err = prop_d_aa - trueprop_d_aa) %>%
  select(method, edge_sample_err, majority_size, h_a) %>%
  filter(method != 'population')

p2 = ggplot(data=edge_sample_df) +
  theme_bw() +
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        legend.position="bottom") +
  geom_hline(yintercept=0, alpha=0.5, linetype='dashed') + 
  geom_violin(aes(y=edge_sample_err, x=method, color=method)) +
  stat_summary(fun.y="mean",
               geom="point",
               shape=43,
               size=3,
               aes(y=edge_sample_err, x=method, color=method)) +
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

ggsave('/Users/g/Drive/project-RA/network-sampling/paper/p2.pdf', width=9, height=6)

#### coleman plots ###############################################################
coleman_sample_df = df %>%
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

p3 = ggplot(data=coleman_sample_df) +
  theme_bw() +
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        legend.position="bottom") +
  geom_hline(yintercept=0, alpha=0.5, linetype='dashed') + 
  geom_violin(aes(y=coleman_err, x=method, color=method)) +
  stat_summary(fun.y="mean",
               geom="point",
               shape=43,
               size=3,
               aes(y=coleman_err, x=method, color=method)) +
  facet_grid(majority_size~h_a) +
  scale_color_discrete(name="Sampling method",
                       labels=c("Edge",
                                "Ego network",
                                "Node",
                                "Random walk",
                                "RDS",
                                "Snowball")) +
  labs(title="Coleman homophily sampling error", y="Sampling error") +
  lims(y=c(-1, 1))

ggsave('/Users/g/Drive/project-RA/network-sampling/paper/p3.pdf', width=9, height=6)

#### tradeoff between edge and node sampling #####################################

tradeoff_df = df %>%
  mutate(
    node_sample_err = prop_d_a - trueprop_d_a,
    edge_sample_err = prop_d_aa - trueprop_d_aa
  ) %>%
  group_by(method, h_a, majority_size) %>%
  summarize(
    node_err_mean = sqrt(mean(node_sample_err^2)),
    edge_err_mean = sqrt(mean(edge_sample_err^2))
  )

ggplot(data=tradeoff_df) +
  geom_point(aes(x=1 - node_err_mean, y=1 - edge_err_mean, color=method)) +
  facet_grid(majority_size~h_a)

tradeoff_agg_df = df %>%
  mutate(
    node_sample_err = prop_d_a - trueprop_d_a,
    edge_sample_err = prop_d_aa - trueprop_d_aa
  ) %>%
  group_by(method) %>%
  summarize(
    node_err_mean = sqrt(mean(node_sample_err^2)),
    edge_err_mean = sqrt(mean(edge_sample_err^2))
  )

ggplot(data=tradeoff_agg_df) +
  theme_bw() +
  geom_point(aes(x=1 - node_err_mean, y=1 - edge_err_mean, color=method)) +
  lims(x=c(0.85, 1.0), y=c(0.85, 1.0))

#### Correlation between edge and node error #####################################
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