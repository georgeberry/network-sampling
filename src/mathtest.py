import numpy as np
import pandas as pd

def convert_edge_matrix(p):
	q = 1-p
	convert = np.matrix([
		[q**2, p*q, p*q, p**2],
		[p*q, q**2, p**2, p*q],
		[p*q, p**2, q**2, p*q],
		[p**2, p*q, p*q, q**2]])
	return convert.I

def convert_node_percent_matrix(p):
	q = 1-p
	convert = np.matrix([
		[1-p, p],
		[p, 1-p]
		])
	return convert.I

if __name__ == "__main__":
	mat = np.genfromtxt("../sim_output/randoutput.tsv", skip_header = 1)

	tot_error = np.matrix([0,0,0,0])
	out = list()
	for i in range(mat.shape[0]):
		p = mat[i, 10]
		conv_edge = convert_edge_matrix(p)
		conv_odds = convert_node_percent_matrix(p)

		true_edges = mat[i,12:16]
		false_edges = mat[i,1:5]
		true_node_odds = mat[i,18:20]
		false_node_odds = mat[i,8:10]

		predict_links = conv_edge.dot(false_edges)
		predict_odds = conv_odds.dot(false_node_odds)

		# predict_links = conv_edge.dot(true_edges)
		
		predict_hom = predict_links[0,0]/(predict_links[0,0]+predict_links[0,1])
		predict_inbreed = (predict_hom - predict_odds[0,0])/(1 - predict_odds[0,0])

		# tot_error = tot_error + (predict - false_edges)

		result = {
			"true_hom": mat[i,16],
			"false_hom": mat[i,6],
			"predict_hom": predict_inbreed,
			"p_wrong": p,
			"true_d_aa": true_edges[0],
			"false_d_aa": false_edges[0],
			"predict_d_aa": predict_links[0,0],
			"true_w_aa": true_node_odds[0],
			"false_w_aa": false_node_odds[0],
			"predict_w_aa": predict_odds[0,0]
		}

		out.append(result)

	df = pd.DataFrame(out)
	df.to_csv("../sim_output/computed.tsv",sep='\t')

	print(np.divide(tot_error,mat.shape[0]))