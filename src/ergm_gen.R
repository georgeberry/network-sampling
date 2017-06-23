library(statnet)

s <- .8 # Majority group fraction
g_size <- 5000 
h <- c(.8,.8) # "Homophily" values

gengraph.net <- network.initialize(g_size, directed=F)
gengraph.net %v% 'group' <- sample(c(rep(0,s*g_size),rep(1,g_size-floor(s*g_size))))

deg_dist <- seq(1,g_size)^(-3)
deg_dist <- deg_dist/deg_dist[g_size]
gengraph.deg <- deg_dist

gengraph.mixmat <- matrix(c(h[0],1-h[0],1-h[1],h[1])*sum(deg_dist)/2,
	nrow=2,byrow=T)

gengraph.edges <- sum(gengraph.mixmat)
gengraph.

