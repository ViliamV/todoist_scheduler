#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta


def parse(s, num_pos=0, text_pos=1):
    if not bool(s):
        return None
    line = s.strip().split(" ")
    number = int(line[num_pos])
    text = line[text_pos][0]
    if text in "Dd":
        return relativedelta(days=number)
    elif text in "Ww":
        return relativedelta(weeks=number)
    elif text in "Mm":
        if len(line) > 2:
            # last day of month
            return relativedelta(months=number, days=-1)
        else:
            return relativedelta(months=number)
    elif text in "Yy":
        return relativedelta(years=number)
    elif text in "Ll":
        return relativedelta(months=number, days=-1)
