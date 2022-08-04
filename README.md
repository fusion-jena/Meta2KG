# Meta2KG
This project aims at the automatic transformation of metadata XML file to a knowledge graph. 
Such transformation is based on embedding-based similarity.
We developed and tested our approach on Biodiversity domain however, our approach is not limited to it.

This repository contains the scripts we developed our pipeline. In this file, we explain the framework then we continue on how to reproduce the results.

## Workflow
The figure below shows our 4 stages workflow. 
1. Data Acquisition: from 7 Biodiversity data portals we collected a set of metadata files. Such that we divided them into Seen and Unseen data.
2. Ontology Development: We work on the Seen Data, the goals of that stage are:
   * To develop a shared underlying schema for the 7 repos. The results is the [Biodiversity Metadata Ontology (BMO)](https://doi.org/10.5281/zenodo.6948519).
   * To Obtain the BMO embeddings that we use for the automatic transformation in the later steps. The results is the [Biodiversity Metadata Ontology Embeddings (BMOE)](https://doi.org/10.5281/zenodo.6951658)
3. Match & Populate: Where we apply the cosine similarity between the BMOE and the Unseen data embeddings. In addition, we provide a validation module that ensure the validity of a KG triple. 
   * We evaluated our approach using a manually annotated ground truth: [Biodiversity Metadata Ground Truth](https://doi.org/10.5281/zenodo.6951623)
4. Release: We publish the final automatically generated knowledge graph in Zenodo [Biodiversity Metadata Knowledge Graph (BMKG)](https://doi.org/10.5281/zenodo.6948573).

![Meta2KG Workflow!](images/workflow.png)

## How to Use

### Preprocessing
* `flatten.py` transforms the XML files into a flat key-value pairs dictionary. a Key would contain the entire heirarchy.
* `transform_keys.py` cleans the generated flat keys of the dictionary above by e.g., removing too broad words.

### Custom Embeddings
* `meta2train.py` artificially creates sentences from the clean dictionary.
* `pretrain_embeddings.py` train a fasttext model on the created sentences. 

### Ontological Embeddings (BMOE)
* `group_keywords.py` since we develop a mean-based strategy to obtain embeddings for keys given their synonyms. This script is meant for catching such synonyms. This script would help figurig out what is related however, we keep the final result for the human.
  * We picked the relevant keys on our own, we put our use case under [/assets/onto_keywords_mapping.csv](/assets/onto_keywords_mapping.csv)
* `construct_onto_embeddings.py` will process the given mappings from the step above. Make sure it is correctly listed under the `config.py`.
  * `use_wiki_embeddings=True` Will activate the pre-trained wiki-based embeddings otherwise it will use our custom embeddings.
  * `use_weighted_embeddings=True` Will activate the weighted mean strategy to calculate the final embedding vector otherwise it has the mean only effect, no variable weights are given for the key's parts.
  * `use_keys_only=True` If true then no synonyms are processed otherwise it considers them.
  * Make sure to correctly place the generated file if you need to test various settings.

## Testing Environment
* This module solves the Unseen data **per repository** since we construct evaluation metrics of the matching techniques per data source.  
* Before you start, have a look on the testing [config.py](testing/config.py) and make sure all the paths of the ontological embeddings, ground truth ... etc. In addition, you tweak the target experiment there by setting if you use the Wiki-based embeddings and/or to use the mean-based technique to calculate the Meta vectors (MetaE)
* You can download the required resources as follows:
  * [Ground Truth (gt)](https://doi.org/10.5281/zenodo.6951623)
  * [Our custom embeddings](https://doi.org/10.5281/zenodo.6951658) 
  * [pretrained-fasttext](https://fasttext.cc/docs/en/english-vectors.html)
* After that you can proceed with the regular steps as follows: 
  * `flatten.py` & `transform_keys.py` apply the same steps for the pre-processing but on the unseen data. 
  * `transformed_keywords_values.py` stores both the clean key, original key and the associated value from the unseen data. This structure maps to the provided ground truth.
  * `match.py` it parses the dictionary that is resulted from above and tries to match it to one of the selected ontological embeddings using cosine similarity. We conduced 6 experiments, please check our paper for more details. 
  * `evaluate.py` calculates the classification report based on the placed ground truth and the resultant solutions. Our results showed that the **Wiki-based embeddings** with the **Weighted Mean** strategy yielded into the best score.

## Knowledge Graph Population
* This module solves the unseen data **per dataset**, it creates a solution/prediction per each file ignoring the original source/repository. Each dataset would be translated into a record/instance of `BMO:Dataset`.
* `flatten.py`, `transform_keys.py`, `transformed_keywords_values.py`, & `match.py` apply the same steps for the pre-processing and matching we did in the _Testing Environment_ , but on the level of the dataset instead of the repository.
* `populate.py` transforms the matched aka solved datasets (key - match) into RDF triples that follows the BMO ontology. 
  * `utils` contain the used data structures, mappings and namespaces.
  * `validate_values` contain regular expressions validator to asset datatype constraints e.g., phone, email, date ... etc.