import io, os
import random

# Read CoNLL-U format
def conll_read_sentence(file_handle):

	sent = []

	for line in file_handle:
		line = line.strip('\n')
		if line.startswith('#') is False:
			toks = line.split("\t")
			if len(toks) != 10 and sent not in [[], ['']]:
				return sent 
			if len(toks) == 10 and '-' not in toks[0] and '.' not in toks[0]:
				if toks[0] == 'q1':
					toks[0] = '1'
				sent.append(toks)

	return None


def n_sents_train(train_file):
	train_data = []
	with open(train_file) as f:
		sent = conll_read_sentence(f)
		while sent is not None:
			words = [tok[1] for tok in sent]
			POS_tags = [tok[3] for tok in sent]
			train_data.append([words, POS_tags])
			sent = conll_read_sentence(f)

	return len(train_data)

# Generate training sets of different sizes 
# with correspondingly differetly sized selection set
# Generate 10 training sets (for now) for each training set size
def generate_train_al(train_file, train_size, treebank, train_n = 10):
	train_data = []
	with open(train_file) as f:
		sent = conll_read_sentence(f)
		while sent is not None:
			words = [tok[1] for tok in sent]
			POS_tags = [tok[3] for tok in sent]
			train_data.append([words, POS_tags])
			sent = conll_read_sentence(f)

	train_data_idx_list = [i for i in range(len(train_data))]

	for i in range(train_n):
		n = i + 1
		train_set_idx_list = random.sample(train_data_idx_list, k = train_size)
		selection_set_idx_list = [idx for idx in train_data_idx_list if idx not in train_set_idx_list]
		train_set = [train_data[idx] for idx in train_set_idx_list]
		select_set = [train_data[idx] for idx in selection_set_idx_list]

		stats_file = io.open('pos_data/al/' + treebank + '/stats.txt', 'w')
		header = ['', 'N_sents', 'N_toks']

		n_toks_train = 0
		for tok in train_set[0]:
			n_toks_train += len(tok)
		train_info = ['train', len(train_set), n_toks_train]

		n_toks_select = 0
		for tok in select_set[0]:
			n_toks_select += len(tok)
		select_info = ['select', len(select_set), n_toks_select]

		stats_file.write(' '.join(w for w in header) + '\n')
		stats_file.write(' '.join(str(tok) for tok in train_info) + '\n')
		stats_file.write(' '.join(str(tok) for tok in select_info) + '\n')

		train_set_input_file = io.open('pos_data/al/' + treebank + '/train.' + str(train_size) + '_' + str(n) + '.input', 'w')
		train_set_output_file = io.open('pos_data/al/' + treebank + '/train.' + str(train_size) + '_' + str(n) + '.output', 'w')
		for tok in train_set:
			train_set_input_file.write(' '.join(w for w in tok[0]) + '\n')
			train_set_output_file.write(' '.join(POS for POS in tok[1]) + '\n')

		select_set_input_file = io.open('pos_data/al/' + treebank + '/select.' + str(train_size) + '_' + str(n) + '.input', 'w')
		select_set_output_file = io.open('pos_data/al/' + treebank + '/select.' + str(train_size) + '_' + str(n) + '.output', 'w')
		for tok in select_set:
			select_set_input_file.write(' '.join(w for w in tok[0]) + '\n')
			select_set_output_file.write(' '.join(POS for POS in tok[1]) + '\n')


# Generate full test data
def generate_test(test_file, treebank):
	test_data = []
	with open(test_file) as f:
		sent = conll_read_sentence(f)
		while sent is not None:
			words = [tok[1] for tok in sent]
			POS_tags = [tok[3] for tok in sent]
			test_data.append([words, POS_tags])
			sent = conll_read_sentence(f)

	test_set_input_file = io.open('pos_data/al/' + treebank + '/test.full.input', 'w')
	test_set_output_file = io.open('pos_data/al/' + treebank + '/test.full.output', 'w')
	for tok in test_data:
		test_set_input_file.write(' '.join(w for w in tok[0]) + '\n')
		test_set_output_file.write(' '.join(w for w in tok[1]) + '\n')

try:
	os.system('mkdir pos_data')
except:
	pass

try:
	os.system('mkdir pos_data/al')
except:
	pass

exception_file = io.open('pos_exceptions.txt', 'w')

for treebank in os.listdir('ud-treebanks-v2.13/'):
	train_file = ''
	test_file = ''
	for file in os.listdir('ud-treebanks-v2.13/' + treebank + '/'):
		if 'train.conllu' in file:
			train_file = 'ud-treebanks-v2.13/' + treebank + '/' + file
		if 'test.conllu' in file:
			test_file = 'ud-treebanks-v2.13/' + treebank + '/' + file

	if train_file != '' and test_file != '':

		os.system('mkdir pos_data/al/' + treebank)

		train_full_size = n_sents_train(train_file)
		if train_full_size <= 25:
			exception_file.write(treebank + ' ' + str(train_full_size) + '\n')
			exception_file.write('\n')
		else:
			start_size = 25
			print(treebank)
			generate_train_al(train_file, start_size, treebank)
			while start_size <= 5000:
				try:
					print(start_size)
					train_full_size = generate_train_al(train_file, start_size, treebank)
				except:
					print(start_size)

				start_size += 25

		generate_test(test_file, treebank)

		print('')
