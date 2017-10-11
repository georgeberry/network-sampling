import numpy as np
import pandas as pd

def convert_edge_matrix(p_a,p_b):
	q_a = 1-p_a
	q_b = 1-p_b
	convert = np.matrix([
		[q_a**2, p_b*q_a, p_b*q_a, p_b**2],
		[p_a*q_a, q_a*q_b, p_a*p_b, p_b*q_b],
		[p_a*q_a, p_a*p_b, q_a*q_b, p_b*q_b],
		[p_a**2, p_a*q_b, p_a*q_b, q_b**2]])
	return convert.I

def convert_node_percent_matrix(p_a,p_b):
	convert = np.matrix([
		[1-p_a, p_b],
		[p_a, 1-p_b]
		])
	return convert.I

if __name__ == "__main__":
	'''
	This code takes the output of a bunch of simulation runs of misclassify_params
	and does some math on it. Each simulation run gets its own line in the output
	file with the true, post-misclassification, and predicted a-a links and a
	node proportions. The predicted links and nodes are generated with some
	pretty straightforward math, and they're functions of the post-misclassification
	links and nodes respectively.
	'''
	INFILE = "../sim_output/randoutput.tsv"
	OUTFILE = "../sim_output/computed.tsv"

	mat = np.genfromtxt(INFILE, skip_header = 1)

	out = list()
	for i in range(mat.shape[0]):
		p_a = mat[i, 10]
		p_b = mat[i, 10] # Right now p_a == p_b.
		conv_edge = convert_edge_matrix(p_a,p_b)
		conv_odds = convert_node_percent_matrix(p_a,p_b)

		true_edges = mat[i,12:16]
		false_edges = mat[i,1:5]
		true_node_odds = mat[i,18:20]
		false_node_odds = mat[i,8:10]

		predict_links = conv_edge.dot(false_edges)
		predict_odds = conv_odds.dot(false_node_odds)
		
		predict_hom = predict_links[0,0]/(predict_links[0,0]+predict_links[0,1])
		predict_inbreed = (predict_hom - predict_odds[0,0])/(1 - predict_odds[0,0])

		# List of output columnns and values.
		result = {
			"true_hom": mat[i,16],
			"false_hom": mat[i,6],
			"predict_hom": predict_inbreed,
			"p_a": p_a,
			"p_b": p_b,
			"true_d_aa": true_edges[0],
			"false_d_aa": false_edges[0],
			"predict_d_aa": predict_links[0,0],
			"true_w_aa": true_node_odds[0],
			"false_w_aa": false_node_odds[0],
			"predict_w_aa": predict_odds[0,0]
		}

		out.append(result)

	df = pd.DataFrame(out)
	df.to_csv(OUTFILE,sep='\t')