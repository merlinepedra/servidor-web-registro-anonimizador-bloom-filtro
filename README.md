# Web Server Log Anonymizer Bloom Filter

A Python 3 program to anonymize web server access logs while retaining an accurate count of unique visitor IP addresses.

For example, anonymizing the following log entry:

`127.0.0.1 - - [16/Dec/2018:16:07:23 +0000] "GET /pages/page1.html?query=string&query2=string2 HTTP/1.1" 200 11576 "https://www.example.com/path/file.html?query=string&query2=string2#fragment1" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"`

...will result in:

`2001:db8::1 - - [16/Dec/2018:16:07:23 +0000] "GET /pages/page1.html HTTP/1.1" 200 11576 "https://www.example.com/" "Chromium"`

Python dependencies: `bitstring`, `apache-log-parser`

    pip3 install bitstring apache-log-parser

## What is this for?

This program allows you to remove confidential user data from web server access logs. In the current version, IP addresses, user agents and referrers are anonymized.

The anonymized logs can then be used to monitor website traffic, performance, security, etc or be fed into another tool such as AWStats.

## How does it work?

A bloom filter is used to determine whether a particular IP address has been seen before, or whether it is a new visitor:

* If the IP *has* been seen before, it is replaced with a generic non-routable IP address.

* If the IP *hasn't* been seen before, it is replaced with a generic non-routable IP address from a counter. Each time a new IP address is found, the counter is incremented - i.e. '1' is literally added to the IP address. In other words, `2001:db8::1` would become `2001:db8::2`.

By default the counter starts at `2001:db8::`, and is incremented each time a new IP is found. After the first increment, it will be `2001:db8::1`, then `2001:db8::2`, and so on...

### IPv6 Counter Address

The reason that `2001:db8::` is used is that the entire `2001:db8::/32` address range is specifically reserved for use in documentation, as defined in [RFC3849](https://tools.ietf.org/html/rfc3849).

I had originally added error handling to allow the counter IP to loop/restart should all of the addresses be consumed. However, since an IPv6 `/32` has over 79 octillion unique addresses (79 followed by 27 zeros), adding the error handling code seemed unnecessary, as this error state will never trigger in normal usage of the program.

To put this into perspective - even if your website has 1 billion unique visitors per second, it would still take over 2.5 trillion years to exhaust the IPv6 counter IP range.

## How anonymous is the data?

### IP Addresses:

All IP addresses are replaced with generic non-routable addresses that can not be programatically reversed. In other words, they are not hashed, obfuscated, etc.

#### There are only a few billion IPv4 addresses, couldn't you just brute-force the bloom filter?

The bloom filter configuration can be controlled so that it relies on [*k*-anonymity](https://en.wikipedia.org/wiki/K-anonymity) to protect IP addresses.

The default configuration uses a 128 KiB (1,048,575 bits) bloom filter, with a single 5 character segment of a SHA-256 hash used as the input.

The maximum base 10 value of 5 hex characters (fffff) is 1,048,575 - which is the same size as the bloom filter. There is exactly 1 unique bit for every possible combination of 5 hex characters.

There are a total of 3,706,452,992 (3.7 billion) possible publicly routable IPv4 addresses. If you divide this number by the size of the bloom filter (3706452992 / 1048575), you get ~3534.75. This means that on average, each bit of the bloom filter could represent 3534.75 possible unique IPv4 addresses. When talking *k*-anonymity, this is ~3535-anonymity.

### User Agents:

All user agents are replaced with one from an approved list by regex matching each entry from the approved list against the user agent from the log until a match is found. If no match is found, 'Other' is used. Please see `browser-user-agents.txt`.

### Referrers:

Referrer URLs are stripped down to the scheme (e.g. `https`) and the Fully Qualified Domain Name (e.g. `www.example.com`).

For example, `https://www.example.com/path/index.html?query1=string&query2=otherstring#fragment1` would become `https://www.example.com/`.

### HTTP Basic Authentication and Ident User IDs

User IDs provided by HTTP Basic Authentication or Ident ([RFC1413](https://tools.ietf.org/html/rfc1413)) are completely removed. These are not widely used on the internet in 2018 anyway.

## How do I use it?

Ensure that the required Python 3 dependencies are installed:

    pip3 install bitstring apache-log-parser

After cloning the repository, edit the file `config.py` and set your desired configuration values.

Then you can run the program with `python3 web-server-log-anonymizer.py`. Debug information will be outputted to stdout, and the anonymized log file will be written to the path that you specified in `config.py`.

### Use on a Live Web Server

If you wish to anonymize logs continuously from a live web server (e.g. Apache), you can set up a cronjob similar to the following:

    0 * * * * mv /var/log/apache2/access.log /path/to/input/log/file && service apache2 reload

Note that with Apache, reloading the service after moving the log file is required for another log file to be created straight away.

Then, **using a separate, non-privileged user**, add a second cronjob:

    0 * * * * sleep 10 && python3 web-server-log-anonymizer.py

For further security, you can automatically transfer the logs to a separate, dedicated logging device and process them there.

## Fuzzing

I've included a basic fuzzing test harness at `radamsa-fuzzing-test-harness.sh`. It's uses [Radamsa](https://gitlab.com/akihe/radamsa) as the fuzzing engine, but you should be able to swap in a different tool if you wish. You'll also most likely have to adjust the file paths a bit to get it working on your system, but other than that it should work as-is. You must provide some sample log entries to be fuzzed in `rawlogs/radamsa-sample.log`, or whichever path you choose.

Please ensure that you run this fuzzing script on a tmpfs/ramdisk, as the high-speed and repeated writes may damage your hard disk or SSD. The below command will create a 128 MB tmpfs for you to use:

    sudo mount -t tmpfs -o size=128m tmpfs /path/to/desired/mount/directory

Then make sure that all of the files the script needs to read and write are on the tmpfs.

I've run this fuzzing script for around 12 hours so far. It found a couple of crashes within 10 minutes, which I've now fixed, but other than that nothing has been found. Please feel free to perform more of your own testing and let me know if you find anything.

## Hacking

This tool is in-scope of my [HackerOne program](https://hackerone.com/jamieweb)!

If you'd like to look for vulnerabilities or crashes, please read-up on the program details and rules. All valid vulnerability submissions will be thanked publicly!
