import json
import matplotlib.pyplot as plt
import numpy as np

def generate_histogram(
    method,
    m, # mean degree
    h, #homophily
    f): #probability of majority group
    
    g = open('data/{}({}, {}){}{}.json'.format(
            method,h[0],h[1],f,m),'r')
    data = json.load(g)
    g.close()

    g = open('data/{}({}, {}){}{}.json'.format(
            'population',h[0],h[1],f,m),'r')
    t_data = json.load(g)
    g.close()

    t_mean = np.mean([d["('a', 'a')"]/(d["('a', 'b')"]+d["('b', 'a')"]+d["('a', 'a')"]) 
            for d in t_data])
    s_mean = np.mean([d["('a', 'a')"]/(d["('a', 'b')"]+d["('b', 'a')"]+d["('a', 'a')"]) 
            for d in data])

    s_var = np.var([d["('a', 'a')"]/(d["('a', 'b')"]+d["('b', 'a')"]+d["('a', 'a')"]) 
            for d in data])

    print("True Mean: " + str(t_mean))
    print("Sample Mean: " + str(s_mean))

    print("True Variance: " + str(t_var))
    print("Sample Variance: " + str(s_var))
    hist = [d["('a', 'a')"]/(d["('a', 'b')"]+d["('b', 'a')"]+d["('a', 'a')"]) 
            for d in data]

    #Graph the histogram
    fig, ax = plt.subplots()
    ax.hist(hist, bins=50, normed=True)

    plt.axvline(s_mean, color = 'r', linestyle='dashed', linewidth=2)
    plt.axvline(t_mean, color = 'y', linestyle='dashed', linewidth=2)
    
    plt.show()

if __name__ == "__main__":
    generate_histogram("sample_random_edges",4,(0.5, 0.5),0.5)
