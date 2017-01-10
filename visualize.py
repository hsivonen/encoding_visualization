#!/usr/bin/python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json

indexes = json.load(open("../encoding/indexes.json", "r"))

names_lengths_langs = [
    ("ibm866", 16, "ru"),
    ("iso-8859-2", 16, "pl"),
    ("iso-8859-3", 16, "tr"),
    ("iso-8859-4", 16, "et"),
    ("iso-8859-5", 16, "ru"),
    ("iso-8859-6", 16, "ar"),
    ("iso-8859-7", 16, "el"),
    ("iso-8859-8", 16, "he"),
    ("iso-8859-10", 16, "no"),
    ("iso-8859-13", 16, "et"),
    ("iso-8859-14", 16, "ga"),
    ("iso-8859-15", 16, "de"),
    ("iso-8859-16", 16, "pl"),
    ("koi8-r", 16, "ru"),
    ("koi8-u", 16, "uk"),
    ("macintosh", 16, "de"),
    ("windows-874", 16, "th"),
    ("windows-1250", 16, "pl"),
    ("windows-1251", 16, "ru"),
    ("windows-1252", 16, "de"),
    ("windows-1253", 16, "el"),
    ("windows-1254", 16, "tr"),
    ("windows-1255", 16, "he"),
    ("windows-1256", 16, "ar"),
    ("windows-1257", 16, "et"),
    ("windows-1258", 16, "vi"),
    ("x-mac-cyrillic", 16, "ru"),
    ("jis0208", 94, "ja"),
    ("jis0212", 94, "ja"),
    ("euc-kr", 190, "ko"),
    ("gb18030", 190, "zh-cn"),
    ("big5", 157, "zh-tw"),
]

def classify(code_point):
    if code_point < 0x80:
        raise Error()
    if code_point < 0x800:
        return "mid"
    if code_point > 0xFFFF:
        return "astral"
    if code_point >= 0xE000 and code_point <= 0xF8FF:
        return "pua"
    return "upper"

def check_duplicate(code_point, pointer, index):
    # Slow but the script doesn't need to be run often
    # Don't post to http://accidentallyquadratic.tumblr.com/
    if code_point in index[:pointer]:
        return " duplicate"
    return ""

def check_duplicate_coverage(code_point, pointer, index):
    if code_point in index[pointer+1:]:
        return " duplicate"
    return ""

def check_compatibility(code_point):
    if code_point >= 0xF900 and code_point <= 0xFAFF:
        return " compatibility"
    if code_point >= 0x3400 and code_point <= 0x4DB5:
        return " ext"
    return ""

def format_index(name, row_length, lang):
    out_file = open("%s.html" % name, "w")
    out_file.write(("<!DOCTYPE html><html lang=%s><meta charset=utf-8><title>%s</title><link rel=stylesheet href=visualization.css type=text/css><h1>%s</h1><table><thead><tr><td><td>") % (lang, name, name));
    for i in range(0, row_length):
        out_file.write("<th>%02d" % i)
    out_file.write("<tr><td><td>");
    for i in range(0, row_length):
        out_file.write("<th>%02X" % i)
    out_file.write("<tbody>");
    previous = None
    new_row = True
    pointer = 0
    row_num = 0
    index = indexes[name]
    for code_point in index:
        if new_row:
            out_file.write("<tr><th>%02d<th>%02X" % (row_num, row_num))
            new_row = False
        if not code_point:
            out_file.write((u"<td class=unmapped title='%d = 0x%X'>\uFFFD" % (pointer, pointer)).encode("utf-8"))
        else:
            out_file.write((u"<td class='%s %s%s%s' title='U+%04X, %d = 0x%X'>%s" % ("contiguous" if previous and previous + 1 == code_point else "discontiguous", classify(code_point), check_duplicate(code_point, pointer, index), check_compatibility(code_point), code_point, pointer, pointer, unichr(code_point))).encode("utf-8"))
        previous = code_point
        pointer += 1
        if pointer % row_length == 0:
            new_row = True
            row_num += 1
    out_file.write("</table><p><a href='%s-bmp.html'>BMP coverage</a><p><a href='./' rel=contents>Back to the table of contents</a>" % name)
    out_file.close()

def format_coverage(name, lang):
    out_file = open("%s-bmp.html" % name, "w")
    out_file.write(("<!DOCTYPE html><html lang=%s><meta charset=utf-8><title>BMP coverage of %s</title><link rel=stylesheet href=visualization.css type=text/css><h1>BMP coverage of %s</h1><table><thead><tr><td><td>") % (lang, name, name));
    for i in range(0, 256):
        out_file.write("<th>%02d" % i)
    out_file.write("<tr><td><td>");
    for i in range(0, 256):
        out_file.write("<th>%02X" % i)
    out_file.write("<tbody>");
    previous = None
    new_row = True
    row_num = -1
    index = indexes[name]
    for code_point in range(0, 0x10000):
        if code_point % 256 == 0:
            new_row = True
            row_num += 1
        pointer = None
        try:
            pointer = index.index(code_point)
        except ValueError:
            pass
        if new_row:
            out_file.write("<tr><th>%02d<th>%02X" % (row_num, row_num))
            new_row = False
        if code_point >= 0xD800 and code_point <= 0xDFFF:
            out_file.write("<td class=surrogate>")
        elif not code_point in index:
            out_file.write((u"<td class=unmapped title=U+%04X>\uFFFD" % code_point).encode("utf-8"))
        else:
            out_file.write((u"<td class='%s %s%s%s' title='U+%04X, %d = 0x%X'>%s" % ("contiguous" if previous and previous + 1 == pointer else "discontiguous", classify(code_point), check_duplicate_coverage(code_point, pointer, index), check_compatibility(code_point), code_point, pointer, pointer, unichr(code_point))).encode("utf-8"))
        previous = pointer
    out_file.write("</table><p><a href='%s.html'>Index</a><p><a href='./' rel=contents>Back to the table of contents</a>" % name)
    out_file.close()

index_file = open("index.html", "w")
index_file.write("""<!DOCTYPE html><html lang=en><meta charset=utf-8><title>Encoding Visualizations</title><link rel=stylesheet href=visualization.css type=text/css>
    <h1>Encoding Visualizations</h1>
    <p>This is a visualization of the indices specified in the <a href='https://encoding.spec.whatwg.org/'>Encoding Standard</a>.
    <h2>Legend</h2>
    <ul>
    <li>The <code>title</code> attribute of each cell gives the code point, the pointer is decimal and the pointer in hex.
    <li class=unmapped>Unmapped
    <li class=mid>Two bytes in UTF-8
    <li class="mid contiguous">Two bytes in UTF-8, code point follows immediately the code point of previous pointer
    <li class=upper>Three bytes in UTF-8 (non-PUA)
    <li class="upper contiguous">Three bytes in UTF-8 (non-PUA), code point follows immediately the code point of previous pointer
    <li class=pua>Private Use
    <li class="pua contiguous">Private Use, code point follows immediately the code point of previous pointer
    <li class=astral>Four bytes in UTF-8
    <li class="astral contiguous">Four bytes in UTF-8, code point follows immediately the code point of previous pointer
    <li class=duplicate>Duplicate code point already mapped at an earlier index
    <li class=compatibility>CJK Compatibility Ideograph
    <li class=ext>CJK Unified Ideographs Extension A
    </ul>
    <h2>The Indices</h2>
    <ul>""");
for (name, row_length, lang) in names_lengths_langs:
    format_index(name, row_length, lang)
    format_coverage(name, lang)
    index_file.write("<li><a href=%s.html>%s</a> (<a href=%s-bmp.html>BMP coverage</a>)" % (name, name, name))
index_file.write('''</ul>
<h2>Source Code</h2>
<ul>
<li><a href=visualize.py>Script for generating these HTML files</a>
<li><a href="https://github.com/hsivonen/encoding_visualization">GitHub repo</a>
</ul>
<hr>
<p><a href=/>Main page</a>''');
