#!/bin/bash
echo "Please ensure that you run this fuzzing script on a tmpfs/ramdisk, as the high-speed and repeated writes may damage your hard disk or SSD."
while true; do
    radamsa rawlogs/radamsa-sample.log > rawlogs/raw-access.log-input
    output=$(python3 /home/bloomfilter/bloomfilter/web-server-log-anonymizer.py 2>&1)
    if [[ $(echo "$output" | tail -n 1) != "Saving..." ]]; then
        #Write crash log to file:
        printf "**Found crash at `date`.**\n\nError output:\n" >> fuzz-output.log
        echo "$output" >> fuzz-output.log
        printf "\nFuzzed input:\n" >> fuzz-output.log
        cat rawlogs/raw-access.log-input >> fuzz-output.log
        printf "\n\n" >> rawlogs/fuzz-output.log >> fuzz-output.log
        #Write summary to stdout:
        printf "**Found crash at `date`. Last 10 lines of output:**\n\n"
        echo "$output" | tail -n 10
        printf "\n\n"
    fi
    rm outputlogs/access.log
done
