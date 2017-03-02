import json
import matplotlib.pyplot as plt

def generate_histogram(
    method,
    m, # mean degree
    h, #homophily
    f): #probability of majority group
    
    f = open('data/{}({}, {}){}{}.json'.format(
            method,h[0],h[1],f,m),'r')
    data = json.load(f)
    f.close()

    hist = [d["('a', 'a')"]/(d["('a', 'b')"]+d["('b', 'a')"]+d["('a', 'a')"]) 
            for d in data]

    #Graph the histogram
    fig, ax = plt.subplots()
    ax.hist(hist, bins=50, normed=True)
    plt.show()

if __name__ == "__main__":
    generate_histogram("sample_random_edges",4,(0.5, 0.5),0.5)