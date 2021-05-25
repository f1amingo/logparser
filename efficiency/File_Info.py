def get_file_size(dataset: str) -> dict:
    file_size = {
        '1m': '%s_1m.log' % dataset,
        '5m': '%s_5m.log' % dataset,
        '10m': '%s_10m.log' % dataset,
        '25m': '%s_25m.log' % dataset,
        '50m': '%s_50m.log' % dataset,
        '75m': '%s_75m.log' % dataset,
        '100m': '%s_100m.log' % dataset,
    }
    return file_size
