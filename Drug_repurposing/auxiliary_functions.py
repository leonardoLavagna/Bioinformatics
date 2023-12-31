## AUXILIARY FUNCTIONS FOR DRUG REPURPOSING PROJECT

import re
import csv
import random
import json
import ast
import os
import statistics
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import markov_clustering as mc
from tqdm import tqdm
from scipy.stats import hypergeom
from sklearn.model_selection import train_test_split

path = './'


def make_seeds_splits(DGA,HSN,disease,path=path):
    """
    Splits the seed genes
    """
    print("Creating seed gene splits...")
    random.seed(123)
    seed_genes = list(set.intersection(set(DGA['geneSymbol'].tolist()), set(HSN['Official Symbol Interactor A'].tolist()).union(HSN['Official Symbol Interactor B'].tolist())))
    with open(f'{path}{disease}_seed_gene.txt','w') as f:
        f.write(str(seed_genes))
    f.close()
    print('Number of genes in disease PPI: ', len(seed_genes))
    
    splits = {}
    for i in range(0,5):
        start = len(seed_genes)//5*i
        splits[i]=seed_genes[start:start + len(seed_genes)//5]
    if len(seed_genes)>len(seed_genes)//5:
        splits[1]+=seed_genes[len(seed_genes):]
        
    with open(f'{path}{disease}_splits.json', 'w') as fp:
        json.dump(splits, fp)

    print('# Process completed.')
    return seed_genes,splits


def import_seeds_split(disease):
  """
  Get the seed genes
  Remark. The ast module is needed here, see 
  https://stackoverflow.com/questions/15197673/using-pythons-eval-vs-ast-literal-eval
  """
  print("Importing seed genes...")
  with open(f'{path}{disease}_seed_gene.txt','r') as f:
      seeds = ast.literal_eval(f.read())
  with open(f'{path}{disease}_splits.json') as json_file:
      splits = json.load(json_file)

  print('# Process completed.') 
  return seeds, splits


def interactome_processing(path=path):
    '''
    Filter out self-loops
    Filter out repetitive interactions ([A-B,B-A] or [A-B,A-B] or [B-A,B-A])
    Filter out interactions that are not physical
    '''
    print("Processing interactome...")
    HSN = pd.read_csv(path, sep = "\t")
    HSN = HSN[HSN['Organism Name Interactor A'] == HSN['Organism Name Interactor B']]
    HSN = HSN[HSN[f'Official Symbol Interactor A'] != HSN[f'Official Symbol Interactor B']] 
    HSN = HSN[HSN['Experimental System Type'] == "physical"]
    print('# Process completed.') 
    return HSN


def make_disease_graph(HSN, DGA, DG_in_PPI):
    '''
    Print Disease LCC size and returns graph with all nodes
    '''
    print("Creating Disease LCC graph...")
    DN = HSN[HSN["Official Symbol Interactor A"].isin(DGA["geneSymbol"]) & HSN["Official Symbol Interactor B"].isin(DGA["geneSymbol"])] 
    G= nx.Graph()
    G.add_nodes_from(DG_in_PPI)
    G.add_edges_from(list(zip(map(int, DN["Entrez Gene Interactor A"]), map(int, DN["Entrez Gene Interactor B"]))))
    print('Nodes in disease LCC ',max([len(G) for G in sorted(nx.connected_components(G), key=len, reverse=True)]))
    print("# Process completed.")
    return G


def DGA_processing(filepath, disease):
    '''
    Filter for disease of interest
    '''
    DGA = pd.read_csv(filepath, sep = '\t')
    DGA = DGA[DGA['diseaseName'] == disease]
    return DGA


def extract_LCC_form_PPI(HSN):
    '''
    Creates graph and returns LCC. Prints LCC size. Save graph adj. matrix as file.
    '''
    print("Extracting LCC...")
    PPI = nx.Graph()
    PPI.add_nodes_from(HSN["Official Symbol Interactor A"].tolist() + HSN["Official Symbol Interactor B"].tolist())
    PPI.add_edges_from(list(zip(HSN["Official Symbol Interactor A"], HSN["Official Symbol Interactor B"])))
    LCCs = [len(PPI) for PPI in sorted(nx.connected_components(PPI), key=len, reverse=True)]
    LCC = PPI.subgraph(max(nx.connected_components(PPI), key=len))
    print('Nodes ',len(max(nx.connected_components(PPI), key=len)),', Connections ', len(LCC.edges()))
    nx.write_adjlist(LCC, "PPI.adjlist")
    print("# Process completed.")
    return LCC


def plot_LCC(LCC, DG_in_PPI):
  """
  Plot LCC
  """
  fig = plt.figure(1, figsize=(8, 8))
  color_map = []
  for node in LCC:
      if node in DG_in_PPI:
          color_map.append('red')
      else: 
          color_map.append('blue')      

  nx.draw(LCC, node_color=color_map, node_size=3)
  plt.show()


def evaluationDiffusion(top_n, cval, t,k,path):
    recalls, precs, f1s, ndcg_scores = ([] for _ in range(4))
    cv = pd.read_csv(path + 'ResDiffusionCross{}_t={}.csv'.format(k,t))
    data=cv.sort_values(by='diffusion_output_heat',ascending=False)['name']
    
    with open(path+'probeset{}.txt'.format(k)) as f:
          probeset = f.read().split(",")
          probeset=set(probeset)
          probeset.remove("")  

    # Subsetting
    top = set(data[0:top_n]) 

    # Intersecting with the probe set  
    inters = top.intersection(probeset) 

    # Appending the results
    recall = round(len(inters)/cval)
    prec = round(len(inters)/top_n)

    try:
      f1s = round(2*((recall*prec)/(recall+prec)))
    except:
      f1s=0

    return {'recall': recall, 
            'precision': prec, 
            'F1 Score': f1s, }


def evaluation(top_n, cval, alg_name,k):
    recalls, precs, f1s, ndcg_scores = ([] for _ in range(4))

    cv = pd.read_csv('res{}.txt'.format(k),sep='\t')
    cv_nodes = cv[alg_name + '_node'].tolist()

    with open(path+'probeset{}.txt'.format(k)) as f:
          probeset = f.read().split(",")
          probeset=set(probeset)
          probeset.remove("")  

    # Subsetting
    top = set(cv_nodes[0:top_n]) 
    
    # Intersecting with the probe set  
    inters = top.intersection(probeset) 
    print(inters)

    # Appending the results
    recall = round(len(inters)/cval)
    prec = round(len(inters)/top_n)
    
    try:
      f1s = round(2*((recall*prec)/(recall+prec)))
    except:
      f1s=0

    return {'recall': recall, 
            'precision': prec, 
            'F1 Score': f1s, }
            

def print_nested_dict(dict_obj, indent = 0):
    ''' Pretty Print nested dictionary with given indent level  
    '''
    # Iterate over all key-value pairs of dictionary
    for key, value in dict_obj.items():
        # If value is dict type, then print nested dict 
        if isinstance(value, dict):
            print(' ' * indent, key, ':', '{')
            print_nested_dict(value, indent + 4)
            print(' ' * indent, '}')
        else:
            print(' ' * indent, key, ':', value)


def display_dict(dict_obj):
    ''' Pretty print nested dictionary
    '''
    print('{')
    print_nested_dict(dict_obj, 4)
    print('}')


def find_best_drugs(df):
  return(df['drug'].value_counts().index.tolist()[:6])
