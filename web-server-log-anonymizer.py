from bitstring import BitArray
from hashlib import sha512, sha256, sha1, md5
from random import randint
from urllib.parse import urlparse
from datetime import datetime, timedelta
from ipaddress import ip_address
import time, re, random, os.path, apache_log_parser

#Import config file
from config import *

#Create log parser
entry_parse = apache_log_parser.make_parser(log_format)

#Open user agent lists
with open(file_bots_path, 'r') as file_bots:
    bots = file_bots.read().splitlines()
with open(file_browsers_path, 'r') as file_browsers:
    browsers = file_browsers.read().splitlines()

#Read IP address counter, or create if required
if(os.path.isfile(file_counter_ip_path)):
    with open(file_counter_ip_path, 'r') as file_counter_ip:
        counter_ip = file_counter_ip.read().rstrip()
        print("Current counter IP: " + counter_ip)
else:
    with open(file_counter_ip_path, 'w') as file_counter_ip:
        counter_ip = "2001:db8::"
        file_counter_ip.write(counter_ip)
        print("Created new counter IP file...")

def bf_create(size):
    global bf
    bf = BitArray(size)

def bf_query(ip, hash_algo, hash_chars, hash_count):
    hash = re.findall('.' * hash_chars, get_hash(ip, hash_algo))[:hash_count]
    global bits
    bits = [int(segment,16) for segment in hash]
    if(bf_read(bits)):
        return("found")
    else:
        return("not found")

def bf_read(bits):
    for bit in bits:
        if(bf[bit] == 0):
            return(0)
    return(1)

def bf_write(bits, value):
    for bit in bits:
        bf.set(value, bit)
    return

def bf_save():
    print("Saving...")
    with open(file_filter_path, 'wb') as bf_file:
        bf.tofile(bf_file)
    with open(file_counter_ip_path, 'w') as file_counter_ip:
        global counter_ip
        file_counter_ip.write(str(counter_ip))

def bf_load():
    with open(file_filter_path, 'rb') as bf_file:
        global bf
        bf = BitArray(filename=file_filter_path)

def bf_decay():
    print("Decaying filter...")
    bf.set(0, randint(0, size - 1))

def get_hash(ip, hash_algo):
    if(hash_algo == "sha512"):
        hash = sha512(ip).hexdigest()
    elif(hash_algo == "sha256"):
        hash = sha256(ip).hexdigest()
    elif(hash_algo == "sha1"):
        hash = sha1(ip).hexdigest()
    elif(hash_algo == "md5"):
        hash = md5(ip).hexdigest()
    return(hash)

def log_readline():
    while(1):
        raw_entry = log.readline()
        if(raw_entry):
            return(raw_entry)
        else:
            print("Reached end of log file. Writing output, saving and quitting...")
            output_write()
            bf_save()
            log.close()
            quit()

def log_process(raw_entry):
    global entry
    try:
        entry = entry_parse(raw_entry)
        if not(entry['request_header_referer'] == "-"):
            referrer = urlparse(entry['request_header_referer'])
            entry['request_header_referer'] = referrer.scheme + "://" + referrer.netloc + "/"
        entry['request_header_user_agent'] = ua_process(entry['request_header_user_agent'])
        return(1)
    except:
        return(0)

def ua_process(ua):
    if(ua == "-"):
        return("-")
    for bot in bots:
        if(bot in ua):
            return(bot)
    for browser in browsers:
        if(browser in ua):
            return(browser)
    return("Other")

def output_genline(counter_ip):
    try:
        output_line = str(counter_ip) + " - - " + str(entry['time_received']) + " \"" + str(entry['request_method']) + " " + str(entry['request_url_path']) + " HTTP/" + str(entry['request_http_ver']) + "\" " + str(entry['status']) + " " + str(entry['response_bytes_clf']) + " \"" + str(entry['request_header_referer']) + "\" \"" + str(entry['request_header_user_agent']) + "\""
        output.append(output_line)
        print(output_line)
    except:
        print("Log entry invalid (missing or invalid elements), skipping...")

def output_write():
    with open(file_output_log_path, 'a') as file_output_log:
        file_output_log.write("\n".join(output))

#Load existing or create new bloom filter in memory
if(os.path.isfile(file_filter_path)):
    print("Loading existing filter...")
    bf_load()
else:
    print("Creating new filter...")
    bf_create(size)

#Open log file
try:
    log = open(file_input_log_path, 'r', errors = 'backslashreplace')
except:
    print("Cannot read log file " + file_input_log_path)
    quit()

#Create list to store output
output = []

#Process log entries
while(1):
    time.sleep(0.01)
    if(log_process(log_readline())):
        print("Log entry valid, ", end='')
    else:
        print("Log entry invalid, skipping...")
        continue

    if(bf_query(entry['remote_host'].encode('utf-8'), hash_algo, hash_chars, hash_count) == "found"):
        #IP already found, log accordingly
        print("IP already exists, logging as " + default_log_ip)
        output_genline(default_log_ip)
    else:
        #New IP, record in bloom filter, then log
        print("new IP found, logging as " + str(counter_ip))
        bf_write(bits, 1)
        output_genline(counter_ip)
        counter_ip = ip_address(counter_ip) + 1
    if(decay_rate != 0) and (randint(1, decay_rate) == 1):
        bf_decay()
