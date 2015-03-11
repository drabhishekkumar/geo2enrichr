"""This module contains functions for parsing SOFT files.

__authors__ = "Gregory Gundersen, Andrew Rouillard, Axel Feldmann, Kevin Hu"
__credits__ = "Yan Kou, Avi Ma'ayan"
__contact__ = "gregory.gundersen@mssm.edu"
"""


import numpy as np


def parse_geo(filename, platform, A_cols, B_cols):
	"""Parses SOFT files, discarding bad dataand converting probe IDs to gene
	sybmols.
	"""

	print('Parsing SOFT file.')

	# COL_OFFSET changes because GDS files are "curated", meaning that they
	# have their gene symbols included. GSE files do not and are 1 column
	# thinner. That said, we do not trust the DGS mapping and do the probe-to-
	# gene mapping ourselves.
	if 'GDS' in filename:
		BOF = '!dataset_table_begin'
		EOF = '!dataset_table_end'
		COL_OFFSET = 2
	else:
		BOF = '!series_matrix_table_begin'
		EOF = '!series_matrix_table_end'
		COL_OFFSET = 1

	genes = []
	A = []
	B = []
	expression_values = {}

	# For statistics about data quality.
	discarded_lines = 0.0
	line_count = 0.0
	unconverted_probes = 0.0
	probe_count = 0.0

	try:
		with open(filename, 'r') as soft_in:
			# Skip comments.
			discard = next(soft_in)
			while discard.rstrip() != BOF:
				discard = next(soft_in)

			# Read header and set column offset.
			header = next(soft_in).rstrip('\r\n').split('\t')
			header = header[COL_OFFSET:]
			line_length = len(header)

			# Find column indices.
			A_incides = [header.index(gsm) for gsm in A_cols]
			B_incides = [header.index(gsm) for gsm in B_cols]
	
			for line in soft_in:
				split_line = line.rstrip('\r\n').split('\t')
				if split_line[0] == EOF or split_line[1] == '--Control':
					continue

				probe  = split_line[0]
				values = split_line[COL_OFFSET:]

				# Perform a conservative cleanup by ignoring any rows that
				# have null values or an atypical number of columns.
				line_count += 1
				if ('' in values or
					'null' in values or
					'NULL' in values or
					len(values) is not line_length or
					# Three forward slashes, \\\, denotes multiple genes.
					'\\\\\\' in probe):
	
					discarded_lines += 1
					continue
				
				# GSD files already contain a column with gene symbols but we
				# do not trust that mapping.
				probe_count += 1
				gene = _probe2gene(platform, probe)
				if gene is None:
					unconverted_probes += 1
					continue

				A_row = [float(values[i]) for i in A_incides]
				B_row = [float(values[i]) for i in B_incides]
				A.append(A_row)
				B.append(B_row)
				genes.append(gene)

		stats = {
			'unconverted_probes_pct': unconverted_probes / probe_count * 100,
			'discarded_lines_pct': discarded_lines / line_count * 100
		}

	# Is this truly exceptional? If someone uses this API endpoint but does
	# not call the dlgeo endpoint first, this file will simply not exist!
	# Is this an acceptable API?
	except IOError:
		raise IOError('Could not read SOFT file from local server.')

	# Convert to numpy arrays, which are more compact and faster.
	return (genes, A, B, stats)


def parse_custom(filename):
	"""Parses custom SOFT files uploaded by the user.
	"""
	genes = []
	A = []
	B = []
	expression_values = {}

	with open(filename) as soft_in:
		samples = next(soft_in).strip().split('\t')
		header = next(soft_in).strip().split('\t')
		A_indices = [i for i,k in enumerate(header) if k == '0']
		B_indices = [i for i,k in enumerate(header) if k == '1']

		for line in soft_in:
			line = line.rstrip().split('\t')
			genes.append(line[0])
			values = line[1:]
			A_row = [float(values[i]) for i in A_indices]
			B_row = [float(values[i]) for i in B_indices]
			A.append(A_row)
			B.append(B_row)
	
	return genes, samples, header, A, B


def platform_supported(platform):
	if platform not in PROBE2GENE:
		return False
	return True


def _probe2gene(platform, probe):
	"""Converts probe IDs to gene symbols. Does not check if the platform is
	supported.
	"""
	# Strip any potential quotation marks.
	probe = probe.replace('"', '').replace('\'', '')
	try:
		if probe in PROBE2GENE[platform]:
			return PROBE2GENE[platform][probe]
	# This should never occur, given that we check if the platform is in the
	# dictionary. But just in case.
	except AttributeError:
		return None
	return None


def build_probe_dict(platform_probesetid_genesym_file):
    """Builds an in-memory dictionary mapping platforms to probe IDs to gene
    symbols.
    """
    # Platform data collected and script written by Andrew Rouillard.
    platform_dict = {}
    with open(platform_probesetid_genesym_file) as f:
        for line in f:
            entries = line.rstrip().split('\t')
            platform = entries[0]
            probesetid = entries[1]
            genesym = entries[2]
            if platform in platform_dict:
                platform_dict[platform][probesetid] = genesym
            else:
                platform_dict[platform] = {probesetid:genesym}
    return platform_dict


PROBE2GENE = build_probe_dict('core/softfile/probe2gene.txt')
