"""Run a shallow parser on the lines present in a file."""
from argparse import ArgumentParser
from json import dumps
import requests
import os
from re import search
# install wxconv
# pip install wxconv
from wxconv import WXC
from re import finditer


url = "http://10.4.16.166:8046/parser"
# but output is not ssf
conv = WXC(order='utf2wx', lang='hin')


def read_lines_from_file(file_path):
    """Read lines from a file using its file path."""
    with open(file_path, 'r', encoding='utf-8') as file_read:
        return [line.strip() for line in file_read.readlines() if line.strip()]


def write_lines_to_file(lines, file_path):
    """Write lines to a file."""
    with open(file_path, 'w', encoding='utf-8') as file_write:
        file_write.write('\n'.join(lines) + '\n')


def send_request_and_get_response(text, langauge='hin'):
    """Send shallow parser request to URL and get the response, update the language if other than hindi is required."""
    data = {'text': text, 'language': langauge, 'mode': 'list'}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=dumps(data), headers=headers)
    return r.json()


def split_feature(token_with_feature, feature):
    """Split feature of a token based on its type."""
    return token_with_feature.split('$%:%$')


def split_token_and_feature_list(features_list, feature):
    """Split token and feature from a list of features."""
    return [split_feature(feat, feature) for feat in features_list]


def convert_conll_to_ssf(conll_lines):
    """Convert conll to ssf format for a conll sentence."""
    sent_count = 1
    cntr = 1
    subcntr = 1
    sent_string = ''
    prev_tag = ''
    prev_sent_count = 0
    for line in conll_lines:
        features = line.split('\t')
        chnk_info = features[2].split('-')
        if search('B-', features[2]) is not None:
            subcntr = 1
            if prev_sent_count != sent_count:
                sent_string += str(cntr) + '\t((\t' + chnk_info[1] + '\t\n'
                prev_sent_count = sent_count
            else:
                cntr += 1
                sent_string += '\t))\n' + str(cntr) + '\t((\t' + chnk_info[1] + '\t\n'
            sent_string += str(cntr) + '.' + str(subcntr) + '\t' + features[0] + '\t' + features[1] + '\t' + features[3] + '\n'
            subcntr += 1
            prev_tag = chnk_info[1]
        elif prev_tag and search('I-' + prev_tag, features[2]) is not None:
            sent_string += str(cntr) + '.' + str(subcntr) + '\t' + features[0] + '\t' + features[1] + '\t' + features[3] + '\n'
            subcntr += 1
            prev_tag = chnk_info[1]
        if prev_tag and prev_tag != chnk_info[1] and chnk_info[0] == 'I':
            subcntr = 1
            cntr += 1
            sent_string += '\t))\n' + str(cntr) + '\t((\t' + chnk_info[1] + '\t\n'
            if len(features) == 4:
                sent_string += str(cntr) + '.' + str(subcntr) + '\t' + features[0] + '\t' + features[1] + '\t' + features[3] + '\n'
            else:
                sent_string += str(cntr) + '.' + str(subcntr) + '\t' + features[0] + '\t' + features[1] + '\n'
            subcntr += 1
            prev_tag = chnk_info[1]
        if not prev_tag and chnk_info[0] == 'I':
            sent_string += str(cntr) + '\t((\t' + chnk_info[1] + '\t\n'
            if len(features) == 4:
                sent_string += str(cntr) + '.' + str(subcntr) + '\t' + features[0] + '\t' + features[1] + '\t' + features[3] + '\n'
            else:
                sent_string += str(cntr) + '.' + str(subcntr) + '\t' + features[0] + '\t' + features[1] + '\n'
            prev_sent_count = sent_count
            prev_tag = chnk_info[1]
            subcntr += 1
    sent_string += "\t))\n</Sentence>"
    return sent_string


def extract_info_from_list_of_dicts_and_convert_to_ssf(dict_features, sent_index, utf2wx_dict={}):
    """Extract info from a list of dicts and convert to ssf."""
    ssf_sentence = "<Sentence id='" + str(sent_index + 1) + "'>\n"
    token_pos = dict_features['pos']
    token_list_pos, pos_list = zip(*split_token_and_feature_list(token_pos, 'pos'))
    token_chunk = dict_features['chunk']
    token_list_chunk, chunk_list = zip(*split_token_and_feature_list(token_chunk, 'chunk'))
    token_root = dict_features['root']
    token_list_root, root_list = zip(*split_token_and_feature_list(token_root, 'root'))
    token_morph_pos = dict_features['hi_morph_pos']
    token_list_morph_pos, morph_pos_list = zip(*split_token_and_feature_list(token_morph_pos, 'morph_pos'))
    token_morph_gender = dict_features['hi_morph_gender']
    token_list_morph_gender, morph_gender_list = zip(*split_token_and_feature_list(token_morph_gender, 'morph_gender'))
    token_morph_number = dict_features['hi_morph_number']
    token_list_morph_number, morph_number_list = zip(*split_token_and_feature_list(token_morph_number, 'morph_number'))
    token_morph_person = dict_features['hi_morph_person']
    token_list_morph_person, morph_person_list = zip(*split_token_and_feature_list(token_morph_person, 'morph_person'))
    token_morph_case = dict_features['hi_morph_case']
    token_list_morph_case, morph_case_list = zip(*split_token_and_feature_list(token_morph_case, 'morph_case'))
    token_morph_vib = dict_features['hi_morph_vib']
    token_list_morph_vib, morph_vib_list = zip(*split_token_and_feature_list(token_morph_vib, 'morph_vib'))
    assert token_list_pos == token_list_chunk == token_list_root == token_list_morph_pos == token_list_morph_gender == token_list_morph_number == token_list_morph_person == token_list_morph_case == token_list_morph_vib
    token_list_with_all_features = []
    for index, token in enumerate(token_list_root):
        if token == ',':
            root = 'COMMA'
        elif token == '/':
            root = 'BACKSLASH'
        else:
            root = root_list[index]
        pos = pos_list[index]
        chunk = chunk_list[index]
        morph_pos = morph_pos_list[index]
        morph_gender = morph_gender_list[index]
        morph_number = morph_number_list[index]
        morph_person = morph_person_list[index]
        morph_case = morph_case_list[index]
        morph_vib = morph_vib_list[index]
        if morph_vib not in utf2wx_dict:
            morph_suff = conv.convert(morph_vib)
        else:
            morph_suff = utf2wx_dict[morph_vib]
        all_morph = ','.join([root, morph_pos, morph_gender, morph_number, morph_person, morph_case, morph_vib, morph_suff])
        token_all_features = '\t'.join([token, pos, chunk, "<fs af='" + all_morph + "'>"])
        token_list_with_all_features.append(token_all_features)
    ssf_sentence += convert_conll_to_ssf(token_list_with_all_features)
    return ssf_sentence, utf2wx_dict


def main():
    """Pass arguments and call functions here."""
    parser = ArgumentParser()
    parser.add_argument('--input', dest='inp', help='Enter the input file path')
    parser.add_argument('--output', dest='out', help='Enter the output file path')
    args = parser.parse_args()
    if not os.path.isdir(args.inp):
        input_lines = read_lines_from_file(args.inp)
        utf2wx_dict = {}
        ssf_sentences = []
        for index, line in enumerate(input_lines):
            resp = send_request_and_get_response(line)
            ssf_sentence, utf2wx_dict = extract_info_from_list_of_dicts_and_convert_to_ssf(resp[0], index, utf2wx_dict)
            ssf_sentences.append(ssf_sentence)
            ssf_sentence = ''
            ssf_sentences.append(ssf_sentence)
        write_lines_to_file(ssf_sentences, args.out)
    else:
        if not os.path.isdir(args.out):
            os.makedirs(args.out)
        output_folder = args.out
        utf2wx_dict = {}
        for root, dirs, files in os.walk(args.inp):
            for fl in files:
                input_path = os.path.join(root, fl)
                print(fl)
                output_file_name = fl[: fl.find('.')]
                input_lines = read_lines_from_file(input_path)
                ssf_sentences = []
                for index, line in enumerate(input_lines):
                    resp = send_request_and_get_response(line)
                    ssf_sentence, utf2wx_dict = extract_info_from_list_of_dicts_and_convert_to_ssf(resp[0], index, utf2wx_dict)
                    ssf_sentences.append(ssf_sentence)
                    ssf_sentence = ''
                    ssf_sentences.append(ssf_sentence)
                output_path = os.path.join(output_folder, output_file_name + '-pos-chunk-mor.txt')
                write_lines_to_file(ssf_sentences, output_path)
                print('Done processing for file:', fl)


if __name__ == '__main__':
    main()
