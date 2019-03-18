# MAG in Elasticsearch

Want to explore the USPTO patnets in a search engine? Use these scripts to put PatentsView dataset in the Elasticsearch!

## Download MAG

Download **OAG** from [here](https://www.openacademic.ai/oag/). **Open Academic Graph (OAG)** unifies two billion-scale academic graphs: **Microsoft Academic Graph (MAG)** and **AMiner**. Two versions of OAG are provided at this time (`2019-03-12`).


## MAG V1

In total, there are 167 files included in `MAG V1` dataset with name `mag_papers_[0-166].txt`. Each line of each file has the JSON format.

### Indexing MAG V1 data

```bash
# use multiple cores to index data in parallel
python gen_index.py --cores [cpus_to_use] --index [index_name] --output [output_directory] --input [input_files]
```
where `cpus_to_use` gives how many cpus to use to paralle the process, `index_name` is the index name used by Elasticsearch, `output_directory` is the directory for output, and `input_files` are all input files. An example can be
```bash
python gen_index.py --cores 4 --index mag_v1 --output mag.index --input mag/*
```

In script `gen_index.py`, context fields `id`, `year`, `title`, `abstract`, `fos` and `keywords` are taken care of, though there are many other fileds in the original datafile. See [here](https://www.openacademic.ai/oag/) for details.

After indexing, the file looks like below.
```json
{"index": {"_index": "publication", "_id": "0000002e-c2f2-4e25-9341-60d39130ac7a"}}
{"year": 2015, "title": "system and method for maskless direct write lithography", "abstract": "a system and method for maskless direct write lithography are disclosed. the method includes receiving a plurality of pixels that represent an integrated circuit (ic) layout; identifying a first subset of the pixels that are suitable for a first compression method; and identifying a second subset of the pixels that are suitable for a second compression method. the method further includes compressing the first and second subset using the first and second compression method respectively, resulting in compressed data. the method further includes delivering the compressed data to a maskless direct writer for manufacturing a substrate. in embodiments, the first compression method uses a run-length encoding and the second compression method uses a dictionary-based encoding. due to the hybrid compression method, the compressed data can be decompressed with a data rate expansion ratio sufficient for high-volume ic manufacturing.", "fos": ["electronic engineering", "computer hardware", "engineering", "engineering drawing"], "keywords": []}
```

### Load dataset to Elasticsearch

By default, `Elasticsearch` supports to insert file less than `100MB`. So if you don't want to change default configuration of Elasticsearch, simplly use script below to split original files to smaller ones
```bash
mkdir [mag.es] && cat [mag.index]/* > [mag.es]/mag.total
cd [mag.es] && split -l 80000 mag.total && rm mag.total
```
where `[mag.index]` is the output directory used in [Indexing MAG V1 data](#indexing-mag-v1-data), and `[mag.es]` is a place to temporarily save mag data preprocessed for Elasticsearch.

Finally, it's time to load dataset into Elasticsearch. 

```bash
bash load_data.sh [index_name] [mag.es]
```
where `[index_name]` is index name used in [Indexing MAG V1 data](#indexing-mag-v1-data), and `mag.es` is the directory name used in the last step.
