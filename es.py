# -*- coding: utf-8 -*-

import subprocess


def create_index(index_name):
    """Create index.

    Parameters
    ----------
    index_name : str
        Index name.

    """

    st = 'curl -o /dev/null -s -X DELETE "localhost:9200/{}"'.format(
            index_name)
    subprocess.Popen(st, shell=True).communicate()
    if index_name == 'patent_tmp':
        st = 'curl -o /dev/null -s -X PUT "localhost:9200/{}" -H '.format(
                index_name) + \
             '\'Content-Type: application/json\' -d \'{"settings": ' + \
             '{"index" : {"number_of_shards" : 5}}, "mappings": ' + \
             '{"doc": {"_field_names": {"enabled": false}, ' + \
             '"properties": {"date": {"type": "date"}, ' + \
             '"id": {"type": "keyword"}, "abstract": {"type": "text"}}}}}\''
    else:
        st = 'curl -o /dev/null -s -X PUT "localhost:9200/{}" -H '.format(
                index_name) + \
             '\'Content-Type: application/json\' -d \'{"settings": ' + \
             '{"index" : {"number_of_shards" : 5}}, "mappings": ' + \
             '{"doc": {"_field_names": {"enabled": false}, ' + \
             '"properties": {"id": {"type": "keyword"}, ' + \
             '"text": {"type": "text"}}}}}\''
    subprocess.Popen(st, shell=True).communicate()
    st = 'curl -o /dev/null -s -X PUT "localhost:9200/{}/_settings" '.format(
            index_name) + \
         '-H \'Content-Type: application/json\' -d \'{"index" : ' + \
         '{"number_of_replicas" : 0, "refresh_interval" : -1}}\''
    subprocess.Popen(st, shell=True).communicate()


def delete_index(index_name):
    """Delete index.

    Parameters
    ----------
    index_name : str
        Index name.

    """

    st = 'curl -o /dev/null -s -X DELETE "localhost:9200/{}"'.format(
            index_name)
    subprocess.Popen(st, shell=True).communicate()


def refresh(index_name):
    """Refresh index.

    Parameters
    ----------
    index_name : str
        Index name.

    """

    st = 'curl -o /dev/null -s -X PUT "localhost:9200/{}/_settings" '.format(
            index_name) + \
        '-H \'Content-Type: application/json\' -d \'{"index" : ' + \
        '{"refresh_interval" : "1s"}}\''
    subprocess.Popen(st, shell=True).communicate()
    st = 'curl -o /dev/null -s -X POST "localhost:9200/{}/_refresh"'.format(
            index_name)
    subprocess.Popen(st, shell=True).communicate()


def bulk_insert(index_name, fp):
    """Use bulk API to load data to Elasticsearch.

    Parameters
    ----------
    index_name : str
        Name of index to handle.
    fp : str
        Path to input data file.

    """

    st = 'curl -o /dev/null -s -H \'Content-Type: application/x-ndjson\' ' +\
         '-XPOST \'localhost:9200/{}/doc/_bulk?pretty\' '.format(index_name) +\
         '--data-binary @{}'.format(fp)
    subprocess.Popen(st, shell=True).communicate()
