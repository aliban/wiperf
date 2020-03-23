#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Set of functions to export results data to a variety of destinations
"""
import csv
import json
import os

from modules.exporters.heclogger import HecLogger

class ResultsExporter(object):
    """
    Class to implement universal resuts exporter for wiperf
    """

    def __init__(self, file_logger, platform):

        self.platform = platform
        self.file_logger = file_logger

    def send_results_to_csv(self, data_file, dict_data, column_headers, file_logger, delete_data_file=True):

        try:
            # if False:
            if os.path.exists(data_file) and (delete_data_file == False):
                with open(data_file, 'a') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=column_headers)
                    writer.writerow(dict_data)
            else:
                with open(data_file, 'w') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=column_headers)
                    writer.writeheader()
                    writer.writerow(dict_data)
        except IOError as err:
            file_logger.error("CSV I/O error: {}".format(err))


    def send_results_to_json(self, data_file, dict_data, file_logger, delete_data_file=True):

        try:
            # change write/append mode depending on whether data file exists
            file_mode = 'w'
            if os.path.exists(data_file) and (delete_data_file == False):
                file_mode = 'a'

            with open(data_file, file_mode) as json_file:
                json.dump(dict_data, json_file)
        except IOError as err:
            file_logger.error("JSON I/O error: {}".format(err))


    def send_results_to_hec(self, host, token, port, dict_data, file_logger, source):

        file_logger.info("Sending event to HEC: {} (dest host: {}, dest port: {})".format(
            source, host, port))
        HecLogger(host, token, port, dict_data, source, file_logger)


    def send_results(self, config_vars, results_dict, column_headers, data_file, test_name, file_logger, delete_data_file=False):

        # dump the results to appropriate destination

        # Check if we are using the Splunk HEC (https transport)
        if config_vars['data_transport'] == 'hec':
            file_logger.info(
                "HEC update: {}, source={}".format(data_file, test_name))
            self.send_results_to_hec(config_vars['data_host'], config_vars['splunk_token'], config_vars['data_port'],
                                results_dict, file_logger, data_file)
        # Create files if we are using the Splunk universal forwarder
        elif config_vars['data_transport'] == 'forwarder':

            # CSV file format for forwarder
            if config_vars['data_format'] == 'csv':
                data_file = "{}/{}.csv".format(config_vars['data_dir'], data_file)
                self.send_results_to_csv(data_file, results_dict, column_headers,
                                    file_logger, delete_data_file=delete_data_file)
            # JSON format for the forwarder
            elif config_vars['data_format'] == 'json':
                data_file = "{}/{}.json".format(config_vars['data_dir'], data_file)
                self.send_results_to_json(data_file, results_dict, file_logger, delete_data_file=delete_data_file)
            else:
                file_logger.info("Unknown file format type in config file: {}".format(
                    config_vars['data_format']))
                exit()
        # Transport type which is not know has been configured in the ini file
        else:
            file_logger.info("Unknown transport type in config file: {}".format(
                config_vars['data_transport']))
            exit()

        return True