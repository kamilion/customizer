#!/bin/bash

exec</etc/mtab
while read line; do
	`echo $line | grep FileSystem | awk '{print $2}' | sed 's/040/ /g'`
done