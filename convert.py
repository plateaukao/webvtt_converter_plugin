from calibre_plugins.webvtt_convert.webvtt import WebVTT
import sys
import argparse
import re
from os import listdir
from os.path import isfile, join
import ntpath

def write(file, str):
    file.write(str + "\n")

def rreplace(s, old, new):
  li = s.rsplit(old, 1)
  return new.join(li)

def convert_file(file_name, main_lang, sub_lang, output_file):
  if main_lang == sub_lang:
    vtt_main = WebVTT.read(file_name)
    for caption in vtt_main:
        write(output_file, "<h3>" + caption.text.replace("&lrm;","") + "</h3>")
    return

  file_name_sub = rreplace(file_name, main_lang, sub_lang)
  vtt_main = WebVTT.read(file_name)
  vtt_sub = WebVTT.read(file_name_sub)

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
def get_film_name(vtt_dir):
  files = [f for f in listdir(vtt_dir) if isfile(join(vtt_dir, f))]
  vtt_files_name = [f for f in files if re.match('.*\.vtt$', f)]
  head, tail = ntpath.split(vtt_files_name[0])
  return tail.split('.')[0]

def get_lang_list(vtt_dir):
  files = [f for f in listdir(vtt_dir) if isfile(join(vtt_dir, f))]
  vtt_files_name = [f for f in files if re.match('.*\.vtt$', f)]
  langs = map(lambda name: re.search('.*\.(.+?)\.vtt', name).group(1) ,vtt_files_name)
  langs = list(set(langs)) # uniq
  langs.sort()
  return langs

def convert_webvtt_to_html(vtt_dir, main_lang, sub_lang, output_file):
  files = [f for f in listdir(vtt_dir) if isfile(join(vtt_dir, f))]
  vtt_files_name = [f for f in files if re.match('.*' + main_lang.replace('[', '\[') + '\.vtt$', f)]
  vtt_files_name.sort()

  is_series = len([vtt for vtt in vtt_files_name if vtt.find('S02') != -1]) != 0

  file = open(output_file, 'w')
  write(file, "<html>")

  for idx, vtt_file_name in enumerate(vtt_files_name):
    vtt_file = join(vtt_dir, vtt_file_name)
    
    if is_series:
      series = vtt_file_name.split('.')[1]
      season = int(series.split('E')[0][1:])
      episode = int(series.split('E')[1])
      write(file, '<div class="chapter"><h1>Season ' + str(season) + ' Episode ' + str(episode) + '</h1></div>')
    else:
      write(file, '<div class="chapter"><h1>Episode ' + str(idx + 1) + '</h1></div>')
    write(file, '<br>')
    write(file, '<br>')
    convert_file(vtt_file, main_lang, sub_lang, file)
  
  write(file, "</html>")
  file.close()