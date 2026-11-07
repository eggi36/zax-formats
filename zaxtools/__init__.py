"""Tools for the file formats of "Zax: The Alien Hunter" (Reflexive, 2001).

Modules:
    datasource  access to Data/ or Data.dat (zip), case-insensitive
    textformat  text tree for .zax/.txt/... - lossless reading and writing
    level       level (.zax) with objects, Plasma Ground, mini map
    way         way point graph (.way) read/write/check
    frm         single images (.frm/.frm16), palette
    mdl         models (.mdl16) with sequences, rotations, layers
    render      draw a level as in the game (approximation)
"""
