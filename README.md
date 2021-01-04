# webvtt_converter_plugin
A Calibre plugin for webvtt subtitle files (from Netflix) conversion to epub format


## To get subtitles from Netflix service, you need to install following two plugins in your chrome browser:

**Tampermonkey** https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo?hl=en

**Netflix - subtitle downloader** https://greasyfork.org/en/scripts/26654-netflix-subtitle-downloader

## How to use the plugin

1. Install it in Calibre.
2. Select the directory that contains subtitle files, or select the download zip file.
3. (Optional) Choose an image file to be the book cover.
4. Select the main language and sub language to be contained in the ebook. sub language is also optional.
5. Press `Convert` button to start converting.

* When all is done, a book will be created in Calibre library with both html format and epub format.
* The main language text will be a bit larger, and sub language will be in gray color.
* Each episode will be put into Table of Contents for easier navigation.
* If the series includes several seasons, they will be included in Table of Contents too.

## Screenshot
<img width="404" alt="image" src="https://user-images.githubusercontent.com/4084738/102599743-e03db500-4158-11eb-997f-e2f374a9bc8d.png">


## Converted epub book

<img width="890" alt="圖片" src="https://user-images.githubusercontent.com/4084738/103549207-f92cc100-4ee1-11eb-8f5f-6fbcbee994a9.png">

