# -*- coding: utf-8 -*-

import os
import argparse
import json
import time

import pandas as pd
import elasticsearch
import elasticsearch.helpers

from es import create_index, refresh, bulk_insert


def index_patent(ipath):
    """Read patent.tsv.

    Parameters
    ----------
    ipath : str
        Path to patent.tsv.

    Returns
    -------
    :class:`pandas.DataFrame`
        Data on granted patents.

    """

    print('Indexing patent.')
    index_name = 'patent_tmp'
    opath = os.path.join(os.path.dirname(ipath), 'patent.index.tmp.json')
    create_index(index_name)
    chunks = pd.read_csv(ipath, sep='\t', quoting=3, lineterminator='\n',
                         dtype=str, chunksize=50000)
    for chunk in chunks:
        chunk.drop(columns=['type', 'number', 'country', 'kind', 'num_claims',
                            'filename', 'withdrawn'], inplace=True)
        chunk['date'] = pd.to_datetime(chunk['date'], errors='coerce')
        chunk.dropna(axis='index', subset=['id', 'title', 'abstract'],
                     how='any', inplace=True)
        with open(opath, 'w') as ofp:
            for _, patent in chunk.iterrows():
                json.dump({'index': {'_index': index_name}}, ofp)
                ofp.write('\n')
                json.dump({'id': patent['id'],
                           'date': str(patent['date'].date()),
                           'title': patent['title'].lower().strip(),
                           'abstract': patent['abstract'].lower().strip()},
                          ofp)
                ofp.write('\n')
        bulk_insert(index_name, opath)
    refresh(index_name)
    os.remove(opath)


def index_claim(ipath):
    """Read claim.tsv.

    Parameters
    ----------
    ipath : str
        Path to patent.tsv.

    Returns
    -------
    :class:`pandas.DataFrame`
        Patent claims and their dependency.

    """

    print('Indexing claim.')
    index_name = 'claim_tmp'
    opath = os.path.join(os.path.dirname(ipath), 'claim.index.tmp.json')
    create_index(index_name)
    chunks = pd.read_csv(ipath, sep='\t', quoting=3, lineterminator='\n',
                         dtype=str, chunksize=50000)
    for chunk in chunks:
        chunk.drop(columns=['dependent', 'sequence', 'exemplary'],
                   inplace=True)
        chunk.dropna(axis='index', subset=['uuid', 'text', 'patent_id'],
                     how='any', inplace=True)
        with open(opath, 'w') as ofp:
            for _, claim in chunk.iterrows():
                json.dump({'index': {'_index': index_name}}, ofp)
                ofp.write('\n')
                json.dump({'id': claim['patent_id'],
                           'text': claim['text'].lower().strip()}, ofp)
                ofp.write('\n')
        bulk_insert(index_name, opath)
    refresh(index_name)
    os.remove(opath)


def index_summary(ipath):
    """Read brf_sum_text.tsv.

    Parameters
    ----------
    ipath : str
        Path to brf_sum_text.tsv.

    Returns
    -------
    :class:`pandas.DataFrame`
        Patent claims and their dependency.

    """

    print('Indexing summary.')
    index_name = 'summary_tmp'
    opath = os.path.join(os.path.dirname(ipath), 'summary.index.tmp.json')
    create_index(index_name)
    chunks = pd.read_csv(ipath, sep='\t', quoting=3, lineterminator='\n',
                         dtype=str, chunksize=5000)
    for chunk in chunks:
        chunk.dropna(axis='index', subset=['uuid', 'text', 'patent_id'],
                     how='any', inplace=True)
        with open(opath, 'w') as ofp:
            for _, summary in chunk.iterrows():
                json.dump({'index': {'_index': index_name}}, ofp)
                ofp.write('\n')
                json.dump({'id': summary['patent_id'],
                           'text': summary['text'].lower().strip()}, ofp)
                ofp.write('\n')
        bulk_insert(index_name, opath)
    refresh(index_name)
    os.remove(opath)


def index_patentsview_for_elasticsearch(args):
    """Index patentsview data before inserting data into elasticsearch."""

    opath = os.path.join(os.path.dirname(args.patent), 'es.tmp.json')
    es = elasticsearch.Elasticsearch()
    hits = elasticsearch.helpers.scan(es, index='patent_tmp',
                                      query={'query': {'match_all': {}}})
    with open(opath, 'w') as ofp:
        for hit in hits:
            patent = hit['_source']
            pid = patent['id']
            claims = elasticsearch.helpers.scan(
                    es, index='claim_tmp',
                    query={'query': {'match': {'id': pid}}})
            patent['claim'] = ' '.join([claim['_source']['text']
                                        for claim in claims])
            summaries = elasticsearch.helpers.scan(
                    es, index='summary_tmp',
                    query={'query': {'match': {'id': pid}}})
            patent['summary'] = ' '.join([summary['_source']['text']
                                          for summary in summaries])
            json.dump({'index': {'_index': 'patentsview'}}, ofp)
            ofp.write('\n')
            json.dump(patent, ofp)
            ofp.write('\n')


if __name__ == "__main__":
    pparser = argparse.ArgumentParser()
    pparser.add_argument('--patent', required=True, type=str,
                         help='Path to patent.tsv')
    pparser.add_argument('--claim', required=True, type=str,
                         help='Path to claim.tsv')
    pparser.add_argument('--summary', required=True, type=str,
                         help='Path to brf_sum_text.tsv')
    args = pparser.parse_args()
    if args.patent:
        index_patent(args.patent)
    if args.claim:
        index_claim(args.claim)
    if args.summary:
        index_summary(args.summary)
    time.sleep(120)  # make sure that elasticsearch have time to refresh
    index_patentsview_for_elasticsearch(args)
