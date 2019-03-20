# PatentsView in Elasticsearch

Want to explore the USPTO patents in a search engine? Use these scripts to put [PatentsView](http://www.patentsview.org/web/#viz/relationships) dataset in the Elasticsearch!

## Download PatentsView

PatentsView provides FREE USPTO patents, which can be downloaded [here](http://www.patentsview.org/download/). You only need to download files which contain patent's context such as `title`, `abstract`, `claim`, `summary`. See table below to choose which one to download.

| Filename | Description |
| -- | -- |
| `claim.tsv` | Claims of patents |
| `brf_sum_text.tsv` | Summary of patents |
| `patent.tsv` | Title and abstract of patents |

## Indexing PatentsView data

`Title`, `abstract`, `claim` and `summary` of a patent are saved in different files as shown in the above table. As a result, one has to join all three files by the patent id column to have all the context fields of a patent available. The most straightforward way is to load the file into memory and join together using `pandas` or `dask`, as long as you have enough memory. An alternative way is to load data into Elasticsearch separately and then join different fields together using Elasticsearch's match function.

```bash
python index_patentsview.py --patent [patent.tsv] --claim [claim.tsv] --summary [brf_sum_text.tsv]
```

For each input file, a temporal index is generated in Elasticsearch which are `patent_tmp`, `claim_tmp` and `summary_tmp` respectively. At last, the above script generates file `es.tmp.json` in the directory where the `[patent.tsv]` is.

## Load dataset to Elasticsearch

By default, Elasticsearch supports to insert file less than `100MB`. So if you don't want to change the default configuration of Elasticsearch, use the script below to split original files to smaller ones
```bash
mkdir [patent.es] && split -d -l 5000 [es.tmp.json] [patent.es]/patent. && rm [es.tmp.json]
```
where `[es.tmp.json]` is data generated in above step.

Finally, it's time to load dataset into Elasticsearch. 

```bash
bash load_data.sh [patent.es]
```
where `[patent.es]` is the directory name used in the last step.

## Clean up temporal indices

The following command lists all indices in your Elasticsearch.
```bash
curl -X GET "localhost:9200/_cat/indices?v&s=index:asc"
```

The result should have three temporal indices we build in step [Indexing PatentsView data](#idexing-patentsview-data), which are `patent_tmp`, `claim_tmp`, and `summary_tmp`. And most importantly, the patents data should be in Elasticsearch under the name `patentsview`. You can quickly do some simple search on it to test if it works as expected. If everything goes well, then it's safe to delete those temporal indices to save space in disk.
```bash
curl -X DELETE "localhost:9200/patent_tmp"
curl -X DELETE "localhost:9200/claim_tmp"
curl -X DELETE "localhost:9200/summary_tmp"
```
