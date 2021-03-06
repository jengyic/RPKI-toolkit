#!/bin/sh -
# $Id: strip_roa.sh 5757 2014-04-05 22:42:12Z sra $
#
# Copyright (C) 2010  Internet Systems Consortium ("ISC")
# 
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND ISC DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS.  IN NO EVENT SHALL ISC BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
# OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#
# Strip boring parts of print_roa's output to make a (somewhat) terser
# description, one line per ROA.  This is intended for use in
# comparing sets of ROAs using text comparision tools like "diff" or
# "comm".  One could definitely do something prettier, but this
# suffices for basic tests.
#
# Use this as in a shell pipeline to postprocess print_roa's output.

awk '
  /Certificate/ {
    roa[++n] = "";
  }
  /asID|addressFamily|IPaddress/ {
    roa[n] = roa[n] " " $0;
  }
  END {
    for (i in roa)
      print roa[i];
  }
' |
tr -s \\011 \\040 |
sort -u
