# Drug-repurposing
<img width="368" alt="Screenshot 2023-01-12 alle 14 41 02" src="https://user-images.githubusercontent.com/91341004/212082115-9f7dcdfb-e688-47cc-8a0e-58faab2c45b8.png">

The aim of this study is to find new drugs, as well as currently used drugs, associated to Hypertensive Disease using a network approach. We used differ- ent algorithms: DIAMOnD, DIaBLE and Diffusion Based. We evaluated each algorithm using standard cross-validation techniques and we found that the latter perform better. We used it to find the 200 best putative genes, carried out enrichment analysis with different tools, and from them we selected the best 20 to find the highest matching drugs for each such gene. We found 6 drugs with the same frequencies, two of them were already discussed in several studies in relation with Hypertensive Disease while the other four weren’t. We also tried to find new putative disease modules from the human interactome network and we found eight list of possible disease associated genes.

### What's in here?
Here you can find:
- the notebook of the project `BI_main.ipynb`
- the files we created and that are needed to run the notebook.
- the report `report.pdf` of the project.

### Dataset
We used two datasets:
- `BIOGRID-ORGANISM-Homo_sapiens-4.4.204.tab3.txt` which contains the Human Interactome, and is available at: https://downloads.thebiogrid.org/BioGRID;
- `curated_gene_disease_associations.tsv` which contains the Disease-Gene Associations, and is available at: https://www.disgenet.org/downloads.

### Disclamair
This project was done in collaboration with Leonardo Skerl and Simone Boesso
