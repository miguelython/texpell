#!/usr/bin/python2
#-*- coding: utf-8 -*-
import matplotlib.pyplot as plt #No sé porque importar este modulo hace que lea bien utf-8
import aspell
import sys
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
def clean_pointuation(w):
    #Supongo que se puede hacer con una lista un diccionario o algo mejor
    if w[-3:]=="..." : w = w[:-3]
    if len(w)>0 and w[-1]=="." : w = w[:-1]
    if len(w)>0 and w[-1]==":" : w = w[:-1]
    if len(w)>0 and w[-1]==";" : w = w[:-1]
    if len(w)>0 and w[-1]=="," : w = w[:-1]
    if len(w)>0 and w[-1]=="!" : w = w[:-1]
    if len(w)>0 and w[-1]=="?" : w = w[:-1]
    if len(w)>0 and w[-1]==")" : w = w[:-1]
    if len(w)>0 and w[-1]=="]" : w = w[:-1]
    if len(w)>0 and w[0]=="(" : w = w[1:]
    if len(w)>0 and w[0]=="[" : w = w[1:]
    return w
def clean_brackets(w):
    if len(w)>0 and w[-1]=="}" : w = w[:-1]
    if len(w)>0 and w[-1]=="{" : w = w[:-1]
    if len(w)>0 and w[0]=="{" : w = w[1:]
    if len(w)>0 and w[0]=="}" : w = w[1:]
    return w
Error_found = False
if "-l" in sys.argv :
    s = aspell.Speller('lang',sys.argv[sys.argv.index("-l")+1])
else :
    s = aspell.Speller('lang', 'fr')
enc =s.ConfigKeys()[8][2]
if "-c" in sys.argv :
    name_file = sys.argv[sys.argv.index("-c")+1]
    file=open( name_file,'r')
    lines = file.readlines()
    file.close()
    math_mode = False
    math_text_mode = False
    starting_line_document = 0
    for num_line in xrange(len(lines)) :
         if "\\begin{document}" in lines[num_line] : starting_line_document=num_line
    for num_line in xrange(starting_line_document,len(lines)) :
        line = lines[num_line]
        #math_text_mode = False
        if "%" in line :
            comment_pos = line.find("%")
            line = line[:comment_pos]            
        if "\\begin" in line :
            math_mode = True
            pass
        if not math_mode :
            words = line.split()
            for word in words :
                w = clean_pointuation(word)
                w = clean_brackets(w)
                w = clean_pointuation(w)
                if not math_text_mode and "$" in w :
                    if w.find("$")==0 : 
                        math_text_mode = True
                        w = w[1:]
                    else : 
                    #No voy a corregir lo que haya pegado antes de un modo math text ya que suelen ser cifras o unidades
                    #print "inside math text mode begin"
                        w = w[w.find("$")+1:]
                        w = clean_brackets(w)
                        w = clean_pointuation(w)
                        #print "inside math text mode begin2"
                        math_text_mode = True
                if len(w)>0 and not math_text_mode :
                    if "\\" in w:
                        #latex command
                        #TO DO :add section, chapter analysis
                        pass
                    else :  
                        w = clean_brackets(w)
                        w = clean_pointuation(w)
                        if s.check(w)==0 : 
                            sugestiones = s.suggest(w)
                            Error_found = True
                            if len(sugestiones)==0 :
                                print num_line+1, bcolors.WARNING + w + bcolors.ENDC, "sin proposiciones"
                            elif len(sugestiones)==1 :
                                print num_line+1, bcolors.WARNING + w + bcolors.ENDC, "(1)", s.suggest(w)[0]
                            elif len(sugestiones)==2 :
                                print num_line+1, bcolors.WARNING + w + bcolors.ENDC , "(1)",s.suggest(w)[0],"(2)",s.suggest(w)[1]
                            else: 
                                print num_line+1, bcolors.WARNING + w + bcolors.ENDC, "(1)", s.suggest(w)[0],"(2)",s.suggest(w)[1],"(3)",s.suggest(w)[2]
                            if '--ask' in sys.argv :
                                entrada = raw_input("Choose wisely : ")
                                if entrada == "1" :
                                    s.addReplacement(w,s.suggest(w)[0])
                                elif entrada == "2" :
                                    s.addReplacement(w,s.suggest(w)[1])
                                elif entrada == "3" :
                                    s.addReplacement(w,s.suggest(w)[2])
                                elif entrada == "a" :
                                    s.addtoPersonal(w)
                                print entrada,w
                elif len(w)>0 and math_text_mode and "$" in w :
                    w = clean_brackets(w)
                    w = clean_pointuation(w)
                    if w.find("$")==len(w)-1 : 
                        #cuidado don los modos $$ $$
                        math_text_mode = False
                    else : 
                        math_text_mode = False
                        #No voy a corregir lo que viene pegado tras un modo math text ya que suelen ser cifras o unidades
                        w = w[w.find("$")+1:]
                        if "$" in w : 
                            #print "más de un modo"
                            math_text_mode = True
                            w = w[w.find("$")+1:]
                        if "$" in w : 
                            #print "más de un modo"
                            math_text_mode = False
        if "\\end" in line :
            math_mode = False
    s.saveAllwords()
    if Error_found : sys.exit( "Se encontraron errores...")
else :
    sys.exit( "Utiliza -c seguido del nombre del fichero tex que quieres comprobar")
