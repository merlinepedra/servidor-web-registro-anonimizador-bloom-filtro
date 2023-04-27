#This file only contains configuration variables and is not designed to be run directly. Edit the file to make changes.

#File path of the input web server log
file_input_log_path = "/home/bloomfilter/rawlogs/raw-access.log-input"

#File path of the desired output file
file_output_log_path = "/home/bloomfilter/outputlogs/access.log"

#File path where you want the bloom filter to be saved
file_filter_path = "/home/bloomfilter/config/filter.bloom"

#A list of bot/crawler/spider user agent excerpts - this file is included in the repository
file_bots_path = "/home/bloomfilter/bloomfilter/bot-user-agents.txt"

#A list of user agent excerpts associated with different browsers - this file is included in the repository
file_browsers_path = "/home/bloomfilter/bloomfilter/browser-user-agents.txt"

#The current counter IP address
file_counter_ip_path = "/home/bloomfilter/config/counter-ip-address.txt"

#Size of the bloom filter in bits
size = 1048575

#sha512, sha256, sha1 or md5
hash_algo = "sha256"

#Split the hash into segments of x characters
hash_chars = 5

#Use x segments of the hash to query the bloom filter
hash_count = 1

#For random 1 in x valid log entries processed, set a random bit to 0
decay_rate = 5000

#Web server log format - the default value is the Combined Log Format
log_format = "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User_Agent}i\""

#The default IP address to use when a non-unique IP address is found
default_log_ip = "192.0.2.1"
