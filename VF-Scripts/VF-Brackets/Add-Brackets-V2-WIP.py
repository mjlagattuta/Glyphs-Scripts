import sys
import os
import re
import time
import copy
from glyphsLib import GSFont
from glyphsLib import GSGlyph
from glyphsLib import GSLayer

filename = sys.argv[-1]
font = GSFont(filename)

needsDup = []
logged = {}

def getBracketGlyphs():
    newAddition = False
    for glyph in font.glyphs:
        try:
            if logged[glyph.name] == True:
                pass
        except:
            for layer in glyph.layers:
                try:
                    if logged[glyph.name] == True:
                        break
                except:
                    if re.match('.*\d\]$', layer.name) != None:
                        needsDup.append(glyph.name)
                        logged.update({glyph.name: True})
                        newAddition = True
                        break
                    else:
                        for component in layer.components:
                            try:
                                if logged[component.name] == True:
                                    needsDup.append(glyph.name)
                                    logged.update({glyph.name: True})
                                    newAddition = True
                                    break
                            except:
                                pass
    if newAddition == True:
        getBracketGlyphs()
        
    print needsDup, len(needsDup)
            
# Recursively goes through all glyphs and determines if they will need a duplicate glyph
getBracketGlyphs()      



for i in range(len(needsDup)):
    dupGlyph = copy.deepcopy(font.glyphs[needsDup[i]])
    dupGlyph.name = needsDup[i] + ".ital"
    dupGlyph.unicode = None
    
    font.glyphs.append(dupGlyph)


    delLayer = []
    for layer in font.glyphs[dupGlyph.name].layers:         
        if re.match("\[.*\d\]$", layer.name) != None:
            dupGlyph.layers[layer.associatedMasterId].paths = layer.paths
            dupGlyph.layers[layer.associatedMasterId].anchors = layer.anchors
            dupGlyph.layers[layer.associatedMasterId].width = layer.width
            delLayer.append(layer.layerId)
        elif re.match("\].*\d\]$", layer.name) != None:
            font.glyphs[needsDup[i]].layers[layer.associatedMasterId].paths = layer.paths
            font.glyphs[needsDup[i]].layers[layer.associatedMasterId].anchors = layer.anchors
            font.glyphs[needsDup[i]].layers[layer.associatedMasterId].width = layer.width
            delLayer.append(layer.layerId)
        else:
            for component in layer.components:
                try:
                    if logged[component.name] == True:
                        component.name = component.name + ".ital"
                except:
                    pass
                    
    for layerId in delLayer:
        del font.glyphs[dupGlyph.name].layers[layerId]
        origGlyph = re.sub(".ital", "", dupGlyph.name)
        del font.glyphs[origGlyph].layers[layerId]

font.save(filename)



######## FROM MACRO:
# #MenuTitle: Check VF Bracket Layer Setup
# # -*- coding: utf-8 -*-

# __doc__="""
# For use in prepping for a variable font export
# Checks if glyphs with bracket layers are properly set up for a VF export
# Does not change anything
# """

# import GlyphsApp
# import re

# font = Glyphs.font

# needsDup = []
# logged = {}

# def getBracketGlyphs():
#     newAddition = False
#     for glyph in font.glyphs:
#         try:
#             if logged[glyph.name] == True:
#                 pass
#         except:
#             for layer in glyph.layers:
#                 try:
#                     if logged[glyph.name] == True:
#                         break
#                 except:
#                     if re.match('.*\d\]$', layer.name) != None:
#                         needsDup.append(glyph.name)
#                         logged.update({glyph.name: True})
#                         newAddition = True
#                         break
#                     else:
#                         for component in layer.components:
#                             try:
#                                 if logged[component.name] == True:
#                                     needsDup.append(glyph.name)
#                                     logged.update({glyph.name: True})
#                                     newAddition = True
#                                     break
#                             except:
#                                 pass
#     if newAddition == True:
#         getBracketGlyphs()
        
#     print needsDup, len(needsDup)
            
# # Recursively goes through all glyphs and determines if they will need a duplicate glyph
# getBracketGlyphs()      



# for i in range(len(needsDup)):
#     dupGlyph = font.glyphs[needsDup[i]].copy()
#     dupGlyph.name = needsDup[i] + ".ital"
#     dupGlyph.unicode = None
    
    
#     font.glyphs.append(dupGlyph)
#     delLayer = []
#     for layer in font.glyphs[dupGlyph.name].layers:         
#         if re.match("\[.*\d\]$", layer.name) != None:
#             dupGlyph.layers[layer.associatedMasterId] = layer.copy()
#             delLayer.append(layer.layerId)
#         elif re.match("\].*\d\]$", layer.name) != None:
#             font.glyphs[needsDup[i]].layers[layer.associatedMasterId] = layer.copy()
#             delLayer.append(layer.layerId)
#         else:
#             for component in layer.components:
#                 try:
#                     if logged[component.name] == True:
#                         component.name = component.name + ".ital"
#                 except:
#                     pass
                    
#     for layerId in delLayer:
#         del font.glyphs[dupGlyph.name].layers[layerId]