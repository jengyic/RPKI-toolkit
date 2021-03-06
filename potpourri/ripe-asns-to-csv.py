# $Id: ripe-asns-to-csv.py 5624 2014-01-09 20:56:06Z sra $
# 
# Copyright (C) 2009-2012  Internet Systems Consortium ("ISC")
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

"""
Parse a WHOIS research dump and write out (just) the RPKI-relevant
fields in myrpki-format CSV syntax.

NB: The input data for this script is publicly available via FTP, but
you'll have to fetch the data from RIPE yourself, and be sure to see
the terms and conditions referenced by the data file header comments.
"""

import gzip
from rpki.csv_utils import csv_writer

class Handle(dict):

  want_tags = ()

  debug = False

  def set(self, tag, val):
    if tag in self.want_tags:
      self[tag] = "".join(val.split(" "))

  def check(self):
    for tag in self.want_tags:
      if not tag in self:
        return False
    if self.debug:
      self.log()
    return True

  def __repr__(self):
    return "<%s %s>" % (self.__class__.__name__,
                        " ".join("%s:%s" % (tag, self.get(tag, "?"))
                                 for tag in self.want_tags))

  def log(self):
    print repr(self)

  def finish(self, ctx):
    self.check()

class aut_num(Handle):
  want_tags = ("aut-num", "mnt-by", "as-name")

  def set(self, tag, val):
    if tag == "aut-num" and val.startswith("AS"):
      val = val[2:]
    Handle.set(self, tag, val)

  def finish(self, ctx):
    if self.check():
      ctx.asns.writerow((self["mnt-by"], self["aut-num"]))

class main(object):

  types = dict((x.want_tags[0], x) for x in (aut_num,))


  def finish_statement(self, done):
    if self.statement:
      tag, sep, val = self.statement.partition(":")
      assert sep, "Couldn't find separator in %r" % self.statement
      tag = tag.strip().lower()
      val = val.strip().upper()
      if self.cur is None:
        self.cur = self.types[tag]() if tag in self.types else False
      if self.cur is not False:
        self.cur.set(tag, val)
    if done and self.cur:
      self.cur.finish(self)
      self.cur = None

  filenames = ("ripe.db.aut-num.gz",)

  def __init__(self):
    self.asns = csv_writer("asns.csv")
    for fn in self.filenames:
      f = gzip.open(fn)
      self.statement = ""
      self.cur = None
      for line in f:
        line = line.expandtabs().partition("#")[0].rstrip("\n")
        if line and not line[0].isalpha():
          self.statement += line[1:] if line[0] == "+" else line
        else:
          self.finish_statement(not line)
          self.statement = line
      self.finish_statement(True)
      f.close()
    self.asns.close()

main()
