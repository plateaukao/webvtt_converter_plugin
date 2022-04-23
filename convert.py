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
  # within how much duration, the captions are considered the same
  threshold = 400
  last_main_start = 0
  #offset = get_time(vtt_main[0].start) - get_time(vtt_sub[0].start)
  while index_main < len(vtt_main):
    while index_sub < len(vtt_sub):
      caption_main = vtt_main[index_main]
      caption_sub = vtt_sub[index_sub]
      main_start = get_time(caption_main.start)
      sub_start = get_time(caption_sub.start) #+ offset

      if (main_start - threshold <= sub_start):
        # show space between conersation interval longer than 5 seconds
        if main_start > last_main_start + 5000:
          write(output_file, '<p/>')
        # if it's [cc], make it smaller
        text = caption_main.text.replace("&lrm;","").replace('\n', ' ')
        if text.startswith('[') and text.endswith(']'):
          write(output_file, '<div class="cc">' + text + '</div>')
        else:
          write(output_file, text)
        last_main_start = main_start
        break
      else:
        write(output_file, '<div class="sub">' + caption_sub.text.replace("&lrm;", '').replace('\n', ' ') + '</div>')
        index_sub += 1
    index_main += 1

  # finish final z index
  while index_sub < len(vtt_sub):
    write(output_file, caption_sub.text)
    index_sub += 1

# 00:00:00.000
def get_time(time_str):
  segments = time_str.split(':')
  second = segments[2].replace(',', '.').split('.')[0]
  millie_second = segments[2].replace(',', '.').split('.')[1]
  return (int(segments[0]) * 3600 + int(segments[1]) * 60 + int(second)) * 1000 + int(millie_second)

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

# S00E00
# return season number, and episod number
def get_series(file_name):
  segments = file_name.split('.')
  for idx, segment in enumerate(segments):
    if len(segment) == 6 and segment[0] == 'S' and segment[3] == 'E':
      return (int(segment[1:3]), int(segment[4:6]))
    if len(segment) == 3 and segment[0] == 'S' and segment[1].isdigit():
      return (int(segment[1:]), segments[idx+1])
  return (0, 0)
          

def convert_webvtt_to_html(vtt_dir, main_lang, sub_lang, output_file):
  files = [f for f in listdir(vtt_dir) if isfile(join(vtt_dir, f))]
  vtt_files_name = [f for f in files if re.match('.*' + main_lang.replace('[', '\[') + '\.vtt$', f)]
  vtt_files_name.sort()

  is_series = len([vtt for vtt in vtt_files_name if vtt.find('S02') != -1]) != 0

  file = open(output_file, 'w')
  write(file, "<html>")
  title = get_film_name(vtt_dir)
  write(file, "<title>" + title + "</title>")
  write(file, '<style> .sub { font-size: 60%; color: gray; margin-top: 0.2em; margin-left: 1.0em; margin-bottom:1.5em; } .cc { font-size: 70%}</style>')

  for idx, vtt_file_name in enumerate(vtt_files_name):
    vtt_file = join(vtt_dir, vtt_file_name)
    
    if is_series:
      season, episode = get_series(vtt_file_name)
      if season != 0:
        title = 'Season ' + str(season)
      if isinstance(episode, int):
        title += ' Episode ' + str(episode)
      else:
        title += ' ' + episode
      write(file, '<div class="chapter"><h1>' + title + '</h1></div>')
    else:
      write(file, '<div class="chapter"><h1>Episode ' + str(idx+1) + '</h1></div>')
    write(file, '<br>')
    write(file, '<br>')
    convert_file(vtt_file, main_lang, sub_lang, file)
  
  write(file, "</html>")
  file.close()