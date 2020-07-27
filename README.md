## CS Source Statistics

This script will take the text file as input, to which the CS Source Console is written. Then, it will calculate and show what happened in the game time, in which you play or watch the rounds. It will be no distinction between teams and rounds. It is a very bold calculation. Who attacks whom and with which weapon? That's all.

When you start the game, enter the command
```
con_logfile tothistext.txt
```

The game will write all the console flood to this txt file. You can find it in CS Source Installation Folder. Then, give this txt file as an argument to the Python-Script.

The calculation is based on the lines in this text file, that describe the events, in which a player killed other player.

For example:
```
Rip nimmt teil.
m_face->glyph->bitmap.width is 0 for ch:32 Verdana
m_face->glyph->bitmap.width is 0 for ch:32 Trebuchet MS
Stone killed Rip with m4a1.
Zed killed Moe with ump45.
Stone killed Ringo with m4a1.
m_face->glyph->bitmap.width is 0 for ch:32 DejaVu Sans
m_face->glyph->bitmap.width is 0 for ch:32 Verdana
```

The Script will extract all these type events, create tuples (Mr.Rip, Mr, Steel, mp5navy) and calculate.

Stone killed Rip with m4a1.

It will create an html file and open it with default browser.

Here is an example:

<p><img src="https://github.com/seyitalitek/CS-Source-Statistics-/blob/master/example_result.jpg" alt="example_screen" /></p>

### Problems

Eventlines must be stand-alone line. At least, the line must start with the name of the attacking player.
