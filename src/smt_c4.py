#!/usr/bin/env python
"""

Python implementation of the ETC C4 Asset Id. https://github.com/etcenter/C4

Sundog Media Toolkit 20th September 2015

"""

import os
import sys
import getopt

import hashlib
import base64
import base58



#Helpers
def draw_progress_bar(percent, barLen = 50):
    """
    Simple command line progress bar
    """
    sys.stdout.write("\r")
    progress = ""
    for i in range(barLen):
        if i < int(barLen * percent / 100):
            progress += "="
        else:
            progress += " "
    sys.stdout.write("[ %s ] %.2f%%" % (progress, percent))
    sys.stdout.flush()


def calculate_hash_512(filepath, verbose):
    """
    SHA512 Hash Digest
    """

    if verbose:
        print 'Calculating hash...'

    sha512_hash = hashlib.sha512()

    with open(filepath, 'rb') as f:
        statinfo = os.stat(filepath)
        block_size = 100 * (2**20)  #Magic number: 100 * 1MB blocks
        nb_blocks = (statinfo.st_size / block_size) + 1
        cnt_blocks = 0
        
        while True:
            block = f.read(block_size) 
            if not block: break
            sha512_hash.update(block)
            cnt_blocks = cnt_blocks + 1
            progress = 100 * cnt_blocks / nb_blocks
            if verbose:
                draw_progress_bar(progress)

        f.close()

    return sha512_hash.digest()


def b58encode(bytes):
    """
    Base58 Encode bytes to string
    """
    __b58chars = '123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
    __b58base = len(__b58chars)

    long_value = int(bytes.encode("hex_codec"), 16)

    result = ''
    while long_value >= __b58base:
        div, mod = divmod(long_value, __b58base)
        result = __b58chars[mod] + result
        long_value = div

    result = __b58chars[long_value] + result

    return result


def _as_hex_str(bytes, deliminator):
    """
    Pretty-prints bytes as hex values separated by a deliminator
    """
    return deliminator.join(map(lambda x: '%02x' % ord(x), bytes))
 



#Lets go ##################################################
def main(argv):


    cmd_usage = "smt_c4.py -v <verbose> -i <input-file> -f <format>\n \t Supportted formats: [ c4 (default), base10, base64 (URL safe), base64old, hex, HEX, h:e:x ]\n"

    #Defaults
    id_format = 'c4'
    verbose = False

    if len(sys.argv) == 1: 
        print cmd_usage
        sys.exit(2)

    try:
        opts, args = getopt.getopt(argv,"hi:f:v",["input-file=", "format=", "verbose"])

    except getopt.GetoptError:
        print cmd_usage
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print cmd_usage
            sys.exit()
        elif opt in ("-i", "--input-file"):
            input_filepath = arg
        elif opt in ("-f", "--format"):
            id_format = arg
        elif opt in ("-v", "--verbose"):
            verbose = True



    #Print Out Args
    if verbose:
        print 'Input File:\t', input_filepath
        print 'Id Format:\t', id_format
        print

    c4_id_length = 90

    #Calculate SHA512 Hash
    hash_sha512 = calculate_hash_512(input_filepath, verbose)

    #Encode hash to required format
    if id_format == 'base10':

        #Base10
        string_id = int(hash_sha512.encode("hex_codec"), 16)

    elif id_format == 'base64old':

        #Base64
        string_id = base64.b64encode(hash_sha512)

    elif id_format == 'base64':

        #URL Safe Base64
        string_id = base64.urlsafe_b64encode(hash_sha512)

    elif id_format == 'hex':

        #lower case hex formatting
        string_id = _as_hex_str(hash_sha512, '')

    elif id_format == 'HEX':

        #upper case hex formatting
        string_id = _as_hex_str(hash_sha512, '').upper()

    elif id_format == 'h:e:x':

        #lowercase hex formatting, with ':' delimination
        string_id = _as_hex_str(hash_sha512, ':')

    elif id_format == 'c4':

        # Base58 - Standard Python Base58 does not work.
        # Charset in standard library appears to be a different order:
        # __b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

        #b58_hash = base58.b58encode(hash_sha512)
        #print b58_hash

        #Alternative Base58
        b58_hash = b58encode(hash_sha512)

        #Pad with '1's if needed
        padding = ''
        if len(b58_hash) < (c4_id_length - 2):
            padding = ('1' * (c4_id_length - 2 - len(b58_hash)))

        #Combine to form C4 ID
        string_id = 'c4' + padding + b58_hash

    else:

        print 'Unrecognised format option'
        print cmd_usage
        sys.exit()


    if verbose:
        print
        print 'Calculated C4 Asset Id:'

    #Write out the formatted Id
    print string_id.strip('\n')



if __name__ == "__main__":
    main(sys.argv[1:])

