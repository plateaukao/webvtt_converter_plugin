import webvtt
import sys
import argparse
import re
from os import listdir
from os.path import isfile, join

def write(file, str):
    file.write(str + "\n")

def rreplace(s, old, new):
  li = s.rsplit(old, 1)
  return new.join(li)

def convert_file(file_name, main_lang, sub_lang, output_file):
  file_name_sub = rreplace(file_name, main_lang, sub_lang)
  vtt_main = webvtt.read(file_name)
  vtt_sub = webvtt.read(file_name_sub)

  # while loop all korean time captions
  index_main = 0
  index_sub = 0
  while index_main < len(vtt_main):
    while index_sub < len(vtt_sub):
      caption_main = vtt_main[index_main]
      caption_sub = vtt_sub[index_sub]

      if (caption_main.start <= caption_sub.start):
        write(output_file, "<h3>" + caption_main.text.replace("&lrm;","") + "</h3>")
        break
      else:
        write(output_file, "<p>" + caption_sub.text.replace("&lrm;", ""))
        write(output_file, "<p>")
        index_sub += 1
    index_main += 1

  # finish final z index
  while index_sub < len(vtt_sub):
    write(output_file, caption_sub.text)
    index_sub += 1

# main

def get_lang_list(vtt_dir):
  files = [f for f in listdir(vtt_dir) if isfile(join(vtt_dir, f))]
  vtt_files_name = [f for f in files if re.match('.*\.vtt$', f)]
  langs = map(lambda name: re.search('.*\.(.+?)\.vtt', name).group(1) ,vtt_files_name)
  langs = list(set(langs)) # uniq
  langs.sort()
  return langs

def convert_webvtt_to_html(vtt_dir, main_lang, sub_lang, output_file):
  files = [f for f in listdir(vtt_dir) if isfile(join(vtt_dir, f))]
  vtt_files_name = [f for f in files if re.match('.*\.vtt$', f)]
  cc_vtt_files_name = [f for f in files if re.match('.*\[cc\]\.vtt$', f)]
  cc_vtt_files_name.sort()

  file = open(output_file, 'w')
  
  write(file, "<html>")
  for idx, vtt_file_name in enumerate(cc_vtt_files_name):
    vtt_file = join(args.dir, vtt_file_name)
    write(file, '<title>Episode' + str(idx + 1) + '</title>')
    write(file, '<p>======================')
    write(file, '<p>Episode ' + str(idx + 1))
    write(file, '<p>======================')
    write(file, '')
    convert_file(vtt_file, langs[main_lang_idx], langs[sub_lang_idx])
  
  write(file, "</html>")
  file.close()
