# Mahjongg Map Tool by Wa (logicplace.com)

Tool to compile, verify, and install maps for Mahjongg (found in Gnome Games).

See `mggmap.py --help` for command line help.

All map formats may have comments via the `#` symbol preceding the comment.

You can define the author and map name in comments with `Author:` and `Map:` at
the beginning of the comment (respectively). (Spaces before them don't matter.)

You may also mark the end of file with `#*` on its own line.

Note that maps are required to have exactly 144 tiles.

## Numbers as depth

Example file: [awesome.txt](awesome.txt)

Simplest format, where numbers represent how many tiles are stacked on that
space. The position of the tile is the column/row in the text. You may use
numbers, space acts as 0, unicode's mahjong set, or the progressively filled
blocks.

To display them (from 0-9):

* 0123456789
* ０１２３４５６７８９
* 🀆🀇🀈🀉🀊🀋🀌🀍🀎🀏
* 🀆🀐🀑🀒🀓🀔🀕🀖🀗🀘
* 🀆🀙🀚🀛🀜🀝🀞🀟🀠🀡
*  ▁▂▃▄▅▆▇█

All other mahjong pieces act as 0, too.

## \*grams for fine depth

Example file: [overpass.txt](overpass.txt)

In unicode there are monograms, digrams, trigrams, and hexgrams used to 
represent some simple eastern concepts. Most notably seen on the Korean flag.
You can use these to represent inconsistent stacks of tiles. Not gonna list
them here though there's too many.

Supports a depth of up to six.
