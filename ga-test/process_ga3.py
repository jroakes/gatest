from ua import UniversalAnalytics, AnalyticsQuery, AnalyticsReport
import pandas as pd
import json

def get_report(ua, ga3_view_id, pull_start_date, pull_end_date, pageToken):
    dimensions = [
        'ga:date',
        'ga:landingPagePath',
        'ga:country',
        'ga:region',
        'ga:city',
        'ga:source',
        'ga:medium',
        'ga:campaign',
    ]

    metrics = [
        'ga:users',
        'ga:newUsers',
        'ga:entrances',
        'ga:sessions',
        'ga:pageviews',
        'ga:uniquePageviews',
        'ga:timeOnPage',
        #{ga:conversion_event},
        'ga:transactionRevenue',
        'ga:transactions',
    ]

    query = (
        AnalyticsQuery(ua, ga3_view_id)
        .date_range([(pull_start_date, pull_end_date)])
        .dimensions(dimensions)
        .metrics(metrics)
        .page_size(10000)
        .page_token(pageToken)
    )
    response = query.get().raw
    return response

def get_token(response):
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader',
                {}).get('metricHeaderEntries', [])
        pageToken = report.get('nextPageToken', None)
    return pageToken

def dict_transfer(response, mylist):
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
        rows = report.get('data', {}).get('rows', [])
        for row in rows:
            dict = {}
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])

            for header, dimension in zip(dimensionHeaders, dimensions):
                dict[header] = dimension

            for i, values in enumerate(dateRangeValues):
                for metric, value in zip(metricHeaders, values.get('values')):
                    if ',' in value or '.' in value:
                        dict[metric.get('name')] = float(value)
                    elif value == '0.0':
                        dict[metric.get('name')] = int(float(value))
                    else:
                        dict[metric.get('name')] = int(value)
            mylist.append(dict)
